from werkzeug.security import generate_password_hash, check_password_hash


class Encryption:
    def convert(self, data):
        """Hash a plain-text password for storage. Salted, one-way (werkzeug/scrypt)."""
        return generate_password_hash(data)

    def verify(self, plain_password, hashed_password):
        """Check a plain-text password against a stored hash."""
        return check_password_hash(hashed_password, plain_password)
