# HydroFlow Tracker Backend

A Flask backend server for the HydroFlow Tracker application with OAuth authentication for admin users.

## Features

- **OAuth Authentication**: Support for Google, GitHub, and local email/password authentication
- **Admin Authorization**: Database-level admin verification using `is_admin` boolean field
- **JWT Token Management**: Secure token-based authentication with Flask-JWT-Extended
- **PostgreSQL Integration**: Full integration with PostGIS for geographic data using SQLAlchemy
- **RESTful API**: Clean API endpoints for admin dashboard functionality
- **Security**: CORS protection, secure session management, and admin-only access

## Prerequisites

- Python 3.8+
- PostgreSQL 16+ with PostGIS extension
- pip (Python package installer)

## Installation

1. **Install dependencies**:
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

2. **Set up the database**:
   - Create a PostgreSQL database named `hydroflow_tracker`
   - Enable PostGIS extension: `CREATE EXTENSION postgis;`
   - Run the schema: `psql -d hydroflow_tracker -f schema.sql`

3. **Configure environment variables**:
   ```bash
   cp env.example .env
   ```
   
   Edit `.env` with your configuration:
   ```env
   # Flask Configuration
   FLASK_ENV=development
   FLASK_APP=app.py
   PORT=3001
   SECRET_KEY=your-super-secret-key
   
   # Database
   DATABASE_URL=postgresql://postgres:password@localhost:5432/hydroflow_tracker
   DB_HOST=localhost
   DB_PORT=5432
   DB_NAME=hydroflow_tracker
   DB_USER=postgres
   DB_PASSWORD=your_password
   
   # Security
   JWT_SECRET_KEY=your-super-secret-jwt-key
   
   # Frontend
   FRONTEND_URL=http://localhost:5173
   
   # OAuth (Optional)
   GOOGLE_CLIENT_ID=your-google-client-id
   GOOGLE_CLIENT_SECRET=your-google-client-secret
   GITHUB_CLIENT_ID=your-github-client-id
   GITHUB_CLIENT_SECRET=your-github-client-secret
   ```

4. **Create an admin user** (for development):
   ```bash
   # Start the server
   python run.py
   
   # Create admin user via API
   curl -X POST http://localhost:3001/api/auth/create-admin \
     -H "Content-Type: application/json" \
     -d '{
       "email": "admin@example.com",
       "password": "admin123",
       "area_id": "your-area-uuid"
     }'
   ```

## Running the Server

- **Development**: `python run.py` or `python app.py`
- **Production**: `gunicorn app:app` or `gunicorn -w 4 -b 0.0.0.0:3001 app:app`

The server will start on port 3001 by default.

## API Endpoints

### Authentication

- `POST /api/auth/login` - Email/password login
- `GET /api/auth/google` - Google OAuth login
- `GET /api/auth/github` - GitHub OAuth login
- `POST /api/auth/logout` - Logout
- `GET /api/auth/me` - Get current user info
- `POST /api/auth/verify-token` - Verify JWT token

### Admin Dashboard

- `GET /api/admin/dashboard` - Get dashboard data (wells, reports, stats)
- `GET /api/admin/wells` - Get wells list
- `GET /api/admin/reports` - Get breakage reports
- `PUT /api/admin/wells/:id/status` - Update well status
- `PUT /api/admin/reports/:id/status` - Update report status
- `GET /api/admin/profile` - Get admin profile

### Health Check

- `GET /api/health` - Server health status

## Authentication Flow

1. **Admin Login**: Users must authenticate via OAuth or email/password
2. **Database Verification**: System checks if user exists in `admins` table with `is_admin = TRUE`
3. **Token Generation**: JWT token issued upon successful authentication
4. **Protected Routes**: All admin endpoints require valid authentication
5. **Session Management**: Secure session handling with automatic token refresh

## Security Features

- **Rate Limiting**: 100 requests per 15 minutes per IP
- **CORS Protection**: Configured for frontend domain
- **Helmet Security**: Security headers and protection
- **Password Hashing**: bcrypt with salt rounds
- **JWT Tokens**: Secure token-based authentication
- **Session Security**: HttpOnly cookies with secure flags

## Database Schema

The backend uses the following key tables:

- `admins`: Admin users with OAuth integration
- `areas`: Geographic administrative regions
- `wells`: Water well locations and status
- `breakage_reports`: User-submitted issue reports
- `well_projects`: Well construction projects

## OAuth Setup

### Google OAuth
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing
3. Enable Google+ API
4. Create OAuth 2.0 credentials
5. Add authorized redirect URI: `http://localhost:3001/api/auth/google/callback`

### GitHub OAuth
1. Go to GitHub Settings > Developer settings > OAuth Apps
2. Create a new OAuth App
3. Set Authorization callback URL: `http://localhost:3001/api/auth/github/callback`

## Development

- Uses ES modules (type: "module" in package.json)
- Nodemon for development auto-reload
- Structured with separate route files
- Comprehensive error handling
- Database connection pooling

## Production Deployment

1. Set `NODE_ENV=production`
2. Use strong, unique secrets for JWT and sessions
3. Configure proper CORS origins
4. Set up SSL/TLS
5. Use environment-specific database credentials
6. Configure reverse proxy (nginx/Apache)
7. Set up monitoring and logging

## Troubleshooting

- **Database Connection Issues**: Verify PostgreSQL is running and credentials are correct
- **OAuth Errors**: Check OAuth app configuration and callback URLs
- **Token Issues**: Verify JWT secret and token expiration settings
- **CORS Issues**: Ensure frontend URL is correctly configured

## License

MIT License - see LICENSE file for details.