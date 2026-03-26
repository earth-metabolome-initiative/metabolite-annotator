import os
from pathlib import Path

import pandas as pd
from cache_decorator import Cache
from downloaders import BaseDownloader

from .constants.cache_duration import VALIDITY_DURATION
from .constants.urls import (
    GNPS_FILENAME,
    GNPS_URL,
    ISDB_NEG_FILENAME,
    ISDB_NEG_URL,
    ISDB_POS_FILENAME,
    ISDB_POS_URL,
)


def default_cache_dir() -> Path:
    home_path: str | None = os.getenv("HOME")
    if not home_path:
        raise RuntimeError(
            "Environment variable HOME is not set ! Please set it either in your .bashrc file or or in a .env file in the current directory"
        )
    home = Path(home_path)
    return home / ".cache/metabolite-annotator"


def _set_cache_dir() -> Path:
    env_dir: str | None = os.getenv("CACHE_DIR")
    if not env_dir:
        return default_cache_dir()

    return Path(env_dir)


os.environ["CACHE_DIR"] = f"{_set_cache_dir()}"


@Cache(
    validity_duration=VALIDITY_DURATION,
)
def _download_gnps(output_dir: str) -> pd.DataFrame:
    output = Path(output_dir)
    if output.exists():
        output.unlink()

    downloader = BaseDownloader(auto_extract=False)
    return downloader.download(
        GNPS_URL,
        str(output),
    )


@Cache(
    validity_duration=VALIDITY_DURATION,
)
def _download_isdb_pos(output_dir: str) -> pd.DataFrame:
    output = Path(output_dir)
    if output.exists():
        output.unlink()

    downloader = BaseDownloader(auto_extract=False)
    return downloader.download(
        ISDB_POS_URL,
        str(output),
    )


@Cache(
    validity_duration=VALIDITY_DURATION,
)
def _download_isdb_neg(output_dir: str) -> pd.DataFrame:
    output = Path(output_dir)
    if output.exists():
        output.unlink()

    downloader = BaseDownloader(auto_extract=False)
    return downloader.download(
        ISDB_NEG_URL,
        str(output),
    )


def default_isdb_pos_dir() -> str:
    return f"{default_cache_dir()}/libraries/{ISDB_POS_FILENAME}"


def default_isdb_neg_dir() -> str:
    return f"{default_cache_dir()}/libraries/{ISDB_NEG_FILENAME}"


def default_gnps_dir() -> str:
    return f"{default_cache_dir()}/libraries/{GNPS_FILENAME}"
