// Main JavaScript functionality for STEWARD

// Global currency variable
let userCurrency = 'USD';

// Navigation enhancement
document.addEventListener('DOMContentLoaded', function() {
    initializeNavigation();
    initializeBreadcrumbs();
    initializePageTransitions();
});

// Initialize navigation functionality
function initializeNavigation() {
    const navToggle = document.getElementById('nav-toggle');
    const navMenu = document.getElementById('nav-menu');
    const navLinks = document.querySelectorAll('.nav-link');
    
    // Mobile menu toggle
    if (navToggle && navMenu) {
        navToggle.addEventListener('click', function() {
            console.log('Mobile menu toggle clicked');
            navToggle.classList.toggle('active');
            navMenu.classList.toggle('active');
            console.log('Menu active state:', navMenu.classList.contains('active'));
        });
        
        // Close menu when clicking outside
        document.addEventListener('click', function(e) {
            if (!navToggle.contains(e.target) && !navMenu.contains(e.target)) {
                navToggle.classList.remove('active');
                navMenu.classList.remove('active');
            }
        });
    }
    
    // Set active navigation link
    setActiveNavLink();
    
    // Add click handlers for navigation links
    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            // Close mobile menu if open
            if (navToggle && navMenu) {
                navToggle.classList.remove('active');
                navMenu.classList.remove('active');
            }
            
            // Add loading state
            showPageLoading();
        });
    });
}

// Set active navigation link based on current page
function setActiveNavLink() {
    const currentPath = window.location.pathname;
    const navLinks = document.querySelectorAll('.nav-link');
    
    navLinks.forEach(link => {
        link.classList.remove('active');
        if (link.getAttribute('href') === currentPath) {
            link.classList.add('active');
        }
    });
}

// Initialize breadcrumb navigation
function initializeBreadcrumbs() {
    const breadcrumbContainer = document.getElementById('breadcrumb-container');
    const breadcrumb = document.getElementById('breadcrumb');
    
    if (!breadcrumbContainer || !breadcrumb) return;
    
    // Show breadcrumb for non-dashboard pages
    const currentPath = window.location.pathname;
    if (currentPath !== '/dashboard') {
        breadcrumbContainer.style.display = 'block';
        updateBreadcrumbs(currentPath);
    }
}

// Update breadcrumb navigation
function updateBreadcrumbs(currentPath) {
    const breadcrumb = document.getElementById('breadcrumb');
    if (!breadcrumb) return;
    
    const breadcrumbItems = [
        { path: '/dashboard', label: 'Dashboard', icon: 'fas fa-home' },
        { path: '/breakdown', label: 'Breakdown', icon: 'fas fa-chart-pie' },
        { path: '/income', label: 'Income', icon: 'fas fa-dollar-sign' },
        { path: '/transactions', label: 'Transactions', icon: 'fas fa-list' },
        { path: '/budgets', label: 'Budgets', icon: 'fas fa-calendar' },
        { path: '/settings', label: 'Settings', icon: 'fas fa-cog' }
    ];
    
    const currentItem = breadcrumbItems.find(item => item.path === currentPath);
    if (!currentItem) return;
    
    breadcrumb.innerHTML = `
        <a href="/dashboard" class="breadcrumb-item">
            <i class="fas fa-home"></i>
            <span>Dashboard</span>
        </a>
        <span class="breadcrumb-separator">/</span>
        <span class="breadcrumb-item active">
            <i class="${currentItem.icon}"></i>
            <span>${currentItem.label}</span>
        </span>
    `;
}

// Initialize page transitions
function initializePageTransitions() {
    const mainContent = document.querySelector('.main-content');
    if (mainContent) {
        mainContent.classList.add('page-transition');
        
        // Add loaded class after a short delay
        setTimeout(() => {
            mainContent.classList.add('loaded');
        }, 100);
    }
}

// Show page loading state
function showPageLoading() {
    const loadingOverlay = document.createElement('div');
    loadingOverlay.className = 'loading-overlay';
    loadingOverlay.innerHTML = '<div class="loading-spinner"></div>';
    document.body.appendChild(loadingOverlay);
    
    // Remove loading overlay after page loads
    window.addEventListener('load', function() {
        setTimeout(() => {
            if (loadingOverlay.parentNode) {
                loadingOverlay.parentNode.removeChild(loadingOverlay);
            }
        }, 500);
    });
}

