from cache_decorator import Cache
from matchms.filtering import default_filters, normalize_intensities
from matchms.importing import load_from_mgf
from tqdm.auto import tqdm

from ..config import config
from ..spectrum import Spectrum
from .download import _download_gnps, _download_isdb_neg, _download_isdb_pos


@Cache(
    validity_duration=config.validity_duration,
)
def load_gnps(file_name: str | None = None) -> list[Spectrum]:
    if not file_name:
        filename = str(config.gnps_path)
    else:
        filename = file_name

    _ = _download_gnps(filename)
    spectra = []
    for spectrum in tqdm(
        load_from_mgf(filename),
        desc="Loading GNPS spectra",
        leave=False,
    ):
        # spectrum = default_filters(spectrum) TODO: do we actually want to clean this ? It comes from Zenodo where it is already cleaned.
        # spectrum = normalize_intensities(spectrum)
        spectrum = Spectrum(
            mz=spectrum.mz,
            intensities=spectrum.intensities,
            metadata=spectrum.metadata,
        )
        spectra.append(spectrum)
    return spectra


@Cache(
    validity_duration=config.validity_duration,
)
def load_isdb_pos(file_name: str | None = None) -> list[Spectrum]:
    if not file_name:
        filename = str(config.isdb_pos_path)
    else:
        filename = file_name

    _ = _download_isdb_pos(filename)
    spectra = []
    for spectrum in tqdm(
        load_from_mgf(filename),
        desc="Loading ISDB positive spectra",
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


@Cache(
    validity_duration=config.validity_duration,
)
def load_isdb_neg(file_name: str | None = None) -> list[Spectrum]:
    if not file_name:
        filename = config.isdb_neg_path
    else:
        filename = file_name

    _ = _download_isdb_neg(filename)
    spectra = []
    for spectrum in tqdm(
        load_from_mgf(filename),
        desc="Loading ISDB negative spectra",
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
