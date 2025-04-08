import os
import logging
import datetime
import time
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from models import db, User, Lead, LeadState
from email_service import send_prospect_confirmation_email, send_attorney_notification_email

# Configure logging
logging.basicConfig(level=logging.INFO)

# Create upload directory if it doesn't exist
upload_dir = os.path.join(os.getcwd(), "uploads")
if not os.path.exists(upload_dir):
    os.makedirs(upload_dir)

# Create app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev_secret_key")

# Configure database
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_pre_ping": True,  # Detect stale connections
    "pool_recycle": 300,    # Recycle connections every 5 minutes
    "connect_args": {
        "connect_timeout": 10,  # Connection timeout in seconds
        "keepalives": 1,        # Enable keepalives
        "keepalives_idle": 30   # Seconds between keepalives
    }
}

# Initialize extensions
db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Create database tables
with app.app_context():
    db.create_all()
    
    # Create a default admin user if none exists
    if not User.query.filter_by(email="admin@example.com").first():
        admin_user = User(
            email="admin@example.com",
            password=generate_password_hash("password"),
            full_name="Admin User",
            is_active=1
        )
        db.session.add(admin_user)
        db.session.commit()

# Routes
@app.route("/")
def index():
    """Render the lead submission form."""
    return render_template("lead_form.html")

@app.route("/submit_lead", methods=["POST"])
def submit_lead():
    """Process lead submission."""
    saved_file = None
    try:
        first_name = request.form.get("first_name")
        last_name = request.form.get("last_name")
        email = request.form.get("email")
        resume = request.files.get("resume")
        
        # Validate input
        if not (first_name and last_name and email and resume):
            flash("All fields are required", "danger")
            return redirect(url_for("index"))
        
        # Save the resume file
        filename = secure_filename(f"{first_name}_{last_name}_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}{os.path.splitext(resume.filename)[1]}")
        file_path = os.path.join(upload_dir, filename)
        resume.save(file_path)
        saved_file = file_path
        
        # Create a new lead
        new_lead = Lead(
            first_name=first_name,
            last_name=last_name,
            email=email,
            resume_path=filename,
            state=LeadState.PENDING
        )
        
        max_retries = 3
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                db.session.add(new_lead)
                db.session.commit()
                
                # Send email to prospect
                prospect_email_sent = send_prospect_confirmation_email(
                    email,
                    first_name,
                    last_name
                )
                
                if prospect_email_sent:
                    app.logger.info(f"Confirmation email sent to {email}")
                else:
                    app.logger.warning(f"Failed to send confirmation email to {email}")
                
                # Send notification email to attorney
                attorney_email_sent = send_attorney_notification_email(
                    first_name,
                    last_name,
                    email,
                    file_path
                )
                
                if attorney_email_sent:
                    app.logger.info("Notification email sent to attorney")
                else:
                    app.logger.warning("Failed to send notification email to attorney")
                
                app.logger.info(f"Lead created successfully for {email}")
                flash("Thank you! Your information has been submitted successfully. Check your email for confirmation.", "success")
                return redirect(url_for("index"))
            
            except Exception as db_error:
                retry_count += 1
                db.session.rollback()
                app.logger.error(f"Database error on attempt {retry_count}: {str(db_error)}")
                
                if retry_count >= max_retries:
                    raise db_error
                
                # Wait a moment before retrying
                time.sleep(1)
    
    except Exception as e:
        app.logger.error(f"Error in submit_lead: {str(e)}")
        # Clean up saved file if database operation failed
        if saved_file and os.path.exists(saved_file):
            try:
                os.remove(saved_file)
                app.logger.info(f"Removed uploaded file after error: {saved_file}")
            except Exception as file_error:
                app.logger.error(f"Failed to remove file: {str(file_error)}")
        
        flash(f"We're sorry, but your application couldn't be processed at this time. Please try again later.", "danger")
        return redirect(url_for("index"))

@app.route("/login", methods=["GET", "POST"])
def login():
    """Handle user login."""
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        
        user = User.query.filter_by(email=email).first()
        
        if user and check_password_hash(user.password, password):
            login_user(user)
            flash("Login successful!", "success")
            return redirect(url_for("dashboard"))
        else:
            flash("Invalid email or password", "danger")
    
    return render_template("login.html")

@app.route("/logout")
@login_required
def logout():
    """Handle user logout."""
    logout_user()
    flash("You have been logged out", "info")
    return redirect(url_for("login"))

@app.route("/dashboard")
@login_required
def dashboard():
    """Render the lead management dashboard."""
    leads = Lead.query.order_by(Lead.created_at.desc()).all()
    return render_template("dashboard.html", leads=leads, LeadState=LeadState)

@app.route("/lead/<int:lead_id>")
@login_required
def view_lead(lead_id):
    """View a specific lead."""
    lead = Lead.query.get_or_404(lead_id)
    return render_template("lead_details.html", lead=lead, LeadState=LeadState)

@app.route("/lead/<int:lead_id>/update", methods=["POST"])
@login_required
def update_lead(lead_id):
    """Update a lead's state and notes."""
    lead = Lead.query.get_or_404(lead_id)
    
    # Update lead state if provided
    state = request.form.get("state")
    if state and state in [e.name for e in LeadState]:
        lead.state = LeadState[state]
    
    # Update notes if provided
    notes = request.form.get("notes")
    if notes is not None:
        lead.notes = notes
    
    # Update the lead
    lead.updated_by = current_user.id
    lead.updated_at = datetime.datetime.utcnow()
    
    db.session.commit()
    flash("Lead updated successfully", "success")
    
    return redirect(url_for("view_lead", lead_id=lead_id))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)