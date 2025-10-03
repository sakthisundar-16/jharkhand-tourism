// Global variables
let selectedGuideId = null;
let selectedGuideName = null;
let selectedGuidePrice = null;

// Document ready function
document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Set minimum date for arrival date input
    const today = new Date().toISOString().split('T')[0];
    const arrivalDateInput = document.querySelector('input[name="arrival_date"]');
    if (arrivalDateInput) {
        arrivalDateInput.setAttribute('min', today);
    }

    // Add loading states to forms
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const submitBtn = form.querySelector('button[type="submit"]');
            if (submitBtn && !submitBtn.disabled) {
                const originalText = submitBtn.innerHTML;
                submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Processing...';
                submitBtn.disabled = true;
                
                // Re-enable button after 10 seconds to prevent permanent lock
                setTimeout(() => {
                    if (submitBtn.disabled) {
                        submitBtn.innerHTML = originalText;
                        submitBtn.disabled = false;
                    }
                }, 10000);
            }
        });
    });

    // Auto-hide alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.classList.add('fade');
            setTimeout(() => {
                alert.remove();
            }, 150);
        }, 5000);
    });
});

// Show login form based on user type (updated for separate forms)
function showLoginForm(userType) {
    // Redirect to appropriate login page
    switch(userType) {
        case 'tourist':
            window.location.href = '/login/tourist';
            break;
        case 'guide':
            window.location.href = '/login/guide';
            break;
        case 'admin':
            // For admin, you might want to keep a modal or separate admin login
            alert('Admin login functionality can be added here');
            break;
        default:
            window.location.href = '/login/tourist';
    }
}

// Show admin login modal
function showAdminlogin() {
    // Close the login type modal
    const loginModal = bootstrap.Modal.getInstance(document.getElementById('loginModal'));
    if (loginModal) {
        loginModal.hide();
    }
    // Show admin login modal
    const adminLoginModal = new bootstrap.Modal(document.getElementById('adminLoginModal'));
    adminLoginModal.show();
}

// Show registration form
function showRegisterForm() {
    const registerModal = new bootstrap.Modal(document.getElementById('registerModal'));
    registerModal.show();
}

// UPDATED: Book guide function for tourist booking - redirects to booking page
function bookGuide(guideId, guideName) {
    // Store guide info in sessionStorage for the booking page
    sessionStorage.setItem('selectedGuideId', guideId);
    sessionStorage.setItem('selectedGuideName', guideName);
    
    // Redirect to detailed booking page
    window.location.href = `/book_guide/${guideId}`;
}

// Legacy function for backward compatibility (if used anywhere)
function selectGuide(guideId, guideName, guidePrice) {
    selectedGuideId = guideId;
    selectedGuideName = guideName;
    selectedGuidePrice = guidePrice;
    
    // Update form fields if they exist
    const guideIdInput = document.getElementById('selectedGuideId');
    const guideNameInput = document.getElementById('selectedGuideName');
    const bookBtn = document.getElementById('bookBtn');

    if (guideIdInput && guideNameInput && bookBtn) {
        guideIdInput.value = guideId;
        guideNameInput.value = guideName;
        bookBtn.disabled = false;
        
        // Add visual feedback
        guideNameInput.classList.add('animate-pulse');
        setTimeout(() => {
            guideNameInput.classList.remove('animate-pulse');
        }, 500);
    }

    // Highlight selected guide card
    const guideCards = document.querySelectorAll('.guide-card');
    guideCards.forEach(card => {
        card.classList.remove('border-success', 'bg-light');
        card.classList.add('border-info');
    });

    // Highlight the selected card
    const selectedCard = event.target.closest('.guide-card');
    if (selectedCard) {
        selectedCard.classList.remove('border-info');
        selectedCard.classList.add('border-success', 'bg-light');
    }

    // Show success message
    showToast('Guide selected successfully!', 'success');
}

// Scroll to about section
function scrollToAbout() {
    const aboutSection = document.getElementById('about');
    if (aboutSection) {
        aboutSection.scrollIntoView({ 
            behavior: 'smooth',
            block: 'start' 
        });
    }
}

