from metabolite_annotator.config import Config
from metabolite_annotator.data import load_isdb_pos
from metabolite_annotator.spectrum import Spectrum


def test_load_isdb_pos():
    config = Config()
    spectra = load_isdb_pos(str(config.isdb_pos_path))
    assert isinstance(spectra[0], Spectrum)
