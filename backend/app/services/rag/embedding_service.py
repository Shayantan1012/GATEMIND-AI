import hashlib
import math
import re
from abc import ABC, abstractmethod

from langchain_core.embeddings import Embeddings


class LocalHashEmbeddings(Embeddings):
    def __init__(self, dimensions: int = 384):
        self.dimensions = dimensions

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return [self._embed(text) for text in texts]

    def embed_query(self, text: str) -> list[float]:
        return self._embed(text)

    def _embed(self, text: str) -> list[float]:
        vector = [0.0] * self.dimensions
        for token in re.findall(r"[a-z0-9]+", text.lower()):
            digest = hashlib.sha256(token.encode("utf-8")).digest()
            index = int.from_bytes(digest[:4], "big") % self.dimensions
            vector[index] += -1.0 if digest[4] % 2 else 1.0
        norm = math.sqrt(sum(value * value for value in vector)) or 1.0
        return [value / norm for value in vector]


class EmbeddingFactory:
    @staticmethod
    def create(config) -> Embeddings:
        if config.get("OPENAI_API_KEY"):
            from langchain_openai import OpenAIEmbeddings

            return OpenAIEmbeddings(
                api_key=config["OPENAI_API_KEY"],
                model=config["OPENAI_EMBEDDING_MODEL"],
            )
        return LocalHashEmbeddings()


class VectorStoreAdapter(ABC):
    @abstractmethod
    def add(self, chunks: list[dict]) -> int:
        raise NotImplementedError

    @abstractmethod
    def search(
        self,
        query_vector: list[float],
        top_k: int,
        filters: dict | None = None,
        query_text: str = "",
    ) -> list[dict]:
        raise NotImplementedError


class MongoVectorStoreAdapter(VectorStoreAdapter):
    def __init__(self, rag_repository):
        self.repository = rag_repository

    def add(self, chunks: list[dict]) -> int:
        return self.repository.save_chunks(chunks)

    def search(
        self,
        query_vector: list[float],
        top_k: int,
        filters: dict | None = None,
        query_text: str = "",
    ) -> list[dict]:
        candidates = self.repository.list_chunks(filters)
        query_terms = set(re.findall(r"[a-z0-9]+", query_text.lower()))
        for item in candidates:
            semantic_score = self._cosine(query_vector, item.get("embedding", []))
            content_terms = set(re.findall(r"[a-z0-9]+", item.get("content", "").lower()))
            lexical_score = len(query_terms & content_terms) / max(len(query_terms), 1)
            item["semantic_score"] = semantic_score
            item["lexical_score"] = lexical_score
            item["score"] = (semantic_score * 0.75) + (lexical_score * 0.25)
        return sorted(candidates, key=lambda item: item["score"], reverse=True)[:top_k]

    @staticmethod
    def _cosine(first: list[float], second: list[float]) -> float:
        if not first or not second or len(first) != len(second):
            return 0.0
        return sum(left * right for left, right in zip(first, second))
