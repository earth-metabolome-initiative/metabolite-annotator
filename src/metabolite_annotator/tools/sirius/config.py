import os
from pathlib import Path

from dotenv import load_dotenv
from PySirius import AccountCredentials, SiriusSDK

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
        self.api = self.sdk.attach_or_start_sirius(headless=True)
        self.api.account().login(accept_terms, account_credentials)
        self.job_config = self.api.jobs().get_default_job_config()
        self.set_instrument_type(InstrumentType.Orbitrap)

        self.project_root: Path = config.sirius_result_dir

    def to_string(self) -> str:
        return self.job_config.to_str()

    def to_dict(self) -> dict:
        return self.job_config.to_dict()

    def to_json(self) -> str:
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
