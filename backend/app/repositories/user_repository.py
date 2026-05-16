from typing import Dict, Optional

from app.models.user import User


class UserRepository:
    def save(self, user: User) -> User:
        raise NotImplementedError

    def find_by_email(self, email: str) -> Optional[User]:
        raise NotImplementedError

    def find_by_id(self, user_id: str) -> Optional[User]:
        raise NotImplementedError

    def update(self, user: User) -> User:
        raise NotImplementedError

    def delete(self, user_id: str) -> bool:
        raise NotImplementedError

    def exists_by_email(self, email: str) -> bool:
        raise NotImplementedError


class InMemoryUserRepository(UserRepository):
    def __init__(self):
        self._users_by_id: Dict[str, User] = {}
        self._email_index: Dict[str, str] = {}

    def save(self, user: User) -> User:
        self._users_by_id[user.user_id] = user
        self._email_index[user.email.lower()] = user.user_id
        return user

    def find_by_email(self, email: str) -> Optional[User]:
        user_id = self._email_index.get(email.lower())
        if not user_id:
            return None
        return self._users_by_id.get(user_id)

    def find_by_id(self, user_id: str) -> Optional[User]:
        return self._users_by_id.get(user_id)

    def update(self, user: User) -> User:
        return self.save(user)

    def delete(self, user_id: str) -> bool:
        user = self._users_by_id.pop(user_id, None)
        if not user:
            return False
        self._email_index.pop(user.email.lower(), None)
        return True

    def exists_by_email(self, email: str) -> bool:
        return email.lower() in self._email_index
