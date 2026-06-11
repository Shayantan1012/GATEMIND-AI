from app.repositories.user_repository_interface import UserRepository


class InMemoryUserRepository(UserRepository):
    def __init__(self):
        self._users_by_id = {}
        self._email_index = {}

    def save(self, user):
        self._users_by_id[user.user_id] = user
        self._email_index[user.email.lower()] = user.user_id
        return user

    def find_by_email(self, email):
        return self._users_by_id.get(self._email_index.get(email.lower()))

    def find_by_id(self, user_id):
        return self._users_by_id.get(user_id)

    def update(self, user):
        return self.save(user)

    def delete(self, user_id):
        user = self._users_by_id.pop(user_id, None)
        if not user:
            return False
        self._email_index.pop(user.email.lower(), None)
        return True

    def exists_by_email(self, email):
        return email.lower() in self._email_index

    def find_by_refresh_token(self, token):
        return next((user for user in self._users_by_id.values() for session in user.sessions if session.refresh_token == token), None)

    def find_all(self, limit=100, skip=0):
        return list(self._users_by_id.values())[skip : skip + limit]

    def count(self):
        return len(self._users_by_id)
