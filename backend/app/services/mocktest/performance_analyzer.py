class PerformanceAnalyzer:
    def analyze(self, results: list[dict]) -> dict:
        breakdown = {}
        for result in results:
            item = breakdown.setdefault(
                result["subject"],
                {"score": 0.0, "total_marks": 0.0, "correct": 0, "incorrect": 0, "unanswered": 0},
            )
            item["score"] += result["awarded_marks"]
            item["total_marks"] += result["max_marks"]
            item["unanswered" if not result["answered"] else "correct" if result["correct"] else "incorrect"] += 1
        for item in breakdown.values():
            item["percentage"] = round(max(item["score"], 0) / item["total_marks"] * 100, 2) if item["total_marks"] else 0.0
        return breakdown
