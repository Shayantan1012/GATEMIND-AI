from abc import ABC, abstractmethod
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from langchain_core.prompts import ChatPromptTemplate

from app.models.rag import Citation, RAGResponse


class IndexingPipeline(ABC):
    def execute(self, file_path: Path, uploaded_by: str, metadata: dict | None = None) -> dict:
        document_id = str(uuid4())
        documents = self.parse(file_path)
        chunks = self.process(documents)
        return self.store(document_id, file_path, uploaded_by, chunks, metadata or {})

    @abstractmethod
    def parse(self, file_path: Path):
        raise NotImplementedError

    @abstractmethod
    def process(self, documents):
        raise NotImplementedError

    @abstractmethod
    def store(self, document_id, file_path, uploaded_by, chunks, metadata):
        raise NotImplementedError


class LangChainIndexingPipeline(IndexingPipeline):
    def __init__(self, repository, vector_store, embeddings, parser_factory, chunking_strategy):
        self.repository = repository
        self.vector_store = vector_store
        self.embeddings = embeddings
        self.parser_factory = parser_factory
        self.chunking_strategy = chunking_strategy

    def parse(self, file_path: Path):
        return self.parser_factory.create(file_path).parse(file_path)

    def process(self, documents):
        return self.chunking_strategy.split(documents)

    def store(self, document_id, file_path, uploaded_by, chunks, metadata):
        uploaded_at = datetime.now(timezone.utc)
        texts = [chunk.page_content for chunk in chunks]
        vectors = self.embeddings.embed_documents(texts)
        chunk_records = []
        for index, (chunk, vector) in enumerate(zip(chunks, vectors)):
            chunk_records.append(
                {
                    "_id": str(uuid4()),
                    "document_id": document_id,
                    "chunk_index": index,
                    "content": chunk.page_content,
                    "embedding": vector,
                    "metadata": {**chunk.metadata, **metadata},
                    "created_at": uploaded_at,
                }
            )
        document = {
            "_id": document_id,
            "source": file_path.name,
            "file_type": file_path.suffix.lower(),
            "uploaded_by": uploaded_by,
            "uploaded_at": uploaded_at,
            "chunk_count": len(chunk_records),
            "metadata": metadata,
        }
        self.repository.save_document(document)
        self.vector_store.add(chunk_records)
        return document


class ContextBuilder:
    def build(self, documents: list[dict], learning_profile: dict | None = None) -> str:
        sections = []
        if learning_profile:
            sections.append(f"User learning profile: {learning_profile}")
        for index, document in enumerate(documents, 1):
            source = document.get("metadata", {}).get("source", "unknown")
            page = document.get("metadata", {}).get("page_no", "?")
            sections.append(f"[{index}] Source: {source}, page: {page}\n{document.get('content', '')}")
        return "\n\n".join(sections)


class HybridReranker:
    def rerank(self, documents: list[dict]) -> list[dict]:
        return sorted(
            documents,
            key=lambda item: (
                item.get("score", 0),
                len(item.get("content", "")),
            ),
            reverse=True,
        )


class LLMService:
    def __init__(self, config):
        self.model = None
        if config.get("OPENAI_API_KEY"):
            from langchain_openai import ChatOpenAI

            self.model = ChatOpenAI(
                api_key=config["OPENAI_API_KEY"],
                model=config["OPENAI_CHAT_MODEL"],
                temperature=0.1,
            )

    def generate(self, system_prompt: str, context: str, query: str) -> str:
        if not self.model:
            if not context:
                return "I could not find relevant indexed material for that question."
            return (
                "No LLM provider is configured. Here is the most relevant indexed context:\n\n"
                + context[:2500]
            )
        prompt = ChatPromptTemplate.from_messages(
            [("system", system_prompt), ("human", "Context:\n{context}\n\nQuestion:\n{query}")]
        )
        response = (prompt | self.model).invoke({"context": context, "query": query})
        return response.content


class RAGChatService:
    SYSTEM_PROMPT = (
        "You are GATEMIND, a precise GATE preparation assistant. Answer using only the supplied "
        "context. Explain reasoning clearly, mention uncertainty, and refer to citation numbers."
    )

    def __init__(self, repository, vector_store, embeddings, reranker, context_builder, llm_service, users, top_k):
        self.repository = repository
        self.vector_store = vector_store
        self.embeddings = embeddings
        self.reranker = reranker
        self.context_builder = context_builder
        self.llm_service = llm_service
        self.users = users
        self.top_k = top_k

    def ask(self, user_id: str, query: str, filters: dict | None = None) -> RAGResponse:
        if not query.strip():
            raise ValueError("query is required")
        query_vector = self.embeddings.embed_query(query)
        storage_filters = {}
        for key, value in (filters or {}).items():
            storage_filters[key if key == "document_id" else f"metadata.{key}"] = value
        retrieved = self.vector_store.search(
            query_vector,
            self.top_k * 2,
            storage_filters or None,
            query,
        )
        retrieved = self.reranker.rerank(retrieved)[: self.top_k]
        user = self.users.find_by_id(user_id)
        learning_profile = None
        if user and user.user_profile:
            learning_profile = {
                "preferred_subject": user.user_profile.preferred_subject,
                "performance_percentage": user.user_profile.performance_percentage,
                "preparation_progress": user.user_profile.preparation_progress,
            }
        context = self.context_builder.build(retrieved, learning_profile)
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
                "created_at": datetime.now(timezone.utc),
            }
        )
        return response

    def history(self, user_id: str) -> list[dict]:
        return self.repository.list_chats(user_id)
