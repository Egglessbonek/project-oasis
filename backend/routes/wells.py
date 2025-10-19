# =============================================================================
#                         Project Oasis - Well Routes
#
# This file contains all API endpoints related to wells.
# =============================================================================

from flask import Blueprint, jsonify, request, current_app
from models import Well, db
from schemas import WellSchema, WellSchema
# Import the new service function
from utils import recalculate_service_areas

# Create a Blueprint for the well routes
wells_bp = Blueprint('wells', __name__, url_prefix='/api/wells')

# Initialize Marshmallow schemas
well_schema = WellSchema()
wells_schema = WellSchema(many=True)


@wells_bp.route('/', methods=['GET', 'POST'])
def handle_wells():
    """
    Endpoint for retrieving a list of all wells and creating a new well.
    """
    if request.method == 'POST':
        # --- Create a new well ---
        data = request.get_json()
        if not data:
            return jsonify({"error": "No input data provided"}), 400

        try:
            new_well = well_schema.load(data)
            db.session.add(new_well)
            db.session.commit()
            return jsonify(well_schema.dump(new_well)), 201
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": "Failed to create well", "messages": str(e)}), 400

    else: # request.method == 'GET'
        # --- Retrieve all wells ---
        all_wells = Well.query.all()
        result = wells_schema.dump(all_wells)
        return jsonify(result)


@wells_bp.route('/<uuid:well_id>', methods=['GET', 'PUT', 'PATCH', 'DELETE'])
def handle_well(well_id):
    """
    Endpoint for handling operations on a single well (Read, Update, Delete).
    """
    well = Well.query.get_or_404(well_id)

    if request.method == 'GET':
        # --- Retrieve a single well ---
        return jsonify(well_schema.dump(well))

    if request.method in ['PUT', 'PATCH']:
        # --- Update an existing well ---
        data = request.get_json()
        if not data:
            return jsonify({"error": "No input data provided"}), 400
        
        is_partial = request.method == 'PATCH'
        try:
            updated_well = well_schema.load(data, instance=well, partial=is_partial, session=db.session)
            db.session.commit()
            return jsonify(well_schema.dump(updated_well))
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": "Failed to update well", "messages": str(e)}), 400

    if request.method == 'DELETE':
        # --- Delete a well ---
        try:
            db.session.delete(well)
            db.session.commit()
            return '', 204
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": "Failed to delete well", "messages": str(e)}), 500


@wells_bp.route('/<uuid:well_id>/attendance', methods=['POST'])
def submit_attendance(well_id):
    """
    Submit attendance for a well by incrementing current_load.
    """
    try:
        well = Well.query.get_or_404(well_id)
        well.current_load += 1
        db.session.commit()
        
        response = {
            'success': True,
            'current_load': well.current_load,
            'capacity': well.capacity,
            'is_near_capacity': well.current_load >= well.capacity * 0.8 if well.capacity else False
        }
        return jsonify(response)
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Submit attendance error: {e}", exc_info=True)
        return jsonify({'error': 'Server error'}), 500


# --- --- --- --- --- --- --- --- --- --- ---
# --- --- --- NEW ENDPOINT HERE --- ---
# --- --- --- --- --- --- --- --- --- --- ---

@wells_bp.route('/<uuid:well_id>/update-weight', methods=['POST'])
def update_well_weight(well_id):
    """
    Updates a well's capacity (weight) based on a relative score
    and triggers a recalculation of the entire area's service polygons.
    """
    data = request.get_json()
    score = data.get('score')

    if score is None:
        return jsonify({"error": "Missing 'score' in request body"}), 400
    
    try:
        score = float(score)
        if not -1.0 <= score <= 1.0:
            raise ValueError("Score must be between -1.0 and 1.0")
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    try:
        well = Well.query.get_or_404(well_id)
        
        # --- 1. Update the well's capacity ---
        current_capacity = well.capacity
        # Apply the relative change
        new_capacity = current_capacity * (1 + score)
        
        # Ensure capacity is an integer and not negative
        well.capacity = max(0, int(new_capacity)) 
        
        # As you described: if score is -1, it implies an issue,
        # so we also mark the well as broken.
        if score == -1.0:
            well.status = 'broken'
        
        db.session.commit()
        current_app.logger.info(f"Updated well {well.id} capacity from {current_capacity} to {well.capacity}")

        # --- 2. Trigger recalculation for the entire area ---
        # This is the most important part.
        current_app.logger.info(f"Triggering recalculation for area {well.area_id}...")
        recalculate_service_areas(well.area_id)

        # --- 3. Return the updated well ---
        return jsonify(well_schema.dump(well))

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error in update-weight: {e}", exc_info=True)
        return jsonify({"error": "Failed to update well weight", "message": str(e)}), 500