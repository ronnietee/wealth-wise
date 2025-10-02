// Authentication JavaScript for Wealth Wise

document.addEventListener('DOMContentLoaded', function() {
    // Check if user is already logged in
    if (getToken() && window.location.pathname === '/') {
        window.location.href = '/dashboard';
    }
    
    // Set up form listeners
    setupAuthListeners();
});

function setupAuthListeners() {
    // Login form
    const loginForm = document.getElementById('loginForm');
    if (loginForm) {
        loginForm.addEventListener('submit', handleLogin);
    }
    
    
    // Forgot password form
    const forgotPasswordForm = document.getElementById('forgotPasswordForm');
    if (forgotPasswordForm) {
        forgotPasswordForm.addEventListener('submit', handleForgotPassword);
    }
    
    // Tab switching
    const tabBtns = document.querySelectorAll('.tab-btn');
    tabBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            const tab = this.textContent.toLowerCase();
            switchTab(tab);
        });
    });
    
}

function handleForgotPassword(e) {
    e.preventDefault();
    
    const formData = new FormData(e.target);
    const email = formData.get('email');
    
    // Validate input
    if (!email) {
        showNotification('Please enter your email address', 'error');
        return;
    }
    
    // Show loading state
    const submitBtn = e.target.querySelector('button[type="submit"]');
    const originalText = submitBtn.innerHTML;
    showLoading(submitBtn);
    
    // Make API call
    fetch('/api/forgot-password', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ email: email })
    })
    .then(response => {
        if (!response.ok) {
            return response.text().then(text => {
                try {
                    const errorData = JSON.parse(text);
                    throw new Error(errorData.message || `HTTP error! status: ${response.status}`);
                } catch (e) {
                    throw new Error(`Server error: ${response.status}`);
                }
            });
        }
        return response.json();
    })
    .then(data => {
        showNotification(data.message, 'success');
        closeForgotPasswordModal();
    })
    .catch(error => {
        console.error('Forgot password error:', error);
        showNotification('Error sending reset email. Please try again.', 'error');
    })
    .finally(() => {
        hideLoading(submitBtn, originalText);
    });
}

function handleLogin(e) {
    e.preventDefault();
    
    const formData = new FormData(e.target);
    const usernameOrEmail = formData.get('username');
    const password = formData.get('password');
    
    // Validate input
    if (!usernameOrEmail || !password) {
        showNotification('Please fill in all fields', 'error');
        return;
    }
    
    // Determine if input is email or username
    const isEmail = usernameOrEmail.includes('@');
    const data = {
        [isEmail ? 'email' : 'username']: usernameOrEmail,
        password: password
    };
    
    console.log('Login attempt with:', { usernameOrEmail, isEmail, data });
    
    // Show loading state
    const submitBtn = e.target.querySelector('button[type="submit"]');
    const originalText = submitBtn.innerHTML;
    showLoading(submitBtn);
    
    // Make API call
    fetch('/api/login', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    })
    .then(response => {
        console.log('Login response status:', response.status);
        if (!response.ok) {
            // Try to parse as JSON, fallback to text if it fails
            return response.text().then(text => {
                try {
                    const errorData = JSON.parse(text);
                    // For 403 errors (email verification required), handle specially
                    if (response.status === 403 && errorData.email_verification_required) {
                        showEmailVerificationMessage(errorData.message, errorData.email);
                        return;
                    }
                    // For 401 errors, show a user-friendly message
                    if (response.status === 401) {
                        throw new Error(errorData.message || 'Invalid username or password. Please check your credentials and try again.');
                    }
                    throw new Error(errorData.message || `HTTP error! status: ${response.status}`);
                } catch (e) {
                    // If JSON parsing fails, show appropriate error based on status code
                    if (response.status === 401) {
                        throw new Error('Invalid username or password. Please check your credentials and try again.');
                    }
                    throw new Error(`Server error: ${response.status}`);
                }
            });
        }
        return response.json();
    })
    .then(data => {
        if (data.token) {
            setToken(data.token);
            showNotification('Login successful!', 'success');
            
            // Redirect to dashboard after a short delay
            setTimeout(() => {
                window.location.href = '/dashboard';
            }, 1000);
        } else {
            showNotification(data.message || 'Login failed', 'error');
        }
    })
    .catch(error => {
        console.error('Login error:', error);
        showNotification(error.message || 'Login failed. Please try again.', 'error');
    })
    .finally(() => {
        hideLoading(submitBtn, originalText);
    });
}


