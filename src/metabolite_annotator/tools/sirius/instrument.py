from enum import Enum

from PySirius import InstrumentProfile


class InstrumentType(Enum):
    QTOF = InstrumentProfile.QTOF
    Orbitrap = InstrumentProfile.ORBITRAP
