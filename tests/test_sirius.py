from pathlib import Path
from metabolite_annotator.config import config
from metabolite_annotator.tools.sirius.sirius_config import Sirius


def test_default_config():
    global config
    sirius = Sirius(config)
    assert sirius.job_config_to_dict()["formulaIdParams"]["massAccuracyMS2ppm"] == 5.0
    assert sirius.shutdown() is None


def test_create_project():
    global config
    sirius = Sirius(config)
    project_path = Path("test_project")
    sirius.create_project(project_path)
    assert project_path.with_suffix(".sirius").exists()

    # We remove the file after the test
    project_path.with_suffix(".sirius").unlink()
    assert sirius.shutdown() is None


def test_run():
    global config
    sirius = Sirius(config)
    project_path = Path("test_project")
    sirius.create_project(project_path)
    assert project_path.with_suffix(".sirius").exists()

    input_mgf = Path("tests/data/input.mgf")
    assert input_mgf.exists()

    sirius.import_spectra(input_mgf)
    sirius.run()

    # all structure annotations for our feature
    first_feature = sirius.api.features().get_aligned_features(
        sirius.project_info.project_id
    )[0]
    feature_structure_annotations = sirius.api.features().get_structure_candidates(
        sirius.project_info.project_id,
        first_feature.aligned_feature_id,
    )
    # best ranking structure SMILES
    assert feature_structure_annotations[0].to_dict()["inchiKey"] == "AXFAVZQXPFQIEI"
    # res = []
    # for feature in sirius.api.features().get_aligned_features(
    #     sirius.project_info.project_id
    # ):
    #     for annotation in sirius.api.features().get_structure_candidates(
    #         sirius.project_info.project_id,
    #         feature.aligned_feature_id,
    #     ):
    #         d = annotation.to_dict()
    #         d["feature_id"] = feature.external_feature_id
    #         res.append(d)

    # We remove the file after the test
    project_path.with_suffix(".sirius").unlink()
    sirius.shutdown()
