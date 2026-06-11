from app.services.rag.retrievers.retriever import Retriever


class HybridRetriever(Retriever):
    def __init__(self, vector_store, embeddings, top_k: int):
        self.vector_store = vector_store
        self.embeddings = embeddings
        self.top_k = top_k

    def retrieve(self, query: str, filters: dict | None = None) -> list[dict]:
        storage_filters = {
            key if key == "document_id" else f"metadata.{key}": value
            for key, value in (filters or {}).items()
        }
        return self.vector_store.search(
            self.embeddings.embed_query(query),
            self.top_k * 2,
            storage_filters or None,
            query,
        )
