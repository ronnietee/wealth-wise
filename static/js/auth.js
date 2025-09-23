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
    
    // Register form
    const registerForm = document.getElementById('registerForm');
    if (registerForm) {
        registerForm.addEventListener('submit', handleRegister);
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

function handleLogin(e) {
    e.preventDefault();
    
    const formData = new FormData(e.target);
    const data = {
        username: formData.get('username'),
        password: formData.get('password')
    };
    
    // Validate input
    if (!data.username || !data.password) {
        showNotification('Please fill in all fields', 'error');
        return;
    }
    
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
            return response.json().then(errorData => {
                console.log('Login error data:', errorData);
                throw new Error(errorData.message || `HTTP error! status: ${response.status}`);
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

function handleRegister(e) {
    e.preventDefault();
    
    const formData = new FormData(e.target);
    const data = {
        username: formData.get('username'),
        email: formData.get('email'),
        password: formData.get('password'),
        currency: formData.get('currency')
    };
    
    // Validate input
    if (!data.username || !data.email || !data.password) {
        showNotification('Please fill in all required fields', 'error');
        return;
    }
    
    if (!validateEmail(data.email)) {
        showNotification('Please enter a valid email address', 'error');
        return;
    }
    
    if (!validatePassword(data.password)) {
        showNotification('Password must be at least 6 characters long', 'error');
        return;
    }
    
    // Show loading state
    const submitBtn = e.target.querySelector('button[type="submit"]');
    const originalText = submitBtn.innerHTML;
    showLoading(submitBtn);
    
    // Make API call
    fetch('/api/register', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    })
    .then(response => {
        if (response.ok) {
            return response.json();
        } else {
            return response.json().then(data => {
                throw new Error(data.message || 'Registration failed');
            });
        }
    })
    .then(data => {
        showNotification('Account created successfully! Please login.', 'success');
        
        // Switch to login tab
        setTimeout(() => {
            switchTab('login');
            e.target.reset();
        }, 1000);
    })
    .catch(error => {
        console.error('Registration error:', error);
        showNotification(error.message || 'Registration failed. Please try again.', 'error');
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
    const registerForm = document.getElementById('registerForm');
    
    if (tab === 'login') {
        if (loginForm) loginForm.style.display = 'block';
        if (registerForm) registerForm.style.display = 'none';
    } else if (tab === 'register') {
        if (loginForm) loginForm.style.display = 'none';
        if (registerForm) registerForm.style.display = 'block';
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

// Close modal when clicking outside
window.addEventListener('click', function(e) {
    const modals = document.querySelectorAll('.modal');
    modals.forEach(modal => {
        if (e.target === modal) {
            modal.style.display = 'none';
            document.body.classList.remove('modal-open');
        }
    });
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
        } else if (form && form.id === 'registerForm') {
            e.preventDefault();
            handleRegister({ preventDefault: () => {}, target: form });
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
`;
document.head.appendChild(style);
