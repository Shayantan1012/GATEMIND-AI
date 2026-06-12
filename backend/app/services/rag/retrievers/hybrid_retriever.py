from app.services.rag.retrievers.retriever import Retriever


class HybridRetriever(Retriever):
    def __init__(self, vector_store, embeddings, top_k: int):
        self.vector_store = vector_store
        self.embeddings = embeddings
        self.top_k = top_k

    def retrieve(self, query: str, filters: dict | None = None) -> list[dict]:
        storage_filters = {}
        for key, value in (filters or {}).items():
            if key == "document_ids":
                storage_filters["document_id"] = {"$in": list(value)}
            elif key == "document_id":
                storage_filters["document_id"] = value
            else:
                storage_filters[f"metadata.{key}"] = value
        return self.vector_store.search(
            self.embeddings.embed_query(query),
            self.top_k * 2,
            storage_filters or None,
            query,
        )
