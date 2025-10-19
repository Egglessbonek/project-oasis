# =============================================================================
#                         Project Oasis - Area Routes
#
# This file contains all API endpoints related to areas.
# =============================================================================

from flask import Blueprint, jsonify
from models import Area
from schemas import AreaSchema

# Create a Blueprint for the area routes
areas_bp = Blueprint('areas', __name__, url_prefix='/api/areas')

# Initialize Marshmallow schemas
area_schema = AreaSchema()
areas_schema = AreaSchema(many=True)

@areas_bp.route('/', methods=['GET'])
def get_areas():
    """
    Endpoint to retrieve a list of all administrative areas.
    """
    all_areas = Area.query.all()
    result = areas_schema.dump(all_areas)
    return jsonify(result)