// Show toast notifications
function showToast(message, type = 'info') {
    // Create toast container if it doesn't exist
    let toastContainer = document.getElementById('toastContainer');
    if (!toastContainer) {
        toastContainer = document.createElement('div');
        toastContainer.id = 'toastContainer';
        toastContainer.className = 'toast-container position-fixed top-0 end-0 p-3';
        toastContainer.style.zIndex = '9999';
        document.body.appendChild(toastContainer);
    }

    // Create toast element
    const toastId = 'toast-' + Date.now();
    const toastHTML = `
        <div id="${toastId}" class="toast align-items-center text-white bg-${type === 'success' ? 'success' : type === 'error' ? 'danger' : 'info'} border-0" role="alert" aria-live="assertive" aria-atomic="true">
            <div class="d-flex">
                <div class="toast-body">
                    <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'error' ? 'exclamation-circle' : 'info-circle'} me-2"></i>
                    ${message}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
            </div>
        </div>
    `;

    toastContainer.insertAdjacentHTML('beforeend', toastHTML);

    // Initialize and show toast
    const toastElement = document.getElementById(toastId);
    const toast = new bootstrap.Toast(toastElement, {
        autohide: true,
        delay: 3000
    });
    toast.show();

    // Remove toast element after it's hidden
    toastElement.addEventListener('hidden.bs.toast', function() {
        toastElement.remove();
    });
}

// Form validation for booking
function validateBookingForm() {
    const form = document.getElementById('bookingForm');
    if (!form) return false;

    const requiredFields = form.querySelectorAll('[required]');
    let isValid = true;

    requiredFields.forEach(field => {
        if (!field.value.trim()) {
            field.classList.add('is-invalid');
            isValid = false;
        } else {
            field.classList.remove('is-invalid');
            field.classList.add('is-valid');
        }
    });

    // Validate phone number
    const phoneField = form.querySelector('input[name="phone"]');
    if (phoneField && phoneField.value) {
        const phoneRegex = /^[0-9]{10}$/;
        if (!phoneRegex.test(phoneField.value.replace(/\D/g, ''))) {
            phoneField.classList.add('is-invalid');
            showToast('Please enter a valid 10-digit phone number', 'error');
            isValid = false;
        }
    }

    // Validate arrival date
    const arrivalDate = form.querySelector('input[name="arrival_date"]');
    if (arrivalDate && arrivalDate.value) {
        const today = new Date();
        const selectedDate = new Date(arrivalDate.value);
        today.setHours(0, 0, 0, 0);
        if (selectedDate < today) {
            arrivalDate.classList.add('is-invalid');
            showToast('Arrival date cannot be in the past', 'error');
            isValid = false;
        }
    }

    return isValid;
}

// File upload preview
function previewImage(input) {
    if (input.files && input.files[0]) {
        const reader = new FileReader();
        reader.onload = function(e) {
            let preview = document.getElementById('imagePreview');
            if (!preview) {
                preview = document.createElement('div');
                preview.id = 'imagePreview';
                preview.className = 'mt-2';
                input.parentNode.appendChild(preview);
            }
            preview.innerHTML = `<img src="${e.target.result}" class="img-thumbnail" style="max-height: 200px;">`;
        };
        reader.readAsDataURL(input.files[0]);
    }
}

// Add event listener for file inputs
document.addEventListener('change', function(e) {
    if (e.target.type === 'file' && e.target.accept && e.target.accept.includes('image')) {
        previewImage(e.target);
    }
});

// Booking form submission with validation
document.addEventListener('submit', function(e) {
    if (e.target.id === 'bookingForm') {
        e.preventDefault();
        
        if (validateBookingForm()) {
            const guideName = e.target.querySelector('input[name="guide_id"]')?.dataset?.guideName || 'this guide';
            // Show confirmation dialog
            if (confirm(`Are you sure you want to book ${guideName} for your Jharkhand tour?`)) {
                e.target.submit();
            } else {
                // Re-enable the submit button if user cancels
                const submitBtn = e.target.querySelector('button[type="submit"]');
                if (submitBtn) {
                    submitBtn.innerHTML = '<i class="fas fa-paper-plane me-2"></i>Send Booking Request';
                    submitBtn.disabled = false;
                }
            }
        } else {
            // Re-enable the submit button if validation fails
            const submitBtn = e.target.querySelector('button[type="submit"]');
            if (submitBtn) {
                submitBtn.innerHTML = '<i class="fas fa-paper-plane me-2"></i>Send Booking Request';
                submitBtn.disabled = false;
            }
        }
    }
});

// Filter guides by district and tour type (for tourist dashboard)
function filterGuidesByDistrict() {
    const selectedDistrict = document.getElementById('districtSelect')?.value || '';
    const selectedTourType = document.getElementById('tourTypeSelect')?.value || '';
    const guideCards = document.querySelectorAll('.guide-card');
    
    guideCards.forEach(card => {
        const location = card.dataset.location || '';
        const specialization = card.dataset.specialization || '';
        
        let showCard = true;
        
        if (selectedDistrict && !location.includes(selectedDistrict) && location !== 'All Jharkhand') {
            showCard = false;
        }
        
        if (selectedTourType && !specialization.includes(selectedTourType)) {
            showCard = false;
        }
        
        card.style.display = showCard ? 'block' : 'none';
    });
}

