from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Admin, Well, Area
from datetime import datetime
import os

admin_bp = Blueprint('admin', __name__)

def require_admin(f):
    """Decorator to require admin authentication"""
    from functools import wraps
    
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            user_id = get_jwt_identity()
            admin = Admin.query.filter_by(id=user_id, is_admin=True).first()
            
            if not admin:
                return jsonify({'error': 'Admin access required'}), 403
            
            # Add admin to request context for use in route
            request.current_admin = admin
            return f(*args, **kwargs)
        except Exception as e:
            return jsonify({'error': 'Authentication required'}), 401
    
    return decorated_function

@admin_bp.route('/dashboard', methods=['GET'])
@jwt_required()
@require_admin
def get_dashboard_data():
    """Get admin dashboard data"""
    try:
        admin = request.current_admin
        
        # Get wells data with issue count
        wells_query = """
            SELECT 
                w.id,
                ST_X(w.location::geometry) as longitude,
                ST_Y(w.location::geometry) as latitude,
                w.status,
                w.capacity,
                w.current_load,
                w.area_id,
                w.service_area,
                w.created_at,
                w.updated_at,
                COUNT(br.id) as issue_count
            FROM wells w
            LEFT JOIN breakage_reports br ON w.id = br.well_id AND br.status != 'fixed'
            WHERE w.area_id = %s
            GROUP BY w.id, w.location, w.status, w.capacity, w.current_load, 
                     w.area_id, w.service_area, w.created_at, w.updated_at
            ORDER BY w.created_at DESC
        """
        
        # Execute wells query
        cursor = db.session.connection().connection.cursor()
        cursor.execute(wells_query, [admin.area_id])
        wells = cursor.fetchall()
        
        wells_data = []
        for well in wells:
            wells_data.append({
                'id': well[0],
                'longitude': float(well[1]) if well[1] is not None else 0,
                'latitude': float(well[2]) if well[2] is not None else 0,
                'status': well[3],
                'capacity': well[4],
                'current_load': well[5],
                'area_id': well[6],
                'service_area': well[7],
                'created_at': well[8].isoformat() if well[8] else None,
                'updated_at': well[9].isoformat() if well[9] else None,
                'issue_count': well[10]
            })
        
        # Get statistics
        stats_query = """
            SELECT 
                COUNT(*) as total_wells,
                COUNT(CASE WHEN status = 'completed' THEN 1 END) as operational_wells,
                COUNT(CASE WHEN status = 'broken' THEN 1 END) as broken_wells,
                COUNT(CASE WHEN status = 'under_maintenance' THEN 1 END) as maintenance_wells,
                COUNT(CASE WHEN status = 'building' THEN 1 END) as building_wells,
                COUNT(CASE WHEN status = 'draft' THEN 1 END) as draft_wells
            FROM wells
            WHERE area_id = %s
        """
        
        # Execute stats query
        cursor.execute(stats_query, [admin.area_id])
        stats_row = cursor.fetchone()
        
        stats = {
            'total': stats_row[0] or 0,
            'operational': stats_row[1] or 0,
            'broken': stats_row[2] or 0,
            'maintenance': stats_row[3] or 0,
            'building': stats_row[4] or 0,
            'draft': stats_row[5] or 0
        }
        
        cursor.close()
        
        return jsonify({
            'wells': wells_data,
            'stats': stats
        })
        
    except Exception as e:
        print(f"Dashboard error: {e}")
        return jsonify({'error': 'Server error'}), 500

def coordinates_to_point(latitude: float, longitude: float) -> str:
    """Convert latitude and longitude to PostGIS POINT format"""
    return f"POINT({longitude} {latitude})"

@admin_bp.route('/wells', methods=['POST'])
@jwt_required()
@require_admin
def create_well():
    """Create a new well"""
    try:
        admin = request.current_admin
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['latitude', 'longitude', 'status', 'capacity', 'current_load', 'service_area']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Validate status
        valid_statuses = ['draft', 'building', 'completed', 'broken', 'under_maintenance']
        if data['status'] not in valid_statuses:
            return jsonify({'error': 'Invalid status'}), 400
        
        # Validate coordinates
        try:
            latitude = float(data['latitude'])
            longitude = float(data['longitude'])
            if not (-90 <= latitude <= 90) or not (-180 <= longitude <= 180):
                return jsonify({'error': 'Invalid coordinates'}), 400
            point_location = coordinates_to_point(latitude, longitude)
        except (ValueError, TypeError):
            return jsonify({'error': 'Invalid coordinates format'}), 400
        
        # Create well with raw SQL
        insert_query = """
            INSERT INTO wells (
                location, status, capacity, current_load, area_id, service_area, created_at, updated_at
            ) VALUES (
                ST_GeomFromText(%s, 4326), %s, %s, %s, %s, %s, NOW(), NOW()
            ) RETURNING id, location, status, capacity, current_load, area_id, service_area, created_at, updated_at
        """
        
        cursor = db.session.connection().connection.cursor()
        cursor.execute(insert_query, [
            point_location,  # Use converted point location
            data['status'],
            data['capacity'],
            data['current_load'],
            admin.area_id,
            data['service_area']
        ])
        
        new_well = cursor.fetchone()
        db.session.commit()
        
        well_data = {
            'id': new_well[0],
            'location': new_well[1],
            'status': new_well[2],
            'capacity': new_well[3],
            'current_load': new_well[4],
            'area_id': new_well[5],
            'service_area': new_well[6],
            'created_at': new_well[7].isoformat() if new_well[7] else None,
            'updated_at': new_well[8].isoformat() if new_well[8] else None
        }
        
        cursor.close()
        return jsonify(well_data), 201
        
    except Exception as e:
        print(f"Create well error: {e}")
        return jsonify({'error': 'Server error'}), 500

