// Onboarding Flow JavaScript
class OnboardingFlow {
    constructor() {
        this.currentStep = 1;
        this.totalSteps = 5;
        this.formData = {};
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.updateProgress();
        this.setupPasswordStrength();
        this.setupReferralDetails();
        this.showStep(1);
    }

    setupEventListeners() {
        // Navigation buttons
        document.getElementById('nextBtn').addEventListener('click', () => this.nextStep());
        document.getElementById('backBtn').addEventListener('click', () => this.previousStep());
        document.getElementById('finishBtn').addEventListener('click', () => this.finishOnboarding());

        // Form validation with real-time checking
        document.getElementById('personalInfoForm').addEventListener('input', () => this.validateCurrentStep());
        document.getElementById('passwordForm').addEventListener('input', () => this.validateCurrentStep());
        document.getElementById('referralForm').addEventListener('change', () => this.validateCurrentStep());
        document.getElementById('detailsForm').addEventListener('change', () => this.validateCurrentStep());

        // Password confirmation validation
        document.getElementById('confirmPassword').addEventListener('input', () => this.validatePasswordMatch());

        // Real-time email validation
        document.getElementById('email').addEventListener('blur', () => this.validateEmail());
        document.getElementById('email').addEventListener('input', () => this.validateEmail());
        
        // Real-time category validation
        document.querySelectorAll('input[name="categories"]').forEach(checkbox => {
            checkbox.addEventListener('change', () => this.validateCurrentStep());
        });
    }

    setupPasswordStrength() {
        const passwordInput = document.getElementById('password');
        const strengthFill = document.getElementById('strengthFill');
        const strengthText = document.getElementById('strengthText');

        passwordInput.addEventListener('input', () => {
            const password = passwordInput.value;
            const strength = this.calculatePasswordStrength(password);
            
            strengthFill.style.width = strength.percentage + '%';
            strengthFill.className = 'strength-fill ' + strength.class;
            strengthText.textContent = strength.text;

            this.updatePasswordRequirements(password);
        });
    }

    setupReferralDetails() {
        const referralRadios = document.querySelectorAll('input[name="referralSource"]');
        const referralDetails = document.getElementById('referralDetails');

        referralRadios.forEach(radio => {
            radio.addEventListener('change', () => {
                if (radio.value === 'other') {
                    referralDetails.style.display = 'block';
                    document.getElementById('referralDetailsText').required = true;
                } else {
                    referralDetails.style.display = 'none';
                    document.getElementById('referralDetailsText').required = false;
                }
            });
        });
    }

