from matchms.filtering import require_correct_ms_level
from matchms.importing import load_from_mgf


def test_load_sirius_mgf():
    filename = "tests/data/input.mgf"

    spectra = [i for i in load_from_mgf(filename)]
    assert len(spectra) == 19

    spectra = [i for i in spectra if require_correct_ms_level(i)]
    assert len(spectra) == 9
