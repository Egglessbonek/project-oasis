# =============================================================================
#                         Project Oasis - Area Routes
#
# This file contains all API endpoints related to areas.
# =============================================================================

from flask import Blueprint, jsonify, current_app
from models import Area
from schemas import AreaSchema, WellSchema
# Import the new service function
from utils import recalculate_service_areas

# Create a Blueprint for the area routes
areas_bp = Blueprint('areas', __name__, url_prefix='/api/areas')

# Initialize Marshmallow schemas
area_schema = AreaSchema()
areas_schema = AreaSchema(many=True)
wells_schema = WellSchema(many=True) # For returning the updated wells

@areas_bp.route('/', methods=['GET'])
def get_areas():
    """
    Endpoint to retrieve a list of all administrative areas.
    """
    all_areas = Area.query.all()
    result = areas_schema.dump(all_areas)
    return jsonify(result)


@areas_bp.route('/<uuid:area_id>/calculate-service-areas', methods=['POST', 'GET'])
def calculate_areas(area_id):
    """
    Triggers the service area recalculation for a given area.
    """
    try:
        updated_wells = recalculate_service_areas(area_id)
        return jsonify(wells_schema.dump(updated_wells))
    except Exception as e:
        current_app.logger.error(f"Failed to calculate areas: {e}", exc_info=True)
        return jsonify({"error": "An error occurred during calculation", "message": str(e)}), 500