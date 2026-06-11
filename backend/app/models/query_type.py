from enum import Enum


class QueryType(str, Enum):
    TEXT = "TEXT"
    IMAGE = "IMAGE"
    HYBRID = "HYBRID"
