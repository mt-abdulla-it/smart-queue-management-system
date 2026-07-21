/**
 * Smart Queue Management System — Main JavaScript
 *
 * Core functionality:
 * - Sidebar toggle (desktop + mobile)
 * - Dark mode toggle with localStorage persistence
 * - AJAX CSRF token setup
 * - Toast notification helper
 * - DataTables initialization
 * - Auto-dismiss flash messages
 * - Animated number counters
 * - Button ripple effects
 * - Scroll-triggered animations
 * - Time-of-day greeting
 */

'use strict';

// =============================================================================
// SIDEBAR TOGGLE
// =============================================================================

document.addEventListener('DOMContentLoaded', function () {
    const sidebar = document.getElementById('sidebar');
    const sidebarToggle = document.getElementById('sidebarToggle');
    const sidebarOverlay = document.getElementById('sidebarOverlay');
    const mainContent = document.getElementById('mainContent');

    if (sidebarToggle && sidebar) {
        sidebarToggle.addEventListener('click', function () {
            sidebar.classList.toggle('show');
            if (sidebarOverlay) {
                sidebarOverlay.classList.toggle('show');
            }
        });
    }

    // Close sidebar when clicking overlay (mobile)
    if (sidebarOverlay) {
        sidebarOverlay.addEventListener('click', function () {
            sidebar.classList.remove('show');
            sidebarOverlay.classList.remove('show');
        });
    }

    // Close sidebar on window resize to desktop
    window.addEventListener('resize', function () {
        if (window.innerWidth > 991) {
            if (sidebar) sidebar.classList.remove('show');
            if (sidebarOverlay) sidebarOverlay.classList.remove('show');
        }
    });
});


// =============================================================================
// DARK MODE TOGGLE
// =============================================================================

document.addEventListener('DOMContentLoaded', function () {
    const darkModeToggle = document.getElementById('darkModeToggle');
    const darkModeIcon = document.getElementById('darkModeIcon');
    const htmlElement = document.documentElement;

    // Load saved preference
    const savedTheme = localStorage.getItem('sqms-theme') || 'light';
    setTheme(savedTheme, false);

    if (darkModeToggle) {
        darkModeToggle.addEventListener('click', function () {
            const currentTheme = htmlElement.getAttribute('data-bs-theme');
            const newTheme = currentTheme === 'dark' ? 'light' : 'dark';

            // Spin animation
            if (darkModeIcon) {
                darkModeIcon.style.transition = 'transform 0.5s ease';
                darkModeIcon.style.transform = 'rotate(360deg)';
                setTimeout(function() { darkModeIcon.style.transform = ''; }, 500);
            }

            setTheme(newTheme, true);
        });
    }

    // Real-time theme sync across open browser tabs
    window.addEventListener('storage', function (e) {
        if (e.key === 'sqms-theme' && e.newValue) {
            setTheme(e.newValue, false);
        }
    });

    function setTheme(theme, notify) {
        htmlElement.setAttribute('data-bs-theme', theme);
        localStorage.setItem('sqms-theme', theme);
        updateDarkModeIcon(theme);

        if (notify && typeof showToast === 'function') {
            const themeLabel = theme === 'dark' ? 'Dark Mode' : 'Light Mode';
            showToast('Switched to ' + themeLabel, 'info', 2000);
        }
    }

    function updateDarkModeIcon(theme) {
        if (darkModeIcon) {
            if (theme === 'dark') {
                darkModeIcon.classList.remove('fa-moon');
                darkModeIcon.classList.add('fa-sun', 'text-warning');
                if (darkModeToggle) darkModeToggle.setAttribute('title', 'Switch to Light Mode');
            } else {
                darkModeIcon.classList.remove('fa-sun', 'text-warning');
                darkModeIcon.classList.add('fa-moon');
                if (darkModeToggle) darkModeToggle.setAttribute('title', 'Switch to Dark Mode');
            }
        }
    }
});


// =============================================================================
// AJAX CSRF TOKEN SETUP
// =============================================================================

