import os

from dotenv import load_dotenv
from PySirius import AccountCredentials, SiriusSDK

from .instrument import InstrumentType

load_dotenv()


class Sirius:
    def __init__(self) -> None:
        self.sdk = SiriusSDK()
        accept_terms = True  # ensure you accept the terms
        account_credentials = AccountCredentials(
            username=os.getenv("SIRIUS_USER"),
            password=os.getenv("SIRIUS_PW"),
        )
        self.api = self.sdk.attach_or_start_sirius(headless=True)
        self.api.account().login(accept_terms, account_credentials)
        self.job_config = self.api.jobs().get_default_job_config()
        self.set_instrument_type()

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
