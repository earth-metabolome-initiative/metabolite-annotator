from pathlib import Path
from typing import Literal
import pandas as pd
from PySirius import (
    AccountCredentials,
    ProjectInfo,
    PySiriusAPI,
    SiriusSDK,
    AlignedFeature,
    AlignedFeatureOptField,
)

from metabolite_annotator.config import Config

from .instrument import InstrumentType


class Sirius:
    def __init__(self, config: Config) -> None:
        self.sdk = SiriusSDK()
        accept_terms = True  # ensure you accept the terms
        account_credentials = AccountCredentials(
            username=config.sirius_user,
            password=config.sirius_pw,
        )
        api = self.sdk.attach_or_start_sirius(headless=True)
        if not api:
            raise RuntimeError("Failed to start Sirius API.")
        self.api: PySiriusAPI = api
        self.api.account().login(accept_terms, account_credentials)
        self.job_config = self.api.jobs().get_default_job_config()
        self.set_instrument_type(config.sirius_instrument_type)

        self.project_root: Path = config.sirius_result_dir
        self.project_info: ProjectInfo | None = None

    def job_config_to_string(self) -> str:
        return self.job_config.to_str()

    def job_config_to_dict(self) -> dict:
        return self.job_config.to_dict()

    def job_config_to_json(self) -> str:
        return self.job_config.to_json()

    def set_instrument_type(
        self,
        instrument_type: InstrumentType = InstrumentType.Orbitrap,
    ) -> None:
        match instrument_type:
            case InstrumentType.Orbitrap:
                self.job_config.formula_id_params.profile = (
                    InstrumentType.Orbitrap.value
                )
                self.job_config.formula_id_params.mass_accuracy_ms2ppm = 5.0

            case InstrumentType.QTOF:
                self.job_config.formula_id_params.profile = InstrumentType.QTOF.value
                self.job_config.formula_id_params.mass_accuracy_ms2ppm = 10.0

            case _:
                raise ValueError("Unkown instrument type")

    def create_project(
        self, path_to_project: Path, project_name: str | None = None
    ) -> None:
        if not project_name:
            project_name = path_to_project.stem
        self.project_info = self.api.projects().create_project(
            project_id=project_name, path_to_project=str(path_to_project.resolve())
        )

    def import_spectra(self, spectra_file: Path) -> None:
        if not self.project_info:
            raise ValueError("A project must be created before importing spectra.")

        import_job = self.api.projects().import_preprocessed_data_as_job(
            self.project_info.project_id,
            input_files=[str(spectra_file.resolve())],
        )
        self.api.wait_for_job_completion(self.project_info, import_job)

    def shutdown(self) -> Literal[False] | None:
        if self.project_info:
            self.api.projects().close_project(self.project_info.project_id)
        return self.sdk.shutdown_sirius()

    def run(self) -> None:
        if not self.project_info:
            raise ValueError("A project must be created before running a job.")
        job = self.api.jobs().start_job(self.project_info.project_id, self.job_config)
        self.api.wait_for_job_completion(self.project_info, job)

    def get_structure_candidates(self) -> pd.DataFrame:
        res = []
        for feature in self.api.features().get_aligned_features(
            self.project_info.project_id,
            opt_fields=[AlignedFeatureOptField.TOPANNOTATIONS],
        ):
            for annotation in self.api.features().get_structure_candidates(
                self.project_info.project_id,
                feature.aligned_feature_id,
            ):
                d = annotation.to_dict()
                d["feature_id"] = feature.external_feature_id
                self._add_npc_metadata(feature=feature, d=d)
                res.append(d)

        df = pd.DataFrame(res)
        df.drop(
            columns=[
                "fingerprint",
                "structureSvg",
                "spectralLibraryMatches",
                "dbLinks",
                "structureName",
            ],
            inplace=True,
        )
        return df

    def _add_npc_metadata(self, feature: AlignedFeature, d: dict) -> dict:
        if feature.top_annotations:
            d["npc_pathway"] = (
                feature.top_annotations.compound_class_annotation.npc_pathway.name
            )
            d["npc_superclass"] = (
                feature.top_annotations.compound_class_annotation.npc_superclass.name
            )
            d["npc_class"] = (
                feature.top_annotations.compound_class_annotation.npc_class.name
            )
        return d
