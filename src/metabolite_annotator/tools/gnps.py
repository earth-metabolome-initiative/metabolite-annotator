from pathlib import Path
from tqdm.auto import tqdm
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
from ..data.data import load_gnps
from ..spectrum import Spectrum
from .spectral_db import SpectralDB
from typing import cast


class GNPS(SpectralDB):
    def __init__(self, config: Config, input_mgf: Path) -> None:
        super().__init__(config, input_mgf)
        self.results_dir: Path = config.gnps_result_dir
        self.database: list[Spectrum] = self.load_database()
        self.query_spectra: list[Spectrum] = self.load_mgf()

    def load_database(self) -> list[Spectrum]:
        spectra = load_gnps(str(self.config.gnps_path))
        match self.ion_mode:
            case IonMode.POS:
                return [i for i in spectra if i.get("ionmode") == "positive"]
            case IonMode.NEG:
                return [i for i in spectra if i.get("ionmode") == "negative"]
            case _:
                raise ValueError(f"Unsupported ionization mode: {self.ion_mode}")

    def load_mgf(self) -> list[Spectrum]:
        if self.input_mgf.suffix.lower() != ".mgf":
            raise ValueError(
                f"Input file must be an .mgf file, got {self.input_mgf.suffix}"
            )
        spectra = [i for i in load_from_mgf(self.input_mgf)]
        spectra = [i for i in spectra if require_correct_ms_level(i)]
        spectra = [default_filters(spectrum) for spectrum in spectra]
        spectra = [normalize_intensities(spectrum) for spectrum in spectra]
        spectra = cast(list[Spectrum], spectra)
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
        interval = 10
        chunks_query = [
            self.query_spectra[x : x + interval]
            for x in range(0, len(self.query_spectra), interval)
        ]
        scans_id_map = {}
        i = 0
        data = []
        for chunk_number, chunk in enumerate(tqdm(chunks_query)):
            scores = calculate_scores(
                references=chunk,  # type: ignore
                queries=self.database,  # type: ignore
                similarity_function=PrecursorMzMatch(
                    tolerance=self.precursor_mz_tolerance,
                    tolerance_type=self.precursor_mz_tolerance_type.value,
                ),
                is_symmetric=False,
                array_type="numpy",
            )
            indices = np.where(np.asarray(scores.scores.to_array()))
            idx_row, idx_col = indices
            for _ in chunk:
                scans_id_map[i] = i
                i += 1

            for x, y in zip(idx_row, idx_col):
                query_spectrum: Spectrum = chunk[x]
                reference_spectrum: Spectrum = self.database[y]
                if x >= y:
                    continue
                res = self.ms2_similarity.pair(query_spectrum, reference_spectrum)
                res = cast(dict, res)
                try:
                    msms_score, _ = res["score"], res["matches"]
                except:
                    msms_score = res
                    _ = None

                entropy_sim = me.calculate_entropy_similarity(
                    query_spectrum.peaks,
                    reference_spectrum.peaks,
                )
                feature_id = scans_id_map[int(x) + int(interval * chunk_number)]
                data.append(
                    {
                        self.ms2_similarity.__class__.__name__: msms_score,
                        "entropy_similarity": entropy_sim,
                        "feature_id": query_spectrum.get("feature_id") or feature_id,
                        "reference_id": y,  # code copied from https://github.com/mandelbrot-project/met_annot_enhancer/blob/f8346fd3f7a9775d1d6638cf091d019167ba7ce1/src/dev/spectral_lib_matcher.py#L175
                        "predicted_inchikey": reference_spectrum.get("inchikey")[:14], # type: ignore
                        "predicted_smiles": reference_spectrum.get("smiles"),
                        "feature_entropy": me.calculate_spectral_entropy(
                            query_spectrum.peaks
                        ),
                        "reference_entropy": me.calculate_spectral_entropy(
                            reference_spectrum.peaks
                        ),
                        "abs_precursor_mz_diff": abs(
                            query_spectrum.get("precursor_mz")  # type: ignore
                            - reference_spectrum.get("precursor_mz")
                        ),
                        "ppm_precursor_mz_diff": abs(
                            query_spectrum.get("precursor_mz")  # type: ignore
                            - reference_spectrum.get("precursor_mz")
                        )
                        / reference_spectrum.get("precursor_mz")
                        * 1e6,
                    }
                )
        df = pd.DataFrame(data)
        df["rank"] = (
            df.groupby("feature_id")["entropy_similarity"]
            .rank(ascending=False, method="first")
            .astype(int)
        )
        return df
