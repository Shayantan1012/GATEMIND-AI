from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import uuid4

from app.models.enums import QuestionType


@dataclass
class Question:
    question_id: str
    question_type: QuestionType
    prompt: str
    subject: str
    marks: float
    negative_marks: float
    correct_answer: object
    options: list[str] = field(default_factory=list)
    explanation: str = ""
    source: str = ""
    created_by: str = ""
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> dict:
        return {
            "_id": self.question_id,
            "question_type": self.question_type.value,
            "prompt": self.prompt,
            "subject": self.subject,
            "marks": self.marks,
            "negative_marks": self.negative_marks,
            "correct_answer": self.correct_answer,
            "options": self.options,
            "explanation": self.explanation,
            "source": self.source,
            "created_by": self.created_by,
            "created_at": self.created_at,
        }

    def public_dict(self) -> dict:
        data = self.to_dict()
        data["question_id"] = data.pop("_id")
        data.pop("correct_answer", None)
        data.pop("explanation", None)
        return data

    @staticmethod
    def from_dict(data: dict) -> "Question":
        return Question(
            question_id=str(data["_id"]),
            question_type=QuestionType(data["question_type"]),
            prompt=data["prompt"],
            subject=data["subject"],
            marks=float(data.get("marks", 1)),
            negative_marks=float(data.get("negative_marks", 0)),
            correct_answer=data.get("correct_answer"),
            options=list(data.get("options", [])),
            explanation=data.get("explanation", ""),
            source=data.get("source", ""),
            created_by=data.get("created_by", ""),
            created_at=data.get("created_at", datetime.now(timezone.utc)),
        )


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