@admin_bp.route('/wells/<well_id>', methods=['PUT'])
@jwt_required()
@require_admin
def update_well(well_id):
    """Update a well"""
    try:
        admin = request.current_admin
        data = request.get_json()
        
        # Validate status if provided
        if 'status' in data:
            valid_statuses = ['draft', 'building', 'completed', 'broken', 'under_maintenance']
            if data['status'] not in valid_statuses:
                return jsonify({'error': 'Invalid status'}), 400
        
        # Build update query dynamically based on provided fields
        update_fields = []
        update_values = []
        valid_fields = ['location', 'status', 'capacity', 'current_load', 'service_area']
        
        for field in valid_fields:
            if field in data:
                update_fields.append(f"{field} = %s")
                update_values.append(data[field])
        
        if not update_fields:
            return jsonify({'error': 'No valid fields to update'}), 400
        
        # Add updated_at and where clause values
        update_values.extend([well_id, admin.area_id])
        
        update_query = f"""
            UPDATE wells 
            SET {', '.join(update_fields)}, updated_at = NOW()
            WHERE id = %s AND area_id = %s
            RETURNING id, location, status, capacity, current_load, area_id, service_area, created_at, updated_at
        """
        
        cursor = db.session.connection().connection.cursor()
        cursor.execute(update_query, update_values)
        
        updated_well = cursor.fetchone()
        if not updated_well:
            return jsonify({'error': 'Well not found or unauthorized'}), 404
        
        db.session.commit()
        
        well_data = {
            'id': updated_well[0],
            'location': updated_well[1],
            'status': updated_well[2],
            'capacity': updated_well[3],
            'current_load': updated_well[4],
            'area_id': updated_well[5],
            'service_area': updated_well[6],
            'created_at': updated_well[7].isoformat() if updated_well[7] else None,
            'updated_at': updated_well[8].isoformat() if updated_well[8] else None
        }
        
        cursor.close()
        return jsonify(well_data)
        
    except Exception as e:
        print(f"Update well error: {e}")
        return jsonify({'error': 'Server error'}), 500

@admin_bp.route('/wells/<well_id>', methods=['DELETE'])
@jwt_required()
@require_admin
def delete_well(well_id):
    """Delete a well"""
    try:
        admin = request.current_admin
        
        delete_query = """
            DELETE FROM wells
            WHERE id = %s AND area_id = %s
            RETURNING id
        """
        
        cursor = db.session.connection().connection.cursor()
        cursor.execute(delete_query, [well_id, admin.area_id])
        
        deleted = cursor.fetchone()
        if not deleted:
            return jsonify({'error': 'Well not found or unauthorized'}), 404
        
        db.session.commit()
        cursor.close()
        
        return jsonify({'message': 'Well deleted successfully'})
        
    except Exception as e:
        print(f"Delete well error: {e}")
        return jsonify({'error': 'Server error'}), 500

@admin_bp.route('/wells/available', methods=['GET'])
def get_available_wells():
    """Get list of available wells for reporting"""
    try:
        # Get only completed wells
        query = """
            SELECT 
                id,
                ST_X(location::geometry) as longitude,
                ST_Y(location::geometry) as latitude,
                status,
                capacity,
                current_load
            FROM wells 
            WHERE status IN ('completed', 'broken', 'under_maintenance')
            ORDER BY created_at DESC
        """
        
        cursor = db.session.connection().connection.cursor()
        cursor.execute(query)
        wells = cursor.fetchall()
        
        wells_data = []
        for well in wells:
            wells_data.append({
                'id': well[0],
                'longitude': float(well[1]) if well[1] is not None else 0,
                'latitude': float(well[2]) if well[2] is not None else 0,
                'status': well[3],
                'capacity': well[4],
                'current_load': well[5]
            })
        
        cursor.close()
        return jsonify(wells_data)
        
    except Exception as e:
        print(f"Get available wells error: {e}")
        return jsonify({'error': 'Server error'}), 500