class AdminDashboardService:
    def __init__(self, users, admins, questions, performance, rag):
        self.users = users
        self.admins = admins
        self.questions = questions
        self.performance = performance
        self.rag = rag

    def summary(self):
        return {
            "users": self.users.count(),
            "admins": self.admins.count(),
            "questions": self.questions.count_questions(),
            "mock_tests": self.questions.count_mock_tests(),
            "mock_test_attempts": self.performance.count(),
            "rag_documents": self.rag.count_documents(),
        }

    def users_overview(self, limit, skip):
        return [
            {
                "user_id": user.user_id,
                "full_name": user.full_name,
                "email": user.email,
                "mobile_number": user.mobile_number,
                "branch": user.branch.value,
                "target_gate_year": user.target_gate_year,
                "is_email_verified": user.is_email_verified,
                "account_status": user.account_status.value,
                "preferred_subjects": user.user_profile.preferred_subjects if user.user_profile else [],
                "college_name": user.user_profile.college_name if user.user_profile else "",
                "current_semester": user.user_profile.current_semester if user.user_profile else 0,
                "exam_goal_score": user.user_profile.exam_goal_score if user.user_profile else 0,
                "daily_study_goal_hours": user.user_profile.daily_study_goal_hours if user.user_profile else 0.0,
                "preparation_progress": user.user_profile.preparation_progress if user.user_profile else 0.0,
                "performance": self.performance.aggregate_user(user.user_id),
            }
            for user in self.users.find_all(limit=limit, skip=skip)
        ]
