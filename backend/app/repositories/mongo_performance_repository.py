class MongoPerformanceRepository:
    def __init__(self, db):
        self.collection = db["performance_records"]
        self.collection.create_index([("user_id", 1), ("attempted_at", -1)])

    def save(self, record):
        data = record.to_dict() if hasattr(record, "to_dict") else record
        self.collection.replace_one({"_id": data["_id"]}, data, upsert=True)
        return data

    def find_by_user(self, user_id, limit=100):
        return list(self.collection.find({"user_id": user_id}).sort("attempted_at", -1).limit(limit))

    def aggregate_user(self, user_id):
        records = self.find_by_user(user_id)
        values = [float(item.get("percentage", 0)) for item in records]
        return {"attempts": len(records), "average_percentage": round(sum(values) / len(values), 2) if values else 0.0, "best_percentage": round(max(values), 2) if values else 0.0}

    def count(self):
        return self.collection.count_documents({})
