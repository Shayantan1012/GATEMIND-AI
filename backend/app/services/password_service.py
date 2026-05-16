from werkzeug.security import check_password_hash, generate_password_hash


class PasswordService:
    def hash_password(self, password: str) -> str:
        return generate_password_hash(password)

    def verify_password(self, raw_password: str, hashed_password: str) -> bool:
        return check_password_hash(hashed_password, raw_password)

    def validate_password_strength(self, password: str) -> bool:
        if not password or len(password) < 8:
            return False
        has_letter = any(character.isalpha() for character in password)
        has_number = any(character.isdigit() for character in password)
        return has_letter and has_number
