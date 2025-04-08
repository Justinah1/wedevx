import os
import uuid
import shutil
from typing import List
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from database import get_db
import models
import schemas
from auth import get_current_active_user
from email_service import send_prospect_confirmation_email, send_attorney_notification_email

router = APIRouter(
    prefix="/leads",
    tags=["leads"],
)

# Ensure uploads directory exists
os.makedirs("uploads", exist_ok=True)

@router.post("/", response_model=schemas.Lead)
async def create_lead(
    first_name: str = Form(...),
    last_name: str = Form(...),
    email: str = Form(...),
    resume: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Public endpoint to submit a new lead with resume upload.
    """
    # Validate file type
    allowed_extensions = [".pdf", ".doc", ".docx", ".txt"]
    file_ext = os.path.splitext(resume.filename)[1].lower()
    
    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type not allowed. Allowed types: {', '.join(allowed_extensions)}"
        )
    
    # Create a unique filename to avoid collisions
    unique_filename = f"{uuid.uuid4()}{file_ext}"
    file_path = os.path.join("uploads", unique_filename)
    
    # Save the uploaded file
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(resume.file, buffer)
    
    # Create the lead in the database
    db_lead = models.Lead(
        first_name=first_name,
        last_name=last_name,
        email=email,
        resume_path=file_path,
        state=models.LeadState.PENDING
    )
    
    db.add(db_lead)
    db.commit()
    db.refresh(db_lead)
    
    # Send emails
    send_prospect_confirmation_email(email, first_name, last_name)
    send_attorney_notification_email(first_name, last_name, email, file_path)
    
    return db_lead

@router.get("/", response_model=List[schemas.Lead])
async def get_leads(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_active_user)
):
    """
    Get a list of all leads. Requires authentication.
    """
    leads = db.query(models.Lead).offset(skip).limit(limit).all()
    return leads

@router.get("/{lead_id}", response_model=schemas.Lead)
async def get_lead(
    lead_id: int,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_active_user)
):
    """
    Get a specific lead by ID. Requires authentication.
    """
    lead = db.query(models.Lead).filter(models.Lead.id == lead_id).first()
    if lead is None:
        raise HTTPException(status_code=404, detail="Lead not found")
    return lead

@router.patch("/{lead_id}", response_model=schemas.Lead)
async def update_lead(
    lead_id: int,
    lead_update: schemas.LeadUpdate,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_active_user)
):
    """
    Update a lead's state or notes. Requires authentication.
    """
    lead = db.query(models.Lead).filter(models.Lead.id == lead_id).first()
    if lead is None:
        raise HTTPException(status_code=404, detail="Lead not found")
    
    # Update the lead with the provided values
    if lead_update.state is not None:
        lead.state = lead_update.state
    
    if lead_update.notes is not None:
        lead.notes = lead_update.notes
    
    # Set the user who updated the lead
    lead.updated_by = current_user.id
    
    db.commit()
    db.refresh(lead)
    return lead
