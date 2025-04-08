from datetime import datetime
import enum
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()

class LeadState(enum.Enum):
    """Enumeration of possible lead states."""
    PENDING = "PENDING"
    REACHED_OUT = "REACHED_OUT"

class User(UserMixin, db.Model):
    """User model for attorney authentication."""
    __tablename__ = "users"
    
    id = db.Column(db.Integer, primary_key=True, index=True)
    email = db.Column(db.String(255), unique=True, index=True)
    password = db.Column(db.String(255))
    full_name = db.Column(db.String(255))
    is_active = db.Column(db.Integer, default=1)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    @property
    def is_active_bool(self):
        return bool(self.is_active)
        
    @is_active_bool.setter
    def is_active_bool(self, value):
        self.is_active = 1 if value else 0

class Lead(db.Model):
    """Lead model to store prospect information."""
    __tablename__ = "leads"
    
    id = db.Column(db.Integer, primary_key=True, index=True)
    first_name = db.Column(db.String(255), nullable=False)
    last_name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), nullable=False, index=True)
    resume_path = db.Column(db.String(255), nullable=False)
    state = db.Column(db.Enum(LeadState), default=LeadState.PENDING)
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    updated_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    
    user = db.relationship("User", foreign_keys=[updated_by])