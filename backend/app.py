from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_session import Session
from dotenv import load_dotenv
import os
from datetime import timedelta, datetime  # moved datetime import here

# Load environment variables
load_dotenv()

# Import blueprints
from routes.auth import auth_bp
from routes.admin import admin_bp
from models import db

def create_app():
    app = Flask(__name__)
    
    # Configuration
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key-change-in-production')
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'your-jwt-secret-change-in-production')
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24)
    
    # Database configuration
    db_user = os.getenv('PG_USER', 'suis')
    db_password = os.getenv('PG_PASSWORD', os.getenv('PG_PASSWORD'))
    db_host = os.getenv('PG_HOST', os.getenv('PG_HOST'))
    db_port = os.getenv('PG_PORT', os.getenv('PG_PORT'))
    db_name = os.getenv('PG_DB', os.getenv('PG_DATABASE'))
    
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv(
        'DATABASE_URL',
        f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
    )
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Session configuration
    app.config['SESSION_TYPE'] = 'filesystem'
    app.config['SESSION_PERMANENT'] = False
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=24)
    
    # CORS configuration
    CORS(app, 
         origins=[os.getenv('FRONTEND_URL', 'http://localhost:8080')],
         supports_credentials=True,
         methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
         allow_headers=['Content-Type', 'Authorization'])
    
    # Initialize extensions
    db.init_app(app)
    jwt = JWTManager(app)
    Session(app)
    
    # Initialize OAuth
    from routes.auth import init_oauth
    init_oauth(app)
    
    # Register blueprints
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(admin_bp, url_prefix='/api/admin')
    
    # Health check endpoint
    @app.route('/api/health')
    def health_check():
        return jsonify({
            'status': 'OK',
            'timestamp': str(datetime.utcnow()),
            'environment': os.getenv('FLASK_ENV', 'development')
        })
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Route not found'}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({'error': 'Internal server error'}), 500
    
    # JWT error handlers
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

if __name__ == '__main__':
    app = create_app()
    
    # Create tables if they don't exist
    with app.app_context():
        db.create_all()
    
    port = int(os.getenv('PORT', 3001))
    debug = os.getenv('FLASK_ENV', 'development') != 'production'
    
    print(f"🚀 Server starting on port {port}")
    print(f"📊 Environment: {os.getenv('FLASK_ENV', 'development')}")
    print(f"🔗 Health check: http://localhost:{port}/api/health")
    
    app.run(host='0.0.0.0', port=port, debug=debug)