function switchTab(tab) {
    // Update tab buttons
    const tabBtns = document.querySelectorAll('.tab-btn');
    tabBtns.forEach(btn => {
        btn.classList.remove('active');
        if (btn.textContent.toLowerCase().includes(tab)) {
            btn.classList.add('active');
        }
    });
    
    // Show/hide forms
    const loginForm = document.getElementById('loginForm');
    
    if (tab === 'login') {
        if (loginForm) loginForm.style.display = 'block';
    }
}

function showLogin() {
    const modal = document.getElementById('authModal');
    if (modal) {
        modal.style.display = 'block';
        document.body.classList.add('modal-open');
        switchTab('login');
    } else {
        console.error('Login modal not found');
    }
}

function showLoginModal() {
    const modal = document.getElementById('loginModal');
    if (modal) {
        modal.style.display = 'block';
        document.body.classList.add('modal-open');
    } else {
        console.error('Login modal not found');
    }
}


function showHowItWorks() {
    const modal = document.getElementById('howItWorksModal');
    if (modal) {
        modal.style.display = 'block';
        document.body.classList.add('modal-open');
    } else {
        console.error('How it works modal not found');
    }
}

function closeModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.style.display = 'none';
        document.body.classList.remove('modal-open');
    } else {
        console.error('Modal not found:', modalId);
    }
}

// Fallback function to close any visible modal
function closeAnyModal() {
    const modals = document.querySelectorAll('.modal');
    modals.forEach(modal => {
        if (modal.style.display === 'block') {
            modal.style.display = 'none';
        }
    });
    document.body.classList.remove('modal-open');
}

// Forgot Password Modal Functions
function openForgotPasswordModal() {
    document.getElementById('forgotPasswordModal').style.display = 'block';
    document.body.classList.add('modal-open');
}

function closeForgotPasswordModal() {
    document.getElementById('forgotPasswordModal').style.display = 'none';
    document.getElementById('forgotPasswordForm').reset();
    document.body.classList.remove('modal-open');
}

// Close modal when clicking outside
window.addEventListener('click', function(e) {
    const modals = document.querySelectorAll('.modal');
    modals.forEach(modal => {
        if (e.target === modal) {
            modal.style.display = 'none';
            document.body.classList.remove('modal-open');
        }
    });
    
    // Handle forgot password modal specifically
    if (e.target.id === 'forgotPasswordModal') {
        closeForgotPasswordModal();
    }
});

// Auto-focus on first input when modal opens
document.addEventListener('DOMContentLoaded', function() {
    const authModal = document.getElementById('authModal');
    if (authModal) {
        const observer = new MutationObserver(function(mutations) {
            mutations.forEach(function(mutation) {
                if (mutation.type === 'attributes' && mutation.attributeName === 'style') {
                    if (authModal.style.display === 'block') {
                        const firstInput = authModal.querySelector('input');
                        if (firstInput) {
                            setTimeout(() => firstInput.focus(), 100);
                        }
                    }
                }
            });
        });
        
        observer.observe(authModal, {
            attributes: true,
            attributeFilter: ['style']
        });
    }
});

// Handle Enter key in forms
document.addEventListener('keydown', function(e) {
    if (e.key === 'Enter') {
        const activeElement = document.activeElement;
        const form = activeElement.closest('form');
        
        if (form && form.id === 'loginForm') {
            e.preventDefault();
            handleLogin({ preventDefault: () => {}, target: form });
        }
    }
});


// Password visibility toggle (if needed)
function togglePasswordVisibility(inputId) {
    const input = document.getElementById(inputId);
    const button = input.nextElementSibling;
    
    if (input.type === 'password') {
        input.type = 'text';
        button.innerHTML = '<i class="fas fa-eye-slash"></i>';
    } else {
        input.type = 'password';
        button.innerHTML = '<i class="fas fa-eye"></i>';
    }
}

// Form validation helpers
function validateForm(form) {
    const inputs = form.querySelectorAll('input[required], select[required]');
    let isValid = true;
    
    inputs.forEach(input => {
        if (!input.value.trim()) {
            input.classList.add('error');
            isValid = false;
        } else {
            input.classList.remove('error');
        }
    });
    
    return isValid;
}

