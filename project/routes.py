# =============================================================================
#                         Project Oasis - API Routes
#
# This file contains the main API endpoints for our application.
# We are now adding a POST method to the /wells route to allow for
# the creation of new wells.
#
# =============================================================================

from flask import Blueprint, jsonify, request
from .models import Area, Well
from .schemas import AreaSchema, WellSchema
from .database import db

# Create a Blueprint for our main API routes
api_bp = Blueprint('api', __name__, url_prefix='/api')

# Initialize Marshmallow schemas
area_schema = AreaSchema()
areas_schema = AreaSchema(many=True)
well_schema = WellSchema()
wells_schema = WellSchema(many=True)


@api_bp.route('/areas', methods=['GET'])
def get_areas():
    """Endpoint to retrieve a list of all administrative areas."""
    all_areas = Area.query.all()
    result = areas_schema.dump(all_areas)
    return jsonify(result)


@api_bp.route('/wells', methods=['GET', 'POST'])
def handle_wells():
    """
    Endpoint to handle retrieving and creating wells.
    """
    if request.method == 'POST':
        # --- Create a new well ---
        data = request.get_json()
        if not data:
            return jsonify({"error": "No input data provided"}), 400

        try:
            # Validate and deserialize the incoming data
            new_well = well_schema.load(data, session=db.session)

            # Add to the session and commit to the database
            db.session.add(new_well)
            db.session.commit()

            # Return the newly created well's data with a 201 Created status
            return jsonify(well_schema.dump(new_well)), 201
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": "Failed to create well", "messages": str(e)}), 400

    else: # request.method == 'GET'
        # --- Retrieve all wells ---
        all_wells = Well.query.all()
        result = wells_schema.dump(all_wells)
        return jsonify(result)