// Initialize Feather icons if available
document.addEventListener('DOMContentLoaded', function() {
    if (typeof feather !== 'undefined') {
        feather.replace();
    }
    
    // Determine which page we're on and initialize accordingly
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
    const successMessage = document.getElementById('successMessage');
    const errorMessage = document.getElementById('errorMessage');
    const errorText = document.getElementById('errorText');
    
    form.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        // Hide previous messages
        successMessage.style.display = 'none';
        errorMessage.style.display = 'none';
        
        // Create FormData from the form
        const formData = new FormData(form);
        
        try {
            const response = await fetch('/leads/', {
                method: 'POST',
                body: formData
            });
            
            if (response.ok) {
                // Show success message
                successMessage.style.display = 'block';
                // Reset form
                form.reset();
            } else {
                // Handle error based on response
                const errorData = await response.json();
                errorText.textContent = errorData.detail || 'There was a problem submitting your application. Please try again.';
                errorMessage.style.display = 'block';
            }
        } catch (error) {
            console.error('Error submitting form:', error);
            errorText.textContent = 'There was a problem connecting to the server. Please try again later.';
            errorMessage.style.display = 'block';
        }
    });
}

/**
 * Initialize the lead management interface and its events
 */
function initLeadManagement() {
    const authForm = document.getElementById('authForm');
    const loginForm = document.getElementById('loginForm');
    const leadsContainer = document.getElementById('leadsContainer');
    const loginError = document.getElementById('loginError');
    const authStatus = document.getElementById('authStatus');
    const logoutBtn = document.getElementById('logoutBtn');
    
    // Check if user is already authenticated
    const token = localStorage.getItem('token');
    if (token) {
        authenticateUI(token);
    }
    
    // Handle login form submission
    authForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const username = document.getElementById('username').value;
        const password = document.getElementById('password').value;
        
        // Hide previous errors
        loginError.style.display = 'none';
        
        try {
            const formData = new URLSearchParams();
            formData.append('username', username);
            formData.append('password', password);
            
            const response = await fetch('/auth/token', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
                body: formData
            });
            
            if (response.ok) {
                const data = await response.json();
                localStorage.setItem('token', data.access_token);
                authenticateUI(data.access_token);
            } else {
                const errorData = await response.json();
                loginError.textContent = errorData.detail || 'Invalid username or password';
                loginError.style.display = 'block';
            }
        } catch (error) {
            console.error('Login error:', error);
            loginError.textContent = 'There was a problem connecting to the server. Please try again.';
            loginError.style.display = 'block';
        }
    });
    
    // Handle logout
    logoutBtn.addEventListener('click', function() {
        localStorage.removeItem('token');
        loginForm.style.display = 'block';
        leadsContainer.style.display = 'none';
        authStatus.innerHTML = '<span class="badge bg-warning text-dark">Not Authenticated</span>';
    });
    
    // Handle lead filtering
    document.getElementById('pendingFilter').addEventListener('click', function(e) {
        e.preventDefault();
        filterLeads('PENDING');
    });
    
    document.getElementById('reachedOutFilter').addEventListener('click', function(e) {
        e.preventDefault();
        filterLeads('REACHED_OUT');
    });
    
    // Handle saving lead changes
    document.getElementById('saveLeadChanges').addEventListener('click', updateLead);
}

/**
 * Update the UI after successful authentication
 */
function authenticateUI(token) {
    const loginForm = document.getElementById('loginForm');
    const leadsContainer = document.getElementById('leadsContainer');
    const authStatus = document.getElementById('authStatus');
    
    loginForm.style.display = 'none';
    leadsContainer.style.display = 'block';
    authStatus.innerHTML = '<span class="badge bg-success">Authenticated</span>';
    
    // Load leads data
    fetchLeads(token);
}

/**
 * Fetch leads from the API
 */
