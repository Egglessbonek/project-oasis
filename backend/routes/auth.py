from flask import Blueprint, request, jsonify, session, redirect, url_for
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import check_password_hash, generate_password_hash
from models import db, Admin, Area
from authlib.integrations.flask_client import OAuth
import os
from datetime import datetime, timedelta
import requests
import secrets

auth_bp = Blueprint('auth', __name__)

# Initialize OAuth
oauth = OAuth()

def init_oauth(app):
    """Initialize OAuth with Flask app"""
    oauth.init_app(app)
    
    # Configure OAuth providers after app initialization
    oauth.register(
        'google',
        client_id=os.getenv('GOOGLE_CLIENT_ID'),
        client_secret=os.getenv('GOOGLE_CLIENT_SECRET'),
        server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
        client_kwargs={'scope': 'openid email profile'}
    )
    
    oauth.register(
        'github',
        client_id=os.getenv('GITHUB_CLIENT_ID'),
        client_secret=os.getenv('GITHUB_CLIENT_SECRET'),
        access_token_url='https://github.com/login/oauth/access_token',
        access_token_params=None,
        authorize_url='https://github.com/login/oauth/authorize',
        authorize_params=None,
        api_base_url='https://api.github.com/',
        client_kwargs={'scope': 'user:email'}
    )
    
    # Get the registered providers
    global google, github
    google = oauth.google
    github = oauth.github

# Helper function to verify admin status
def verify_admin(user_id):
    """Verify that user is an admin"""
    admin = Admin.query.filter_by(id=user_id, is_admin=True).first()
    return admin is not None

# Helper function to get or create admin from OAuth
def get_or_create_admin_from_oauth(provider, oauth_data):
    """Get existing admin or create new one from OAuth data"""
    oauth_id = str(oauth_data.get('id'))
    email = oauth_data.get('email')
    
    # First, check if user exists by OAuth ID
    admin = Admin.query.filter_by(oauth_id=oauth_id).first()
    
    if admin:
        # User exists, check if they are admin
        if admin.is_admin:
            # Update tokens and allow access
            admin.access_token = oauth_data.get('access_token')
            admin.refresh_token = oauth_data.get('refresh_token')
            admin.token_expires_at = datetime.utcnow() + timedelta(hours=1)
            admin.updated_at = datetime.utcnow()
            db.session.commit()
            return admin
        else:
            # User exists but is_admin is False, set it to True and allow access
            admin.is_admin = True
            admin.access_token = oauth_data.get('access_token')
            admin.refresh_token = oauth_data.get('refresh_token')
            admin.token_expires_at = datetime.utcnow() + timedelta(hours=1)
            admin.updated_at = datetime.utcnow()
            db.session.commit()
            return admin
    
    # User doesn't exist, check if there's an existing admin with same email
    admin = Admin.query.filter_by(email=email).first()
    if admin:
        # Admin exists with this email, link OAuth and ensure is_admin = True
        admin.oauth_id = oauth_id
        admin.is_admin = True
        admin.access_token = oauth_data.get('access_token')
        admin.refresh_token = oauth_data.get('refresh_token')
        admin.token_expires_at = datetime.utcnow() + timedelta(hours=1)
        admin.updated_at = datetime.utcnow()
        db.session.commit()
        return admin
    
    # User doesn't exist at all, create new admin with is_admin = True
    # Get the first area for the new admin (you might want to modify this logic)
    area = Area.query.first()
    if not area:
        # No area exists, cannot create admin
        return None
    
    admin = Admin(
        email=email,
        area_id=area.id,
        is_admin=True,
        oauth_id=oauth_id,
        access_token=oauth_data.get('access_token'),
        refresh_token=oauth_data.get('refresh_token'),
        token_expires_at=datetime.utcnow() + timedelta(hours=1)
    )
    # Set a default password hash (user won't use it since they use OAuth)
    admin.password_hash = generate_password_hash('oauth_user_default_password')
    
    db.session.add(admin)
    db.session.commit()
    return admin

@auth_bp.route('/login', methods=['POST'])
def login():
    """Email/password login"""
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        
        if not email or not password:
            return jsonify({'error': 'Email and password required'}), 400
        
        # Find admin user
        admin = Admin.query.filter_by(email=email, is_admin=True).first()
        
        if not admin or not admin.check_password(password):
            return jsonify({'error': 'Invalid credentials'}), 401
        
        # Create JWT token
        access_token = create_access_token(
            identity=admin.id,
            additional_claims={
                'email': admin.email,
                'is_admin': admin.is_admin,
                'area_id': admin.area_id
            }
        )
        
        return jsonify({
            'success': True,
            'user': {
                'id': admin.id,
                'email': admin.email,
                'area_id': admin.area_id,
                'is_admin': admin.is_admin
            },
            'token': access_token
        })
        
    except Exception as e:
        return jsonify({'error': 'Server error'}), 500

@auth_bp.route('/google')
def google_login():
    """Initiate Google OAuth login"""
    redirect_uri = url_for('auth.google_callback', _external=True)
    return google.authorize_redirect(redirect_uri)

