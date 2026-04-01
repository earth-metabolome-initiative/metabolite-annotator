from abc import ABC, abstractmethod
from pathlib import Path

from matchms.similarity.BaseSimilarity import BaseSimilarity

from metabolite_annotator.config import Config, IonMode, PrecursorMZToleranceType
from metabolite_annotator.spectrum import Spectrum


class SpectralDB(ABC):
    def __init__(self, config: Config, input_mgf: Path) -> None:
        self.input_mgf: Path = input_mgf
        self.ion_mode: IonMode = config.ionization_mode
        self.precursor_mz_tolerance_type: PrecursorMZToleranceType = (
            config.precursor_mz_tolerance_type
        )
        self.precursor_mz_tolerance: float = config.precursor_mz_tolerance
        self.ms2_similarity: BaseSimilarity = config.ms2_similarity
        self.config: Config = config

    @abstractmethod
    def load_database(self) -> list[Spectrum]:
        raise NotImplementedError("Subclasses must implement this method.")

    @abstractmethod
    def load_mgf(self) -> list[Spectrum]:
        raise NotImplementedError("Subclasses must implement this method.")
