# =============================================================================
#                        Project Oasis - Schemas
#
# This file defines the Marshmallow schemas for our models.
#
# We are now adding explicit nested schemas to handle relationships and
# prevent circular serialization loops, which was causing the 500 error.
#
# =============================================================================

from marshmallow import fields, ValidationError
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from geoalchemy2.shape import to_shape
from shapely.geometry import shape
from models import Area, Admin, Well, WellProject, BreakageReport

# --- Custom Field for GeoJSON ---
class GeometryField(fields.Field):
    """
    Custom Marshmallow field to serialize/deserialize GeoAlchemy2 Geometry
    objects into/from GeoJSON format.
    """
    def _serialize(self, value, attr, obj, **kwargs):
        if value is None:
            return None
        return to_shape(value).__geo_interface__

    def _deserialize(self, value, attr, data, **kwargs):
        if not isinstance(value, dict) or 'type' not in value or 'coordinates' not in value:
            raise ValidationError("Invalid GeoJSON object.")
        try:
            geom = shape(value)
            return f'SRID=4326;{geom.wkt}'
        except Exception as e:
            raise ValidationError(f"Could not parse GeoJSON: {e}")


# --- Model Schemas (Updated with explicit nesting) ---

class WellProjectSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = WellProject
        load_instance = True
        include_fk = True
        # Exclude the back-reference to prevent loops
        exclude = ("well",)

class BreakageReportSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = BreakageReport
        load_instance = True
        include_fk = True
        # Exclude the back-reference to prevent loops
        exclude = ("well",)

class WellSchema(SQLAlchemyAutoSchema):
    location = GeometryField(attribute='location')
    service_area = GeometryField(attribute='service_area')
    
    # --- ADDED: Explicitly define nested relationships ---
    # This tells WellSchema how to serialize the related objects.
    well_project = fields.Nested(WellProjectSchema, allow_none=True)
    breakage_reports = fields.Nested(BreakageReportSchema, many=True)

    class Meta:
        model = Well
        load_instance = True
        include_fk = True

class AreaSchema(SQLAlchemyAutoSchema):
    boundary = GeometryField(attribute='boundary')
    # We can also nest the wells within an area if needed, but will exclude for now
    # to keep the payload smaller.
    
    class Meta:
        model = Area
        load_instance = True
        include_fk = True

class AdminSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Admin
        load_instance = True
        # Never expose sensitive info in API responses
        exclude = ('password_hash', 'access_token', 'refresh_token')
