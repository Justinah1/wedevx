import os
import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import importlib.util

# Create upload directory if it doesn't exist
upload_dir = "uploads"
if not os.path.exists(upload_dir):
    os.makedirs(upload_dir)

# Create templates directory if it doesn't exist
templates_dir = "templates"
if not os.path.exists(templates_dir):
    os.makedirs(templates_dir)
    
    # Create basic templates
    with open(os.path.join(templates_dir, "lead_form.html"), "w") as f:
        f.write("""
<!DOCTYPE html>
<html>
<head>
    <title>Lead Submission Form</title>
    <link href="https://cdn.replit.com/agent/bootstrap-agent-dark-theme.min.css" rel="stylesheet">
    <script src="/static/scripts.js" defer></script>
</head>
<body class="container mt-4">
    <h1>Lead Submission Form</h1>
    <form id="leadForm" enctype="multipart/form-data">
        <div class="mb-3">
            <label for="firstName" class="form-label">First Name</label>
            <input type="text" class="form-control" id="firstName" name="firstName" required>
        </div>
        <div class="mb-3">
            <label for="lastName" class="form-label">Last Name</label>
            <input type="text" class="form-control" id="lastName" name="lastName" required>
        </div>
        <div class="mb-3">
            <label for="email" class="form-label">Email</label>
            <input type="email" class="form-control" id="email" name="email" required>
        </div>
        <div class="mb-3">
            <label for="resume" class="form-label">Resume/CV</label>
            <input type="file" class="form-control" id="resume" name="resume" required>
        </div>
        <button type="submit" class="btn btn-primary">Submit</button>
    </form>
    <div id="submissionMessage" class="alert alert-success mt-3" style="display: none;"></div>
</body>
</html>
        """)
    
    with open(os.path.join(templates_dir, "lead_management.html"), "w") as f:
        f.write("""
<!DOCTYPE html>
<html>
<head>
    <title>Lead Management</title>
    <link href="https://cdn.replit.com/agent/bootstrap-agent-dark-theme.min.css" rel="stylesheet">
    <script src="/static/scripts.js" defer></script>
</head>
<body class="container mt-4">
    <h1>Lead Management Dashboard</h1>
    <div id="loginForm">
        <h2>Login</h2>
        <form id="authForm">
            <div class="mb-3">
                <label for="email" class="form-label">Email</label>
                <input type="email" class="form-control" id="email" name="email" required>
            </div>
            <div class="mb-3">
                <label for="password" class="form-label">Password</label>
                <input type="password" class="form-control" id="password" name="password" required>
            </div>
            <button type="submit" class="btn btn-primary">Login</button>
        </form>
    </div>
    <div id="dashboard" style="display: none;">
        <div class="d-flex justify-content-between align-items-center">
            <h2>Leads</h2>
            <div class="btn-group" role="group">
                <button class="btn btn-outline-secondary" onclick="filterLeads(null)">All</button>
                <button class="btn btn-outline-secondary" onclick="filterLeads('PENDING')">Pending</button>
                <button class="btn btn-outline-secondary" onclick="filterLeads('REACHED_OUT')">Reached Out</button>
            </div>
        </div>
        <div class="table-responsive mt-3">
            <table class="table table-striped">
                <thead>
                    <tr>
                        <th>Name</th>
                        <th>Email</th>
                        <th>State</th>
                        <th>Submitted</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody id="leadsTableBody"></tbody>
            </table>
        </div>
    </div>
    <div class="modal fade" id="leadDetailsModal" tabindex="-1" aria-hidden="true">
        <div class="modal-dialog">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title">Lead Details</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                </div>
                <div class="modal-body">
                    <div id="leadDetails"></div>
                    <form id="updateLeadForm" class="mt-3">
                        <input type="hidden" id="leadId">
                        <div class="mb-3">
                            <label for="leadState" class="form-label">State</label>
                            <select class="form-control" id="leadState" name="state">
                                <option value="PENDING">Pending</option>
                                <option value="REACHED_OUT">Reached Out</option>
                            </select>
                        </div>
                        <div class="mb-3">
                            <label for="leadNotes" class="form-label">Notes</label>
                            <textarea class="form-control" id="leadNotes" name="notes" rows="3"></textarea>
                        </div>
                    </form>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
                    <button type="button" class="btn btn-primary" onclick="updateLead()">Update</button>
                </div>
            </div>
        </div>
    </div>
</body>
</html>
        """)

