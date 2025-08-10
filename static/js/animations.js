// Neural Dreams Inc. - Interactive Animations and Effects

document.addEventListener('DOMContentLoaded', function() {
    initializeFloatingElements();
    initializeDreamCardHovers();
    initializeScrollAnimations();
    initializeParticleEffects();
    initializeTypingEffect();
    initializePulseEffects();
    initializeImageLazyLoading();
    initializeTooltips();
});

// ===== FLOATING ELEMENTS ANIMATION =====
function initializeFloatingElements() {
    const shapes = document.querySelectorAll('.floating-shape');
    
    shapes.forEach((shape, index) => {
        // Add random delay to each shape
        shape.style.animationDelay = `${Math.random() * 2}s`;
        
        // Add random movement patterns
        setInterval(() => {
            const randomX = Math.random() * 100;
            const randomY = Math.random() * 100;
            const randomScale = 0.8 + Math.random() * 0.4;
            
            shape.style.transform = `translate(${randomX}vw, ${randomY}vh) scale(${randomScale})`;
            shape.style.transition = 'transform 10s ease-in-out';
        }, 10000 + Math.random() * 5000);
    });
}

// ===== DREAM CARD HOVER EFFECTS =====
function initializeDreamCardHovers() {
    const dreamCards = document.querySelectorAll('.dream-card');
    
    dreamCards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            // Add glow effect
            this.style.boxShadow = '0 20px 60px rgba(102, 126, 234, 0.3)';
            this.style.transform = 'translateY(-8px) scale(1.02)';
            
            // Animate card content
            const image = this.querySelector('.dream-card-image img');
            if (image) {
                image.style.transform = 'scale(1.1)';
            }
            
            // Add sparkle effect
            addSparkleEffect(this);
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.boxShadow = '0 8px 32px rgba(31, 38, 135, 0.15)';
            this.style.transform = 'translateY(0) scale(1)';
            
            const image = this.querySelector('.dream-card-image img');
            if (image) {
                image.style.transform = 'scale(1)';
            }
            
            // Remove sparkles
            removeSparkleEffect(this);
        });
    });
}

// ===== SPARKLE EFFECT =====
function addSparkleEffect(element) {
    const sparkleCount = 6;
    
    for (let i = 0; i < sparkleCount; i++) {
        const sparkle = document.createElement('div');
        sparkle.className = 'sparkle';
        sparkle.style.cssText = `
            position: absolute;
            width: 4px;
            height: 4px;
            background: linear-gradient(45deg, #fff, #ffd700);
            border-radius: 50%;
            pointer-events: none;
            z-index: 1000;
            animation: sparkleFloat 2s ease-in-out infinite;
            left: ${Math.random() * 100}%;
            top: ${Math.random() * 100}%;
            animation-delay: ${Math.random() * 2}s;
        `;
        
        element.style.position = 'relative';
        element.appendChild(sparkle);
    }
    
    // Add sparkle animation keyframes if not exists
    if (!document.querySelector('#sparkle-keyframes')) {
        const style = document.createElement('style');
        style.id = 'sparkle-keyframes';
        style.textContent = `
            @keyframes sparkleFloat {
                0%, 100% {
                    opacity: 0;
                    transform: translateY(0px) scale(0);
                }
                50% {
                    opacity: 1;
                    transform: translateY(-20px) scale(1);
                }
            }
        `;
        document.head.appendChild(style);
    }
}

function removeSparkleEffect(element) {
    const sparkles = element.querySelectorAll('.sparkle');
    sparkles.forEach(sparkle => {
        sparkle.style.animation = 'sparkleFloat 0.5s ease-out forwards';
        setTimeout(() => {
            if (sparkle.parentNode) {
                sparkle.parentNode.removeChild(sparkle);
            }
        }, 500);
    });
}

// ===== SCROLL ANIMATIONS =====
function initializeScrollAnimations() {
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };
    
    const observer = new IntersectionObserver(function(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('animate__animated', 'animate__fadeInUp');
                entry.target.style.opacity = '1';
            }
        });
    }, observerOptions);
    
    // Observe elements that should animate on scroll
    const animatableElements = document.querySelectorAll(
        '.dream-card, .stat-card, .profile-section, .leaderboard-row, .rating-card'
    );
    
    animatableElements.forEach(el => {
        el.style.opacity = '0';
        observer.observe(el);
    });
}

