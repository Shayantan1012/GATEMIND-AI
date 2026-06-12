class MongoRAGRepository:
    def __init__(self, db):
        self.documents = db["rag_documents"]
        self.chunks = db["rag_chunks"]
        self.chats = db["rag_chats"]
        self.conversations = db["rag_conversations"]
        self.conversations.create_index([("user_id", 1), ("updated_at", -1)])
        self.chats.create_index([("conversation_id", 1), ("created_at", 1)])

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

    def list_documents_by_uploader(self, uploaded_by, limit=100):
        return list(self.documents.find({"uploaded_by": uploaded_by}).sort("uploaded_at", -1).limit(limit))

    def find_documents_by_ids(self, document_ids):
        return list(self.documents.find({"_id": {"$in": list(document_ids)}}))

    def find_document(self, document_id):
        return self.documents.find_one({"_id": document_id})

    def delete_document(self, document_id):
        self.chunks.delete_many({"document_id": document_id})
        result = self.documents.delete_one({"_id": document_id})
        return result.deleted_count > 0

    def save_chat(self, chat):
        self.chats.insert_one(chat)
        return chat

    def list_chats(self, user_id, conversation_id=None, limit=100):
        query = {"user_id": user_id}
        if conversation_id:
            query["conversation_id"] = conversation_id
        return list(self.chats.find(query).sort("created_at", 1).limit(limit))

    def save_conversation(self, conversation):
        self.conversations.replace_one({"_id": conversation["_id"]}, conversation, upsert=True)
        return conversation

    def find_conversation(self, conversation_id, user_id):
        return self.conversations.find_one({"_id": conversation_id, "user_id": user_id})

    def list_conversations(self, user_id, limit=100):
        return list(self.conversations.find({"user_id": user_id}).sort("updated_at", -1).limit(limit))

    def delete_conversation(self, conversation_id, user_id):
        result = self.conversations.delete_one({"_id": conversation_id, "user_id": user_id})
        if result.deleted_count:
            self.chats.delete_many({"conversation_id": conversation_id, "user_id": user_id})
        return result.deleted_count > 0

    def count_documents(self):
        return self.documents.count_documents({})
