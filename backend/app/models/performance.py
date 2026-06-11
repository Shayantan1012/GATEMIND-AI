from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import uuid4


@dataclass
class PerformanceRecord:
    performance_id: str
    user_id: str
    mock_test_id: str
    score: float
    total_marks: float
    correct_count: int
    incorrect_count: int
    unanswered_count: int
    subject_breakdown: dict
    answers: list[dict]
    attempted_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    @property
    def percentage(self) -> float:
        return round((self.score / self.total_marks) * 100, 2) if self.total_marks else 0.0

    def to_dict(self) -> dict:
        return {
            "_id": self.performance_id,
            "user_id": self.user_id,
            "mock_test_id": self.mock_test_id,
            "score": self.score,
            "total_marks": self.total_marks,
            "percentage": self.percentage,
            "correct_count": self.correct_count,
            "incorrect_count": self.incorrect_count,
            "unanswered_count": self.unanswered_count,
            "subject_breakdown": self.subject_breakdown,
            "answers": self.answers,
            "attempted_at": self.attempted_at,
        }

    @staticmethod
    def create(**kwargs) -> "PerformanceRecord":
        return PerformanceRecord(performance_id=str(uuid4()), **kwargs)
