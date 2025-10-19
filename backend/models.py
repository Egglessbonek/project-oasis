# =============================================================================
#                         Project Oasis - Models
#
# This file defines the SQLAlchemy db object and all our database models.
# It has been updated to merge naming conventions and add password
# helper methods to the Admin model.
# =============================================================================

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import UUID, ENUM
from geoalchemy2 import Geometry
from geoalchemy2.shape import to_shape
import uuid
from werkzeug.security import generate_password_hash, check_password_hash

# Create the SQLAlchemy instance. This object will be the primary way we
# interact with the database.
db = SQLAlchemy()

class Area(db.Model):
    __tablename__ = 'areas'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = db.Column(db.Text, nullable=False, unique=True)
    boundary = db.Column(Geometry(geometry_type='POLYGON', srid=4326), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), server_default=db.func.now())

    # Relationships are kept, as they match the intent of 'backref'
    admins = db.relationship('Admin', back_populates='area', lazy=True)
    wells = db.relationship('Well', back_populates='area', lazy=True)

    def __repr__(self):
        return f'<Area {self.name}>'
        
    def to_dict(self):
        return {
            'id': str(self.id),
            'name': self.name,
            'boundary': to_shape(self.boundary).__geo_interface__ if self.boundary else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class Admin(db.Model):
    __tablename__ = 'admins'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = db.Column(db.String(255), nullable=False, unique=True)
    password_hash = db.Column(db.Text, nullable=False)
    area_id = db.Column(UUID(as_uuid=True), db.ForeignKey('areas.id'), nullable=False)
    is_admin = db.Column(db.Boolean, nullable=False, default=True)
    oauth_id = db.Column(db.String(255))
    access_token = db.Column(db.Text)
    refresh_token = db.Column(db.Text)
    token_expires_at = db.Column(db.DateTime(timezone=True))
    created_at = db.Column(db.DateTime(timezone=True), server_default=db.func.now())
    updated_at = db.Column(db.DateTime(timezone=True), server_default=db.func.now(), onupdate=db.func.now())

    area = db.relationship('Area', back_populates='admins')

    def __repr__(self):
        return f'<Admin {self.email}>'
    
    # --- APPENDED FUNCTIONALITY ---
    def set_password(self, password):
        """Hash and set the password"""
        self.password_hash = generate_password_hash(password)
    
    # --- APPENDED FUNCTIONALITY ---
    def check_password(self, password):
        """Check if provided password matches the hash"""
        return check_password_hash(self.password_hash, password)
        
    def to_dict(self):
        # Excludes sensitive info like password_hash and tokens
        return {
            'id': str(self.id),
            'email': self.email,
            'area_id': str(self.area_id) if self.area_id else None,
            'is_admin': self.is_admin,
            'oauth_id': self.oauth_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class Well(db.Model):
    __tablename__ = 'wells'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    location = db.Column(Geometry(geometry_type='POINT', srid=4326), nullable=False)
    service_area = db.Column(Geometry(geometry_type='POLYGON', srid=4326))
    
    status = db.Column(ENUM('draft', 'building', 'completed', 'broken', 'under_maintenance', name='well_status'), nullable=False, default='draft')
    capacity = db.Column(db.Integer, nullable=False)
    current_load = db.Column(db.Integer, nullable=False, default=0)

    weight = db.Column(db.Integer, nullable=False, default=0)
    
    area_id = db.Column(UUID(as_uuid=True), db.ForeignKey('areas.id'), nullable=False)
    area = db.relationship('Area', back_populates='wells')
    
    # --- NAME CHANGED ---
    # Renamed from 'project' to 'well_project' to match your new code
    well_project = db.relationship('WellProject', back_populates='well', uselist=False, cascade="all, delete-orphan")
    # --- NAME CHANGED ---
    # Renamed from 'reports' to 'breakage_reports' to match your new code
    breakage_reports = db.relationship('BreakageReport', back_populates='well', cascade="all, delete-orphan")
    
    created_at = db.Column(db.DateTime(timezone=True), server_default=db.func.now())
    updated_at = db.Column(db.DateTime(timezone=True), server_default=db.func.now(), onupdate=db.func.now())
    
    def to_dict(self):
        return {
            'id': str(self.id),
            'location': to_shape(self.location).__geo_interface__ if self.location else None,
            'service_area': to_shape(self.service_area).__geo_interface__ if self.service_area else None,
            'status': self.status,
            'capacity': self.capacity,
            'current_load': self.current_load,
            'weight': self.weight,
            'area_id': str(self.area_id),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class WellProject(db.Model):
    __tablename__ = 'well_projects'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    well_id = db.Column(UUID(as_uuid=True), db.ForeignKey('wells.id'), nullable=False, unique=True)
    project_name = db.Column(db.Text, nullable=False)
    estimated_build_cost = db.Column(db.Numeric(12, 2), nullable=False)
    predicted_lifetime_cost = db.Column(db.Numeric(12, 2))
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime(timezone=True), server_default=db.func.now())
    
    # --- NAME CHANGED ---
    # back_populates now refers to 'well_project' to match the change in the Well model
    well = db.relationship('Well', back_populates='well_project')
    
    def to_dict(self):
        return {
            'id': str(self.id),
            'well_id': str(self.well_id),
            'project_name': self.project_name,
            # Convert Decimal to float for JSON compatibility
            'estimated_build_cost': float(self.estimated_build_cost) if self.estimated_build_cost is not None else None,
            'predicted_lifetime_cost': float(self.predicted_lifetime_cost) if self.predicted_lifetime_cost is not None else None,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class BreakageReport(db.Model):
    __tablename__ = 'breakage_reports'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    well_id = db.Column(UUID(as_uuid=True), db.ForeignKey('wells.id'), nullable=False)
    image_url = db.Column(db.Text)
    summary = db.Column(db.Text, nullable=False)
    status = db.Column(ENUM('reported', 'in_progress', 'fixed', name='report_status'), nullable=False, default='reported')
    fix_priority = db.Column(db.Integer, nullable=False, default=0)
    created_at = db.Column(db.DateTime(timezone=True), server_default=db.func.now())
    
    # --- NAME CHANGED ---
    # back_populates now refers to 'breakage_reports' to match the change in the Well model
    well = db.relationship('Well', back_populates='breakage_reports')
    
    def to_dict(self):
        return {
            'id': str(self.id),
            'well_id': str(self.well_id),
            'image_url': self.image_url,
            'summary': self.summary,
            'status': self.status,
            'fix_priority': self.fix_priority,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

