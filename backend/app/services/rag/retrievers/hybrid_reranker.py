class HybridReranker:
    def rerank(self, documents: list[dict]) -> list[dict]:
        return sorted(
            documents,
            key=lambda item: (item.get("score", 0), len(item.get("content", ""))),
            reverse=True,
        )
