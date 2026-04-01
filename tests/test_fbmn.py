from metabolite_annotator.config import Config
from metabolite_annotator.tools.fbmn import FBMN
from pathlib import Path


def test_similarity_matrix():
    config = Config()
    fbmn = FBMN(config=config, input_mgf=Path("tests/data/input.mgf"))
    assert fbmn.ms2_similarity_matrix.shape == (len(fbmn.spectra), len(fbmn.spectra))
    graph = fbmn.create_molecular_network()
    assert graph.number_of_nodes() == len(fbmn.spectra)
    assert 1 == 0, print(graph.get_edge_data(0, 8))
