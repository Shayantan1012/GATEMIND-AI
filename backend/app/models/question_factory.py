from uuid import uuid4

from app.models.enums import QuestionType
from app.models.question import Question


class QuestionFactory:
    @staticmethod
    def create(data: dict, created_by: str) -> Question:
        question_type = QuestionType(data.get("question_type", "MCQ").upper())
        options = list(data.get("options", []))
        if question_type in {QuestionType.MCQ, QuestionType.MSQ} and len(options) < 2:
            raise ValueError("MCQ and MSQ questions require at least two options")
        return Question(
            question_id=str(uuid4()),
            question_type=question_type,
            prompt=data["prompt"].strip(),
            subject=data["subject"].strip(),
            marks=float(data.get("marks", 1)),
            negative_marks=float(data.get("negative_marks", 0)),
            correct_answer=data["correct_answer"],
            options=options,
            explanation=data.get("explanation", "").strip(),
            source=data.get("source", "").strip(),
            created_by=created_by,
        )
