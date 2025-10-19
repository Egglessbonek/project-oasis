# =============================================================================
#                  Project Oasis - Flask Backend (app.py)
#
# This is the main entry point for our Flask application. It uses the
# 'create_app' factory pattern to initialize the app, extensions, and routes.
#
# =============================================================================

import os
from flask import Flask, jsonify, request, Response
from flask_cors import CORS
from datetime import timedelta, datetime
from flask_jwt_extended import JWTManager
from flask_session import Session
from dotenv import load_dotenv
from sqlalchemy import text

# Load environment variables from .env file
load_dotenv()

# Import the db object from our models file
from models import db

# Import all our route blueprints
from routes.auth import auth_bp
from routes.admin import admin_bp
from routes.reports import reports_bp
from routes.wells import wells_bp
from routes.areas import areas_bp # <-- This was the missing import

def create_app():
    app = Flask(__name__)
    
    # --- Core Configuration ---
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key-change-in-production')
    
    # --- Database Configuration (Simplified) ---
    # We will use the single DATABASE_URL from the .env file, which is cleaner.
    DATABASE_URL = os.getenv("DATABASE_URL")
    if not DATABASE_URL:
        raise RuntimeError("DATABASE_URL is not set in the .env file")
    app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # --- JWT Configuration ---
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'your-jwt-secret-change-in-production')
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24)
    
    # --- Session Configuration ---
    app.config['SESSION_TYPE'] = 'filesystem'
    app.config['SESSION_PERMANENT'] = False
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=24)
    
    # --- CORS Configuration ---
    CORS(app, 
         origins=[os.getenv('FRONTEND_URL', 'http://localhost:8080')],
         supports_credentials=True,
         methods=['GET', 'POST', 'PUT', 'PATCH', 'DELETE', 'OPTIONS'],
         allow_headers=['Content-Type', 'Authorization'])
    
    # --- Initialize Extensions ---
    db.init_app(app)
    jwt = JWTManager(app)
    Session(app)
    
    # --- Initialize OAuth (if it exists in your auth routes) ---
    from routes.auth import init_oauth
    init_oauth(app)
    
    # --- Register Blueprints ---
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(admin_bp, url_prefix='/api/admin')
    app.register_blueprint(reports_bp, url_prefix='/api/reports')
    app.register_blueprint(wells_bp) # url_prefix is already in the blueprint file
    app.register_blueprint(areas_bp) # <-- This was the missing registration
    

    # --- App-level Routes ---
    @app.route('/sms', methods=['POST'])
    def sms_reply():
        sender_number = request.form.get('From')
        message_body = request.form.get('Body')
        image_url = request.form.get('MediaUrl0')

        app.logger.info("---- NEW REPORT from %s ----", sender_number)
        app.logger.info("Message: %s", message_body)
        if image_url:
            app.logger.info("Image URL: %s", image_url)
        
        return Response(status=200)
    
    @app.route('/api/health')
    def health_check():
        """A robust health check that also verifies database connectivity."""
        try:
            # A simple query to confirm the database connection is live.
            db.session.execute(text('SELECT 1'))
            return jsonify({
                'status': 'OK',
                'database_status': 'connected',
                'timestamp': str(datetime.utcnow())
            })
        except Exception as e:
            app.logger.error(f"Health check failed: {e}")
            return jsonify({
                'status': 'ERROR',
                'database_status': 'disconnected',
                'timestamp': str(datetime.utcnow()),
                'error': str(e)
            }), 503
    
    # --- Error Handlers ---
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Route not found'}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({'error': 'Internal server error'}), 500
    
    # --- JWT Error Handlers ---
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return jsonify({'error': 'Token has expired'}), 401
    
    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return jsonify({'error': 'Invalid token'}), 401
    
    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return jsonify({'error': 'Authorization token required'}), 401
    
    return app

# --- Main Execution Block ---
if __name__ == '__main__':
    app = create_app()
    
    # NOTE: It's better to manage your database schema with your schema.sql script
    # (and eventually a migration tool like Alembic) rather than db.create_all().
    # This line can be useful for quick tests but is removed for best practice.
    # with app.app_context():
    #     db.create_all()
    
    port = int(os.getenv('PORT', 3001))
    debug = os.getenv('FLASK_ENV', 'development') != 'production'
    
    print(f"🚀 Server starting on port {port}")
    print(f"📊 Environment: {os.getenv('FLASK_ENV', 'development')}")
    print(f"🔗 Health check: http://localhost:{port}/api/health")
    
    app.run(host='0.0.0.0', port=port, debug=debug)

