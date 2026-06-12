class PersonalizedRAGUpdater:
    def __init__(self, user_repository):
        self.user_repository = user_repository

    def update(self, user_id, record):
        user = self.user_repository.find_by_id(user_id)
        if not user or not user.user_profile:
            return
        profile = user.user_profile
        previous_attempts = profile.total_mock_tests
        profile.total_mock_tests += 1
        profile.performance_percentage = round(
            ((profile.performance_percentage * previous_attempts) + record.percentage) / profile.total_mock_tests,
            2,
        )
        profile.overall_progress = max(profile.overall_progress, record.percentage)
        answered = record.correct_count + record.incorrect_count
        completion_ratio = answered / max(answered + record.unanswered_count, 1)
        profile.preparation_progress = min(100.0, round(profile.preparation_progress + (completion_ratio * 2.0), 2))

        for subject, result in record.subject_breakdown.items():
            previous = profile.subject_performance.get(subject, {"attempts": 0, "average_percentage": 0.0})
            attempts = int(previous.get("attempts", 0)) + 1
            average = round(
                ((float(previous.get("average_percentage", 0.0)) * (attempts - 1)) + result["percentage"]) / attempts,
                2,
            )
            profile.subject_performance[subject] = {
                "attempts": attempts,
                "average_percentage": average,
                "latest_percentage": result["percentage"],
            }

        profile.weak_subjects = [
            subject
            for subject, result in sorted(
                profile.subject_performance.items(),
                key=lambda item: item[1]["average_percentage"],
            )
            if result["average_percentage"] < 50
        ][:5]
        profile.strong_subjects = [
            subject
            for subject, result in sorted(
                profile.subject_performance.items(),
                key=lambda item: item[1]["average_percentage"],
                reverse=True,
            )
            if result["average_percentage"] >= 70
        ][:5]
        profile.mock_test_history.append(
            {
                "performance_id": record.performance_id,
                "mock_test_id": record.mock_test_id,
                "mock_test_title": record.mock_test_title,
                "score": record.score,
                "total_marks": record.total_marks,
                "percentage": record.percentage,
                "time_taken_seconds": record.time_taken_seconds,
                "subject_breakdown": record.subject_breakdown,
                "attempted_at": record.attempted_at.isoformat(),
            }
        )
        self.user_repository.update(user)
