from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import uuid4


@dataclass
class MockTest:
    mock_test_id: str
    title: str
    question_ids: list[str]
    duration_minutes: int
    created_by: str
    is_published: bool = False
    description: str = ""
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> dict:
        return {
            "_id": self.mock_test_id,
            "title": self.title,
            "description": self.description,
            "question_ids": self.question_ids,
            "duration_minutes": self.duration_minutes,
            "created_by": self.created_by,
            "is_published": self.is_published,
            "created_at": self.created_at,
        }

    @staticmethod
    def from_dict(data: dict) -> "MockTest":
        return MockTest(
            mock_test_id=str(data["_id"]),
            title=data["title"],
            description=data.get("description", ""),
            question_ids=list(data.get("question_ids", [])),
            duration_minutes=int(data.get("duration_minutes", 60)),
            created_by=data.get("created_by", ""),
            is_published=data.get("is_published", False),
            created_at=data.get("created_at", datetime.now(timezone.utc)),
        )

    @staticmethod
    def create(data: dict, created_by: str) -> "MockTest":
        return MockTest(
            mock_test_id=str(uuid4()),
            title=data["title"].strip(),
            description=data.get("description", "").strip(),
            question_ids=list(data["question_ids"]),
            duration_minutes=int(data.get("duration_minutes", 60)),
            created_by=created_by,
            is_published=bool(data.get("is_published", False)),
        )
