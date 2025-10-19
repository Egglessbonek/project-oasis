# =============================================================================
#                         Project Oasis - Models
#
# This file defines the Python classes that represent our database tables.
#
# We are changing the type of our geospatial columns from Geography to Geometry.
# This is a common fix to resolve function compatibility issues within PostGIS,
# as the Geometry type is more universally supported by PostGIS functions.
#
# =============================================================================

from .database import db
from sqlalchemy.dialects.postgresql import UUID, ENUM
from geoalchemy2 import Geometry # We are using Geometry, not Geography
import uuid

class Area(db.Model):
    __tablename__ = 'areas'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = db.Column(db.Text, nullable=False, unique=True)
    # CHANGED from Geography to Geometry
    boundary = db.Column(Geometry(geometry_type='POLYGON', srid=4326), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), server_default=db.func.now())

    admins = db.relationship('Admin', back_populates='area', lazy=True)
    wells = db.relationship('Well', back_populates='area', lazy=True)

    def __repr__(self):
        return f'<Area {self.name}>'

class Admin(db.Model):
    __tablename__ = 'admins'
    # ... (no changes in this class) ...
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = db.Column(db.String(255), nullable=False, unique=True)
    password_hash = db.Column(db.Text, nullable=False)
    area_id = db.Column(UUID(as_uuid=True), db.ForeignKey('areas.id'), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), server_default=db.func.now())
    area = db.relationship('Area', back_populates='admins')
    def __repr__(self):
        return f'<Admin {self.email}>'


class Well(db.Model):
    __tablename__ = 'wells'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    # CHANGED from Geography to Geometry
    location = db.Column(Geometry(geometry_type='POINT', srid=4326), nullable=False)
    service_area = db.Column(Geometry(geometry_type='POLYGON', srid=4326))
    
    status = db.Column(ENUM('draft', 'building', 'completed', 'broken', 'under_maintenance', name='well_status'), nullable=False, default='draft')
    capacity = db.Column(db.Integer, nullable=False)
    current_load = db.Column(db.Integer, nullable=False, default=0)
    
    area_id = db.Column(UUID(as_uuid=True), db.ForeignKey('areas.id'), nullable=False)
    area = db.relationship('Area', back_populates='wells')
    
    project = db.relationship('WellProject', back_populates='well', uselist=False, cascade="all, delete-orphan")
    reports = db.relationship('BreakageReport', back_populates='well', cascade="all, delete-orphan")
    
    created_at = db.Column(db.DateTime(timezone=True), server_default=db.func.now())
    updated_at = db.Column(db.DateTime(timezone=True), server_default=db.func.now(), onupdate=db.func.now())

# ... (no changes in WellProject or BreakageReport) ...
class WellProject(db.Model):
    __tablename__ = 'well_projects'
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    well_id = db.Column(UUID(as_uuid=True), db.ForeignKey('wells.id'), nullable=False, unique=True)
    project_name = db.Column(db.Text, nullable=False)
    estimated_build_cost = db.Column(db.Numeric(12, 2), nullable=False)
    predicted_lifetime_cost = db.Column(db.Numeric(12, 2))
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime(timezone=True), server_default=db.func.now())
    well = db.relationship('Well', back_populates='project')

class BreakageReport(db.Model):
    __tablename__ = 'breakage_reports'
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    well_id = db.Column(UUID(as_uuid=True), db.ForeignKey('wells.id'), nullable=False)
    image_url = db.Column(db.Text)
    summary = db.Column(db.Text, nullable=False)
    status = db.Column(ENUM('reported', 'in_progress', 'fixed', name='report_status'), nullable=False, default='reported')
    fix_priority = db.Column(db.Integer, nullable=False, default=0)
    created_at = db.Column(db.DateTime(timezone=True), server_default=db.func.now())
    well = db.relationship('Well', back_populates='reports')

