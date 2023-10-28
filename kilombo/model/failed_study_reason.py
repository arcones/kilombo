from enum import auto
from enum import Enum


class FailedStudyReason(Enum):
    GSM_FOUND = "GSM_FOUND"
    PYSRADB_NONE_TYPE = "PYSRADB_NONE_TYPE"
    PYSRADB_ARRAY_LENGTH = "PYSRADB_ARRAY_LENGTH"