@auth_bp.route('/google/callback')
def google_callback():
    """Handle Google OAuth callback"""
    try:
        token = google.authorize_access_token()
        user_info = token.get('userinfo')
        
        if not user_info:
            return redirect(f"{os.getenv('FRONTEND_URL', 'http://localhost:8080')}/login?error=oauth_failed")
        
        oauth_data = {
            'id': user_info['sub'],
            'email': user_info['email'],
            'access_token': token['access_token'],
            'refresh_token': token.get('refresh_token')
        }
        
        admin = get_or_create_admin_from_oauth('google', oauth_data)
        
        if not admin:
            return redirect(f"{os.getenv('FRONTEND_URL', 'http://localhost:8080')}/login?error=no_area_available")
        
        # Create JWT token
        access_token = create_access_token(
            identity=admin.id,
            additional_claims={
                'email': admin.email,
                'is_admin': admin.is_admin,
                'area_id': admin.area_id
            }
        )
        
        # Redirect to frontend OAuth callback route
        return redirect(f"{os.getenv('FRONTEND_URL', 'http://localhost:8080')}/oauth/callback?token={access_token}")
        
    except Exception as e:
        print(f"Google OAuth error: {e}")
        return redirect(f"{os.getenv('FRONTEND_URL', 'http://localhost:8080')}/login?error=oauth_failed")

@auth_bp.route('/github')
def github_login():
    """Initiate GitHub OAuth login"""
    redirect_uri = url_for('auth.github_callback', _external=True)
    return github.authorize_redirect(redirect_uri)

@auth_bp.route('/github/callback')
def github_callback():
    """Handle GitHub OAuth callback"""
    try:
        token = github.authorize_access_token()
        resp = github.get('user', token=token)
        user_info = resp.json()
        
        # Get user email (might need separate API call)
        email_resp = github.get('user/emails', token=token)
        emails = email_resp.json()
        primary_email = next((email['email'] for email in emails if email['primary']), None)
        
        if not primary_email:
            return redirect(f"{os.getenv('FRONTEND_URL', 'http://localhost:5173')}/login?error=oauth_failed")
        
        oauth_data = {
            'id': user_info['id'],
            'email': primary_email,
            'access_token': token['access_token'],
            'refresh_token': token.get('refresh_token')
        }
        
        admin = get_or_create_admin_from_oauth('github', oauth_data)
        
        if not admin:
            return redirect(f"{os.getenv('FRONTEND_URL', 'http://localhost:8080')}/login?error=no_area_available")
        
        # Create JWT token
        access_token = create_access_token(
            identity=admin.id,
            additional_claims={
                'email': admin.email,
                'is_admin': admin.is_admin,
                'area_id': admin.area_id
            }
        )
        
        # Redirect to frontend OAuth callback route
        return redirect(f"{os.getenv('FRONTEND_URL', 'http://localhost:8080')}/oauth/callback?token={access_token}")
        
    except Exception as e:
        print(f"GitHub OAuth error: {e}")
        return redirect(f"{os.getenv('FRONTEND_URL', 'http://localhost:5173')}/login?error=oauth_failed")

@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """Logout user"""
    try:
        # In a more sophisticated setup, you might want to blacklist the token
        return jsonify({'success': True, 'message': 'Logged out successfully'})
    except Exception as e:
        return jsonify({'error': 'Logout failed'}), 500

@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """Get current user info"""
    try:
        user_id = get_jwt_identity()
        admin = Admin.query.filter_by(id=user_id).first()
        
        if not admin:
            return jsonify({'error': 'User not found'}), 404
        
        return jsonify({
            'user': {
                'id': admin.id,
                'email': admin.email,
                'area_id': admin.area_id,
                'is_admin': admin.is_admin
            }
        })
        
    except Exception as e:
        return jsonify({'error': 'Server error'}), 500

@auth_bp.route('/verify-token', methods=['POST'])
def verify_token():
    """Verify JWT token"""
    try:
        data = request.get_json()
        token = data.get('token')
        
        if not token:
            return jsonify({'error': 'Token required'}), 400
        
        # Verify token (this will raise an exception if invalid)
        from flask_jwt_extended import decode_token
        decoded = decode_token(token)
        
        user_id = decoded['sub']
        
        # Verify user still exists and is admin
        admin = Admin.query.filter_by(id=user_id, is_admin=True).first()
        
        if not admin:
            return jsonify({'error': 'Invalid token'}), 401
        
        return jsonify({
            'valid': True,
            'user': {
                'id': admin.id,
                'email': admin.email,
                'area_id': admin.area_id,
                'is_admin': admin.is_admin
            }
        })
        
    except Exception as e:
        return jsonify({'error': 'Invalid token'}), 401

@auth_bp.route('/create-admin', methods=['POST'])
def create_admin():
    """Create admin account (development only)"""
    if os.getenv('FLASK_ENV') == 'production':
        return jsonify({'error': 'Not allowed in production'}), 403
    
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        area_id = data.get('area_id')
        
        if not all([email, password, area_id]):
            return jsonify({'error': 'Email, password, and area_id required'}), 400
        
        # Check if admin already exists
        existing_admin = Admin.query.filter_by(email=email).first()
        if existing_admin:
            return jsonify({'error': 'Admin with this email already exists'}), 400
        
        # Verify area exists
        area = Area.query.filter_by(id=area_id).first()
        if not area:
            return jsonify({'error': 'Area not found'}), 400
        
        # Create admin
        admin = Admin(
            email=email,
            area_id=area_id,
            is_admin=True
        )
        admin.set_password(password)
        
        db.session.add(admin)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'admin': admin.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Server error'}), 500
