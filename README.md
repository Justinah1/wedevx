# Lead Management System

A Flask-based lead management system with a public submission form, resume upload, email notifications, and an authenticated lead management interface.

## Features

- Public lead submission form with file upload
- Resume/CV file upload and storage
- Email notifications for both the prospect and attorney
- Authenticated interface for retrieving and managing leads
- Lead state management (PENDING → REACHED_OUT)
- Data persistence with PostgreSQL

## Technical Stack

- Python 3.9+
- Flask framework
- Flask-SQLAlchemy ORM with PostgreSQL
- Flask-Login for authentication
- Werkzeug for secure password hashing
- SendGrid for email notifications
- Bootstrap for responsive UI design

## Setup Instructions

### Prerequisites

- Python 3.9 or higher
- PostgreSQL database
- SendGrid API key (for email notifications)

### Environment Variables

Create a `.env` file in the root directory with the following variables:

```
# Database configuration
DATABASE_URL=postgresql://username:password@localhost:5432/lead_management

# Email configuration
SENDGRID_API_KEY=your_sendgrid_api_key
ATTORNEY_EMAIL=attorney@example.com
DEFAULT_FROM_EMAIL=no-reply@example.com
COMPANY_NAME="Your Company Name"

# Security
SESSION_SECRET=your_secret_key
```

### Installation

1. Clone the repository:
   ```
   git clone https://github.com/your-username/lead-management-system.git
   cd lead-management-system
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Initialize the database:
   ```
   python -c "from app import app, db; app.app_context().push(); db.create_all()"
   ```

4. Run the application:
   ```
   python main.py
   ```
   
   Or with Gunicorn for production:
   ```
   gunicorn --bind 0.0.0.0:5000 main:app
   ```

5. Access the application:
   - Public lead submission form: http://localhost:5000/
   - Attorney login: http://localhost:5000/login
   - Default credentials: admin@example.com / password

## Usage Guide

### For Prospects:
1. Navigate to the home page
2. Fill out the lead submission form with your details:
   - First Name
   - Last Name 
   - Email Address
   - Resume/CV (PDF, DOC, DOCX)
3. Submit the form
4. Receive a confirmation email

### For Attorneys:
1. Log in using your credentials
2. View the dashboard with all leads
3. Click on individual leads to view details
4. Update lead states from PENDING to REACHED_OUT
5. Add notes about the lead