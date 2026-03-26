from cache_decorator import Cache
from matchms.filtering import default_filters, normalize_intensities
from matchms.importing import load_from_mgf
from tqdm.auto import tqdm

from .constants.cache_duration import VALIDITY_DURATION
from .download import (
    default_gnps_dir,
    default_isdb_neg_dir,
    default_isdb_pos_dir,
    download_gnps,
    download_isdb_neg,
    download_isdb_pos,
)
from .spectrum import Spectrum


@Cache(validity_duration=VALIDITY_DURATION)
def load_gnps(file_name: str | None = None) -> list[Spectrum]:
    if not file_name:
        filename = default_gnps_dir()
    else:
        filename = file_name

    _ = download_gnps(filename)
    spectra = []
    for spectrum in tqdm(
        load_from_mgf(filename),
        desc="Loading GNPS spectra",
        leave=False,
    ):
        spectrum = Spectrum(
            mz=spectrum.mz,
            intensities=spectrum.intensities,
            metadata=spectrum.metadata,
        )
        spectra.append(spectrum)
    return spectra


@Cache(validity_duration=VALIDITY_DURATION)
def load_isdb_pos(file_name: str | None = None) -> list[Spectrum]:
    if not file_name:
        filename = default_isdb_pos_dir()
    else:
        filename = file_name

    _ = download_isdb_pos(filename)
    spectra = []
    for spectrum in tqdm(
        load_from_mgf(filename),
        desc="Loading GNPS spectra",
        leave=False,
    ):
        spectrum = default_filters(spectrum)
        spectrum = normalize_intensities(spectrum)
        spectrum = Spectrum(
            mz=spectrum.mz,
            intensities=spectrum.intensities,
            metadata=spectrum.metadata,
        )
        spectra.append(spectrum)
    return spectra


@Cache(validity_duration=VALIDITY_DURATION)
def load_isdb_neg(file_name: str | None = None) -> list[Spectrum]:
    if not file_name:
        filename = default_isdb_neg_dir()
    else:
        filename = file_name

    _ = download_isdb_neg(filename)
    spectra = []
    for spectrum in tqdm(
        load_from_mgf(filename),
        desc="Loading GNPS spectra",
        leave=False,
    ):
        spectrum = default_filters(spectrum)
        spectrum = normalize_intensities(spectrum)
        spectrum = Spectrum(
            mz=spectrum.mz,
            intensities=spectrum.intensities,
            metadata=spectrum.metadata,
        )
        spectra.append(spectrum)
    return spectra
