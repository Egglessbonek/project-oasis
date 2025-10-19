from flask import Blueprint, request, jsonify
from models import db
from datetime import datetime
import json

reports_bp = Blueprint('reports', __name__)

@reports_bp.route('', methods=['POST'])
def create_report():
    """Create a new report"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['wellId', 'issueType', 'description']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Map issue type to well status
        issue_status_map = {
            'no-water': 'broken',
            'low-pressure': 'under_maintenance',
            'contamination': 'broken',
            'mechanical': 'under_maintenance',
            'electrical': 'broken',
            'leak': 'broken',
            'other': 'under_maintenance'
        }
        
        # Format new report as a string
        new_report = f"""[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {data['issueType']}: {data['description']} - Reporter: {data.get('contactName', 'Anonymous')} ({data.get('contactPhone', 'Not provided')})"""

        # First get current comments array
        cursor = db.session.connection().connection.cursor()
        cursor.execute(
            "SELECT comments FROM wells WHERE id = %s",
            [data['wellId']]
        )
        result = cursor.fetchone()
        
        if not result:
            return jsonify({'error': 'Well not found'}), 404
            
        current_comments = result[0] or []  # If None, use empty array
        
        # Append new report to comments array
        if not current_comments:
            # If no comments exist, create new array with single item
            array_literal = '{' + f'"{new_report}"' + '}'
        else:
            # Append to existing array
            array_literal = '{' + ','.join(f'"{comment}"' for comment in current_comments) + f',"{new_report}"' + '}'

        # Update well with new status and comments array
        update_query = """
            UPDATE wells
            SET status = %s,
                comments = %s::TEXT[],
                updated_at = NOW()
            WHERE id = %s
            RETURNING id
        """
        
        cursor.execute(update_query, [
            issue_status_map[data['issueType']],
            array_literal,
            data['wellId']
        ])
        
        db.session.commit()
        cursor.close()
        
        return jsonify({'success': True}), 201
        
    except Exception as e:
        print(f"Create report error: {e}")
        return jsonify({'error': 'Server error'}), 500