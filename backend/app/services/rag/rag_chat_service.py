from datetime import datetime, timezone
from uuid import uuid4

from app.models.rag import Citation, RAGResponse


class RAGChatService:
    SYSTEM_PROMPT = (
        "You are GATEMIND, a precise GATE preparation assistant. Answer using only the supplied "
        "context. Explain reasoning clearly, mention uncertainty, and refer to citation numbers."
    )

    def __init__(self, repository, retriever, reranker, context_builder, llm_service, users, top_k):
        self.repository = repository
        self.retriever = retriever
        self.reranker = reranker
        self.context_builder = context_builder
        self.llm_service = llm_service
        self.users = users
        self.top_k = top_k

    def ask(self, user_id: str, query: str, filters: dict | None = None) -> RAGResponse:
        if not query.strip():
            raise ValueError("query is required")
        document_ids = (filters or {}).get("document_ids", [])
        if document_ids:
            documents = self.repository.find_documents_by_ids(document_ids)
            owned_ids = {item["_id"] for item in documents if item.get("uploaded_by") == user_id}
            if owned_ids != set(document_ids):
                raise ValueError("One or more attached documents are unavailable")
        retrieved = self.reranker.rerank(self.retriever.retrieve(query, filters))[: self.top_k]
        user = self.users.find_by_id(user_id)
        profile = None
        if user and user.user_profile:
            profile = {
                "preferred_subject": user.user_profile.preferred_subject,
                "performance_percentage": user.user_profile.performance_percentage,
                "preparation_progress": user.user_profile.preparation_progress,
            }
        context = self.context_builder.build(retrieved, profile)
        answer = self.llm_service.generate(self.SYSTEM_PROMPT, context, query)
        citations = [
            Citation(
                document_id=item["document_id"],
                source=item.get("metadata", {}).get("source", "unknown"),
                page_no=item.get("metadata", {}).get("page_no"),
                chunk_id=str(item["_id"]),
            )
            for item in retrieved
        ]
        response = RAGResponse(answer=answer, citations=citations)
        self.repository.save_chat(
            {
                "_id": str(uuid4()),
                "user_id": user_id,
                "query": query,
                "answer": answer,
                "citations": [item.to_dict() for item in citations],
                "filters": filters or {},
                "created_at": datetime.now(timezone.utc),
            }
        )
        return response

    def history(self, user_id: str) -> list[dict]:
        return self.repository.list_chats(user_id)
