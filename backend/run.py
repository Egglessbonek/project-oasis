#!/usr/bin/env python3
"""
Development server runner for HydroFlow Tracker Flask backend
"""

import os
from app import create_app

if __name__ == '__main__':
    app = create_app()
    
    # Create tables if they don't exist
    with app.app_context():
        from models import db
        db.create_all()
    
    port = int(os.getenv('PORT', 3001))
    debug = os.getenv('FLASK_ENV') != 'production'
    
    print(f"🚀 Flask server starting on port {port}")
    print(f"📊 Environment: {os.getenv('FLASK_ENV', 'development')}")
    print(f"🔗 Health check: http://localhost:{port}/api/health")
    print(f"🔑 Admin login: http://localhost:{port}/api/auth/google")
    
    app.run(host='0.0.0.0', port=port, debug=debug)