async function fetchLeads(token, filterState = null) {
    try {
        const response = await fetch('/leads/', {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        if (response.ok) {
            const leads = await response.json();
            
            // Filter leads if a filter is specified
            const filteredLeads = filterState 
                ? leads.filter(lead => lead.state === filterState)
                : leads;
                
            renderLeadsTable(filteredLeads);
        } else {
            // Handle error (e.g., token expired)
            if (response.status === 401) {
                localStorage.removeItem('token');
                document.getElementById('loginForm').style.display = 'block';
                document.getElementById('leadsContainer').style.display = 'none';
                document.getElementById('authStatus').innerHTML = '<span class="badge bg-warning text-dark">Not Authenticated</span>';
            }
        }
    } catch (error) {
        console.error('Error fetching leads:', error);
    }
}

/**
 * Render the leads table with the provided data
 */
function renderLeadsTable(leads) {
    const tableBody = document.getElementById('leadsTableBody');
    tableBody.innerHTML = '';
    
    if (leads.length === 0) {
        tableBody.innerHTML = `
            <tr>
                <td colspan="7" class="text-center">No leads found</td>
            </tr>
        `;
        return;
    }
    
    leads.forEach(lead => {
        const row = document.createElement('tr');
        row.setAttribute('data-lead-id', lead.id);
        
        // Format date
        const createdDate = new Date(lead.created_at);
        const formattedDate = createdDate.toLocaleDateString() + ' ' + createdDate.toLocaleTimeString();
        
        // Status badge
        const statusBadge = lead.state === 'PENDING' 
            ? '<span class="badge badge-pending">Pending</span>'
            : '<span class="badge badge-reached-out">Reached Out</span>';
        
        row.innerHTML = `
            <td>${lead.id}</td>
            <td>${lead.first_name} ${lead.last_name}</td>
            <td>${lead.email}</td>
            <td>${formattedDate}</td>
            <td>${statusBadge}</td>
            <td><a href="${lead.resume_path}" target="_blank">View</a></td>
            <td>
                <button class="btn btn-sm btn-primary view-lead-btn" data-lead-id="${lead.id}">
                    View Details
                </button>
            </td>
        `;
        
        tableBody.appendChild(row);
    });
    
    // Add click event to view details buttons
    document.querySelectorAll('.view-lead-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const leadId = this.getAttribute('data-lead-id');
            showLeadDetails(leadId);
        });
    });
}

/**
 * Show lead details in a modal
 */
async function showLeadDetails(leadId) {
    const token = localStorage.getItem('token');
    
    try {
        const response = await fetch(`/leads/${leadId}`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        if (response.ok) {
            const lead = await response.json();
            
            // Populate modal with lead details
            document.getElementById('detailName').textContent = `${lead.first_name} ${lead.last_name}`;
            document.getElementById('detailEmail').textContent = lead.email;
            document.getElementById('detailCreated').textContent = new Date(lead.created_at).toLocaleString();
            document.getElementById('detailResumeLink').href = lead.resume_path;
            
            // Set current state and notes
            document.getElementById('leadState').value = lead.state;
            document.getElementById('leadNotes').value = lead.notes || '';
            
            // Store lead ID in the modal for when saving changes
            document.getElementById('saveLeadChanges').setAttribute('data-lead-id', lead.id);
            
            // Show the modal
            const modal = new bootstrap.Modal(document.getElementById('leadDetailsModal'));
            modal.show();
        }
    } catch (error) {
        console.error('Error fetching lead details:', error);
    }
}

/**
 * Update a lead's state and notes
 */
async function updateLead() {
    const leadId = this.getAttribute('data-lead-id');
    const state = document.getElementById('leadState').value;
    const notes = document.getElementById('leadNotes').value;
    const token = localStorage.getItem('token');
    
    try {
        const response = await fetch(`/leads/${leadId}`, {
            method: 'PATCH',
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
            // Close the modal
            const modalElement = document.getElementById('leadDetailsModal');
            const modal = bootstrap.Modal.getInstance(modalElement);
            modal.hide();
            
            // Refresh leads list
            fetchLeads(token);
        }
    } catch (error) {
        console.error('Error updating lead:', error);
    }
}

/**
 * Filter leads by state
 */
function filterLeads(state) {
    const token = localStorage.getItem('token');
    if (token) {
        fetchLeads(token, state);
    }
}