/**
 * Get the CSRF token from the cookie.
 * Required for all AJAX POST/PUT/DELETE requests.
 */
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Set up CSRF token for all jQuery AJAX requests
if (typeof $ !== 'undefined') {
    $.ajaxSetup({
        beforeSend: function (xhr, settings) {
            if (!/^(GET|HEAD|OPTIONS|TRACE)$/i.test(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader('X-CSRFToken', getCookie('csrftoken'));
            }
        }
    });
}

// Also set up for fetch API
const csrfToken = getCookie('csrftoken');


// =============================================================================
// TOAST NOTIFICATIONS (Enhanced with progress bar)
// =============================================================================

/**
 * Show a toast notification with slide-in animation and auto-dismiss progress.
 *
 * @param {string} message - The message to display.
 * @param {string} type - Bootstrap alert type: 'success', 'danger', 'warning', 'info'.
 * @param {number} duration - Auto-dismiss duration in ms (default: 5000).
 */
function showToast(message, type, duration) {
    type = type || 'info';
    duration = duration || 5000;

    // Create toast container if it doesn't exist
    var container = document.getElementById('toastContainer');
    if (!container) {
        container = document.createElement('div');
        container.id = 'toastContainer';
        container.className = 'position-fixed bottom-0 end-0 p-3';
        container.style.zIndex = '1100';
        document.body.appendChild(container);
    }

    var icons = {
        success: 'fa-check-circle',
        danger: 'fa-exclamation-circle',
        warning: 'fa-exclamation-triangle',
        info: 'fa-info-circle'
    };

    var toastId = 'toast-' + Date.now();
    var toastHTML = '' +
        '<div id="' + toastId + '" class="toast align-items-center text-bg-' + type + ' border-0 mb-2" role="alert" style="animation: slideInRight 0.3s ease-out;">' +
            '<div class="d-flex">' +
                '<div class="toast-body">' +
                    '<i class="fas ' + (icons[type] || icons.info) + ' me-2"></i>' + message +
                '</div>' +
                '<button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>' +
            '</div>' +
            '<div style="height: 3px; background: rgba(255,255,255,0.3); border-radius: 0 0 4px 4px;">' +
                '<div style="height: 100%; background: rgba(255,255,255,0.7); border-radius: 0 0 4px 4px; animation: toastProgress ' + duration + 'ms linear forwards;"></div>' +
            '</div>' +
        '</div>';

    container.insertAdjacentHTML('beforeend', toastHTML);
    var toastElement = document.getElementById(toastId);
    var toast = new bootstrap.Toast(toastElement, { delay: duration });
    toast.show();

    // Remove from DOM after hidden
    toastElement.addEventListener('hidden.bs.toast', function () {
        toastElement.remove();
    });
}

// Inject toast keyframe animations
(function () {
    var style = document.createElement('style');
    style.textContent = '' +
        '@keyframes slideInRight { from { transform: translateX(100%); opacity: 0; } to { transform: translateX(0); opacity: 1; } }' +
        '@keyframes toastProgress { from { width: 100%; } to { width: 0%; } }';
    document.head.appendChild(style);
})();


// =============================================================================
// DATATABLES INITIALIZATION
// =============================================================================

document.addEventListener('DOMContentLoaded', function () {
    // Auto-initialize DataTables on tables with .data-table class
    if (typeof $.fn.DataTable !== 'undefined') {
        $('.data-table').DataTable({
            responsive: true,
            pageLength: 20,
            language: {
                search: '',
                searchPlaceholder: 'Search...',
                lengthMenu: 'Show _MENU_ entries',
                info: 'Showing _START_ to _END_ of _TOTAL_ entries',
                paginate: {
                    previous: '<i class="fas fa-chevron-left"></i>',
                    next: '<i class="fas fa-chevron-right"></i>'
                }
            },
            dom: '<"d-flex justify-content-between align-items-center mb-3"lf>t<"d-flex justify-content-between align-items-center mt-3"ip>'
        });
    }
});


// =============================================================================
// AUTO-DISMISS FLASH MESSAGES
// =============================================================================

document.addEventListener('DOMContentLoaded', function () {
    // Auto-dismiss alerts after 6 seconds
    var alerts = document.querySelectorAll('.messages-container .alert');
    alerts.forEach(function (alert) {
        setTimeout(function () {
            var bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
            if (bsAlert) {
                bsAlert.close();
            }
        }, 6000);
    });
});


// =============================================================================
// ANIMATED NUMBER COUNTERS
// =============================================================================

/**
 * Animate a number from 0 to its target value.
 * Elements with class `.counter-animate` or `.stat-info h3` will auto-animate.
 */
function animateCounter(element) {
    var text = element.textContent.trim();
    // Try to parse as a number (supports decimals like 4.5)
    var target = parseFloat(text);
    if (isNaN(target)) return;

    var isFloat = text.indexOf('.') !== -1;
    var decimals = isFloat ? (text.split('.')[1] || '').length : 0;
    var duration = 1200;
    var startTime = null;
    var suffix = text.replace(/[\d.,\-]/g, '').trim();

    element.textContent = isFloat ? '0.' + '0'.repeat(decimals) : '0';

    function step(timestamp) {
        if (!startTime) startTime = timestamp;
        var progress = Math.min((timestamp - startTime) / duration, 1);
        // Ease-out cubic
        var easedProgress = 1 - Math.pow(1 - progress, 3);
        var current = easedProgress * target;

        if (isFloat) {
            element.textContent = current.toFixed(decimals) + suffix;
        } else {
            element.textContent = Math.floor(current).toLocaleString() + suffix;
        }

        if (progress < 1) {
            requestAnimationFrame(step);
        } else {
            element.textContent = text;
        }
    }

    requestAnimationFrame(step);
}

document.addEventListener('DOMContentLoaded', function () {
    // Auto-animate stat card numbers
    var statNumbers = document.querySelectorAll('.stat-info h3, .counter-animate');
    statNumbers.forEach(function (el) {
        animateCounter(el);
    });
});


// =============================================================================
// BUTTON RIPPLE EFFECT
// =============================================================================

document.addEventListener('DOMContentLoaded', function () {
    document.addEventListener('click', function (e) {
        var btn = e.target.closest('.btn');
        if (!btn) return;

        var ripple = document.createElement('span');
        ripple.className = 'ripple';
        var rect = btn.getBoundingClientRect();
        var size = Math.max(rect.width, rect.height);
        ripple.style.width = ripple.style.height = size + 'px';
        ripple.style.left = (e.clientX - rect.left - size / 2) + 'px';
        ripple.style.top = (e.clientY - rect.top - size / 2) + 'px';

        btn.appendChild(ripple);
        ripple.addEventListener('animationend', function () {
            ripple.remove();
        });
    });
});


// =============================================================================
// SCROLL-TRIGGERED ANIMATIONS
// =============================================================================

document.addEventListener('DOMContentLoaded', function () {
    if (!('IntersectionObserver' in window)) return;

    var animatedElements = document.querySelectorAll('.animate-on-scroll');
    if (animatedElements.length === 0) return;

    var observer = new IntersectionObserver(function (entries) {
        entries.forEach(function (entry) {
            if (entry.isIntersecting) {
                entry.target.classList.add('animate-fade-in-up');
                entry.target.style.opacity = '1';
                observer.unobserve(entry.target);
            }
        });
    }, { threshold: 0.1 });

    animatedElements.forEach(function (el) {
        el.style.opacity = '0';
        observer.observe(el);
    });
});


// =============================================================================
// TIME-OF-DAY GREETING
// =============================================================================

/**
 * Set greeting text and emoji based on current time.
 * Targets element with id="greetingText" and id="greetingEmoji".
 */
document.addEventListener('DOMContentLoaded', function () {
    var greetingEl = document.getElementById('greetingText');
    var emojiEl = document.getElementById('greetingEmoji');
    if (!greetingEl) return;

    var hour = new Date().getHours();
    var greeting, emoji;

    if (hour < 12) {
        greeting = 'Good Morning';
        emoji = '☀️';
    } else if (hour < 17) {
        greeting = 'Good Afternoon';
        emoji = '🌤️';
    } else {
        greeting = 'Good Evening';
        emoji = '🌙';
    }

    greetingEl.textContent = greeting;
    if (emojiEl) emojiEl.textContent = emoji;
});


// =============================================================================
// NOTIFICATION BELL ANIMATION
// =============================================================================

document.addEventListener('DOMContentLoaded', function () {
    var notifBadges = document.querySelectorAll('.notification-badge');
    notifBadges.forEach(function (badge) {
        var btn = badge.closest('.btn, button');
        if (btn) {
            btn.classList.add('has-notifications');
        }
    });
});


// =============================================================================
// CONFIRM DELETE UTILITY
// =============================================================================

/**
 * Show a confirmation dialog before performing a delete action.
 *
 * @param {string} itemName - Name of the item being deleted.
 * @param {string} deleteUrl - URL to redirect to for deletion.
 */
function confirmDelete(itemName, deleteUrl) {
    if (confirm('Are you sure you want to delete "' + itemName + '"? This action cannot be undone.')) {
        window.location.href = deleteUrl;
    }
}


// =============================================================================
// FORMAT NUMBER UTILITY
// =============================================================================

/**
 * Format a number with commas for thousands separator.
 */
function formatNumber(num) {
    return new Intl.NumberFormat('en-US').format(num);
}


// =============================================================================
// LANDING PAGE — Navbar Scroll Effect
// =============================================================================

document.addEventListener('DOMContentLoaded', function () {
    var landingNavbar = document.getElementById('landingNavbar');
    if (!landingNavbar) return;

    function handleNavbarScroll() {
        if (window.scrollY > 60) {
            landingNavbar.classList.add('scrolled');
        } else {
            landingNavbar.classList.remove('scrolled');
        }
    }

    window.addEventListener('scroll', handleNavbarScroll, { passive: true });
    handleNavbarScroll(); // Check on load

    // Mobile nav toggle
    var mobileToggle = document.getElementById('navMobileToggle');
    var mobileMenu = document.getElementById('navMobileMenu');
    if (mobileToggle && mobileMenu) {
        mobileToggle.addEventListener('click', function () {
            mobileToggle.classList.toggle('active');
            mobileMenu.classList.toggle('show');
        });

        // Close menu when clicking a link
        mobileMenu.querySelectorAll('a').forEach(function (link) {
            link.addEventListener('click', function () {
                mobileToggle.classList.remove('active');
                mobileMenu.classList.remove('show');
            });
        });
    }
});


// =============================================================================
// LANDING PAGE — Smooth Scroll for Anchor Links
// =============================================================================

document.addEventListener('DOMContentLoaded', function () {
    document.querySelectorAll('a[href^="#"]').forEach(function (anchor) {
        anchor.addEventListener('click', function (e) {
            var targetId = this.getAttribute('href');
            if (targetId === '#') return;
            var targetEl = document.querySelector(targetId);
            if (targetEl) {
                e.preventDefault();
                var navHeight = 70;
                var targetPosition = targetEl.getBoundingClientRect().top + window.pageYOffset - navHeight;
                window.scrollTo({
                    top: targetPosition,
                    behavior: 'smooth'
                });
            }
        });
    });
});


// =============================================================================
// LANDING PAGE — Animated Number Counters
// =============================================================================

document.addEventListener('DOMContentLoaded', function () {
    var counters = document.querySelectorAll('.stat-counter-value');
    if (!counters.length) return;

    var animated = false;

    function animateCounters() {
        if (animated) return;
        animated = true;

        counters.forEach(function (counter) {
            var target = parseFloat(counter.getAttribute('data-target'));
            var decimals = parseInt(counter.getAttribute('data-decimals')) || 0;
            var duration = 2000;
            var startTime = null;

            function step(timestamp) {
                if (!startTime) startTime = timestamp;
                var progress = Math.min((timestamp - startTime) / duration, 1);
                // Ease-out quad
                var eased = 1 - Math.pow(1 - progress, 3);
                var current = eased * target;

                if (decimals > 0) {
                    counter.textContent = current.toFixed(decimals);
                } else {
                    counter.textContent = Math.floor(current).toLocaleString();
                }

                if (progress < 1) {
                    requestAnimationFrame(step);
                } else {
                    if (decimals > 0) {
                        counter.textContent = target.toFixed(decimals);
                    } else {
                        counter.textContent = target.toLocaleString();
                    }
                }
            }

            requestAnimationFrame(step);
        });
    }

    // Use IntersectionObserver to trigger when stats section is visible
    var statsSection = document.getElementById('stats');
    if (statsSection && 'IntersectionObserver' in window) {
        var observer = new IntersectionObserver(function (entries) {
            entries.forEach(function (entry) {
                if (entry.isIntersecting) {
                    animateCounters();
                    observer.unobserve(entry.target);
                }
            });
        }, { threshold: 0.1 });

        observer.observe(statsSection);

        // Fallback: if counters haven't animated after 4 seconds of page load,
        // check if the stats section is in the viewport
        setTimeout(function () {
            if (!animated) {
                var rect = statsSection.getBoundingClientRect();
                if (rect.top < window.innerHeight && rect.bottom > 0) {
                    animateCounters();
                }
            }
        }, 4000);
    }
});


// =============================================================================
// LANDING PAGE — Scroll Reveal Animation
// =============================================================================

document.addEventListener('DOMContentLoaded', function () {
    var reveals = document.querySelectorAll('.scroll-reveal');
    if (!reveals.length || !('IntersectionObserver' in window)) return;

    var revealObserver = new IntersectionObserver(function (entries) {
        entries.forEach(function (entry) {
            if (entry.isIntersecting) {
                var delay = parseInt(entry.target.getAttribute('data-delay')) || 0;
                setTimeout(function () {
                    entry.target.classList.add('revealed');
                }, delay);
                revealObserver.unobserve(entry.target);
            }
        });
    }, { threshold: 0.15, rootMargin: '0px 0px -40px 0px' });

    reveals.forEach(function (el) {
        revealObserver.observe(el);
    });
});
