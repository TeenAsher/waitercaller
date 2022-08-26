from werkzeug.security import generate_password_hash, check_password_hash

class PasswordHelper:

    def get_hash(self, plain):
        hashed = generate_password_hash(plain, method='sha256')
        return hashed

    def validate_password(self, hashed, password):
        return check_password_hash(hashed, password)
