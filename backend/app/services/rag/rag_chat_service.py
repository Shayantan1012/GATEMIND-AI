from datetime import datetime, timezone
from uuid import uuid4

from app.models.rag import Citation, RAGResponse


class RAGChatService:
    SYSTEM_PROMPT = (
        "You are GATEMIND, a personalized GATE preparation assistant. "
        "Answer only using the provided context. Explain concepts clearly and concisely, "
        "cite the relevant source numbers when applicable, and do not make up information. "
        "If the context is insufficient, explicitly state that you do not have enough information."
    )
    def __init__(self, repository, retriever, reranker, context_builder, llm_service, users, top_k):
        self.repository = repository
        self.retriever = retriever
        self.reranker = reranker
        self.context_builder = context_builder
        self.llm_service = llm_service
        self.users = users
        self.top_k = top_k

    def create_conversation(self, user_id: str, title: str = "New chat") -> dict:
        now = datetime.now(timezone.utc)
        conversation = {
            "_id": str(uuid4()),
            "user_id": user_id,
            "title": title.strip()[:80] or "New chat",
            "created_at": now,
            "updated_at": now,
        }
        return self.repository.save_conversation(conversation)

    def ask(self, user_id: str, query: str, filters: dict | None = None, conversation_id: str | None = None) -> tuple[RAGResponse, dict]:
        if not query.strip():
            raise ValueError("query is required")
        conversation = (
            self.repository.find_conversation(conversation_id, user_id)
            if conversation_id
            else self.create_conversation(user_id, query)
        )
        if not conversation:
            raise ValueError("Conversation not found")
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
                "preferred_subjects": user.user_profile.preferred_subjects,
                "performance_percentage": user.user_profile.performance_percentage,
                "preparation_progress": user.user_profile.preparation_progress,
                "total_mock_tests": user.user_profile.total_mock_tests,
                "weak_subjects": user.user_profile.weak_subjects,
                "strong_subjects": user.user_profile.strong_subjects,
                "subject_performance": user.user_profile.subject_performance,
            }
        previous_messages = self.repository.list_chats(user_id, conversation["_id"], limit=12)
        conversation_context = self._conversation_context(previous_messages)
        context = self.context_builder.build(retrieved, profile)
        if conversation_context:
            context = f"Recent conversation:\n{conversation_context}\n\n{context}".strip()
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
        now = datetime.now(timezone.utc)
        self.repository.save_chat(
            {
                "_id": str(uuid4()),
                "conversation_id": conversation["_id"],
                "user_id": user_id,
                "query": query,
                "answer": answer,
                "citations": [item.to_dict() for item in citations],
                "filters": filters or {},
                "created_at": now,
            }
        )
        if conversation["title"] == "New chat":
            conversation["title"] = self._title_from_query(query)
        conversation["updated_at"] = now
        self.repository.save_conversation(conversation)
        return response, conversation

    def conversations(self, user_id: str) -> list[dict]:
        return self.repository.list_conversations(user_id)

    def history(self, user_id: str, conversation_id: str | None = None) -> list[dict]:
        if conversation_id and not self.repository.find_conversation(conversation_id, user_id):
            raise ValueError("Conversation not found")
        return self.repository.list_chats(user_id, conversation_id)

    def delete_conversation(self, user_id: str, conversation_id: str) -> bool:
        if not self.repository.delete_conversation(conversation_id, user_id):
            raise ValueError("Conversation not found")
        return True

    @staticmethod
    def _title_from_query(query: str) -> str:
        cleaned = " ".join(query.strip().split())
        return cleaned[:60] + ("..." if len(cleaned) > 60 else "")

    @staticmethod
    def _conversation_context(messages: list[dict]) -> str:
        sections = []
        for message in messages[-6:]:
            sections.append(f"User: {message.get('query', '')}\nAssistant: {message.get('answer', '')[:800]}")
        return "\n\n".join(sections)
