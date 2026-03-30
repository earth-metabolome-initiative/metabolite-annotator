import os
from dataclasses import dataclass, field
from enum import Enum
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


class IonMode(Enum):
    POS = "pos"
    NEG = "neg"


class PrecursorMZToleranceType(Enum):
    PPM = "ppm"
    Dalton = "Dalton"


@dataclass
class Config:
    cache_dir: Path = field(default_factory=_default_cache_dir)
    project_root: Path = field(default_factory=lambda: Path.cwd())
    sirius_result_dir: Path = field(
        default_factory=lambda: Path.cwd() / "sirius_results"
    )
    cfmid_result_dir: Path = field(default_factory=lambda: Path.cwd() / "cfmid_results")
    gnps_result_dir: Path = field(default_factory=lambda: Path.cwd() / "gnps_results")

    ionization_mode: IonMode = IonMode.POS
    precursor_mz_tolerance_type: PrecursorMZToleranceType = PrecursorMZToleranceType.PPM
    precursor_mz_tolerance: float = 20.0
    ms2_similarity: BaseSimilarity = ModifiedCosineGreedy(tolerance=0.01)

    def __post_init__(self) -> None:
        if not isinstance(self.cache_dir, Path):
            self.cache_dir = Path(self.cache_dir)
        if not isinstance(self.project_root, Path):
            self.project_root = Path(self.project_root)

        os.environ["CACHE_DIR"] = str(self.cache_dir)

    @property
    def validity_duration(self) -> str:
        return VALIDITY_DURATION

    @property
    def isdb_pos_path(self) -> str:
        return str(self.cache_dir / "libraries" / ISDB_POS_FILENAME)

    @property
    def isdb_neg_path(self) -> str:
        return str(self.cache_dir / "libraries" / ISDB_NEG_FILENAME)

    @property
    def gnps_path(self) -> str:
        return str(self.cache_dir / "libraries" / GNPS_FILENAME)

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
config = Config(cache_dir=_default_cache_dir())
