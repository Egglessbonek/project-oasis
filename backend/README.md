# HydroFlow Tracker Backend

A Flask-based REST API backend for the HydroFlow Tracker application with PostgreSQL database integration.

## Features

- **User Authentication**: JWT-based authentication with user registration and login
- **Report Management**: Create, read, update, and delete issue reports
- **Comment System**: Add comments to reports for discussion
- **Admin Dashboard**: Admin-only endpoints for user and statistics management
- **PostgreSQL Integration**: Robust database with proper relationships and migrations

## API Endpoints

### Authentication (`/auth`)
- `POST /auth/register` - Register a new user
- `POST /auth/login` - Login user
- `GET /auth/profile` - Get current user profile
- `PUT /auth/profile` - Update current user profile

### Reports (`/api`)
- `GET /api/reports` - Get all reports (with filtering and pagination)
- `POST /api/reports` - Create a new report
- `GET /api/reports/<id>` - Get specific report with comments
- `PUT /api/reports/<id>` - Update a report
- `DELETE /api/reports/<id>` - Delete a report

### Comments (`/api`)
- `POST /api/reports/<id>/comments` - Add comment to report
- `PUT /api/comments/<id>` - Update a comment
- `DELETE /api/comments/<id>` - Delete a comment

### Admin (`/api`)
- `GET /api/admin/users` - Get all users (admin only)
- `GET /api/admin/stats` - Get dashboard statistics (admin only)

## Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Database Setup

1. Install PostgreSQL on your system
2. Create a database named `hydroflow_db`
3. Update the database connection string in your `.env` file

### 3. Environment Configuration

1. Copy `env.example` to `.env`
2. Update the following variables:
   - `DATABASE_URL`: Your PostgreSQL connection string
   - `SECRET_KEY`: A secure secret key for Flask
   - `JWT_SECRET_KEY`: A secure secret key for JWT tokens

### 4. Database Migration

```bash
# Initialize migration repository
flask db init

# Create initial migration
flask db migrate -m "Initial migration"

# Apply migration
flask db upgrade
```

### 5. Run the Application

```bash
python app.py
```

The API will be available at `http://localhost:5000`

## Database Schema

### Users Table
- `id` (Primary Key)
- `username` (Unique)
- `email` (Unique)
- `password_hash`
- `is_admin` (Boolean)
- `created_at`, `updated_at`

### Reports Table
- `id` (Primary Key)
- `title`, `description`
- `status` (open, in_progress, resolved, closed)
- `priority` (low, medium, high, critical)
- `category`, `location`
- `user_id` (Foreign Key)
- `created_at`, `updated_at`

### Comments Table
- `id` (Primary Key)
- `content`
- `report_id` (Foreign Key)
- `user_id` (Foreign Key)
- `created_at`, `updated_at`

## Development

### Adding New Features

1. Create new models in `app/models.py`
2. Add routes in `app/routes/` directory
3. Update database migrations as needed
4. Test endpoints thoroughly

### Database Migrations

When you modify models:

```bash
# Create new migration
flask db migrate -m "Description of changes"

# Apply migration
flask db upgrade
```

## Production Deployment

1. Set `FLASK_ENV=production` in your environment
2. Use a production WSGI server like Gunicorn
3. Configure proper database credentials
4. Set up SSL/HTTPS
5. Use environment variables for all sensitive configuration

## Security Notes

- Change default secret keys in production
- Use strong passwords for database
- Implement proper CORS policies
- Add rate limiting for API endpoints
- Validate all input data
- Use HTTPS in production
