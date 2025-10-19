# =============================================================================
#                        Project Oasis - Schemas
#
# This file defines the Marshmallow schemas for our models.
#
# We are now updating our custom GeometryField to handle deserialization.
# This will allow it to take incoming GeoJSON from a POST request and convert
# it into a format that SQLAlchemy and PostGIS can understand and save.
#
# =============================================================================

from marshmallow import fields, ValidationError
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from geoalchemy2.shape import to_shape
from shapely.geometry import shape # Used for deserialization
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
            # Convert the GeoJSON dict to a Shapely object
            geom = shape(value)
            # Convert the Shapely object to a WKT string with SRID, which GeoAlchemy2 understands
            return f'SRID=4326;{geom.wkt}'
        except Exception as e:
            raise ValidationError(f"Could not parse GeoJSON: {e}")


# --- Model Schemas ---
class AreaSchema(SQLAlchemyAutoSchema):
    # We make the geometry field writeable by removing dump_only=True
    boundary = GeometryField(attribute='boundary')

    class Meta:
        model = Area
        load_instance = True
        include_fk = True

class AdminSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Admin
        load_instance = True
        exclude = ('password_hash',)

class WellSchema(SQLAlchemyAutoSchema):
    # We make the geometry fields writeable by removing dump_only=True
    location = GeometryField(attribute='location')
    service_area = GeometryField(attribute='service_area')

    class Meta:
        model = Well
        load_instance = True
        include_fk = True

class WellProjectSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = WellProject
        load_instance = True
        include_fk = True

class BreakageReportSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = BreakageReport
        load_instance = True
        include_fk = True