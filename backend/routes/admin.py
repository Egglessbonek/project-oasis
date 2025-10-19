from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Admin, Well, BreakageReport, Area
from sqlalchemy import func, text
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
                w.location,
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
                'location': well[1],
                'status': well[2],
                'capacity': well[3],
                'current_load': well[4],
                'area_id': well[5],
                'service_area': well[6],
                'created_at': well[7].isoformat() if well[7] else None,
                'updated_at': well[8].isoformat() if well[8] else None,
                'issue_count': well[9]
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

@admin_bp.route('/wells', methods=['GET'])
@jwt_required()
@require_admin
def get_wells():
    """Get wells list"""
    try:
        admin = request.current_admin
        
        # Get query parameters
        status = request.args.get('status')
        limit = int(request.args.get('limit', 50))
        offset = int(request.args.get('offset', 0))
        
        # Build query
        query = Well.query.filter_by(area_id=admin.area_id)
        
        if status:
            query = query.filter_by(status=status)
        
        wells = query.order_by(Well.created_at.desc()).offset(offset).limit(limit).all()
        
        wells_data = []
        for well in wells:
            # Get issue count
            issue_count = BreakageReport.query.filter(
                BreakageReport.well_id == well.id,
                BreakageReport.status != 'fixed'
            ).count()
            
            wells_data.append({
                'id': well.id,
                'status': well.status,
                'capacity': well.capacity,
                'current_load': well.current_load,
                'location': well.location,
                'created_at': well.created_at.isoformat() if well.created_at else None,
                'updated_at': well.updated_at.isoformat() if well.updated_at else None,
                'issue_count': issue_count
            })
        
        return jsonify(wells_data)
        
    except Exception as e:
        print(f"Wells list error: {e}")
        return jsonify({'error': 'Server error'}), 500

@admin_bp.route('/reports', methods=['GET'])
@jwt_required()
@require_admin
def get_reports():
    """Get breakage reports"""
    try:
        admin = request.current_admin
        
        # Get query parameters
        status = request.args.get('status')
        limit = int(request.args.get('limit', 50))
        offset = int(request.args.get('offset', 0))
        
        # Build query
        query = db.session.query(BreakageReport).join(
            Well, BreakageReport.well_id == Well.id
        ).filter(Well.area_id == admin.area_id)
        
        if status:
            query = query.filter(BreakageReport.status == status)
        
        reports = query.order_by(
            BreakageReport.fix_priority.desc(), 
            BreakageReport.created_at.desc()
        ).offset(offset).limit(limit).all()
        
        reports_data = []
        for report in reports:
            reports_data.append(report.to_dict())
        
        return jsonify(reports_data)
        
    except Exception as e:
        print(f"Reports list error: {e}")
        return jsonify({'error': 'Server error'}), 500

@admin_bp.route('/wells/<well_id>/status', methods=['PUT'])
@jwt_required()
@require_admin
def update_well_status(well_id):
    """Update well status"""
    try:
        admin = request.current_admin
        data = request.get_json()
        status = data.get('status')
        
        # Validate status
        valid_statuses = ['draft', 'building', 'completed', 'broken', 'under_maintenance']
        if status not in valid_statuses:
            return jsonify({'error': 'Invalid status'}), 400
        
        # Find well in admin's area
        well = Well.query.filter_by(
            id=well_id, 
            area_id=admin.area_id
        ).first()
        
        if not well:
            return jsonify({'error': 'Well not found'}), 404
        
        # Update status
        well.status = status
        db.session.commit()
        
        return jsonify({
            'id': well.id,
            'status': well.status,
            'updated_at': well.updated_at.isoformat() if well.updated_at else None
        })
        
    except Exception as e:
        db.session.rollback()
        print(f"Update well status error: {e}")
        return jsonify({'error': 'Server error'}), 500

@admin_bp.route('/reports/<report_id>/status', methods=['PUT'])
@jwt_required()
@require_admin
def update_report_status(report_id):
    """Update report status"""
    try:
        admin = request.current_admin
        data = request.get_json()
        status = data.get('status')
        
        # Validate status
        valid_statuses = ['reported', 'in_progress', 'fixed']
        if status not in valid_statuses:
            return jsonify({'error': 'Invalid status'}), 400
        
        # Find report in admin's area
        report = db.session.query(BreakageReport).join(
            Well, BreakageReport.well_id == Well.id
        ).filter(
            BreakageReport.id == report_id,
            Well.area_id == admin.area_id
        ).first()
        
        if not report:
            return jsonify({'error': 'Report not found'}), 404
        
        # Update status
        report.status = status
        db.session.commit()
        
        return jsonify({
            'id': report.id,
            'status': report.status
        })
        
    except Exception as e:
        db.session.rollback()
        print(f"Update report status error: {e}")
        return jsonify({'error': 'Server error'}), 500

@admin_bp.route('/profile', methods=['GET'])
@jwt_required()
@require_admin
def get_profile():
    """Get admin profile"""
    try:
        admin = request.current_admin
        
        # Get area name
        area = Area.query.filter_by(id=admin.area_id).first()
        
        profile_data = {
            'id': admin.id,
            'email': admin.email,
            'area_id': admin.area_id,
            'area_name': area.name if area else None,
            'is_admin': admin.is_admin,
            'created_at': admin.created_at.isoformat() if admin.created_at else None
        }
        
        return jsonify(profile_data)
        
    except Exception as e:
        print(f"Get profile error: {e}")
        return jsonify({'error': 'Server error'}), 500