// Performance optimizations
// Debounce function for performance
function debounce(func, wait, immediate) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            timeout = null;
            if (!immediate) func(...args);
        };
        const callNow = immediate && !timeout;
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
        if (callNow) func(...args);
    };
}

// Throttle function for performance
function throttle(func, limit) {
    let inThrottle;
    return function() {
        const args = arguments;
        const context = this;
        if (!inThrottle) {
            func.apply(context, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
}

// Optimized event listeners with passive options
function addOptimizedEventListener(element, event, handler, options = {}) {
    const defaultOptions = {
        passive: true,
        capture: false
    };
    
    element.addEventListener(event, handler, { ...defaultOptions, ...options });
}

// Intersection Observer for lazy loading
function initializeLazyLoading() {
    if ('IntersectionObserver' in window) {
        const imageObserver = new IntersectionObserver((entries, observer) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    img.src = img.dataset.src;
                    img.classList.add('loaded');
                    observer.unobserve(img);
                }
            });
        });

        document.querySelectorAll('img[data-src]').forEach(img => {
            imageObserver.observe(img);
        });
    }
}

// Optimized scroll handler
const optimizedScrollHandler = throttle(function() {
    // Handle scroll events efficiently
    const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
    
    // Add/remove classes based on scroll position
    if (scrollTop > 100) {
        document.body.classList.add('scrolled');
    } else {
        document.body.classList.remove('scrolled');
    }
}, 16); // ~60fps

// Initialize performance optimizations
document.addEventListener('DOMContentLoaded', function() {
    initializeLazyLoading();
    addOptimizedEventListener(window, 'scroll', optimizedScrollHandler);
});

// Memory management
function cleanupEventListeners() {
    // Remove event listeners when navigating away
    const elements = document.querySelectorAll('[data-cleanup]');
    elements.forEach(element => {
        const events = element.dataset.cleanup.split(',');
        events.forEach(event => {
            element.removeEventListener(event.trim(), null);
        });
    });
}

// Optimized API calls with caching
const apiCache = new Map();
const CACHE_DURATION = 5 * 60 * 1000; // 5 minutes

function getCachedData(key) {
    const cached = apiCache.get(key);
    if (cached && Date.now() - cached.timestamp < CACHE_DURATION) {
        return cached.data;
    }
    return null;
}

function setCachedData(key, data) {
    apiCache.set(key, {
        data: data,
        timestamp: Date.now()
    });
}

// Optimized fetch with caching
async function fetchWithCache(url, options = {}) {
    const cacheKey = `${url}_${JSON.stringify(options)}`;
    const cached = getCachedData(cacheKey);
    
    if (cached) {
        return cached;
    }
    
    try {
        const response = await fetch(url, options);
        const data = await response.json();
        setCachedData(cacheKey, data);
        return data;
    } catch (error) {
        console.error('Fetch error:', error);
        throw error;
    }
}

// Clean up cache periodically
setInterval(() => {
    const now = Date.now();
    for (const [key, value] of apiCache.entries()) {
        if (now - value.timestamp > CACHE_DURATION) {
            apiCache.delete(key);
        }
    }
}, CACHE_DURATION);

// Load user settings
async function loadUserSettings() {
    try {
        const response = await fetch('/api/user/settings', {
            headers: {
                'Authorization': `Bearer ${getToken()}`
            }
        });
        
        if (response.ok) {
            const settings = await response.json();
            userCurrency = settings.currency;
            document.dispatchEvent(new CustomEvent('currencyLoaded', { detail: { currency: userCurrency } }));
            return settings;
        }
    } catch (error) {
        console.error('Error loading user settings:', error);
    }
}

// Check if user is authenticated
function checkAuth() {
    const token = localStorage.getItem('token');
    if (!token) {
        window.location.href = '/';
        return false;
    }
    return true;
}

// Get token from localStorage
function getToken() {
    return localStorage.getItem('token');
}

// Set token in localStorage
function setToken(token) {
    localStorage.setItem('token', token);
}

