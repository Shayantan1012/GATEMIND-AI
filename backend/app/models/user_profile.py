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