    calculatePasswordStrength(password) {
        let score = 0;
        const requirements = {
            length: password.length >= 8,
            uppercase: /[A-Z]/.test(password),
            lowercase: /[a-z]/.test(password),
            number: /\d/.test(password),
            special: /[!@#$%^&*(),.?":{}|<>]/.test(password)
        };

        Object.values(requirements).forEach(met => {
            if (met) score++;
        });

        if (score < 2) return { percentage: 20, class: 'weak', text: 'Weak password' };
        if (score < 4) return { percentage: 60, class: 'medium', text: 'Medium strength' };
        if (score < 5) return { percentage: 80, class: 'strong', text: 'Strong password' };
        return { percentage: 100, class: 'very-strong', text: 'Very strong password' };
    }

    updatePasswordRequirements(password) {
        const requirements = {
            length: password.length >= 8,
            uppercase: /[A-Z]/.test(password),
            lowercase: /[a-z]/.test(password),
            number: /\d/.test(password),
            special: /[!@#$%^&*(),.?":{}|<>]/.test(password)
        };

        Object.keys(requirements).forEach(req => {
            const element = document.getElementById('req-' + req);
            if (requirements[req]) {
                element.classList.add('met');
            } else {
                element.classList.remove('met');
            }
        });
    }

    validatePasswordMatch() {
        const password = document.getElementById('password').value;
        const confirmPassword = document.getElementById('confirmPassword').value;
        const confirmInput = document.getElementById('confirmPassword');

        if (confirmPassword && password !== confirmPassword) {
            confirmInput.setCustomValidity('Passwords do not match');
            this.showFieldError('confirmPassword', 'Passwords do not match');
        } else {
            confirmInput.setCustomValidity('');
            this.clearFieldError('confirmPassword');
        }
    }

    async validateEmail() {
        const email = document.getElementById('email').value;
        const emailInput = document.getElementById('email');
        
        if (!email) {
            this.clearFieldError('email');
            return;
        }

        // Basic email format validation
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(email)) {
            this.showFieldError('email', 'Please enter a valid email address');
            return;
        }

        // Clear any existing timeout
        if (this.emailValidationTimeout) {
            clearTimeout(this.emailValidationTimeout);
        }

        // Debounce the API call
        this.emailValidationTimeout = setTimeout(async () => {
            try {
                const response = await fetch('/api/validate-email', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': this.getCsrfToken()
                    },
                    body: JSON.stringify({ email: email })
                });

                const result = await response.json();
                
                if (result.exists) {
                    this.showFieldError('email', 'An account with this email already exists');
                } else {
                    this.clearFieldError('email');
                }
            } catch (error) {
                console.error('Email validation error:', error);
                // Don't show error for network issues, just clear any existing errors
                this.clearFieldError('email');
            }
        }, 500); // 500ms delay
    }

    showFieldError(fieldId, message) {
        const field = document.getElementById(fieldId);
        const errorId = `${fieldId}-error`;
        
        // Remove existing error
        this.clearFieldError(fieldId);
        
        // Special handling for different field types
        if (fieldId === 'categories') {
            // Handle category grid error
            const categoryGrid = document.querySelector('.category-grid');
            categoryGrid.classList.add('error');
            
            // Create error message
            const errorDiv = document.createElement('div');
            errorDiv.id = errorId;
            errorDiv.className = 'field-error';
            errorDiv.textContent = message;
            
            // Insert error after category grid
            categoryGrid.parentNode.insertBefore(errorDiv, categoryGrid.nextSibling);
        } else if (fieldId === 'referralSource') {
            // Handle referral source error
            const radioGroup = document.querySelector('.radio-group');
            radioGroup.style.border = '2px solid #dc3545';
            radioGroup.style.borderRadius = '8px';
            radioGroup.style.padding = '0.5rem';
            radioGroup.style.background = 'rgba(220, 53, 69, 0.05)';
            
            // Create error message
            const errorDiv = document.createElement('div');
            errorDiv.id = errorId;
            errorDiv.className = 'field-error';
            errorDiv.textContent = message;
            
            // Insert error after radio group
            radioGroup.parentNode.insertBefore(errorDiv, radioGroup.nextSibling);
        } else if (field) {
            // Regular field error
            field.style.borderColor = '#dc3545';
            
            // Create error message
            const errorDiv = document.createElement('div');
            errorDiv.id = errorId;
            errorDiv.className = 'field-error';
            errorDiv.textContent = message;
            
            // Insert error after field
            field.parentNode.insertBefore(errorDiv, field.nextSibling);
        }
    }

    clearFieldError(fieldId) {
        const field = document.getElementById(fieldId);
        const errorId = `${fieldId}-error`;
        const errorDiv = document.getElementById(errorId);
        
        if (errorDiv) {
            errorDiv.remove();
        }
        
        // Special handling for different field types
        if (fieldId === 'categories') {
            const categoryGrid = document.querySelector('.category-grid');
            categoryGrid.classList.remove('error');
        } else if (fieldId === 'referralSource') {
            const radioGroup = document.querySelector('.radio-group');
            radioGroup.style.border = '';
            radioGroup.style.borderRadius = '';
            radioGroup.style.padding = '';
            radioGroup.style.background = '';
        } else if (field) {
            // Reset field styling
            field.style.borderColor = '#e9ecef';
        }
    }

    validateCurrentStep() {
        const currentForm = document.querySelector(`#step${this.currentStep} form`);
        if (!currentForm) return true;

        let isValid = true;
        let hasErrors = false;

        // Clear all previous field errors
        this.clearAllFieldErrors();

        // Step 1: Personal Information
        if (this.currentStep === 1) {
            isValid = this.validatePersonalInfo() && isValid;
        }
        
        // Step 2: Password
        if (this.currentStep === 2) {
            isValid = this.validatePassword() && isValid;
        }
        
        // Step 3: Referral Source
        if (this.currentStep === 3) {
            isValid = this.validateReferralSource() && isValid;
        }
        
        // Step 4: Currency and Categories
        if (this.currentStep === 4) {
            isValid = this.validateDetails() && isValid;
        }

        // Update next button state
        const nextBtn = document.getElementById('nextBtn');
        const finishBtn = document.getElementById('finishBtn');
        
        if (this.currentStep < this.totalSteps) {
            nextBtn.disabled = !isValid;
        } else {
            finishBtn.disabled = !isValid;
        }

        return isValid;
    }

    validatePersonalInfo() {
        let isValid = true;
        
        // First Name
        const firstName = document.getElementById('firstName').value.trim();
        if (!firstName) {
            this.showFieldError('firstName', 'First name is required');
            isValid = false;
        }

        // Last Name
        const lastName = document.getElementById('lastName').value.trim();
        if (!lastName) {
            this.showFieldError('lastName', 'Last name is required');
            isValid = false;
        }

        // Email
        const email = document.getElementById('email').value.trim();
        if (!email) {
            this.showFieldError('email', 'Email address is required');
            isValid = false;
        } else {
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            if (!emailRegex.test(email)) {
                this.showFieldError('email', 'Please enter a valid email address');
                isValid = false;
            }
        }

        // Username (optional)
        const username = document.getElementById('username').value.trim();
        if (username) {
            // Validate username format if provided
            const usernameRegex = /^[a-zA-Z0-9_]{3,20}$/;
            if (!usernameRegex.test(username)) {
                this.showFieldError('username', 'Username must be 3-20 characters, letters, numbers, and underscores only');
                isValid = false;
            }
        }

        // Country
        const country = document.getElementById('country').value;
        if (!country) {
            this.showFieldError('country', 'Please select your country');
            isValid = false;
        }

        // Preferred Name (optional)
        const preferredName = document.getElementById('preferredName').value.trim();

        return isValid;
    }

    validatePassword() {
        let isValid = true;
        const password = document.getElementById('password').value;
        const confirmPassword = document.getElementById('confirmPassword').value;

        // Password requirements
        const requirements = {
            length: password.length >= 8,
            uppercase: /[A-Z]/.test(password),
            lowercase: /[a-z]/.test(password),
            number: /\d/.test(password),
            special: /[!@#$%^&*(),.?":{}|<>]/.test(password)
        };

        if (!password) {
            this.showFieldError('password', 'Password is required');
            isValid = false;
        } else {
            // Check each requirement
            if (!requirements.length) {
                this.showFieldError('password', 'Password must be at least 8 characters long');
                isValid = false;
            } else if (!requirements.uppercase) {
                this.showFieldError('password', 'Password must contain at least one uppercase letter');
                isValid = false;
            } else if (!requirements.lowercase) {
                this.showFieldError('password', 'Password must contain at least one lowercase letter');
                isValid = false;
            } else if (!requirements.number) {
                this.showFieldError('password', 'Password must contain at least one number');
                isValid = false;
            } else if (!requirements.special) {
                this.showFieldError('password', 'Password must contain at least one special character');
                isValid = false;
            }
        }

        // Confirm Password
        if (!confirmPassword) {
            this.showFieldError('confirmPassword', 'Please confirm your password');
            isValid = false;
        } else if (password !== confirmPassword) {
            this.showFieldError('confirmPassword', 'Passwords do not match');
            isValid = false;
        }

        return isValid;
    }

    validateReferralSource() {
        let isValid = true;
        const referralSource = document.querySelector('input[name="referralSource"]:checked');
        
        if (!referralSource) {
            this.showFieldError('referralSource', 'Please select how you heard about us');
            isValid = false;
        } else if (referralSource.value === 'other') {
            const referralDetails = document.getElementById('referralDetailsText').value.trim();
            if (!referralDetails) {
                this.showFieldError('referralDetailsText', 'Please specify how you heard about us');
                isValid = false;
            }
        }

        return isValid;
    }

    validateDetails() {
        let isValid = true;
        
        // Currency
        const currency = document.getElementById('currency').value;
        if (!currency) {
            this.showFieldError('currency', 'Please select your currency');
            isValid = false;
        }

        // Categories
        const selectedCategories = document.querySelectorAll('input[name="categories"]:checked');
        if (selectedCategories.length === 0) {
            this.showFieldError('categories', 'Please select at least one spending category');
            isValid = false;
        }

        return isValid;
    }

    setupCategoryInteractions() {
        // Handle category header clicks to toggle subcategories
        const categoryHeaders = document.querySelectorAll('.category-header');
        categoryHeaders.forEach(header => {
            const checkbox = header.querySelector('input[type="checkbox"]');
            const categorySection = header.closest('.category-section');
            const subcategories = categorySection.querySelector('.subcategories');
            
            // Toggle subcategories when category is unchecked
            checkbox.addEventListener('change', function() {
                if (!this.checked) {
                    // Uncheck all subcategories when parent is unchecked
                    const subcategoryCheckboxes = subcategories.querySelectorAll('input[type="checkbox"]');
                    subcategoryCheckboxes.forEach(subCheckbox => {
                        subCheckbox.checked = false;
                    });
                    categorySection.classList.add('disabled');
                } else {
                    categorySection.classList.remove('disabled');
                }
            });
        });

        // Handle subcategory changes
        const subcategoryCheckboxes = document.querySelectorAll('input[name="subcategories"]');
        subcategoryCheckboxes.forEach(checkbox => {
            checkbox.addEventListener('change', function() {
                const categorySection = this.closest('.category-section');
                const categoryCheckbox = categorySection.querySelector('.category-header input[type="checkbox"]');
                const subcategoryCheckboxes = categorySection.querySelectorAll('input[name="subcategories"]');
                const checkedSubcategories = categorySection.querySelectorAll('input[name="subcategories"]:checked');
                
                // If any subcategory is checked, check the parent category
                if (checkedSubcategories.length > 0) {
                    categoryCheckbox.checked = true;
                    categorySection.classList.remove('disabled');
                }
                // If no subcategories are checked, uncheck the parent category
                else if (checkedSubcategories.length === 0) {
                    categoryCheckbox.checked = false;
                    categorySection.classList.add('disabled');
                }
            });
        });
    }

    clearAllFieldErrors() {
        // Clear all field errors
        const errorElements = document.querySelectorAll('.field-error');
        errorElements.forEach(error => error.remove());
        
        // Reset all field borders
        const allInputs = document.querySelectorAll('input, select');
        allInputs.forEach(input => {
            input.style.borderColor = '#e9ecef';
        });
    }

    showStep(stepNumber) {
        // Hide all steps
        for (let i = 1; i <= this.totalSteps; i++) {
            document.getElementById(`step${i}`).style.display = 'none';
        }
        
        // Show current step
        document.getElementById(`step${stepNumber}`).style.display = 'block';
        this.currentStep = stepNumber;
        
        // Setup step-specific interactions
        if (stepNumber === 4) {
            // Setup category interactions for step 4
            setTimeout(() => this.setupCategoryInteractions(), 100);
        }
        
        // Update UI
        this.updateProgress();
        this.updateNavigationButtons();
        this.validateCurrentStep();
    }

    nextStep() {
        if (!this.validateCurrentStep()) return;

        // Save current step data
        this.saveCurrentStepData();

        // Show next step
        this.showStep(this.currentStep + 1);
    }

    previousStep() {
        // Show previous step
        this.showStep(this.currentStep - 1);
    }

    saveCurrentStepData() {
        const currentForm = document.querySelector(`#step${this.currentStep} form`);
        if (!currentForm) return;

        const formData = new FormData(currentForm);
        
        // Convert FormData to object
        const stepData = {};
        for (let [key, value] of formData.entries()) {
            if (stepData[key]) {
                // Handle multiple values (like checkboxes)
                if (Array.isArray(stepData[key])) {
                    stepData[key].push(value);
                } else {
                    stepData[key] = [stepData[key], value];
                }
            } else {
                stepData[key] = value;
            }
        }

        this.formData = { ...this.formData, ...stepData };
    }

    updateProgress() {
        const progressFill = document.getElementById('progressFill');
        const currentStepSpan = document.getElementById('currentStep');
        const totalStepsSpan = document.getElementById('totalSteps');

        const percentage = (this.currentStep / this.totalSteps) * 100;
        progressFill.style.width = percentage + '%';
        currentStepSpan.textContent = this.currentStep;
        totalStepsSpan.textContent = this.totalSteps;
    }

    updateNavigationButtons() {
        const backBtn = document.getElementById('backBtn');
        const nextBtn = document.getElementById('nextBtn');
        const finishBtn = document.getElementById('finishBtn');
        const navigation = document.querySelector('.onboarding-navigation');

        // Hide navigation on welcome page (step 5)
        if (this.currentStep === 5) {
            navigation.style.display = 'none';
            return;
        } else {
            navigation.style.display = 'flex';
        }

        // Show/hide back button
        backBtn.style.display = this.currentStep > 1 ? 'block' : 'none';

        // Show/hide next/finish buttons
        if (this.currentStep < 4) { // Show next button for steps 1-3
            nextBtn.style.display = 'block';
            finishBtn.style.display = 'none';
        } else if (this.currentStep === 4) { // Show finish button for step 4
            nextBtn.style.display = 'none';
            finishBtn.style.display = 'block';
        } else { // Hide both for step 5 (welcome page)
            nextBtn.style.display = 'none';
            finishBtn.style.display = 'none';
        }
    }

    async finishOnboarding() {
        if (!this.validateCurrentStep()) return;

        // Save final step data
        this.saveCurrentStepData();

        // Show loading state
        const finishBtn = document.getElementById('finishBtn');
        const originalText = finishBtn.textContent;
        finishBtn.textContent = 'Creating Account...';
        finishBtn.disabled = true;

        try {
            // Send data to backend
            const response = await fetch('/api/onboarding/complete', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCsrfToken()
                },
                body: JSON.stringify(this.formData)
            });

            const result = await response.json();

            if (result.success) {
                if (result.email_verification_required) {
                    // Show email verification step instead of welcome page
                    this.showEmailVerificationStep(result);
                } else {
                    // Store JWT token for API access (for existing users)
                    if (result.token) {
                        localStorage.setItem('token', result.token);
                        localStorage.setItem('steward_token', result.token);
                    }
                    
                    // Show welcome page (step 5) after successful account creation
                    this.showStep(5);
                }
            } else {
                // Show specific error message from server
                this.showError(result.message || 'Account creation failed');
                return;
            }
        } catch (error) {
            console.error('Onboarding error:', error);
            this.showError('Network error. Please check your connection and try again.');
        } finally {
            finishBtn.textContent = originalText;
            finishBtn.disabled = false;
        }
    }

    showEmailVerificationStep(result) {
        // Hide all steps
        for (let i = 1; i <= this.totalSteps; i++) {
            document.getElementById(`step${i}`).style.display = 'none';
        }
        
        // Hide navigation
        document.querySelector('.onboarding-navigation').style.display = 'none';
        
        // Create email verification step
        const verificationStep = document.createElement('div');
        verificationStep.id = 'step-verification';
        verificationStep.className = 'onboarding-step verification-step';
        verificationStep.innerHTML = `
            <div class="verification-content">
                <div class="verification-icon">
                    <i class="fas fa-envelope-open"></i>
                </div>
                <h2>Check Your Email</h2>
                <p class="verification-message">${result.message}</p>
                <div class="verification-details">
                    <p>We've sent a verification link to:</p>
                    <p class="email-address">${result.user.email}</p>
                    <p class="verification-note">Please check your inbox and click the verification link to complete your account setup.</p>
                </div>
                <div class="verification-actions">
                    <button onclick="resendVerificationEmail('${result.user.email}')" class="btn btn-secondary">
                        <i class="fas fa-redo"></i>
                        Resend Verification Email
                    </button>
                    <button onclick="goToLogin()" class="btn btn-primary">
                        <i class="fas fa-sign-in-alt"></i>
                        Go to Login
                    </button>
                </div>
            </div>
        `;
        
        // Insert after the last step
        const lastStep = document.getElementById(`step${this.totalSteps}`);
        lastStep.parentNode.insertBefore(verificationStep, lastStep.nextSibling);
        
        // Show the verification step
        verificationStep.style.display = 'block';
    }

    showError(message) {
        // Create or update error message display
        let errorDiv = document.getElementById('onboarding-error');
        if (!errorDiv) {
            errorDiv = document.createElement('div');
            errorDiv.id = 'onboarding-error';
            errorDiv.className = 'onboarding-error';
            
            // Insert error div after the onboarding content
            const onboardingContent = document.querySelector('.onboarding-content');
            onboardingContent.parentNode.insertBefore(errorDiv, onboardingContent.nextSibling);
        }
        
        errorDiv.innerHTML = `
            <div class="error-content">
                <i class="fas fa-exclamation-triangle"></i>
                <span>${message}</span>
                <button class="error-close" onclick="this.parentElement.parentElement.style.display='none'">&times;</button>
            </div>
        `;
        errorDiv.style.display = 'block';
        
        // Scroll to error message
        errorDiv.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }

    getCsrfToken() {
        const metaToken = document.querySelector('meta[name="csrf-token"]');
        return metaToken ? metaToken.getAttribute('content') : 'dummy_token';
    }
}

// Global functions for email verification
function resendVerificationEmail(email) {
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
            alert('Verification email sent successfully! Please check your inbox.');
        } else {
            alert('Error: ' + result.message);
        }
    })
    .catch(error => {
        console.error('Error resending verification:', error);
        alert('Error sending verification email. Please try again.');
    })
    .finally(() => {
        button.innerHTML = originalText;
        button.disabled = false;
    });
}

function goToLogin() {
    window.location.href = '/?showLogin=true';
}

// Initialize onboarding flow when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    new OnboardingFlow();
});