// Remove token from localStorage
function removeToken() {
    localStorage.removeItem('token');
}

// Show notification
function showNotification(message, type = 'success') {
    // Remove existing notifications
    const existingNotifications = document.querySelectorAll('.notification');
    existingNotifications.forEach(notification => notification.remove());
    
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.textContent = message;
    
    document.body.appendChild(notification);
    
    // Auto remove after 5 seconds
    setTimeout(() => {
        notification.remove();
    }, 5000);
}

// Logout function
function logout() {
    if (confirm('Are you sure you want to logout?')) {
        removeToken();
        window.location.href = '/';
    }
}

// Mobile navigation toggle
document.addEventListener('DOMContentLoaded', function() {
    const navToggle = document.getElementById('nav-toggle');
    const navMenu = document.getElementById('nav-menu');
    
    if (navToggle && navMenu) {
        navToggle.addEventListener('click', function() {
            navMenu.classList.toggle('active');
        });
    }
    
    // Close mobile menu when clicking on a link
    const navLinks = document.querySelectorAll('.nav-link');
    navLinks.forEach(link => {
        link.addEventListener('click', function() {
            navMenu.classList.remove('active');
        });
    });
    
    // Close mobile menu when clicking outside
    document.addEventListener('click', function(e) {
        if (!navToggle.contains(e.target) && !navMenu.contains(e.target)) {
            navMenu.classList.remove('active');
        }
    });
});

// Format currency
function formatCurrency(amount, currency = 'USD') {
    const symbol = getCurrencySymbol(currency);
    const formatter = new Intl.NumberFormat('en-US', {
        style: 'decimal',
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    });
    return symbol + formatter.format(amount || 0);
}

// Load user currency setting
function loadUserCurrency() {
    fetch('/api/user/settings', {
        headers: {
            'Authorization': 'Bearer ' + getToken()
        }
    })
    .then(response => response.json())
    .then(data => {
        userCurrency = data.currency || 'USD';
        // Update all currency displays on the page
        updateAllCurrencyDisplays();
        // Trigger a custom event to notify other scripts
        window.dispatchEvent(new CustomEvent('currencyLoaded', { detail: { currency: userCurrency } }));
    })
    .catch(error => {
        console.error('Error loading user currency:', error);
        userCurrency = 'USD';
        window.dispatchEvent(new CustomEvent('currencyLoaded', { detail: { currency: 'USD' } }));
    });
}

// Update all currency displays on the page
function updateAllCurrencyDisplays() {
    // Update any currency symbols in the UI
    const currencySymbols = document.querySelectorAll('[data-currency-symbol]');
    currencySymbols.forEach(symbol => {
        symbol.textContent = getCurrencySymbol(userCurrency);
    });
}

// Get currency symbol
function getCurrencySymbol(currency) {
    const symbols = {
        'USD': '$',
        'ZAR': 'R',
        'EUR': '€',
        'GBP': '£'
    };
    return symbols[currency] || '$';
}

// Format date
function formatDate(date) {
    return new Date(date).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
    });
}

// Close modal when clicking outside
window.addEventListener('click', function(e) {
    const modals = document.querySelectorAll('.modal');
    modals.forEach(modal => {
        if (e.target === modal) {
            modal.style.display = 'none';
        }
    });
});

// Close modal with Escape key
document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') {
        const modals = document.querySelectorAll('.modal');
        modals.forEach(modal => {
            if (modal.style.display === 'block') {
                modal.style.display = 'none';
            }
        });
    }
});

// API helper functions
async function apiCall(url, options = {}) {
    const token = getToken();
    const defaultOptions = {
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
        }
    };
    
    const mergedOptions = {
        ...defaultOptions,
        ...options,
        headers: {
            ...defaultOptions.headers,
            ...options.headers
        }
    };
    
    try {
        const response = await fetch(url, mergedOptions);
        
        if (response.status === 401) {
            // Token expired or invalid
            removeToken();
            window.location.href = '/';
            return;
        }
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.message || 'An error occurred');
        }
        
        return await response.json();
    } catch (error) {
        console.error('API call failed:', error);
        showNotification(error.message || 'An error occurred', 'error');
        throw error;
    }
}

