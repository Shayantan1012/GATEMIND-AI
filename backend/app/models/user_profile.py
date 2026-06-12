from dataclasses import dataclass, field
from typing import List


@dataclass
class UserProfile:
    profile_id: str
    preferred_subjects: List[str] = field(default_factory=list)
    profile_image: str = ""
    headline: str = ""
    bio: str = ""
    college_name: str = ""
    current_semester: int = 1
    graduation_year: int = 0
    daily_study_goal_hours: float = 0.0
    weekly_mock_test_goal: int = 0
    exam_goal_score: int = 0
    total_mock_tests: int = 0
    weak_subjects: List[str] = field(default_factory=list)
    strong_subjects: List[str] = field(default_factory=list)
    subject_performance: dict = field(default_factory=dict)
    overall_progress: float = 0.0
    performance_percentage: float = 0.0
    preparation_progress: float = 0.0
    mock_test_history: List[dict] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "profile_id": self.profile_id,
            "preferred_subjects": self.preferred_subjects,
            "profile_image": self.profile_image,
            "headline": self.headline,
            "bio": self.bio,
            "college_name": self.college_name,
            "current_semester": self.current_semester,
            "graduation_year": self.graduation_year,
            "daily_study_goal_hours": self.daily_study_goal_hours,
            "weekly_mock_test_goal": self.weekly_mock_test_goal,
            "exam_goal_score": self.exam_goal_score,
            "total_mock_tests": self.total_mock_tests,
            "weak_subjects": self.weak_subjects,
            "strong_subjects": self.strong_subjects,
            "subject_performance": self.subject_performance,
            "overall_progress": self.overall_progress,
            "performance_percentage": self.performance_percentage,
            "preparation_progress": self.preparation_progress,
            "mock_test_history": self.mock_test_history,
        }

    @staticmethod
    def from_dict(data: dict) -> "UserProfile":
        if not data:
            return None
        preferred_subjects = data.get("preferred_subjects")
        if preferred_subjects is None:
            legacy_subject = data.get("preferred_subject", "")
            preferred_subjects = [legacy_subject] if legacy_subject else []
        return UserProfile(
            profile_id=str(data.get("profile_id", "")),
            preferred_subjects=list(preferred_subjects),
            profile_image=data.get("profile_image", ""),
            headline=data.get("headline", ""),
            bio=data.get("bio", ""),
            college_name=data.get("college_name", ""),
            current_semester=int(data.get("current_semester", 1)),
            graduation_year=int(data.get("graduation_year", 0)),
            daily_study_goal_hours=float(data.get("daily_study_goal_hours", 0.0)),
            weekly_mock_test_goal=int(data.get("weekly_mock_test_goal", 0)),
            exam_goal_score=int(data.get("exam_goal_score", 0)),
            total_mock_tests=int(data.get("total_mock_tests", 0)),
            weak_subjects=list(data.get("weak_subjects", [])),
            strong_subjects=list(data.get("strong_subjects", [])),
            subject_performance=dict(data.get("subject_performance", {})),
            overall_progress=float(data.get("overall_progress", 0.0)),
            performance_percentage=float(data.get("performance_percentage", 0.0)),
            preparation_progress=float(data.get("preparation_progress", 0.0)),
            mock_test_history=list(data.get("mock_test_history", [])),
        )
