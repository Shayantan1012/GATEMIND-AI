from enum import Enum


class Branch(str, Enum):
    CSE = "CSE"
    ECE = "ECE"
    EE = "EE"
    ME = "ME"
    CE = "CE"
    OTHER = "OTHER"
