"""
Database models for Placement Management System
"""
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import secrets

db = SQLAlchemy()


class User(db.Model):
    """User model for authentication"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='teacher')  # 'admin' or 'teacher'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationships
    teacher = db.relationship('Teacher', backref='user', uselist=False, cascade='all, delete-orphan')
    
    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Verify password"""
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.username}>'


class Teacher(db.Model):
    """Teacher model"""
    __tablename__ = 'teachers'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)
    full_name = db.Column(db.String(120))
    email = db.Column(db.String(120))
    phone = db.Column(db.String(15))
    department = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    classes = db.relationship('Class', backref='teacher', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Teacher {self.user.username}>'


class Class(db.Model):
    """Class model"""
    __tablename__ = 'classes'
    
    id = db.Column(db.Integer, primary_key=True)
    teacher_id = db.Column(db.Integer, db.ForeignKey('teachers.id'), nullable=False)
    course = db.Column(db.String(100), nullable=False)
    specialisation = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationships
    students = db.relationship('Student', backref='class_ref', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Class {self.course} - {self.specialisation}>'


class Student(db.Model):
    """Student model with comprehensive placement information"""
    __tablename__ = 'students'
    
    id = db.Column(db.Integer, primary_key=True)
    class_id = db.Column(db.Integer, db.ForeignKey('classes.id'), nullable=False)
    
    # Personal Information
    usn = db.Column(db.String(20), unique=True, nullable=False, index=True)
    full_name = db.Column(db.String(120), nullable=False)
    phone_number = db.Column(db.String(15), nullable=False)
    email_id = db.Column(db.String(120), nullable=False)
    mother_tongue = db.Column(db.String(50))
    
    # Parent Information
    parent_name = db.Column(db.String(120), nullable=False)
    parent_phone = db.Column(db.String(15), nullable=False)
    parent_email = db.Column(db.String(120), nullable=False)
    
    # Placement Information
    company_name = db.Column(db.String(120))
    package = db.Column(db.String(50))
    confirmation_letter_path = db.Column(db.String(255))
    
    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    notification_sent = db.Column(db.Boolean, default=False)
    notification_sent_at = db.Column(db.DateTime)
    send_whatsapp = db.Column(db.Boolean, default=True)  # Enable/disable WhatsApp notifications
    whatsapp_notification_sent = db.Column(db.Boolean, default=False)  # Track WhatsApp send status

    # Bulk Excel / notification metadata (added for Excel import & bulk notifications)
    is_active = db.Column(db.Boolean, default=True)
    last_notification_sent_at = db.Column(db.DateTime)
    last_whatsapp_status = db.Column(db.String(50))
    last_call_status = db.Column(db.String(50))
    preferred_voice = db.Column(db.String(80))
    preferred_prosody = db.Column(db.String(80))
    external_id = db.Column(db.String(120), index=True)

    def __repr__(self):
        return f'<Student {self.usn} - {self.full_name}>'
    
    def to_dict(self):
        """Convert to dictionary for easier access (extended for Excel/import)"""
        return {
            'id': self.id,
            'usn': self.usn,
            'full_name': self.full_name,
            'phone_number': self.phone_number,
            'email_id': self.email_id,
            'parent_name': self.parent_name,
            'parent_phone': self.parent_phone,
            'parent_email': self.parent_email,
            'mother_tongue': self.mother_tongue,
            'company_name': self.company_name,
            'package': self.package,
            'confirmation_letter_path': self.confirmation_letter_path,
            'is_active': self.is_active,
            'last_notification_sent_at': self.last_notification_sent_at,
            'last_whatsapp_status': self.last_whatsapp_status,
            'last_call_status': self.last_call_status,
            'preferred_voice': self.preferred_voice,
            'preferred_prosody': self.preferred_prosody,
            'external_id': self.external_id
        }


class UserSession(db.Model):
    """User session model for multi-device login support"""
    __tablename__ = 'user_sessions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    session_token = db.Column(db.String(255), unique=True, nullable=False, index=True)
    user_agent = db.Column(db.String(500))  # Browser/device info
    ip_address = db.Column(db.String(50))   # IP address
    device_name = db.Column(db.String(100), default='Unknown Device')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_activity = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    expires_at = db.Column(db.DateTime)  # Session expiration time
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationship
    user = db.relationship('User', backref='sessions')
    
    @staticmethod
    def create_session(user_id, user_agent=None, ip_address=None, device_name='Unknown Device'):
        """Create a new session for a user"""
        from datetime import timedelta
        token = secrets.token_urlsafe(32)
        expires_at = datetime.utcnow() + timedelta(days=1)  # 24 hours
        
        session = UserSession(
            user_id=user_id,
            session_token=token,
            user_agent=user_agent,
            ip_address=ip_address,
            device_name=device_name,
            expires_at=expires_at
        )
        return session
    
    def is_valid(self):
        """Check if session is still valid"""
        if not self.is_active:
            return False
        if self.expires_at and datetime.utcnow() > self.expires_at:
            return False
        return True
    
    def __repr__(self):
        return f'<UserSession {self.device_name} - {self.user.username}>'
