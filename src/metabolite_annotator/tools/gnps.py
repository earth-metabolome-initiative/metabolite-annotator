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
from tqdm.contrib import tzip

from ..config import Config, IonMode
from ..data.data import load_gnps
from ..spectrum import Spectrum
from .spectral_db import SpectralDB


class GNPS(SpectralDB):
    def __init__(self, config: Config, input_mgf: Path) -> None:
        super().__init__(config, input_mgf)
        self.results_dir: Path = config.cfmid_result_dir
        self.database: list[Spectrum] = self.load_database()
        self.query_spectra: list[Spectrum] = self.load_mgf()

    def load_database(self) -> list[Spectrum]:
        spectra = load_gnps()
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
        spectra = [
            Spectrum(
                mz=spectrum.mz,
                intensities=spectrum.intensities,
                metadata=spectrum.metadata,
            )
            for spectrum in spectra
        ]
        return spectra
