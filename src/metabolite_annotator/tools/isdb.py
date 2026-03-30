from pathlib import Path

import ms_entropy as me
import numpy as np
import pandas as pd
from matchms import calculate_scores
from matchms.filtering import (
    default_filters,
    normalize_intensities,
    require_correct_ms_level,
)
from matchms.importing import load_from_mgf
from matchms.similarity import PrecursorMzMatch

from ..config import Config, IonMode
from ..data.data import load_isdb_neg, load_isdb_pos
from ..spectrum import Spectrum
from .spectral_db import SpectralDB


class ISDB(SpectralDB):
    def __init__(self, config: Config, input_mgf: Path) -> None:
        super().__init__(config, input_mgf)
        self.results_dir: Path = config.cfmid_result_dir
        self.database: list[Spectrum] = self.load_database()
        self.query_spectra: list[Spectrum] = self.load_mgf()

    def load_database(self) -> list[Spectrum]:
        match self.ion_mode:
            case IonMode.POS:
                return load_isdb_pos()
            case IonMode.NEG:
                return load_isdb_neg()
            case _:
                raise ValueError(f"Unsupported ionization mode: {self.ion_mode}")

    def load_mgf(self) -> list[Spectrum]:
        spectra = [i for i in load_from_mgf(self.input_mgf)]
        spectra = [i for i in spectra if require_correct_ms_level(i)]
        spectra = [default_filters(spectrum) for spectrum in spectra]
        spectra = [normalize_intensities(spectrum) for spectrum in spectra]
        spectra = [
            Spectrum(
                mz=spectrum.mz,
                intensities=spectrum.intensities,
                metadata=spectrum.metadata,
            )
            for spectrum in spectra
        ]
        return spectra

    def annotate(self) -> pd.DataFrame:
        scores = calculate_scores(
            references=self.query_spectra,
            queries=self.database,
            array_type="numpy",
            is_symmetric=False,
            similarity_function=PrecursorMzMatch(
                tolerance=self.precursor_mz_tolerance,
                tolerance_type=self.precursor_mz_tolerance_type.value,
            ),
        )
        indices = np.where(np.asarray(scores.scores.to_array()))
        idx_row, idx_col = indices
        data = []
        for x, y in tzip(idx_row, idx_col):
            msms_score, n_matches = self.ms2_similarity.pair(
                self.msg_spectra[x], self.isdb_spectra[y]
            )[()]

            entropy_sim = me.calculate_entropy_similarity(
                self.msg_spectra[x].peaks,
                self.isdb_spectra[y].peaks,
                ms2_tolerance_in_da=0.01,
            )

            data.append(
                {
                    self.ms2_similarity.__class__.__name__: msms_score,
                    "entropy_similarity": entropy_sim,
                    "matched_peaks": n_matches if n_matches is not None else np.nan,
                    "matched_ratio": n_matches
                    / max(
                        len(self.msg_spectra[x].peaks.intensities),
                        len(self.isdb_spectra[y].peaks.intensities),
                    ),
                    "feature_id": self.msg_spectra[x].get("feature_id") or x + 1,
                    "reference_id": y,  # code copied from https://github.com/mandelbrot-project/met_annot_enhancer/blob/f8346fd3f7a9775d1d6638cf091d019167ba7ce1/src/dev/spectral_lib_matcher.py#L175
                    "inchikey_isdb": self.isdb_spectra[y].get("compound_name"),
                    "smiles_isdb": self.isdb_spectra[y].get("smiles"),
                    "inchikey_msg": self.msg_spectra[x].get("inchikey"),
                    "smiles_msg": self.msg_spectra[x].get("smiles"),
                    "adduct": self.msg_spectra[x].get("adduct"),
                    "instrument": self.msg_spectra[x].get("instrument_type"),
                    "identifier": self.msg_spectra[x].get("identifier"),
                    "fold": self.msg_spectra[x].get("fold"),
                }
            )
        df = pd.DataFrame(data)
