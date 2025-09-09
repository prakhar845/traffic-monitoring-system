import hashlib
import secrets
import jwt
from datetime import datetime, timedelta
from typing import Optional, Dict
from sqlalchemy.orm import Session
from database.models import User
import os
from dotenv import load_dotenv

load_dotenv()

class AuthService:
    def __init__(self):
        self.secret_key = os.getenv("JWT_SECRET_KEY", "your-secret-key-here")
        self.algorithm = "HS256"
        self.access_token_expire_minutes = 30
        self.refresh_token_expire_days = 7
    
    def hash_password(self, password: str) -> str:
        """Hash password using SHA-256 with salt"""
        salt = secrets.token_hex(16)
        password_hash = hashlib.sha256((password + salt).encode()).hexdigest()
        return f"{salt}:{password_hash}"
    
    def verify_password(self, password: str, hashed_password: str) -> bool:
        """Verify password against hash"""
        try:
            salt, password_hash = hashed_password.split(':')
            return hashlib.sha256((password + salt).encode()).hexdigest() == password_hash
        except:
            return False
    
    def create_access_token(self, user_id: int, username: str, role: str) -> str:
        """Create JWT access token"""
        expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
        payload = {
            "user_id": user_id,
            "username": username,
            "role": role,
            "exp": expire,
            "type": "access"
        }
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
    
    def create_refresh_token(self, user_id: int) -> str:
        """Create JWT refresh token"""
        expire = datetime.utcnow() + timedelta(days=self.refresh_token_expire_days)
        payload = {
            "user_id": user_id,
            "exp": expire,
            "type": "refresh"
        }
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
    
    def verify_token(self, token: str) -> Optional[Dict]:
        """Verify and decode JWT token"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
    
    def authenticate_user(self, db: Session, username: str, password: str) -> Optional[User]:
        """Authenticate user with username and password"""
        user = db.query(User).filter(
            User.username == username,
            User.is_active == True
        ).first()
        
        if user and self.verify_password(password, user.password_hash):
            return user
        return None
    
    def get_user_by_id(self, db: Session, user_id: int) -> Optional[User]:
        """Get user by ID"""
        return db.query(User).filter(
            User.id == user_id,
            User.is_active == True
        ).first()
    
    def create_user(self, db: Session, username: str, email: str, password: str, role: str = "viewer") -> Optional[User]:
        """Create new user"""
        # Check if user already exists
        existing_user = db.query(User).filter(
            (User.username == username) | (User.email == email)
        ).first()
        
        if existing_user:
            return None
        
        # Create new user
        hashed_password = self.hash_password(password)
        user = User(
            username=username,
            email=email,
            password_hash=hashed_password,
            role=role
        )
        
        db.add(user)
        db.commit()
        db.refresh(user)
        
        return user
    
    def update_user_role(self, db: Session, user_id: int, new_role: str) -> bool:
        """Update user role"""
        user = db.query(User).filter(User.id == user_id).first()
        if user:
            user.role = new_role
            db.commit()
            return True
        return False
    
    def deactivate_user(self, db: Session, user_id: int) -> bool:
        """Deactivate user account"""
        user = db.query(User).filter(User.id == user_id).first()
        if user:
            user.is_active = False
            db.commit()
            return True
        return False
