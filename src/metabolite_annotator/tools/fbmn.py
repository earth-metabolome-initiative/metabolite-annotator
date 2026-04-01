from pathlib import Path
from metabolite_annotator.config import Config
from metabolite_annotator.spectrum import Spectrum
from matchms.filtering import (
    default_filters,
    normalize_intensities,
    require_correct_ms_level,
)
from matchms.importing import load_from_mgf
from .spectral_db import SpectralDB
from typing import cast
import numpy as np
from matchms.similarity import FlashSimilarity
from sklearn.neighbors import kneighbors_graph
import networkx as nx


class FBMN(SpectralDB):
    def __init__(self, config: Config, input_mgf: Path) -> None:
        super().__init__(config, input_mgf)
        self.spectra: list[Spectrum] = self.load_mgf()
        self.ms2_similarity_matrix: np.ndarray = self.calculate_similarity_matrix()

    def load_database(self) -> list[Spectrum]:
        raise NotImplementedError("No database needed for FBMN.")

    def load_mgf(self) -> list[Spectrum]:
        if self.input_mgf.suffix.lower() != ".mgf":
            raise ValueError(
                f"Input file must be an .mgf file, got {self.input_mgf.suffix}"
            )
        spectra = [i for i in load_from_mgf(self.input_mgf)]
        spectra = [i for i in spectra if require_correct_ms_level(i)]
        spectra = [default_filters(spectrum) for spectrum in spectra]
        spectra = [normalize_intensities(spectrum) for spectrum in spectra]
        spectra = cast(list[Spectrum], spectra)
        spectra = [
            Spectrum(
                mz=spectrum.mz,
                intensities=spectrum.intensities,
                metadata=spectrum.metadata,
            )
            for spectrum in spectra
        ]
        return spectra

    def calculate_similarity_matrix(self) -> np.ndarray:
        similarity = FlashSimilarity(
            score_type=self.config.fbmn_similarity_type.value,
        )
        return similarity.matrix(
            self.spectra, self.spectra, array_type="numpy", is_symmetric=True
        )

    def create_molecular_network(self) -> nx.Graph:
        sim_matrix = self.ms2_similarity_matrix.copy()
        distance_matrix = 1 - sim_matrix
        distance_matrix = distance_matrix.clip(min=0.0, max=1.0)
        A = kneighbors_graph(
            distance_matrix,
            n_neighbors=self.config.knn_neighbours,
            mode="distance",
            include_self=False,
            metric="precomputed",
        )
        A = A.toarray()  # type: ignore

        # convert back to a similarity matrix
        np.putmask(A, A > 0.0, 1 - A)

        # drop the values below the threshold
        np.putmask(A, A < self.config.fbmn_sim_threshold, 0.0)

        G = nx.from_numpy_array(A)
        G.remove_edges_from(nx.selfloop_edges(G))
        return G
