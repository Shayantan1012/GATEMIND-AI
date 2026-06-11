class MongoRAGRepository:
    def __init__(self, db):
        self.documents = db["rag_documents"]
        self.chunks = db["rag_chunks"]
        self.chats = db["rag_chats"]

    def save_document(self, document):
        self.documents.replace_one({"_id": document["_id"]}, document, upsert=True)
        return document

    def save_chunks(self, chunks):
        if chunks:
            self.chunks.insert_many(chunks)
        return len(chunks)

    def list_chunks(self, filters=None):
        return list(self.chunks.find(filters or {}))

    def list_documents(self, limit=100):
        return list(self.documents.find().sort("uploaded_at", -1).limit(limit))

    def save_chat(self, chat):
        self.chats.insert_one(chat)
        return chat

    def list_chats(self, user_id, limit=50):
        return list(self.chats.find({"user_id": user_id}).sort("created_at", -1).limit(limit))

    def count_documents(self):
        return self.documents.count_documents({})
