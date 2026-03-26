from metabolite_annotator.constants.urls import ISDB_POS_FILENAME
from metabolite_annotator.data import load_isdb_pos
from metabolite_annotator.download import default_cache_dir, download_isdb_pos
from metabolite_annotator.spectrum import Spectrum


def test_download_isdb_pos():
    output = f"{default_cache_dir()}/libraries/{ISDB_POS_FILENAME}"
    df = download_isdb_pos(output)
    assert not df.empty


def test_load_gnps_pos():
    spectra = load_isdb_pos()
    assert isinstance(spectra[0], Spectrum)
