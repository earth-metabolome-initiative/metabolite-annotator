from .config import Config
from pathlib import Path


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