// ===== PARTICLE EFFECTS =====
function initializeParticleEffects() {
    const particleContainer = document.createElement('div');
    particleContainer.className = 'particle-container';
    particleContainer.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        pointer-events: none;
        z-index: -1;
        overflow: hidden;
    `;
    
    document.body.appendChild(particleContainer);
    
    // Create floating particles
    function createParticle() {
        const particle = document.createElement('div');
        particle.className = 'dream-particle';
        particle.style.cssText = `
            position: absolute;
            width: ${Math.random() * 6 + 2}px;
            height: ${Math.random() * 6 + 2}px;
            background: linear-gradient(45deg, rgba(102, 126, 234, 0.6), rgba(217, 70, 239, 0.6));
            border-radius: 50%;
            left: ${Math.random() * 100}%;
            top: 100%;
            animation: floatUp ${Math.random() * 10 + 10}s linear infinite;
        `;
        
        particleContainer.appendChild(particle);
        
        // Remove particle after animation
        setTimeout(() => {
            if (particle.parentNode) {
                particle.parentNode.removeChild(particle);
            }
        }, 20000);
    }
    
    // Add particle animation keyframes
    if (!document.querySelector('#particle-keyframes')) {
        const style = document.createElement('style');
        style.id = 'particle-keyframes';
        style.textContent = `
            @keyframes floatUp {
                0% {
                    transform: translateY(0) rotate(0deg);
                    opacity: 0;
                }
                10% {
                    opacity: 1;
                }
                90% {
                    opacity: 1;
                }
                100% {
                    transform: translateY(-100vh) rotate(360deg);
                    opacity: 0;
                }
            }
        `;
        document.head.appendChild(style);
    }
    
    // Create particles periodically
    setInterval(createParticle, 2000);
}

// ===== TYPING EFFECT =====
function initializeTypingEffect() {
    const typingElements = document.querySelectorAll('.typing-effect');
    
    typingElements.forEach(element => {
        const text = element.textContent;
        element.textContent = '';
        element.style.borderRight = '2px solid #667eea';
        
        let index = 0;
        const timer = setInterval(() => {
            if (index < text.length) {
                element.textContent += text.charAt(index);
                index++;
            } else {
                clearInterval(timer);
                element.style.borderRight = 'none';
            }
        }, 100);
    });
}

// ===== PULSE EFFECTS =====
function initializePulseEffects() {
    const pulseElements = document.querySelectorAll('.btn-dream, .dream-orb, .podium-card');
    
    pulseElements.forEach(element => {
        element.addEventListener('mouseenter', function() {
            this.style.animation = 'dreamPulse 0.6s ease-in-out';
        });
        
        element.addEventListener('animationend', function() {
            this.style.animation = '';
        });
    });
}

// ===== LAZY LOADING FOR IMAGES =====
function initializeImageLazyLoading() {
    const images = document.querySelectorAll('img[data-src]');
    
    const imageObserver = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const img = entry.target;
                img.src = img.dataset.src;
                img.classList.remove('lazy');
                imageObserver.unobserve(img);
            }
        });
    });
    
    images.forEach(img => imageObserver.observe(img));
}

// ===== DYNAMIC TOOLTIPS =====
function initializeTooltips() {
    const tooltipElements = document.querySelectorAll('[data-tooltip]');
    
    tooltipElements.forEach(element => {
        element.addEventListener('mouseenter', function(e) {
            const tooltip = document.createElement('div');
            tooltip.className = 'dream-tooltip';
            tooltip.textContent = this.dataset.tooltip;
            tooltip.style.cssText = `
                position: absolute;
                background: rgba(0, 0, 0, 0.9);
                color: white;
                padding: 8px 12px;
                border-radius: 8px;
                font-size: 0.9rem;
                white-space: nowrap;
                z-index: 10000;
                pointer-events: none;
                opacity: 0;
                transition: opacity 0.3s ease;
            `;
            
            document.body.appendChild(tooltip);
            
            const rect = this.getBoundingClientRect();
            tooltip.style.left = rect.left + rect.width / 2 - tooltip.offsetWidth / 2 + 'px';
            tooltip.style.top = rect.top - tooltip.offsetHeight - 10 + 'px';
            
            setTimeout(() => tooltip.style.opacity = '1', 10);
            
            this.tooltipElement = tooltip;
        });
        
        element.addEventListener('mouseleave', function() {
            if (this.tooltipElement) {
                this.tooltipElement.style.opacity = '0';
                setTimeout(() => {
                    if (this.tooltipElement && this.tooltipElement.parentNode) {
                        this.tooltipElement.parentNode.removeChild(this.tooltipElement);
                    }
                }, 300);
            }
        });
    });
}

// ===== DREAM RATING STARS INTERACTION =====
function initializeRatingStars() {
    const ratingContainers = document.querySelectorAll('.rating-input');
    
    ratingContainers.forEach(container => {
        const stars = container.querySelectorAll('.star');
        const input = container.querySelector('input[type="hidden"]');
        
        stars.forEach((star, index) => {
            star.addEventListener('mouseenter', function() {
                highlightStars(stars, index + 1);
            });
            
            star.addEventListener('click', function() {
                if (input) {
                    input.value = index + 1;
                }
                setRating(stars, index + 1);
            });
        });
        
        container.addEventListener('mouseleave', function() {
            const currentRating = input ? parseInt(input.value) : 0;
            setRating(stars, currentRating);
        });
    });
}

function highlightStars(stars, rating) {
    stars.forEach((star, index) => {
        if (index < rating) {
            star.classList.add('highlighted');
        } else {
            star.classList.remove('highlighted');
        }
    });
}

function setRating(stars, rating) {
    stars.forEach((star, index) => {
        if (index < rating) {
            star.classList.add('active');
        } else {
            star.classList.remove('active');
        }
    });
}

// ===== SMOOTH SCROLLING =====
function initializeSmoothScrolling() {
    const links = document.querySelectorAll('a[href^="#"]');
    
    links.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            
            const targetId = this.getAttribute('href');
            const targetElement = document.querySelector(targetId);
            
            if (targetElement) {
                targetElement.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
}

// ===== FORM ENHANCEMENTS =====
function initializeFormEnhancements() {
    const forms = document.querySelectorAll('form');
    
    forms.forEach(form => {
        // Add loading state to submit buttons
        form.addEventListener('submit', function() {
            const submitBtn = this.querySelector('button[type="submit"]');
            if (submitBtn) {
                submitBtn.disabled = true;
                submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Processing...';
            }
        });
        
        // Enhanced input focus effects
        const inputs = form.querySelectorAll('.dream-input');
        inputs.forEach(input => {
            input.addEventListener('focus', function() {
                this.parentElement.classList.add('input-focused');
            });
            
            input.addEventListener('blur', function() {
                this.parentElement.classList.remove('input-focused');
            });
        });
    });
}

// ===== MOBILE OPTIMIZATIONS =====
function initializeMobileOptimizations() {
    // Touch-friendly interactions
    if ('ontouchstart' in window) {
        document.body.classList.add('touch-device');
        
        // Enhance touch interactions for cards
        const cards = document.querySelectorAll('.dream-card');
        cards.forEach(card => {
            card.addEventListener('touchstart', function() {
                this.classList.add('touch-active');
            });
            
            card.addEventListener('touchend', function() {
                setTimeout(() => {
                    this.classList.remove('touch-active');
                }, 150);
            });
        });
    }
}

// ===== PERFORMANCE OPTIMIZATIONS =====
function optimizePerformance() {
    // Debounce scroll events
    let scrollTimer;
    window.addEventListener('scroll', function() {
        if (scrollTimer) {
            clearTimeout(scrollTimer);
        }
        scrollTimer = setTimeout(() => {
            handleScroll();
        }, 16); // ~60fps
    });
    
    // Throttle resize events
    let resizeTimer;
    window.addEventListener('resize', function() {
        if (resizeTimer) {
            clearTimeout(resizeTimer);
        }
        resizeTimer = setTimeout(() => {
            handleResize();
        }, 250);
    });
}

function handleScroll() {
    // Add scroll-based animations here
    const scrollTop = window.pageYOffset;
    const navbar = document.querySelector('.dream-navbar');
    
    if (navbar) {
        if (scrollTop > 50) {
            navbar.classList.add('scrolled');
        } else {
            navbar.classList.remove('scrolled');
        }
    }
}

function handleResize() {
    // Handle responsive adjustments
    const screenWidth = window.innerWidth;
    
    // Adjust particle effects for smaller screens
    if (screenWidth < 768) {
        const particles = document.querySelectorAll('.dream-particle');
        particles.forEach(particle => {
            particle.style.display = 'none';
        });
    }
}

// ===== ERROR HANDLING =====
window.addEventListener('error', function(e) {
    console.error('Dream Marketplace Error:', e.error);
    
    // Show user-friendly error message
    showNotification('Something went wrong. Please refresh the page.', 'error');
});

function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification notification-${type} animate__animated animate__fadeInDown`;
    notification.style.cssText = `
        position: fixed;
        top: 100px;
        right: 20px;
        background: ${type === 'error' ? '#ef4444' : '#10b981'};
        color: white;
        padding: 1rem 1.5rem;
        border-radius: 12px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        z-index: 10000;
        max-width: 300px;
    `;
    
    notification.textContent = message;
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.classList.add('animate__fadeOutUp');
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 500);
    }, 5000);
}

// Initialize all enhancements
document.addEventListener('DOMContentLoaded', function() {
    initializeRatingStars();
    initializeSmoothScrolling();
    initializeFormEnhancements();
    initializeMobileOptimizations();
    optimizePerformance();
});
