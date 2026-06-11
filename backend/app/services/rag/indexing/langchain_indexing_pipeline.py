from datetime import datetime, timezone
from uuid import uuid4

from app.services.rag.indexing.indexing_pipeline import IndexingPipeline


class LangChainIndexingPipeline(IndexingPipeline):
    def __init__(self, repository, vector_store, embeddings, parser_factory, chunking_strategy):
        self.repository = repository
        self.vector_store = vector_store
        self.embeddings = embeddings
        self.parser_factory = parser_factory
        self.chunking_strategy = chunking_strategy

    def parse(self, file_path):
        return self.parser_factory.create(file_path).parse(file_path)

    def process(self, documents):
        return self.chunking_strategy.split(documents)

    def store(self, document_id, file_path, uploaded_by, chunks, metadata):
        uploaded_at = datetime.now(timezone.utc)
        vectors = self.embeddings.embed_documents([chunk.page_content for chunk in chunks])
        records = [
            {
                "_id": str(uuid4()),
                "document_id": document_id,
                "chunk_index": index,
                "content": chunk.page_content,
                "embedding": vector,
                "metadata": {**chunk.metadata, **metadata},
                "created_at": uploaded_at,
            }
            for index, (chunk, vector) in enumerate(zip(chunks, vectors))
        ]
        document = {
            "_id": document_id,
            "source": file_path.name,
            "file_type": file_path.suffix.lower(),
            "uploaded_by": uploaded_by,
            "uploaded_at": uploaded_at,
            "chunk_count": len(records),
            "metadata": metadata,
        }
        self.repository.save_document(document)
        self.vector_store.add(records)
        return document
