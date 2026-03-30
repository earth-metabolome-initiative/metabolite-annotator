from metabolite_annotator.config import Config, config
from metabolite_annotator.data import load_isdb_pos
from metabolite_annotator.spectrum import Spectrum


def test_load_gnps_pos():
    spectra = load_isdb_pos()
    assert isinstance(spectra[0], Spectrum)
