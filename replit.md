# Korean Job Community Platform (무빙브릿지)

## Overview

This is a Flask-based web application designed to connect foreign workers with moving companies in Korea. The platform serves as a community board where foreign workers can post self-introductions and moving companies can post job opportunities. The application is built with Flask and supports both SQLite (for development) and PostgreSQL (for production) databases.

## System Architecture

The application follows a traditional MVC architecture with Flask serving as the web framework:

- **Frontend**: Server-side rendered HTML templates using Jinja2
- **Backend**: Flask web application with Python
- **Database**: Dual database support - SQLite for development/local testing, PostgreSQL for production
- **Deployment**: Configured for Replit deployment with Gunicorn as the WSGI server

## Key Components

### Database Layer
- **Development Database**: SQLite with file-based storage (`movingbridge.db`)
- **Production Database**: PostgreSQL (configured via `DATABASE_URL` environment variable)
- **Database Setup Scripts**: 
  - `init_db.py` for SQLite initialization
  - `database_setup.py` for PostgreSQL initialization
- **Core Tables**:
  - `users` - User authentication and management
  - `jobs` - Job postings from moving companies
  - `introductions` - Self-introductions from foreign workers
  - `notices` - Administrative announcements
  - `forum` - Community discussion posts

### Authentication & Security
- **Session Management**: Flask sessions with secure cookie configuration
- **CSRF Protection**: Flask-WTF CSRF tokens for form security
- **Input Sanitization**: Custom sanitization functions to prevent XSS
- **Admin Authentication**: Simple username/password admin system
- **Password Hashing**: Werkzeug password hashing for secure storage

### Application Structure
- **Main Application**: `app.py` contains all routes and business logic
- **Entry Point**: `main.py` serves as the application entry point
- **Templates**: Jinja2 templates in `templates/` directory with responsive Bootstrap design
- **Forms**: WTForms integration for form handling and validation

### Core Features
1. **Job Board**: Companies can post job opportunities
2. **Self-Introduction Board**: Workers can post their profiles
3. **Community Forum**: General discussion and information sharing
4. **Notice Board**: Administrative announcements
5. **Admin Dashboard**: Administrative interface for content management

## Data Flow

1. **User Registration/Login**: Users register through forms, passwords are hashed and stored
2. **Content Creation**: Authenticated users can create posts through web forms
3. **Content Display**: Posts are retrieved from database and displayed via templates
4. **Admin Management**: Admins can manage all content through dedicated admin interface
5. **Database Operations**: Raw SQL queries using psycopg2 for PostgreSQL or sqlite3 for SQLite

## External Dependencies

### Python Packages
- **Flask**: Web framework
- **psycopg2-binary**: PostgreSQL database adapter
- **Flask-WTF**: Form handling and CSRF protection
- **Flask-Talisman**: Security headers (configured but not fully implemented)
- **Werkzeug**: Password hashing utilities
- **python-dotenv**: Environment variable management
- **Gunicorn**: WSGI server for production

### Frontend Dependencies
- **Bootstrap 5.3.0**: CSS framework for responsive design
- **Font Awesome 6.0.0**: Icon library
- **Google Fonts**: Noto Sans KR for Korean typography

## Deployment Strategy

### Replit Configuration
- **Environment**: Python 3.11 with PostgreSQL 16
- **Deployment Target**: Autoscale deployment
- **Port Configuration**: Application runs on port 5000, exposed on port 80
- **Process Management**: Gunicorn with auto-reload enabled for development

### Environment Variables
- `SESSION_SECRET`: Flask session encryption key
- `ADMIN_USERNAME`/`ADMIN_PASSWORD`: Admin credentials
- `DATABASE_URL`: PostgreSQL connection string (auto-provided by Replit)
- `FLASK_ENV`: Environment setting (production/development)

### Startup Process
1. Pre-deployment checks verify environment variables and database connectivity
2. Database tables are created if they don't exist
3. Gunicorn starts the Flask application with appropriate configuration

## Changelog

Recent Changes:
- June 24, 2025: Initial setup with PostgreSQL database
- June 24, 2025: Converted all boards from card format to table format
- June 24, 2025: Implemented 2-step registration system for foreign workers
- June 24, 2025: Added separate registration flows for companies and workers
- June 24, 2025: Created company registration with business verification fields
- June 24, 2025: Enhanced nationality dropdown with 41 countries (Asia, North America, Europe, South America)
- June 24, 2025: Improved language selection with English labels and 36 language options
- June 24, 2025: Implemented environment separation (development/production) with different database and security settings

## User Preferences

Preferred communication style: Simple, everyday language.
User satisfaction confirmed: Dual registration system (company/worker) implementation successful.