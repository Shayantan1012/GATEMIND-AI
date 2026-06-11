class MongoAuditRepository:
    def __init__(self, db):
        self.collection = db["audit_logs"]
        self.collection.create_index([("actor_id", 1), ("created_at", -1)])

    def save(self, event):
        self.collection.insert_one(event)
        return event