// Add event listener for tour type filter
document.addEventListener('DOMContentLoaded', function() {
    const tourTypeSelect = document.getElementById('tourTypeSelect');
    if (tourTypeSelect) {
        tourTypeSelect.addEventListener('change', filterGuidesByDistrict);
    }
});

// Calculate total cost for tourist booking
function calculateTotal() {
    const daysSelect = document.querySelector('select[name="days_to_stay"]');
    const groupSizeSelect = document.querySelector('select[name="group_size"]');
    const totalCostElement = document.getElementById('totalCost');
    
    if (daysSelect && totalCostElement) {
        const days = parseInt(daysSelect.value) || 1;
        const groupSize = parseInt(groupSizeSelect?.value) || 1;
        const pricePerDay = window.guidePrice || 2000; // Default price
        
        const total = days * pricePerDay;
        totalCostElement.textContent = '₹' + total.toLocaleString();
        
        // Update selected days display
        const selectedDaysElement = document.getElementById('selectedDays');
        if (selectedDaysElement) {
            selectedDaysElement.textContent = days + ' day' + (days > 1 ? 's' : '');
        }
        
        // Update selected group size display
        const selectedGroupSizeElement = document.getElementById('selectedGroupSize');
        if (selectedGroupSizeElement) {
            selectedGroupSizeElement.textContent = groupSize + ' person' + (groupSize > 1 ? 's' : '');
        }
    }
}

// Update booking status for guides
function updateBookingStatus(bookingId, status) {
    const confirmMessages = {
        'confirmed': 'Are you sure you want to confirm this Jharkhand tour booking?',
        'cancelled': 'Are you sure you want to cancel this booking?',
        'completed': 'Mark this Jharkhand tour as completed?'
    };
    
    if (confirm(confirmMessages[status] || `Are you sure you want to ${status} this booking?`)) {
        window.location.href = `/update_booking_status/${bookingId}/${status}`;
    }
}

// Search functionality for admin dashboard
function searchTable(inputId, tableId) {
    const input = document.getElementById(inputId);
    const table = document.getElementById(tableId);
    
    if (input && table) {
        input.addEventListener('keyup', function() {
            const filter = input.value.toLowerCase();
            const rows = table.getElementsByTagName('tr');
            
            for (let i = 1; i < rows.length; i++) {
                const row = rows[i];
                const cells = row.getElementsByTagName('td');
                let found = false;
                
                for (let j = 0; j < cells.length; j++) {
                    if (cells[j].textContent.toLowerCase().includes(filter)) {
                        found = true;
                        break;
                    }
                }
                
                row.style.display = found ? '' : 'none';
            }
        });
    }
}

// Initialize search for admin tables
document.addEventListener('DOMContentLoaded', function() {
    // Add search inputs to admin tables if they exist
    const tables = document.querySelectorAll('.table');
    tables.forEach((table, index) => {
        if (table.closest('#adminTabsContent')) {
            const searchId = `search-${index}`;
            const searchInput = `
                <div class="mb-3">
                    <input type="text" id="${searchId}" class="form-control" placeholder="Search table...">
                </div>
            `;
            table.parentNode.insertAdjacentHTML('afterbegin', searchInput);
            searchTable(searchId, table.id || `table-${index}`);
            if (!table.id) table.id = `table-${index}`;
        }
    });
});

// Smooth scrolling for anchor links
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

// Handle window resize for responsive design
window.addEventListener('resize', function() {
    // Adjust hero section height on mobile
    const heroSection = document.querySelector('.hero-section');
    if (heroSection && window.innerWidth < 768) {
        heroSection.style.minHeight = 'calc(100vh - 70px)';
    } else if (heroSection) {
        heroSection.style.minHeight = '100vh';
    }
});

