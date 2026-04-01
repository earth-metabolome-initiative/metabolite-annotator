import os
from dataclasses import dataclass, field
from enum import StrEnum
from pathlib import Path

from dotenv import load_dotenv
from matchms.similarity import ModifiedCosineGreedy
from matchms.similarity.BaseSimilarity import BaseSimilarity

from .constants.cache_duration import VALIDITY_DURATION
from .constants.urls import GNPS_FILENAME, ISDB_NEG_FILENAME, ISDB_POS_FILENAME

load_dotenv()


def _default_cache_dir() -> Path:
    home_path: str | None = os.getenv("HOME")
    if not home_path:
        raise RuntimeError(
            "Environment variable HOME is not set ! Please set it either in your .bashrc file or or in a .env file in the current directory"
        )
    home = Path(home_path)
    return home / ".cache/metabolite-annotator"


class IonMode(StrEnum):
    POS = "pos"
    NEG = "neg"


class PrecursorMZToleranceType(StrEnum):
    PPM = "ppm"
    DALTON = "Dalton"


@dataclass
class Config:
    project_root: Path = field(default_factory=lambda: Path.cwd())

    results_dir: Path = field(default_factory=lambda: Path.cwd() / "results")

    ionization_mode: IonMode = IonMode.POS
    precursor_mz_tolerance_type: PrecursorMZToleranceType = PrecursorMZToleranceType.PPM
    precursor_mz_tolerance: float = 20.0
    ms2_similarity: BaseSimilarity = ModifiedCosineGreedy()

    def __post_init__(self) -> None:
        if not isinstance(self.project_root, Path):
            self.project_root = Path(self.project_root)

        self.cache_dir = None

    @property
    def cache_dir(self) -> Path:
        return self._cache_dir

    @cache_dir.setter
    def cache_dir(self, value: Path | None = None) -> None:
        if value is None:
            self._cache_dir = _default_cache_dir()
        else:
            self._cache_dir = value
        os.environ["CACHE_DIR"] = str(self._cache_dir)

    @property
    def sirius_result_dir(self) -> Path:
        return self.results_dir / "sirius"

    @property
    def cfmid_result_dir(self) -> Path:
        return self.results_dir / "cfmid"

    @property
    def gnps_result_dir(self) -> Path:
        return self.results_dir / "gnps"

    @property
    def validity_duration(self) -> str:
        return VALIDITY_DURATION

    @property
    def isdb_pos_path(self) -> Path:
        return self.cache_dir / "libraries" / ISDB_POS_FILENAME

    @property
    def isdb_neg_path(self) -> Path:
        return self.cache_dir / "libraries" / ISDB_NEG_FILENAME

    @property
    def gnps_path(self) -> Path:
        return self.cache_dir / "libraries" / GNPS_FILENAME

    @property
    def sirius_user(self) -> str:
        user = os.getenv("SIRIUS_USER")
        if not user:
            raise RuntimeError(
                "Environment variable SIRIUS_USER is not set ! Please set it in a .env file in the current directory."
            )
        return user

    @property
    def sirius_pw(self) -> str:
        pw = os.getenv("SIRIUS_PW")
        if not pw:
            raise RuntimeError(
                "Environment variable SIRIUS_PW is not set ! Please set it in a .env file in the current directory."
            )
        return pw


# Module-level singleton — instantiated at import time so CACHE_DIR is set
# before any @Cache decorator in download.py or loaders.py runs.
config = Config()
