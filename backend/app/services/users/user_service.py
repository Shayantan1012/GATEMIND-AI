from app.models.branch import Branch


class UserService:
    def __init__(self, user_repository, password_service):
        self.user_repository = user_repository
        self.password_service = password_service

    def get_user_profile(self, user_id: str):
        user = self.user_repository.find_by_id(user_id)
        if not user:
            raise ValueError("User not found")
        return user.user_profile

    def update_profile(self, user_id: str, data: dict):
        user = self.user_repository.find_by_id(user_id)
        if not user:
            raise ValueError("User not found")

        profile = user.user_profile
        preferred_subjects = data.get("preferred_subjects")
        if preferred_subjects is not None:
            normalized_subjects = []
            seen_subjects = set()
            for subject in preferred_subjects:
                cleaned = str(subject).strip()
                key = cleaned.lower()
                if cleaned and key not in seen_subjects:
                    normalized_subjects.append(cleaned)
                    seen_subjects.add(key)
            profile.preferred_subjects = normalized_subjects

        profile.profile_image = str(data.get("profile_image", profile.profile_image)).strip()
        profile.headline = str(data.get("headline", profile.headline)).strip()
        profile.bio = str(data.get("bio", profile.bio)).strip()
        profile.college_name = str(data.get("college_name", profile.college_name)).strip()
        profile.current_semester = self._coerce_int(data.get("current_semester"), profile.current_semester, minimum=1, maximum=12)
        profile.graduation_year = self._coerce_int(data.get("graduation_year"), profile.graduation_year, minimum=0, maximum=2100)
        profile.daily_study_goal_hours = self._coerce_float(data.get("daily_study_goal_hours"), profile.daily_study_goal_hours, minimum=0.0, maximum=24.0)
        profile.weekly_mock_test_goal = self._coerce_int(data.get("weekly_mock_test_goal"), profile.weekly_mock_test_goal, minimum=0, maximum=14)
        profile.exam_goal_score = self._coerce_int(data.get("exam_goal_score"), profile.exam_goal_score, minimum=0, maximum=1000)

        branch = data.get("branch")
        if branch:
            normalized_branch = str(branch).strip().upper()
            if normalized_branch not in Branch._value2member_map_:
                raise ValueError("Invalid branch selected")
            user.branch = Branch(normalized_branch)

        self.user_repository.update(user)
        return user

    def update_profile_image(self, user_id: str, image_url: str):
        user = self.user_repository.find_by_id(user_id)
        if not user:
            raise ValueError("User not found")
        user.user_profile.profile_image = image_url
        self.user_repository.update(user)
        return user

    def change_password(self, user_id: str, old_password: str, new_password: str) -> bool:
        user = self.user_repository.find_by_id(user_id)
        if not user:
            raise ValueError("User not found")
        if not self.password_service.verify_password(old_password, user.password_hash):
            raise ValueError("Old password is incorrect")
        if not self.password_service.validate_password_strength(new_password):
            raise ValueError("Password must be at least 8 characters and include letters and numbers")
        user.password_hash = self.password_service.hash_password(new_password)
        self.user_repository.update(user)
        return True

    def get_preparation_progress(self, user_id: str) -> dict:
        profile = self.get_user_profile(user_id)
        return {
            "overall_progress": profile.overall_progress,
            "performance_percentage": profile.performance_percentage,
            "preparation_progress": profile.preparation_progress,
        }

    def get_mock_test_history(self, user_id: str) -> list:
        profile = self.get_user_profile(user_id)
        return profile.mock_test_history

    @staticmethod
    def _coerce_int(value, fallback: int, minimum: int | None = None, maximum: int | None = None) -> int:
        if value in (None, ""):
            return fallback
        parsed = int(value)
        if minimum is not None:
            parsed = max(minimum, parsed)
        if maximum is not None:
            parsed = min(maximum, parsed)
        return parsed

    @staticmethod
    def _coerce_float(value, fallback: float, minimum: float | None = None, maximum: float | None = None) -> float:
        if value in (None, ""):
            return fallback
        parsed = float(value)
        if minimum is not None:
            parsed = max(minimum, parsed)
        if maximum is not None:
            parsed = min(maximum, parsed)
        return parsed