function showEmailVerificationMessage(message, email) {
    // Hide the login form
    const loginForm = document.getElementById('loginForm');
    if (loginForm) {
        loginForm.style.display = 'none';
    }
    
    // Create verification message
    const verificationDiv = document.createElement('div');
    verificationDiv.id = 'email-verification-message';
    verificationDiv.className = 'verification-message';
    verificationDiv.innerHTML = `
        <div class="verification-content">
            <div class="verification-icon">
                <i class="fas fa-envelope-open"></i>
            </div>
            <h3>Email Verification Required</h3>
            <p>${message}</p>
            <div class="verification-details">
                <p>We've sent a verification link to:</p>
                <p class="email-address">${email}</p>
                <p class="verification-note">Please check your inbox and click the verification link to complete your account setup.</p>
            </div>
            <div class="verification-actions">
                <button onclick="resendVerificationFromLogin('${email}')" class="btn btn-secondary">
                    <i class="fas fa-redo"></i>
                    Resend Verification Email
                </button>
                <button onclick="backToLogin()" class="btn btn-primary">
                    <i class="fas fa-arrow-left"></i>
                    Back to Login
                </button>
            </div>
        </div>
    `;
    
    // Insert after the login form
    const authModal = document.getElementById('authModal');
    if (authModal) {
        const modalBody = authModal.querySelector('.modal-body');
        modalBody.appendChild(verificationDiv);
    }
}

function resendVerificationFromLogin(email) {
    const button = event.target;
    const originalText = button.innerHTML;
    button.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Sending...';
    button.disabled = true;
    
    fetch('/api/resend-verification', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ email: email })
    })
    .then(response => response.json())
    .then(result => {
        if (result.success) {
            showNotification('Verification email sent successfully! Please check your inbox.', 'success');
        } else {
            showNotification('Error: ' + result.message, 'error');
        }
    })
    .catch(error => {
        console.error('Error resending verification:', error);
        showNotification('Error sending verification email. Please try again.', 'error');
    })
    .finally(() => {
        button.innerHTML = originalText;
        button.disabled = false;
    });
}

function backToLogin() {
    // Hide verification message
    const verificationDiv = document.getElementById('email-verification-message');
    if (verificationDiv) {
        verificationDiv.remove();
    }
    
    // Show login form
    const loginForm = document.getElementById('loginForm');
    if (loginForm) {
        loginForm.style.display = 'block';
    }
}

// Add error styling
const style = document.createElement('style');
style.textContent = `
    .error {
        border-color: #ff6b6b !important;
        box-shadow: 0 0 0 3px rgba(255, 107, 107, 0.1) !important;
    }
    
    .error-message {
        color: #ff6b6b;
        font-size: 0.875rem;
        margin-top: 0.25rem;
    }
    
    .verification-message {
        text-align: center;
        padding: 20px;
    }
    
    .verification-content {
        max-width: 400px;
        margin: 0 auto;
    }
    
    .verification-icon {
        width: 60px;
        height: 60px;
        background: linear-gradient(135deg, #8B4513, #A0522D);
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        margin: 0 auto 20px;
        color: white;
        font-size: 24px;
    }
    
    .verification-content h3 {
        color: #333;
        margin-bottom: 15px;
        font-size: 20px;
        font-weight: 600;
    }
    
    .verification-content p {
        color: #666;
        margin-bottom: 15px;
        line-height: 1.5;
    }
    
    .verification-details {
        background: #f8f9fa;
        padding: 15px;
        border-radius: 6px;
        margin-bottom: 20px;
    }
    
    .verification-details p {
        margin: 0 0 8px 0;
        color: #555;
        font-size: 14px;
    }
    
    .email-address {
        font-weight: 600;
        color: #8B4513 !important;
        font-size: 16px;
    }
    
    .verification-note {
        font-style: italic;
        color: #777 !important;
        font-size: 13px;
    }
    
    .verification-actions {
        display: flex;
        gap: 10px;
        justify-content: center;
        flex-wrap: wrap;
    }
    
    .verification-actions .btn {
        min-width: 150px;
        font-size: 14px;
        padding: 10px 16px;
    }
    
    @media (max-width: 480px) {
        .verification-actions {
            flex-direction: column;
        }
        
        .verification-actions .btn {
            width: 100%;
        }
    }
`;
document.head.appendChild(style);
