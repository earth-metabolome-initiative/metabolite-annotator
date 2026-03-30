from pathlib import Path

from metabolite_annotator.config import Config, config
from metabolite_annotator.tools.cfm import CFM


def delete_folder(pth: Path) -> None:
    for sub in pth.iterdir():
        if sub.is_dir():
            delete_folder(sub)
        else:
            sub.unlink()
    pth.rmdir()


def test_cfm_run():
    global config
    input_mgf = Path("tests/data/input.mgf")
    results_dir = Path("tests/results").resolve()
    results_dir.mkdir(parents=True, exist_ok=True)

    config = Config(results_dir=results_dir)
    config.cfmid_result_dir.mkdir(parents=True, exist_ok=True)
    cfm = CFM(config, input_mgf)
    df = cfm.annotate()
    assert len(cfm.database) > 0
    assert len(cfm.query_spectra) > 0
    assert not df.empty
    assert df.isna().sum().sum() == 0

    df.to_csv(results_dir / "cfm_results.csv", index=False)
    delete_folder(results_dir)
