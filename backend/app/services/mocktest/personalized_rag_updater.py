class PersonalizedRAGUpdater:
    def __init__(self, user_repository):
        self.user_repository = user_repository

    def update(self, user_id, record):
        user = self.user_repository.find_by_id(user_id)
        if not user or not user.user_profile:
            return
        profile = user.user_profile
        profile.performance_percentage = record.percentage
        profile.overall_progress = max(profile.overall_progress, record.percentage)
        profile.preparation_progress = min(100.0, profile.preparation_progress + 2.0)
        profile.mock_test_history.append(
            {
                "performance_id": record.performance_id,
                "mock_test_id": record.mock_test_id,
                "score": record.score,
                "total_marks": record.total_marks,
                "percentage": record.percentage,
                "attempted_at": record.attempted_at.isoformat(),
            }
        )
        self.user_repository.update(user)