# Create static directory if it doesn't exist
static_dir = "static"
if not os.path.exists(static_dir):
    os.makedirs(static_dir)
    
    # Create basic static files
    with open(os.path.join(static_dir, "scripts.js"), "w") as f:
        f.write("""
document.addEventListener('DOMContentLoaded', function() {
    if (document.getElementById('leadForm')) {
        initLeadForm();
    } else if (document.getElementById('authForm')) {
        initLeadManagement();
    }
});

/**
 * Initialize the lead submission form and its events
 */
function initLeadForm() {
    const form = document.getElementById('leadForm');
    form.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const formData = new FormData(form);
        try {
            const response = await fetch('/leads/', {
                method: 'POST',
                body: formData
            });
            
            if (response.ok) {
                const result = await response.json();
                form.reset();
                const message = document.getElementById('submissionMessage');
                message.textContent = 'Lead submitted successfully. Check your email for confirmation.';
                message.style.display = 'block';
                setTimeout(() => { message.style.display = 'none'; }, 5000);
            } else {
                const error = await response.json();
                alert(`Error: ${error.detail || 'Failed to submit lead'}`);
            }
        } catch (error) {
            alert('An error occurred. Please try again.');
            console.error(error);
        }
    });
}

/**
 * Initialize the lead management interface and its events
 */
function initLeadManagement() {
    const authForm = document.getElementById('authForm');
    authForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const formData = new FormData(authForm);
        try {
            const response = await fetch('/auth/token', {
                method: 'POST',
                body: new URLSearchParams({
                    'username': formData.get('email'),
                    'password': formData.get('password')
                }),
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded'
                }
            });
            
            if (response.ok) {
                const tokenData = await response.json();
                localStorage.setItem('access_token', tokenData.access_token);
                authenticateUI(tokenData.access_token);
            } else {
                alert('Invalid credentials');
            }
        } catch (error) {
            alert('An error occurred during login');
            console.error(error);
        }
    });
    
    // Check if already authenticated
    const token = localStorage.getItem('access_token');
    if (token) {
        authenticateUI(token);
    }
}

/**
 * Update the UI after successful authentication
 */
function authenticateUI(token) {
    document.getElementById('loginForm').style.display = 'none';
    document.getElementById('dashboard').style.display = 'block';
    fetchLeads(token);
}

/**
 * Fetch leads from the API
 */
async function fetchLeads(token, filterState = null) {
    try {
        let url = '/leads/';
        if (filterState) {
            url += `?state=${filterState}`;
        }
        
        const response = await fetch(url, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        if (response.ok) {
            const leads = await response.json();
            renderLeadsTable(leads);
        } else if (response.status === 401) {
            // Token expired or invalid
            localStorage.removeItem('access_token');
            document.getElementById('loginForm').style.display = 'block';
            document.getElementById('dashboard').style.display = 'none';
            alert('Your session has expired. Please login again.');
        } else {
            alert('Failed to load leads');
        }
    } catch (error) {
        console.error(error);
        alert('An error occurred while fetching leads');
    }
}

/**
 * Render the leads table with the provided data
 */
function renderLeadsTable(leads) {
    const tableBody = document.getElementById('leadsTableBody');
    tableBody.innerHTML = '';
    
    if (leads.length === 0) {
        const row = document.createElement('tr');
        row.innerHTML = '<td colspan="5" class="text-center">No leads found</td>';
        tableBody.appendChild(row);
        return;
    }
    
    leads.forEach(lead => {
        const row = document.createElement('tr');
        const createdAt = new Date(lead.created_at).toLocaleDateString();
        
        row.innerHTML = `
            <td>${lead.first_name} ${lead.last_name}</td>
            <td>${lead.email}</td>
            <td><span class="badge ${lead.state === 'PENDING' ? 'bg-warning' : 'bg-success'}">${lead.state}</span></td>
            <td>${createdAt}</td>
            <td>
                <button class="btn btn-sm btn-info" onclick="showLeadDetails(${lead.id})">View</button>
            </td>
        `;
        
        tableBody.appendChild(row);
    });
}

/**
 * Show lead details in a modal
 */
async function showLeadDetails(leadId) {
    const token = localStorage.getItem('access_token');
    if (!token) return;
    
    try {
        const response = await fetch(`/leads/${leadId}`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        if (response.ok) {
            const lead = await response.json();
            const detailsDiv = document.getElementById('leadDetails');
            const createdAt = new Date(lead.created_at).toLocaleString();
            const updatedAt = new Date(lead.updated_at).toLocaleString();
            
            detailsDiv.innerHTML = `
                <p><strong>Name:</strong> ${lead.first_name} ${lead.last_name}</p>
                <p><strong>Email:</strong> ${lead.email}</p>
                <p><strong>Resume:</strong> <a href="/uploads/${lead.resume_path}" target="_blank">View Resume</a></p>
                <p><strong>Status:</strong> ${lead.state}</p>
                <p><strong>Submitted:</strong> ${createdAt}</p>
                <p><strong>Last Updated:</strong> ${updatedAt}</p>
            `;
            
            document.getElementById('leadId').value = lead.id;
            document.getElementById('leadState').value = lead.state;
            document.getElementById('leadNotes').value = lead.notes || '';
            
            const modal = new bootstrap.Modal(document.getElementById('leadDetailsModal'));
            modal.show();
        } else {
            alert('Failed to load lead details');
        }
    } catch (error) {
        console.error(error);
        alert('An error occurred while loading lead details');
    }
}

/**
 * Update a lead's state and notes
 */
async function updateLead() {
    const token = localStorage.getItem('access_token');
    if (!token) return;
    
    const leadId = document.getElementById('leadId').value;
    const state = document.getElementById('leadState').value;
    const notes = document.getElementById('leadNotes').value;
    
    try {
        const response = await fetch(`/leads/${leadId}`, {
            method: 'PUT',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                state: state,
                notes: notes
            })
        });
        
        if (response.ok) {
            const modal = bootstrap.Modal.getInstance(document.getElementById('leadDetailsModal'));
            modal.hide();
            fetchLeads(token); // Refresh the leads list
            alert('Lead updated successfully');
        } else {
            alert('Failed to update lead');
        }
    } catch (error) {
        console.error(error);
        alert('An error occurred while updating the lead');
    }
}

/**
 * Filter leads by state
 */
function filterLeads(state) {
    const token = localStorage.getItem('access_token');
    if (token) {
        fetchLeads(token, state);
    }
}
        """)

# Initialize FastAPI app
app = FastAPI(title="Lead Management System")

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Templates
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    """Serve the public lead submission form."""
    return templates.TemplateResponse("lead_form.html", {"request": request})

@app.get("/admin", response_class=HTMLResponse)
async def admin_panel(request: Request):
    """Serve the admin lead management interface."""
    return templates.TemplateResponse("lead_management.html", {"request": request})

# Import routers if they exist
try:
    # Dynamically import routers
    from routers import auth, leads
    app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
    app.include_router(leads.router, prefix="/leads", tags=["Leads"])
except ImportError:
    # Create placeholder routes for demo
    @app.post("/auth/token")
    async def get_token():
        return {"access_token": "demo_token", "token_type": "bearer"}
    
    @app.get("/leads/")
    async def get_leads():
        return []

# For local development
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5000)