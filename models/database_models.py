"""
Database models for Virtual Try-On application
"""

from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import json

db = SQLAlchemy()

class User(UserMixin, db.Model):
    """User model for authentication and profiles"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationships
    measurements = db.relationship('UserMeasurement', backref='user', lazy=True, cascade='all, delete-orphan')
    tryon_sessions = db.relationship('TryOnSession', backref='user', lazy=True, cascade='all, delete-orphan')
    wishlist_items = db.relationship('WishlistItem', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def set_password(self, password):
        """Set password hash"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check password"""
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'is_active': self.is_active
        }

class ClothingItem(db.Model):
    """Clothing items available for virtual try-on"""
    __tablename__ = 'clothing_items'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    category = db.Column(db.String(50), nullable=False)
    brand = db.Column(db.String(50))
    price = db.Column(db.Numeric(10, 2))
    image_url = db.Column(db.String(255))
    model_path = db.Column(db.String(255))  # Path to 3D model
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    # JSON field for additional attributes
    attributes = db.Column(db.Text)  # JSON string for colors, sizes, materials, etc.
    
    # Relationships
    tryon_sessions = db.relationship('TryOnSession', backref='clothing_item', lazy=True)
    wishlist_items = db.relationship('WishlistItem', backref='clothing_item', lazy=True)
    
    def get_attributes(self):
        """Get attributes as dictionary"""
        if self.attributes:
            return json.loads(self.attributes)
        return {}
    
    def set_attributes(self, attrs_dict):
        """Set attributes from dictionary"""
        self.attributes = json.dumps(attrs_dict)
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'category': self.category,
            'brand': self.brand,
            'price': float(self.price) if self.price else None,
            'image_url': self.image_url,
            'attributes': self.get_attributes(),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'is_active': self.is_active
        }

class UserMeasurement(db.Model):
    """User body measurements for size estimation"""
    __tablename__ = 'user_measurements'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Body measurements (in cm)
    height = db.Column(db.Float)
    chest_width = db.Column(db.Float)
    shoulder_width = db.Column(db.Float)
    waist_width = db.Column(db.Float)
    hip_width = db.Column(db.Float)
    torso_length = db.Column(db.Float)
    arm_length = db.Column(db.Float)
    leg_length = db.Column(db.Float)
    
    # Measurement source
    source = db.Column(db.String(50), default='ai_estimation')  # 'ai_estimation', 'manual', 'camera'
    confidence_score = db.Column(db.Float)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'height': self.height,
            'chest_width': self.chest_width,
            'shoulder_width': self.shoulder_width,
            'waist_width': self.waist_width,
            'hip_width': self.hip_width,
            'torso_length': self.torso_length,
            'arm_length': self.arm_length,
            'leg_length': self.leg_length,
            'source': self.source,
            'confidence_score': self.confidence_score,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class TryOnSession(db.Model):
    """Virtual try-on sessions"""
    __tablename__ = 'tryon_sessions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)  # Can be anonymous
    clothing_item_id = db.Column(db.Integer, db.ForeignKey('clothing_items.id'), nullable=False)
    
    # Session data
    session_token = db.Column(db.String(100), unique=True)
    selected_size = db.Column(db.String(10))
    selected_color = db.Column(db.String(50))
    
    # AI results
    pose_data = db.Column(db.Text)  # JSON string of pose landmarks
    size_recommendation = db.Column(db.String(10))
    confidence_score = db.Column(db.Float)
    fit_analysis = db.Column(db.Text)  # JSON string of fit analysis
    
    # Media
    original_image_path = db.Column(db.String(255))
    tryon_image_path = db.Column(db.String(255))
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
    status = db.Column(db.String(20), default='started')  # 'started', 'processing', 'completed', 'failed'
    
    def get_pose_data(self):
        """Get pose data as dictionary"""
        if self.pose_data:
            return json.loads(self.pose_data)
        return {}
    
    def set_pose_data(self, data_dict):
        """Set pose data from dictionary"""
        self.pose_data = json.dumps(data_dict)
    
    def get_fit_analysis(self):
        """Get fit analysis as dictionary"""
        if self.fit_analysis:
            return json.loads(self.fit_analysis)
        return {}
    
    def set_fit_analysis(self, analysis_dict):
        """Set fit analysis from dictionary"""
        self.fit_analysis = json.dumps(analysis_dict)
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'clothing_item_id': self.clothing_item_id,
            'session_token': self.session_token,
            'selected_size': self.selected_size,
            'selected_color': self.selected_color,
            'pose_data': self.get_pose_data(),
            'size_recommendation': self.size_recommendation,
            'confidence_score': self.confidence_score,
            'fit_analysis': self.get_fit_analysis(),
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None
        }

class WishlistItem(db.Model):
    """User wishlist items"""
    __tablename__ = 'wishlist_items'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    clothing_item_id = db.Column(db.Integer, db.ForeignKey('clothing_items.id'), nullable=False)
    
    # User preferences for this item
    preferred_size = db.Column(db.String(10))
    preferred_color = db.Column(db.String(50))
    notes = db.Column(db.Text)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Unique constraint to prevent duplicates
    __table_args__ = (db.UniqueConstraint('user_id', 'clothing_item_id', name='unique_user_clothing'),)
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'clothing_item_id': self.clothing_item_id,
            'preferred_size': self.preferred_size,
            'preferred_color': self.preferred_color,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
