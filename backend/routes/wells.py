from flask import Blueprint, request, jsonify
from models import db
from datetime import datetime
from typing import Dict, Any

wells_bp = Blueprint('wells', __name__)

@wells_bp.route('/map', methods=['GET'])
def get_wells_for_map():
    """Get all wells with their locations and status for the map"""
    try:
        query = """
            SELECT 
                id,
                ST_X(location::geometry) as longitude,
                ST_Y(location::geometry) as latitude,
                status,
                capacity,
                current_load,
                service_area
            FROM wells
            WHERE status != 'draft'
            ORDER BY created_at DESC
        """
        
        cursor = db.session.connection().connection.cursor()
        cursor.execute(query)
        wells = cursor.fetchall()
        
        wells_data = []
        for well in wells:
            # Calculate usage percentage
            capacity = well[4] or 0
            current_load = well[5] or 0
            usage_percentage = (current_load / capacity * 100) if capacity > 0 else 0
            
            # Determine status color based on status and usage
            status_color = get_status_color(well[3], usage_percentage)
            
            wells_data.append({
                'id': well[0],
                'longitude': float(well[1]) if well[1] is not None else 0,
                'latitude': float(well[2]) if well[2] is not None else 0,
                'status': well[3],
                'capacity': capacity,
                'current_load': current_load,
                'usage_percentage': round(usage_percentage, 1),
                'status_color': status_color,
                'service_area': well[6] if well[6] else None
            })
        
        cursor.close()
        return jsonify(wells_data)
        
    except Exception as e:
        print(f"Get wells for map error: {e}")
        return jsonify({'error': 'Server error'}), 500

def get_status_color(status: str, usage_percentage: float) -> str:
    """Get the color for a well's marker based on its status and usage"""
    if status == 'broken':
        return '#EF4444'  # Red
    elif status == 'under_maintenance':
        return '#F59E0B'  # Yellow
    elif status == 'building':
        return '#6366F1'  # Indigo
    elif status == 'completed':
        if usage_percentage >= 90:
            return '#DC2626'  # Red
        elif usage_percentage >= 75:
            return '#F59E0B'  # Yellow
        else:
            return '#10B981'  # Green
    else:
        return '#6B7280'  # Gray

@wells_bp.route('/<well_id>/attendance', methods=['POST'])
def submit_attendance(well_id):
    """Submit attendance for a well by incrementing current_load"""
    try:
        # Update well's current_load
        update_query = """
            UPDATE wells
            SET current_load = current_load + 1,
                updated_at = NOW()
            WHERE id = %s
            RETURNING id, current_load, capacity
        """
        
        cursor = db.session.connection().connection.cursor()
        cursor.execute(update_query, [well_id])
        result = cursor.fetchone()
        
        if not result:
            return jsonify({'error': 'Well not found'}), 404
            
        well_id, current_load, capacity = result
        db.session.commit()
        cursor.close()
        
        # Return warning if well is getting full
        response = {
            'success': True,
            'current_load': current_load,
            'capacity': capacity,
            'is_near_capacity': current_load >= capacity * 0.8 if capacity else False
        }
        
        return jsonify(response)
        
    except Exception as e:
        print(f"Submit attendance error: {e}")
        return jsonify({'error': 'Server error'}), 500
