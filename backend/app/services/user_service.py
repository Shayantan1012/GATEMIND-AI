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
        profile.preferred_subject = data.get("preferred_subject", profile.preferred_subject)
        profile.profile_image = data.get("profile_image", profile.profile_image)
        self.user_repository.update(user)
        return profile

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
# /////////////////////////////////////////////////////////////////////////////////////////////////
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
