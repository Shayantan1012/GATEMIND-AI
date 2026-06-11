from enum import Enum


class QuestionType(str, Enum):
    MCQ = "MCQ"
    MSQ = "MSQ"
    NAT = "NAT"
