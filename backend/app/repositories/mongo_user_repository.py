from pymongo.database import Database

from app.models.user import User
from app.repositories.user_repository_interface import UserRepository


class MongoUserRepository(UserRepository):
    def __init__(self, db: Database):
        self.collection = db["users"]
        self.collection.create_index("email", unique=True)
        self.collection.create_index("sessions.refresh_token")

    def save(self, user: User) -> User:
        self.collection.replace_one({"_id": user.user_id}, user.to_dict(), upsert=True)
        return user

    def find_by_email(self, email: str) -> User | None:
        doc = self.collection.find_one({"email": email.lower()})
        return User.from_dict(doc) if doc else None

    def find_by_id(self, user_id: str) -> User | None:
        doc = self.collection.find_one({"_id": user_id})
        return User.from_dict(doc) if doc else None

    def update(self, user: User) -> User:
        result = self.collection.replace_one({"_id": user.user_id}, user.to_dict(), upsert=False)
        if result.matched_count == 0:
            raise ValueError("User not found")
        return user

    def delete(self, user_id: str) -> bool:
        result = self.collection.delete_one({"_id": user_id})
        return result.deleted_count > 0

    def exists_by_email(self, email: str) -> bool:
        return self.collection.count_documents({"email": email.lower()}, limit=1) > 0

    def find_by_refresh_token(self, refresh_token: str):
        doc = self.collection.find_one({"sessions.refresh_token": refresh_token})
        return User.from_dict(doc) if doc else None

    def find_all(self, limit: int = 100, skip: int = 0) -> list[User]:
        return [User.from_dict(doc) for doc in self.collection.find().skip(skip).limit(limit)]

    def count(self) -> int:
        return self.collection.count_documents({})
