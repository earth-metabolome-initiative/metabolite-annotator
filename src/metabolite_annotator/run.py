from pathlib import Path
from .config import Config
from .tools.sirius.sirius_config import Sirius


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

    df = sirius.results_to_dataframe()
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
