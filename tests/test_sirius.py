from metabolite_annotator.tools import Sirius


def test_default_config():
    sirus = Sirius()
    assert sirus.to_dict()["formulaIdParams"]["massAccuracyMS2ppm"] == 5.0
