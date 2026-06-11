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
                "branch": user.branch.value,
                "account_status": user.account_status.value,
                "performance": self.performance.aggregate_user(user.user_id),
            }
            for user in self.users.find_all(limit=limit, skip=skip)
        ]
