# Lead Management System: Design Document

## Project Overview

The Lead Management System is a web application designed to streamline the process of collecting and managing leads (prospective clients) for a legal firm. The system allows prospects to submit their information and resume, while providing attorneys with tools to manage, track, and follow up with these leads.

## Architecture

The application follows a traditional Model-View-Controller (MVC) architecture using Flask as the framework:

- **Model**: SQLAlchemy ORM with PostgreSQL database
- **View**: Jinja2 templates with Bootstrap CSS framework
- **Controller**: Flask routes and business logic

## Key Components

### 1. User Management

- Authentication using Flask-Login
- Password hashing with Werkzeug security
- Role-based access (public vs. attorney-only areas)
- Session management for secure login/logout

### 2. Lead Submission & Storage

- Public form for lead submission
- File upload handling for resumes/CVs
- Database storage of lead information
- Enum-based state tracking (PENDING → REACHED_OUT)
- Input validation and sanitization

### 3. Email Notifications

- SendGrid integration for email delivery
- HTML email templates for professional appearance
- Confirmation emails to prospects
- Notification emails to attorneys (with resume attachments)
- Error handling for email delivery failures

### 4. Dashboard & Lead Management

- Secure, attorney-only dashboard
- Sortable/filterable lead list
- Detailed lead view with all information
- State transition controls
- Note-taking functionality
- Resume file download

## Design Decisions

### 1. Framework Selection: Flask

Flask was chosen over FastAPI for this application because:

- This application is primarily a traditional web application rather than an API
- Flask has more mature ecosystem for server-side rendering of HTML templates
- Integration with SQLAlchemy is more straightforward
- Flask-Login provides a complete authentication solution
- Less complexity for basic form handling and file uploads

### 2. Database Architecture

The database schema consists of two main models:

**User Model**:
- Represents attorneys who can access the system
- Contains authentication and user information

**Lead Model**:
- Represents submitted leads/prospects
- Contains all lead information and status
- Tracks state changes and notes
- Links to the physical resume file

### 3. Security Considerations

- Password hashing using Werkzeug's secure methods
- Authentication required for sensitive routes
- CSRF protection on all forms
- Input validation to prevent injection attacks
- Secure storage of uploaded files with sanitized filenames
- Environment variables for sensitive credentials

### 4. Email System Design

SendGrid was chosen for email delivery because:
- It provides reliable email delivery at scale
- Has comprehensive APIs for programmatic sending
- Supports HTML email templates
- Provides delivery tracking and analytics
- Handles attachment sending efficiently

### 5. UI/UX Design Patterns

- Clean, minimal interface for lead submission to maximize conversions
- Comprehensive dashboard for attorneys with all necessary data
- Responsive design using Bootstrap for mobile access
- Intuitive state management controls
- Clear feedback messages for all actions

## Future Enhancements

1. **Advanced Analytics**: Add reporting dashboard for lead conversion rates
2. **Email Campaigns**: Integrate with marketing email capabilities
3. **Calendar Integration**: Allow scheduling of follow-up calls directly in the app
4. **Document Generation**: Create custom documents based on lead information
5. **Multiple Attorney Assignment**: Assign leads to specific attorneys
6. **Task Management**: Create and track follow-up tasks for each lead
