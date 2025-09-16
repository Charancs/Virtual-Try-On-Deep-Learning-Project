// Main application JavaScript
document.addEventListener('DOMContentLoaded', function() {
    // Initialize the application
    initializeApp();
    
    // Add smooth scrolling to navigation links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
    
    // Add animation to feature cards
    animateFeatureCards();
    
    // Initialize demo interactions
    initializeDemoSection();
});

function initializeApp() {
    console.log('Virtual Try-On App Initialized');
    
    // Check for WebRTC support
    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
        showNotification('Your browser does not support camera access. Please use a modern browser.', 'warning');
        return;
    }
    
    // Initialize navigation
    initializeNavigation();
    
    // Initialize call-to-action buttons
    initializeCTAButtons();
}

function initializeNavigation() {
    const navbar = document.querySelector('.navbar');
    if (!navbar) return;
    
    // Add scroll effect to navbar
    window.addEventListener('scroll', function() {
        if (window.scrollY > 50) {
            navbar.classList.add('scrolled');
        } else {
            navbar.classList.remove('scrolled');
        }
    });
    
    // Mobile menu toggle
    const menuToggle = document.querySelector('.navbar-toggler');
    const mobileMenu = document.querySelector('.navbar-collapse');
    
    if (menuToggle && mobileMenu) {
        menuToggle.addEventListener('click', function() {
            mobileMenu.classList.toggle('show');
        });
    }
}

function initializeCTAButtons() {
    // Try Now buttons
    document.querySelectorAll('.btn-try-now, .btn-primary').forEach(button => {
        if (button.textContent.includes('Try') || button.textContent.includes('Start')) {
            button.addEventListener('click', function(e) {
                if (this.getAttribute('href') === '#' || !this.getAttribute('href')) {
                    e.preventDefault();
                    window.location.href = '/tryon';
                }
            });
        }
    });
    
    // Demo buttons
    document.querySelectorAll('.btn-demo').forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            scrollToDemo();
        });
    });
}

function animateFeatureCards() {
    const cards = document.querySelectorAll('.feature-card, .card');
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        });
    }, {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    });
    
    cards.forEach(card => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(30px)';
        card.style.transition = 'all 0.6s ease';
        observer.observe(card);
    });
}

function initializeDemoSection() {
    const demoSection = document.querySelector('#demo, .demo-section');
    if (!demoSection) return;
    
    // Create interactive demo elements
    createInteractiveDemo();
}

function createInteractiveDemo() {
    const demoContainer = document.querySelector('.demo-interface, .demo-preview');
    if (!demoContainer) return;
    
    // Add hover effects to demo elements
    demoContainer.addEventListener('mousemove', function(e) {
        const rect = this.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;
        
        // Create subtle parallax effect
        const moveX = (x - rect.width / 2) * 0.02;
        const moveY = (y - rect.height / 2) * 0.02;
        
        this.style.transform = `translate(${moveX}px, ${moveY}px)`;
    });
    
    demoContainer.addEventListener('mouseleave', function() {
        this.style.transform = 'translate(0, 0)';
    });
}

function scrollToDemo() {
    const demoSection = document.querySelector('#demo, .demo-section');
    if (demoSection) {
        demoSection.scrollIntoView({
            behavior: 'smooth',
            block: 'start'
        });
    }
}

function showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} notification`;
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        z-index: 9999;
        min-width: 300px;
        padding: 15px;
        border-radius: 6px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        animation: slideIn 0.3s ease;
    `;
    notification.textContent = message;
    
    // Add close button
    const closeBtn = document.createElement('button');
    closeBtn.innerHTML = '&times;';
    closeBtn.style.cssText = `
        float: right;
        background: none;
        border: none;
        font-size: 20px;
        cursor: pointer;
        margin-left: 10px;
    `;
    closeBtn.onclick = () => notification.remove();
    
    notification.appendChild(closeBtn);
    document.body.appendChild(notification);
    
    // Auto remove after 5 seconds
    setTimeout(() => {
        if (notification.parentNode) {
            notification.remove();
        }
    }, 5000);
}

// Add CSS for animations
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    .navbar.scrolled {
        background: rgba(255, 255, 255, 0.95) !important;
        backdrop-filter: blur(10px);
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
    }
    
    .feature-card:hover {
        transform: translateY(-5px) !important;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1) !important;
    }
`;
document.head.appendChild(style);

// Loading state management
function showLoading(element) {
    if (element) {
        element.style.opacity = '0.6';
        element.style.pointerEvents = 'none';
    }
}

function hideLoading(element) {
    if (element) {
        element.style.opacity = '1';
        element.style.pointerEvents = 'auto';
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

// Performance monitoring
function logPerformance(label) {
    if (performance && performance.mark) {
        performance.mark(label);
        console.log(`Performance mark: ${label}`);
    }
}

// Initialize performance monitoring
logPerformance('app-start');

// Export functions for use in other scripts
window.VirtualTryOn = {
    showNotification,
    showLoading,
    hideLoading,
    debounce,
    throttle,
    logPerformance
};