// Utility functions
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

function throttle(func, limit) {
    let inThrottle;
    return function() {
        const args = arguments;
        const context = this;
        if (!inThrottle) {
            func.apply(context, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
}

// Input validation
function validateEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
}

function validatePassword(password) {
    return password.length >= 6;
}

function validateAmount(amount) {
    return !isNaN(amount) && amount > 0;
}

// Form helpers
function clearForm(formId) {
    const form = document.getElementById(formId);
    if (form) {
        form.reset();
    }
}

function getFormData(formId) {
    const form = document.getElementById(formId);
    if (!form) return {};
    
    const formData = new FormData(form);
    const data = {};
    
    for (let [key, value] of formData.entries()) {
        data[key] = value;
    }
    
    return data;
}

// Loading states
function showLoading(element) {
    if (element) {
        element.disabled = true;
        element.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Loading...';
    }
}

function hideLoading(element, originalText) {
    if (element) {
        element.disabled = false;
        element.innerHTML = originalText;
    }
}

// Animation helpers
function fadeIn(element, duration = 300) {
    element.style.opacity = '0';
    element.style.display = 'block';
    
    let start = performance.now();
    
    function animate(currentTime) {
        const elapsed = currentTime - start;
        const progress = Math.min(elapsed / duration, 1);
        
        element.style.opacity = progress;
        
        if (progress < 1) {
            requestAnimationFrame(animate);
        }
    }
    
    requestAnimationFrame(animate);
}

function fadeOut(element, duration = 300) {
    let start = performance.now();
    
    function animate(currentTime) {
        const elapsed = currentTime - start;
        const progress = Math.min(elapsed / duration, 1);
        
        element.style.opacity = 1 - progress;
        
        if (progress < 1) {
            requestAnimationFrame(animate);
        } else {
            element.style.display = 'none';
        }
    }
    
    requestAnimationFrame(animate);
}

// Local storage helpers
function saveToLocalStorage(key, data) {
    try {
        localStorage.setItem(key, JSON.stringify(data));
    } catch (error) {
        console.error('Error saving to localStorage:', error);
    }
}

function loadFromLocalStorage(key, defaultValue = null) {
    try {
        const data = localStorage.getItem(key);
        return data ? JSON.parse(data) : defaultValue;
    } catch (error) {
        console.error('Error loading from localStorage:', error);
        return defaultValue;
    }
}

// Date helpers
function getCurrentMonth() {
    const now = new Date();
    return `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}`;
}

function getCurrentDate() {
    return new Date().toISOString().split('T')[0];
}

function getDateRange(month) {
    const [year, monthNum] = month.split('-');
    const startDate = new Date(year, monthNum - 1, 1);
    const endDate = new Date(year, monthNum, 0);
    
    return {
        start: startDate.toISOString().split('T')[0],
        end: endDate.toISOString().split('T')[0]
    };
}

// Chart helpers (for future use)
function createPieChart(canvasId, data, colors) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    const centerX = canvas.width / 2;
    const centerY = canvas.height / 2;
    const radius = Math.min(centerX, centerY) - 10;
    
    let currentAngle = 0;
    
    data.forEach((item, index) => {
        const sliceAngle = (item.value / data.reduce((sum, d) => sum + d.value, 0)) * 2 * Math.PI;
        
        ctx.beginPath();
        ctx.arc(centerX, centerY, radius, currentAngle, currentAngle + sliceAngle);
        ctx.lineTo(centerX, centerY);
        ctx.fillStyle = colors[index % colors.length];
        ctx.fill();
        
        currentAngle += sliceAngle;
    });
}

// Export functions for global use
window.WealthWise = {
    checkAuth,
    getToken,
    setToken,
    removeToken,
    showNotification,
    logout,
    formatCurrency,
    formatDate,
    closeModal,
    apiCall,
    debounce,
    throttle,
    validateEmail,
    validatePassword,
    validateAmount,
    clearForm,
    getFormData,
    showLoading,
    hideLoading,
    fadeIn,
    fadeOut,
    saveToLocalStorage,
    loadFromLocalStorage,
    getCurrentMonth,
    getCurrentDate,
    getDateRange,
    createPieChart
};
