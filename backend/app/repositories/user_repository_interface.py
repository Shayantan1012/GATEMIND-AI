from abc import ABC, abstractmethod


class UserRepository(ABC):
    @abstractmethod
    def save(self, user):
        raise NotImplementedError

    @abstractmethod
    def find_by_email(self, email):
        raise NotImplementedError

    @abstractmethod
    def find_by_id(self, user_id):
        raise NotImplementedError

    @abstractmethod
    def update(self, user):
        raise NotImplementedError

    @abstractmethod
    def delete(self, user_id):
        raise NotImplementedError

    @abstractmethod
    def exists_by_email(self, email):
        raise NotImplementedError

    @abstractmethod
    def find_all(self, limit=100, skip=0):
        raise NotImplementedError

    @abstractmethod
    def count(self):
        raise NotImplementedError
