from pathlib import Path

import pandas as pd
from cache_decorator import Cache
from downloaders import BaseDownloader

from ..config import config
from ..constants.urls import GNPS_URL, ISDB_NEG_URL, ISDB_POS_URL


@Cache(
    validity_duration=config.validity_duration,
    cache_dir=str(config.cache_dir),
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
    validity_duration=config.validity_duration,
    cache_dir=str(config.cache_dir),
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
    validity_duration=config.validity_duration,
    cache_dir=str(config.cache_dir),
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
