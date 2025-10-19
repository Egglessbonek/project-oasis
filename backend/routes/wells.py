from flask import Blueprint, request, jsonify
from models import db
from datetime import datetime

wells_bp = Blueprint('wells', __name__)

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
