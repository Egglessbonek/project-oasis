from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models import User, Report, Comment

api_bp = Blueprint('api', __name__)

# Reports endpoints
@api_bp.route('/reports', methods=['GET'])
@jwt_required()
def get_reports():
    """Get all reports with optional filtering"""
    try:
        # Get query parameters
        status = request.args.get('status')
        priority = request.args.get('priority')
        category = request.args.get('category')
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        # Build query
        query = Report.query
        
        if status:
            query = query.filter(Report.status == status)
        if priority:
            query = query.filter(Report.priority == priority)
        if category:
            query = query.filter(Report.category == category)
        
        # Paginate results
        reports = query.order_by(Report.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'reports': [report.to_dict() for report in reports.items],
            'total': reports.total,
            'pages': reports.pages,
            'current_page': page,
            'per_page': per_page
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/reports', methods=['POST'])
@jwt_required()
def create_report():
    """Create a new report"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data or not data.get('title') or not data.get('description'):
            return jsonify({'error': 'Title and description are required'}), 400
        
        report = Report(
            title=data['title'],
            description=data['description'],
            priority=data.get('priority', 'medium'),
            category=data.get('category'),
            location=data.get('location'),
            user_id=user_id
        )
        
        db.session.add(report)
        db.session.commit()
        
        return jsonify({
            'message': 'Report created successfully',
            'report': report.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@api_bp.route('/reports/<int:report_id>', methods=['GET'])
@jwt_required()
def get_report(report_id):
    """Get a specific report with comments"""
    try:
        report = Report.query.get(report_id)
        
        if not report:
            return jsonify({'error': 'Report not found'}), 404
        
        report_data = report.to_dict()
        report_data['comments'] = [comment.to_dict() for comment in report.comments]
        
        return jsonify({'report': report_data}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/reports/<int:report_id>', methods=['PUT'])
@jwt_required()
def update_report(report_id):
    """Update a specific report"""
    try:
        user_id = get_jwt_identity()
        report = Report.query.get(report_id)
        
        if not report:
            return jsonify({'error': 'Report not found'}), 404
        
        # Check if user owns the report or is admin
        user = User.query.get(user_id)
        if report.user_id != user_id and not user.is_admin:
            return jsonify({'error': 'Not authorized to update this report'}), 403
        
        data = request.get_json()
        
        # Update allowed fields
        if 'title' in data:
            report.title = data['title']
        if 'description' in data:
            report.description = data['description']
        if 'status' in data:
            report.status = data['status']
        if 'priority' in data:
            report.priority = data['priority']
        if 'category' in data:
            report.category = data['category']
        if 'location' in data:
            report.location = data['location']
        
        db.session.commit()
        
        return jsonify({
            'message': 'Report updated successfully',
            'report': report.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@api_bp.route('/reports/<int:report_id>', methods=['DELETE'])
@jwt_required()
def delete_report(report_id):
    """Delete a specific report"""
    try:
        user_id = get_jwt_identity()
        report = Report.query.get(report_id)
        
        if not report:
            return jsonify({'error': 'Report not found'}), 404
        
        # Check if user owns the report or is admin
        user = User.query.get(user_id)
        if report.user_id != user_id and not user.is_admin:
            return jsonify({'error': 'Not authorized to delete this report'}), 403
        
        db.session.delete(report)
        db.session.commit()
        
        return jsonify({'message': 'Report deleted successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Comments endpoints
@api_bp.route('/reports/<int:report_id>/comments', methods=['POST'])
@jwt_required()
def create_comment(report_id):
    """Create a comment on a report"""
    try:
        user_id = get_jwt_identity()
        report = Report.query.get(report_id)
        
        if not report:
            return jsonify({'error': 'Report not found'}), 404
        
        data = request.get_json()
        
        if not data or not data.get('content'):
            return jsonify({'error': 'Content is required'}), 400
        
        comment = Comment(
            content=data['content'],
            report_id=report_id,
            user_id=user_id
        )
        
        db.session.add(comment)
        db.session.commit()
        
        return jsonify({
            'message': 'Comment created successfully',
            'comment': comment.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@api_bp.route('/comments/<int:comment_id>', methods=['PUT'])
@jwt_required()
def update_comment(comment_id):
    """Update a comment"""
    try:
        user_id = get_jwt_identity()
        comment = Comment.query.get(comment_id)
        
        if not comment:
            return jsonify({'error': 'Comment not found'}), 404
        
        # Check if user owns the comment or is admin
        user = User.query.get(user_id)
        if comment.user_id != user_id and not user.is_admin:
            return jsonify({'error': 'Not authorized to update this comment'}), 403
        
        data = request.get_json()
        
        if not data or not data.get('content'):
            return jsonify({'error': 'Content is required'}), 400
        
        comment.content = data['content']
        db.session.commit()
        
        return jsonify({
            'message': 'Comment updated successfully',
            'comment': comment.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@api_bp.route('/comments/<int:comment_id>', methods=['DELETE'])
@jwt_required()
def delete_comment(comment_id):
    """Delete a comment"""
    try:
        user_id = get_jwt_identity()
        comment = Comment.query.get(comment_id)
        
        if not comment:
            return jsonify({'error': 'Comment not found'}), 404
        
        # Check if user owns the comment or is admin
        user = User.query.get(user_id)
        if comment.user_id != user_id and not user.is_admin:
            return jsonify({'error': 'Not authorized to delete this comment'}), 403
        
        db.session.delete(comment)
        db.session.commit()
        
        return jsonify({'message': 'Comment deleted successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Admin endpoints
@api_bp.route('/admin/users', methods=['GET'])
@jwt_required()
def get_all_users():
    """Get all users (admin only)"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user or not user.is_admin:
            return jsonify({'error': 'Admin access required'}), 403
        
        users = User.query.all()
        
        return jsonify({
            'users': [user.to_dict() for user in users]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/admin/stats', methods=['GET'])
@jwt_required()
def get_admin_stats():
    """Get admin dashboard statistics"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user or not user.is_admin:
            return jsonify({'error': 'Admin access required'}), 403
        
        stats = {
            'total_users': User.query.count(),
            'total_reports': Report.query.count(),
            'open_reports': Report.query.filter_by(status='open').count(),
            'in_progress_reports': Report.query.filter_by(status='in_progress').count(),
            'resolved_reports': Report.query.filter_by(status='resolved').count(),
            'closed_reports': Report.query.filter_by(status='closed').count(),
            'total_comments': Comment.query.count()
        }
        
        return jsonify({'stats': stats}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
