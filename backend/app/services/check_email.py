import re


class CheckEmail:
    EMAIL_PATTERN = re.compile(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$")

    @classmethod
    def contains_necessary_character(cls, email: str) -> bool:
        return bool(email and cls.EMAIL_PATTERN.match(email))