// View content details
function viewContent(contentId) {
    fetch(`/content/${contentId}`)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                const content = data.content;
                
                // Update modal title
                const modalTitle = document.getElementById('contentModalTitle');
                if (modalTitle) {
                    modalTitle.textContent = content.title;
                }
                
                // Build modal content
                let modalContent = `
                    <div class="row">
                        ${content.image_path ? `
                            <div class="col-12 mb-3">
                                <img src="/static/${content.image_path}" class="img-fluid rounded" alt="${content.title}">
                            </div>
                        ` : ''}
                        <div class="col-12">
                            <div class="content-details">
                                <div class="mb-3">
                                    <span class="badge bg-${content.upload_type === 'event' ? 'warning' : content.upload_type === 'photo' ? 'info' : 'success'} mb-2">
                                        <i class="fas fa-${content.upload_type === 'event' ? 'calendar-alt' : content.upload_type === 'photo' ? 'camera' : 'map-marker-alt'}"></i>
                                        ${content.upload_type.charAt(0).toUpperCase() + content.upload_type.slice(1)}
                                    </span>
                                    ${content.location ? `
                                        <div class="text-muted small">
                                            <i class="fas fa-map-pin me-1"></i> ${content.location}
                                        </div>
                                    ` : ''}
                                </div>
                                
                                <h6>Description</h6>
                                <p class="text-muted">${content.description}</p>
                                
                                <hr>
                                
                                <div class="guide-info d-flex align-items-center">
                                    <i class="fas fa-user-circle fa-3x text-primary me-3"></i>
                                    <div>
                                        <h6 class="mb-1">${content.guide_name}</h6>
                                        <small class="text-muted">Professional Local Guide</small>
                                        <div class="text-muted small">
                                            <i class="fas fa-calendar me-1"></i>
                                            Shared on ${new Date(content.upload_date).toLocaleDateString()}
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                `;
                
                const modalBody = document.getElementById('contentModalBody');
                if (modalBody) {
                    modalBody.innerHTML = modalContent;
                }
                
                // Update contact button
                const contactBtn = document.getElementById('contactGuideBtn');
                if (contactBtn) {
                    contactBtn.onclick = () => contactGuide(content.guide_username);
                }
                
                // Show modal
                const modalElement = document.getElementById('contentModal');
                if (modalElement) {
                    const modal = new bootstrap.Modal(modalElement);
                    modal.show();
                }
            } else {
                showToast('Failed to load content details', 'error');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showToast('Error loading content', 'error');
        });
}

// Contact guide function
function contactGuide(guideUsername) {
    // Check if user is logged in (assuming session info is available)
    if (typeof session === 'undefined' || !session || !session.username) {
        showToast('Please login to contact guides', 'warning');
        // Redirect to login page
        window.location.href = '/login/tourist';
        return;
    }
    
    if (session.user_type === 'tourist') {
        // Redirect to tourist dashboard to find and book the guide
        window.location.href = '/tourist_dashboard';
    } else {
        showToast('Only tourists can book guides', 'info');
    }
}

// Initialize page animations
function initPageAnimations() {
    // Animate elements on scroll
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver(function(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('fade-in-up');
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);

    // Observe elements that should animate
    const animateElements = document.querySelectorAll('.feature-card, .destination-card, .card');
    animateElements.forEach(el => {
        observer.observe(el);
    });
}

// Initialize animations when page loads
document.addEventListener('DOMContentLoaded', initPageAnimations);

// Error handling for images
document.addEventListener('error', function(e) {
    if (e.target.tagName === 'IMG') {
        e.target.src = 'data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" width="200" height="200" viewBox="0 0 200 200"><rect width="200" height="200" fill="%23f8f9fa"/><text x="100" y="100" text-anchor="middle" dominant-baseline="central" fill="%236c757d" font-family="Arial" font-size="14">Image not found</text></svg>';
        e.target.alt = 'Image not available';
    }
}, true);

// Enhanced map features
document.addEventListener('DOMContentLoaded', function() {
    // Add loading effect to map
    const mapIframe = document.querySelector('.map-container iframe');
    if (mapIframe) {
        mapIframe.addEventListener('load', function() {
            this.classList.remove('map-loading');
        });
    }

    // Add click tracking for map controls
    document.querySelectorAll('.map-controls .btn').forEach(button => {
        button.addEventListener('click', function() {
            const action = this.textContent.includes('Full Map') ? 'View Full Map' : 'Get Directions';
            console.log(`Map Action: ${action}`);
            // You can add analytics tracking here
        });
    });
    
    // Initialize cost calculation if on booking page
    const daysSelect = document.querySelector('select[name="days_to_stay"]');
    const groupSizeSelect = document.querySelector('select[name="group_size"]');
    
    if (daysSelect) {
        daysSelect.addEventListener('change', calculateTotal);
        calculateTotal(); // Initial calculation
    }
    
    if (groupSizeSelect) {
        groupSizeSelect.addEventListener('change', calculateTotal);
    }
});

// Smooth scroll to map function
function scrollToMap() {
    const mapContainer = document.querySelector('.map-container');
    if (mapContainer) {
        mapContainer.scrollIntoView({
            behavior: 'smooth',
            block: 'center'
        });
    }
}

// Export functions for global use
window.showLoginForm = showLoginForm;
window.showRegisterForm = showRegisterForm;
window.selectGuide = selectGuide;
window.bookGuide = bookGuide;
window.scrollToAbout = scrollToAbout;
window.showToast = showToast;
window.filterGuidesByDistrict = filterGuidesByDistrict;
window.calculateTotal = calculateTotal;
window.updateBookingStatus = updateBookingStatus;
window.viewContent = viewContent;
window.contactGuide = contactGuide;
window.scrollToMap = scrollToMap;
