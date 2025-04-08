import os
import logging
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email, To, Content, Attachment, FileContent, FileName, FileType, Disposition

# Configure logging
logger = logging.getLogger(__name__)

# Get API key from environment
SENDGRID_API_KEY = os.environ.get('SENDGRID_API_KEY')
ATTORNEY_EMAIL = os.environ.get('ATTORNEY_EMAIL', 'attorney@example.com')
COMPANY_NAME = os.environ.get('COMPANY_NAME', 'Lead Management System')
DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', 'no-reply@leadmanagementsystem.com')

def send_prospect_confirmation_email(prospect_email, first_name, last_name):
    """
    Send a confirmation email to the prospect after they submit a lead.
    
    Args:
        prospect_email: The prospect's email address
        first_name: The prospect's first name
        last_name: The prospect's last name
    """
    subject = f"Thank you for your application, {first_name}!"
    
    content = f"""
    <html>
    <body>
        <h2>Thank you for your application!</h2>
        
        <p>Dear {first_name} {last_name},</p>
        
        <p>We have received your application and resume. Our team will review your information 
        and get back to you as soon as possible.</p>
        
        <p>If you have any questions in the meantime, please feel free to contact us.</p>
        
        <p>Best regards,<br>
        The {COMPANY_NAME} Team</p>
    </body>
    </html>
    """
    
    return _send_email(prospect_email, subject, content)

def send_attorney_notification_email(first_name, last_name, prospect_email, resume_path):
    """
    Send a notification email to the attorney when a new lead is submitted.
    
    Args:
        first_name: The prospect's first name
        last_name: The prospect's last name
        prospect_email: The prospect's email address
        resume_path: Path to the uploaded resume file
    """
    subject = f"New Application: {first_name} {last_name}"
    
    content = f"""
    <html>
    <body>
        <h2>New Application Submitted</h2>
        
        <p>A new application has been submitted with the following details:</p>
        
        <ul>
            <li><strong>Name:</strong> {first_name} {last_name}</li>
            <li><strong>Email:</strong> {prospect_email}</li>
        </ul>
        
        <p>The applicant's resume is attached to this email. You can also view and manage 
        this application in the <a href="http://localhost:5000/dashboard">Lead Management Dashboard</a>.</p>
    </body>
    </html>
    """
    
    return _send_email(ATTORNEY_EMAIL, subject, content, attachment_path=resume_path)

def _send_email(recipient, subject, html_content, attachment_path=None):
    """
    Helper function to send an email.
    
    Args:
        recipient: The recipient's email address
        subject: The email subject
        html_content: The email body (HTML)
        attachment_path: Optional path to an attachment file
    """
    if not SENDGRID_API_KEY:
        logger.error("SendGrid API key is not set. Email will not be sent.")
        return False
    
    message = Mail(
        from_email=Email(DEFAULT_FROM_EMAIL),
        to_emails=To(recipient),
        subject=subject,
        html_content=Content("text/html", html_content)
    )
    
    # Add attachment if provided
    if attachment_path and os.path.exists(attachment_path):
        try:
            with open(attachment_path, 'rb') as f:
                file_content = f.read()
                
            file_name = os.path.basename(attachment_path)
            file_type = "application/pdf"  # Default to PDF
            
            # Try to determine file type based on extension
            if file_name.lower().endswith('.docx'):
                file_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            elif file_name.lower().endswith('.doc'):
                file_type = "application/msword"
            elif file_name.lower().endswith('.txt'):
                file_type = "text/plain"
                
            attachment = Attachment()
            attachment.file_content = FileContent(file_content)
            attachment.file_name = FileName(file_name)
            attachment.file_type = FileType(file_type)
            attachment.disposition = Disposition("attachment")
            
            message.attachment = attachment
        except Exception as e:
            logger.error(f"Failed to attach file to email: {str(e)}")
    
    try:
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        response = sg.send(message)
        
        if response.status_code >= 200 and response.status_code < 300:
            logger.info(f"Email sent successfully to {recipient}")
            return True
        else:
            logger.error(f"Failed to send email: {response.status_code} - {response.body}")
            return False
            
    except Exception as e:
        logger.error(f"Error sending email: {str(e)}")
        return False