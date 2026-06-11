from app.models.admin import Admin


class MongoAdminRepository:
    def __init__(self, db):
        self.collection = db["admins"]
        self.collection.create_index("email", unique=True)
        self.collection.create_index("sessions.refresh_token")

    def save(self, admin):
        self.collection.replace_one({"_id": admin.admin_id}, admin.to_dict(), upsert=True)
        return admin

    def update(self, admin):
        return self.save(admin)

    def find_by_id(self, admin_id):
        data = self.collection.find_one({"_id": admin_id})
        return Admin.from_dict(data) if data else None

    def find_by_email(self, email):
        data = self.collection.find_one({"email": email.strip().lower()})
        return Admin.from_dict(data) if data else None

    def find_by_refresh_token(self, token):
        data = self.collection.find_one({"sessions.refresh_token": token})
        return Admin.from_dict(data) if data else None

    def exists_by_email(self, email):
        return self.collection.count_documents({"email": email.strip().lower()}, limit=1) > 0

    def count(self):
        return self.collection.count_documents({})
