from dataclasses import dataclass, field
from typing import List


@dataclass
class UserProfile:
    profile_id: str
    preferred_subject: str = ""
    profile_image: str = ""
    overall_progress: float = 0.0
    performance_percentage: float = 0.0
    preparation_progress: float = 0.0
    mock_test_history: List[dict] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "profile_id": self.profile_id,
            "preferred_subject": self.preferred_subject,
            "profile_image": self.profile_image,
            "overall_progress": self.overall_progress,
            "performance_percentage": self.performance_percentage,
            "preparation_progress": self.preparation_progress,
            "mock_test_history": self.mock_test_history,
        }

    @staticmethod
    def from_dict(data: dict) -> "UserProfile":
        if not data:
            return None
        return UserProfile(
            profile_id=str(data.get("profile_id", "")),
            preferred_subject=data.get("preferred_subject", ""),
            profile_image=data.get("profile_image", ""),
            overall_progress=float(data.get("overall_progress", 0.0)),
            performance_percentage=float(data.get("performance_percentage", 0.0)),
            preparation_progress=float(data.get("preparation_progress", 0.0)),
            mock_test_history=list(data.get("mock_test_history", [])),
        )
