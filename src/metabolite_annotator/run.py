from pathlib import Path
from .config import Config
from .tools.sirius.sirius_config import Sirius
import networkx as nx
import pandas as pd


def _run_cfmid(config: Config, input_mgf: Path) -> None:
    from .tools.cfm import CFM

    config.cfmid_result_dir.mkdir(parents=True, exist_ok=True)
    cfm = CFM(config=config, input_mgf=input_mgf)
    df = cfm.annotate()
    output_file = config.cfmid_result_dir / "annotation_results.csv"
    df.to_csv(output_file, index=False)


def _run_gnps(config: Config, input_mgf: Path) -> None:
    from .tools.gnps import GNPS

    config.gnps_result_dir.mkdir(parents=True, exist_ok=True)
    gnps = GNPS(config=config, input_mgf=input_mgf)
    df = gnps.annotate()
    output_file = config.gnps_result_dir / "annotation_results.csv"
    df.to_csv(output_file, index=False)


def _run_sirius(
    config: Config,
    input_mgf: Path,
    project_name: str,
    ms2_only: bool = False,
) -> None:
    config.sirius_result_dir.mkdir(parents=True, exist_ok=True)
    sirius = Sirius(config=config)
    project_path = config.sirius_result_dir / project_name
    sirius.create_project(path_to_project=project_path, project_name=project_name)
    if ms2_only:
        _sirius_ms2_only(sirius, input_mgf)
    else:
        _sirius_all(sirius, input_mgf)

    df = sirius.get_structure_candidates()
    output_file = config.sirius_result_dir / "annotation_results.csv"
    df.to_csv(output_file, index=False)
    if project_path.with_suffix(".sirius").exists():
        project_path.with_suffix(".sirius").unlink()
    sirius.shutdown()


def _sirius_all(sirius: Sirius, input_mgf: Path):
    sirius.import_spectra(input_mgf)
    sirius.run()


def _sirius_ms2_only(sirius: Sirius, input_mgf: Path):
    from matchms.importing import load_from_mgf
    from matchms.filtering import require_correct_ms_level
    from matchms.exporting import save_as_mgf

    spectra = [i for i in load_from_mgf(input_mgf)]
    spectra = [i for i in spectra if require_correct_ms_level(i)]
    for s in spectra:
        s.set("PEPMASS", s.get("precursor_mz"))

    mgf_path = input_mgf.with_suffix(".ms2_only.mgf")
    save_as_mgf(spectra, str(mgf_path), file_mode="w")
    sirius.import_spectra(mgf_path)
    sirius.run()


def _run_fbmn(config: Config, input_file: Path):
    from .tools.fbmn import FBMN

    config.fbmn_result_dir.mkdir(parents=True, exist_ok=True)
    molecular_network_file = config.fbmn_result_dir / "fbmn_network.graphml"
    fbmn = FBMN(config=config, input_mgf=input_file)

    graph = fbmn.create_molecular_network()

    for spectrum, node_id in zip(fbmn.spectra, graph.nodes):
        graph.nodes[node_id]["precursor_mz"] = spectrum.get("precursor_mz")
        graph.nodes[node_id]["feature_id"] = int(spectrum.get("feature_id"))
        graph.nodes[node_id]["charge"] = spectrum.get("charge")
        graph.nodes[node_id]["RT_seconds"] = spectrum.get("retention_time")

    if (config.cfmid_result_dir / "annotation_results.csv").exists():
        df = pd.read_csv(config.cfmid_result_dir / "annotation_results.csv")
        _add_metadata_to_graph(graph, df, prefix="cfmid")

    if (config.gnps_result_dir / "annotation_results.csv").exists():
        df = pd.read_csv(config.gnps_result_dir / "annotation_results.csv")
        _add_metadata_to_graph(graph, df, prefix="gnps")

    if (config.gnps_result_dir / "annotation_results.csv").exists():
        df = pd.read_csv(config.gnps_result_dir / "annotation_results.csv")
        _add_metadata_to_graph(graph, df, prefix="sirius")

    nx.write_graphml(graph, molecular_network_file)


def _add_metadata_to_graph(graph: nx.Graph, df: pd.DataFrame, prefix: str) -> None:
    df = df[df["rank"] == 1]
    df.set_index("feature_id", inplace=True)
    d = df.to_dict(orient="index")

    node_id_feature_id_pairs = list(graph.nodes(data="feature_id"))

    for node_id, feature_id in node_id_feature_id_pairs:
        dict_for_feature = d[feature_id]
        for key in list(
            dict_for_feature.keys()
        ):  # have to create a list else we change the dict in the iteration and returns an error
            dict_for_feature[prefix + "_" + key] = dict_for_feature.pop(key)

        graph.nodes[node_id].update(dict_for_feature)
