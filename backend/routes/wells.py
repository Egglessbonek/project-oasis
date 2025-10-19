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

@wells_bp.route('/map', methods=['GET'])
def get_wells_for_map():
    """
    Get wells data formatted for map display.
    """
    try:
        # Use raw SQL to extract coordinates and create service areas within area boundaries
        from sqlalchemy import text
        
        # Query wells with coordinates, service areas, and area boundaries
        query = text("""
            SELECT 
                w.id,
                ST_Y(w.location) as latitude,
                ST_X(w.location) as longitude,
                w.status,
                w.capacity,
                w.current_load,
                ST_AsText(w.service_area) as service_area_text,
                ST_AsText(a.boundary) as area_boundary_text,
                a.id as area_id,
                a.name as area_name
            FROM wells w
            JOIN areas a ON w.area_id = a.id
        """)
        
        result = db.session.execute(query)
        wells_data = result.fetchall()
        
        # Format wells data for map display
        map_wells = []
        area_boundaries = {}  # Store unique area boundaries
        
        for well in wells_data:
            # Parse area boundary coordinates
            area_coords = []
            if well.area_boundary_text:
                import re
                # Handle different geometry types (POLYGON, MULTIPOLYGON, etc.)
                geometry_match = re.search(r'(POLYGON|MULTIPOLYGON)\(\(([^)]+)\)\)', well.area_boundary_text)
                if geometry_match:
                    coords_str = geometry_match.group(2)
                    # Split by comma and parse each coordinate pair
                    coord_pairs = coords_str.split(',')
                    for pair in coord_pairs:
                        parts = pair.strip().split()
                        if len(parts) >= 2:
                            lng = float(parts[0])
                            lat = float(parts[1])
                            area_coords.append([lat, lng])  # Leaflet expects [lat, lng]
                else:
                    # Fallback: try to extract any coordinates from the geometry
                    numbers = re.findall(r'-?\d+\.?\d*', well.area_boundary_text)
                    if len(numbers) >= 4:  # At least 2 coordinate pairs
                        for i in range(0, len(numbers) - 1, 2):
                            lng = float(numbers[i])
                            lat = float(numbers[i + 1])
                            area_coords.append([lat, lng])
            
            # Parse service area coordinates
            service_area_coords = []
            if well.service_area_text:
                import re
                # Handle different geometry types (POLYGON, MULTIPOLYGON, etc.)
                geometry_match = re.search(r'(POLYGON|MULTIPOLYGON)\(\(([^)]+)\)\)', well.service_area_text)
                if geometry_match:
                    coords_str = geometry_match.group(2)
                    # Split by comma and parse each coordinate pair
                    coord_pairs = coords_str.split(',')
                    for pair in coord_pairs:
                        parts = pair.strip().split()
                        if len(parts) >= 2:
                            lng = float(parts[0])
                            lat = float(parts[1])
                            service_area_coords.append([lat, lng])  # Leaflet expects [lat, lng]
                else:
                    # Fallback: try to extract any coordinates from the geometry
                    numbers = re.findall(r'-?\d+\.?\d*', well.service_area_text)
                    if len(numbers) >= 4:  # At least 2 coordinate pairs
                        for i in range(0, len(numbers) - 1, 2):
                            lng = float(numbers[i])
                            lat = float(numbers[i + 1])
                            service_area_coords.append([lat, lng])
            
            # Store area boundary if not already stored
            if well.area_id not in area_boundaries and area_coords:
                area_boundaries[well.area_id] = {
                    'id': str(well.area_id),
                    'name': well.area_name,
                    'boundary_coords': area_coords
                }
            
            map_well = {
                'id': str(well.id),
                'latitude': float(well.latitude),
                'longitude': float(well.longitude),
                'status': well.status,
                'capacity': well.capacity,
                'current_load': well.current_load,
                'usage_percentage': well.current_load / well.capacity * 100 if well.capacity > 0 else 0,
                'status_color': '#10B981' if well.status == 'completed' else '#EF4444',
                'area_id': str(well.area_id),
                'area_name': well.area_name,
                'service_area_coords': service_area_coords
            }
            map_wells.append(map_well)
        
        # Add area boundaries to response
        response_data = {
            'wells': map_wells,
            'area_boundaries': list(area_boundaries.values())
        }
        
        current_app.logger.info(f"Retrieved {len(map_wells)} wells and {len(area_boundaries)} area boundaries for map display")
        return jsonify(response_data)
    except Exception as e:
        current_app.logger.error(f"Error getting wells for map: {e}", exc_info=True)
        return jsonify({"error": "Failed to get wells for map"}), 500


@wells_bp.route('/map/<uuid:area_id>', methods=['GET'])
def get_wells_for_map_by_area(area_id):
    """
    Get wells data formatted for map display for a specific area.
    Uses the area's boundary to create proper service areas.
    """
    try:
        # Use raw SQL to extract coordinates and create service areas within specific area boundary
        from sqlalchemy import text
        
        # Query wells for specific area with existing service areas
        query = text("""
            SELECT 
                w.id,
                ST_Y(w.location) as latitude,
                ST_X(w.location) as longitude,
                w.status,
                w.capacity,
                w.current_load,
                ST_AsText(w.service_area) as service_area_text,
                a.boundary as area_boundary
            FROM wells w
            JOIN areas a ON w.area_id = a.id
            WHERE a.id = :area_id
        """)
        
        result = db.session.execute(query, {"area_id": str(area_id)})
        wells_data = result.fetchall()
        
        # Format wells data for map display
        map_wells = []
        for well in wells_data:
            # Parse existing service area coordinates
            service_area_coords = []
            if well.service_area_text:
                import re
                # Handle different geometry types (POLYGON, MULTIPOLYGON, etc.)
                geometry_match = re.search(r'(POLYGON|MULTIPOLYGON)\(\(([^)]+)\)\)', well.service_area_text)
                if geometry_match:
                    coords_str = geometry_match.group(2)
                    # Split by comma and parse each coordinate pair
                    coord_pairs = coords_str.split(',')
                    for pair in coord_pairs:
                        parts = pair.strip().split()
                        if len(parts) >= 2:
                            lng = float(parts[0])
                            lat = float(parts[1])
                            service_area_coords.append([lat, lng])  # Leaflet expects [lat, lng]
                else:
                    # Fallback: try to extract any coordinates from the geometry
                    numbers = re.findall(r'-?\d+\.?\d*', well.service_area_text)
                    if len(numbers) >= 4:  # At least 2 coordinate pairs
                        for i in range(0, len(numbers) - 1, 2):
                            lng = float(numbers[i])
                            lat = float(numbers[i + 1])
                            service_area_coords.append([lat, lng])
            
            map_well = {
                'id': str(well.id),
                'latitude': float(well.latitude),
                'longitude': float(well.longitude),
                'status': well.status,
                'capacity': well.capacity,
                'current_load': well.current_load,
                'usage_percentage': well.current_load / well.capacity * 100 if well.capacity > 0 else 0,
                'status_color': '#10B981' if well.status == 'completed' else '#EF4444',
                'service_area': well.service_area_text,
                'service_area_coords': service_area_coords
            }
            map_wells.append(map_well)
        
        current_app.logger.info(f"Retrieved {len(map_wells)} wells for area {area_id}")
        return jsonify(map_wells)
    except Exception as e:
        current_app.logger.error(f"Error getting wells for map by area: {e}", exc_info=True)
        return jsonify({"error": "Failed to get wells for map by area"}), 500


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