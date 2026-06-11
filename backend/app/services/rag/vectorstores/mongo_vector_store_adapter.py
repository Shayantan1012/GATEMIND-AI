import re

from app.services.rag.vectorstores.vector_store_adapter import VectorStoreAdapter


class MongoVectorStoreAdapter(VectorStoreAdapter):
    def __init__(self, rag_repository):
        self.repository = rag_repository

    def add(self, chunks: list[dict]) -> int:
        return self.repository.save_chunks(chunks)

    def search(self, query_vector, top_k, filters=None, query_text="") -> list[dict]:
        candidates = self.repository.list_chunks(filters)
        query_terms = set(re.findall(r"[a-z0-9]+", query_text.lower()))
        for item in candidates:
            semantic = self._cosine(query_vector, item.get("embedding", []))
            terms = set(re.findall(r"[a-z0-9]+", item.get("content", "").lower()))
            lexical = len(query_terms & terms) / max(len(query_terms), 1)
            item.update(semantic_score=semantic, lexical_score=lexical, score=(semantic * 0.75) + (lexical * 0.25))
        return sorted(candidates, key=lambda item: item["score"], reverse=True)[:top_k]

    @staticmethod
    def _cosine(first, second):
        if not first or not second or len(first) != len(second):
            return 0.0
        return sum(left * right for left, right in zip(first, second))
