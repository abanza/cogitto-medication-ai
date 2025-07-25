# app/infrastructure/auth/password_manager.py
from passlib.context import CryptContext
from passlib.hash import bcrypt
import secrets
import string

class PasswordManager:
    """Secure password hashing and verification"""
    
    def __init__(self):
        # Use bcrypt for password hashing
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    
    def hash_password(self, password: str) -> str:
        """Hash a password securely"""
        return self.pwd_context.hash(password)
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash"""
        return self.pwd_context.verify(plain_password, hashed_password)
    
    def generate_secure_token(self, length: int = 32) -> str:
        """Generate a secure random token"""
        alphabet = string.ascii_letters + string.digits
        return ''.join(secrets.choice(alphabet) for _ in range(length))
