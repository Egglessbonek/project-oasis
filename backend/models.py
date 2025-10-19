from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import uuid
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class Area(db.Model):
    __tablename__ = 'areas'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(255), nullable=False, unique=True)
    boundary = db.Column(db.Text)  # PostGIS geography data as text
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    # Relationships
    admins = db.relationship('Admin', backref='area', lazy=True)
    wells = db.relationship('Well', backref='area', lazy=True)

class Admin(db.Model):
    __tablename__ = 'admins'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = db.Column(db.String(255), nullable=False, unique=True)
    password_hash = db.Column(db.String(255), nullable=False)
    area_id = db.Column(db.String(36), db.ForeignKey('areas.id'), nullable=True)
    is_admin = db.Column(db.Boolean, nullable=False, default=True)
    oauth_id = db.Column(db.String(255))
    access_token = db.Column(db.Text)
    refresh_token = db.Column(db.Text)
    token_expires_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def set_password(self, password):
        """Hash and set the password"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check if provided password matches the hash"""
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'email': self.email,
            'area_id': self.area_id,
            'is_admin': self.is_admin,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class Well(db.Model):
    __tablename__ = 'wells'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    location = db.Column(db.Text)  # PostGIS point data as text
    status = db.Column(db.Enum('draft', 'building', 'completed', 'broken', 'under_maintenance', name='well_status'), nullable=False, default='draft')
    capacity = db.Column(db.Integer, nullable=False)
    current_load = db.Column(db.Integer, nullable=False, default=0)
    area_id = db.Column(db.String(36), db.ForeignKey('areas.id'), nullable=False)
    service_area = db.Column(db.Text)  # PostGIS polygon data as text
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    well_project = db.relationship('WellProject', backref='well', uselist=False, cascade='all, delete-orphan')
    breakage_reports = db.relationship('BreakageReport', backref='well', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'location': self.location,
            'status': self.status,
            'capacity': self.capacity,
            'current_load': self.current_load,
            'area_id': self.area_id,
            'service_area': self.service_area,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class WellProject(db.Model):
    __tablename__ = 'well_projects'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    well_id = db.Column(db.String(36), db.ForeignKey('wells.id'), nullable=False, unique=True)
    project_name = db.Column(db.String(255), nullable=False)
    estimated_build_cost = db.Column(db.Numeric(12, 2), nullable=False)
    predicted_lifetime_cost = db.Column(db.Numeric(12, 2))
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'well_id': self.well_id,
            'project_name': self.project_name,
            'estimated_build_cost': float(self.estimated_build_cost) if self.estimated_build_cost else None,
            'predicted_lifetime_cost': float(self.predicted_lifetime_cost) if self.predicted_lifetime_cost else None,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class BreakageReport(db.Model):
    __tablename__ = 'breakage_reports'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    well_id = db.Column(db.String(36), db.ForeignKey('wells.id'), nullable=False)
    image_url = db.Column(db.Text)
    summary = db.Column(db.Text, nullable=False)
    status = db.Column(db.Enum('reported', 'in_progress', 'fixed', name='report_status'), nullable=False, default='reported')
    fix_priority = db.Column(db.Integer, nullable=False, default=0)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'well_id': self.well_id,
            'image_url': self.image_url,
            'summary': self.summary,
            'status': self.status,
            'fix_priority': self.fix_priority,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
