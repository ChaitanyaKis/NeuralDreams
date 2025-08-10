# Neural Dreams Inc. - Surreal Dream Marketplace

## Overview

Neural Dreams Inc. is a surreal dream marketplace web application where users can buy, sell, and explore imaginative dream visions. The platform operates on a points-based economy where users start with 1,000 points and can trade dreams across categories like surreal, funny, scary, romantic, and bizarre. The application features user authentication, dream posting with image uploads, ratings, purchases, and a leaderboard system.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Web Framework
- **Flask**: Chosen as the primary web framework for its simplicity and flexibility
- **Blueprint Architecture**: Routes are organized into logical modules (auth_routes, marketplace_routes, profile_routes) for better code organization and maintainability
- **Template Engine**: Uses Jinja2 templating with a base template system for consistent UI

### Database Layer
- **SQLAlchemy ORM**: Provides database abstraction and relationship management
- **Database Models**: Three core entities - User, Dream, and supporting models for ratings and purchases
- **Database URI**: Configurable through environment variables, defaults to SQLite for development
- **Connection Pooling**: Configured with pool recycling and pre-ping for reliability

### Authentication & Authorization
- **Flask-Login**: Manages user sessions and authentication state
- **Password Security**: Uses Werkzeug's password hashing for secure password storage
- **Session Management**: Configured with secret keys and remember-me functionality
- **Access Control**: Login-required decorators protect sensitive routes

### File Upload System
- **Image Processing**: PIL (Pillow) for image resizing and optimization
- **File Security**: Secure filename generation with UUID and extension validation
- **Storage**: Local file storage in static/uploads directory with 16MB size limit
- **Image Optimization**: Automatic thumbnail generation (800x600) with quality compression

### Frontend Architecture
- **Bootstrap 5**: Responsive CSS framework for consistent styling
- **Custom CSS**: Extensive custom styling with CSS variables and gradient themes
- **JavaScript Animations**: Custom animations for interactive elements and visual effects
- **Font Integration**: Google Fonts (Comfortaa, Fredoka) for typography
- **Icon System**: Font Awesome for consistent iconography

### Points Economy System
- **Starting Points**: New users receive 1,000 points upon registration
- **Transaction Logic**: Validates user balances before allowing purchases
- **Points Transfer**: Automatic point transfer between buyers and sellers
- **Weekly Bonuses**: 100-point weekly bonus system (configured but not fully implemented)

### Search & Discovery
- **Multi-criteria Search**: Title and description text search with category filtering
- **Price Range Filtering**: Min/max price filtering for targeted browsing
- **Sorting Options**: Multiple sort criteria (newest, oldest, price, rating)
- **Pagination**: Built-in pagination for large result sets

### Rating System
- **Star Ratings**: 5-star rating system for dream quality assessment
- **Average Calculation**: Automatic calculation and storage of average ratings
- **Rating Display**: Visual star representations throughout the interface

## External Dependencies

### Python Packages
- **Flask Ecosystem**: Flask, Flask-SQLAlchemy, Flask-Login, Flask-WTF for core functionality
- **Image Processing**: Pillow (PIL) for image manipulation and optimization
- **Forms**: WTForms for form validation and rendering
- **Security**: Werkzeug for password hashing and security utilities

### Frontend Libraries
- **Bootstrap 5**: CDN-hosted responsive CSS framework
- **Animate.css**: Animation library for visual effects
- **Font Awesome**: Icon library for UI elements
- **Google Fonts**: Typography enhancement

### Database
- **SQLite**: Default development database (configurable to PostgreSQL or other databases)
- **Environment Configuration**: DATABASE_URL environment variable for production database selection

### Static Assets
- **Local Storage**: Images stored locally in static/uploads directory
- **CDN Resources**: External libraries loaded via CDN for performance

### Configuration Management
- **Environment Variables**: SESSION_SECRET and DATABASE_URL for deployment flexibility
- **Config Class**: Centralized configuration with development defaults
- **Upload Configuration**: File size limits and allowed extensions