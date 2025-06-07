/**
 * CinemaTicket - Main JavaScript
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    const tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Initialize popovers
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    const popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
    
    // Auto close alerts after 5 seconds
    setTimeout(function() {
        const alerts = document.querySelectorAll('.alert');
        alerts.forEach(function(alert) {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        });
    }, 5000);
    
    // Smooth scroll to anchors
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            if (this.getAttribute('href') !== '#') {
                e.preventDefault();
                document.querySelector(this.getAttribute('href')).scrollIntoView({
                    behavior: 'smooth'
                });
            }
        });
    });
    
    // Add animation classes to elements when they come into view
    const animateOnScroll = function() {
        const elements = document.querySelectorAll('.animate-on-scroll');
        
        elements.forEach(element => {
            const elementPosition = element.getBoundingClientRect().top;
            const windowHeight = window.innerHeight;
            
            if (elementPosition < windowHeight - 50) {
                const animationClass = element.dataset.animation || 'fade-in';
                element.classList.add(animationClass);
            }
        });
    };
    
    // Run once on page load
    animateOnScroll();
    
    // Add scroll event listener
    window.addEventListener('scroll', animateOnScroll);
    
    // Mobile menu toggle
    const mobileMenuToggle = document.getElementById('mobile-menu-toggle');
    if (mobileMenuToggle) {
        mobileMenuToggle.addEventListener('click', function() {
            const mobileMenu = document.getElementById('mobile-menu');
            mobileMenu.classList.toggle('show');
        });
    }
    
    // Movie search functionality
    const searchForm = document.getElementById('movie-search-form');
    if (searchForm) {
        searchForm.addEventListener('submit', function(e) {
            const searchInput = document.getElementById('movie-search-input');
            if (!searchInput.value.trim()) {
                e.preventDefault();
            }
        });
    }
    
    // Date picker initialization
    const datePickers = document.querySelectorAll('.datepicker');
    if (datePickers.length > 0) {
        datePickers.forEach(picker => {
            // This is a placeholder - in a real app you'd use a library like flatpickr or bootstrap-datepicker
            picker.addEventListener('click', function() {
                console.log('Date picker clicked - would initialize date picker here');
            });
        });
    }
    
    // Handle back button functionality
    const backButtons = document.querySelectorAll('.btn-back');
    backButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            window.history.back();
        });
    });
    
    // Movie trailer modal functionality
    const trailerLinks = document.querySelectorAll('.trailer-link');
    trailerLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const trailerUrl = this.getAttribute('data-trailer-url');
            const trailerModal = document.getElementById('trailerModal');
            
            if (trailerModal && trailerUrl) {
                const videoFrame = trailerModal.querySelector('iframe');
                if (videoFrame) {
                    // Extract YouTube ID and set src
                    let youtubeId = '';
                    if (trailerUrl.includes('youtube.com/watch?v=')) {
                        youtubeId = trailerUrl.split('v=')[1].split('&')[0];
                    } else if (trailerUrl.includes('youtu.be/')) {
                        youtubeId = trailerUrl.split('youtu.be/')[1];
                    }
                    
                    if (youtubeId) {
                        videoFrame.src = `https://www.youtube.com/embed/${youtubeId}?autoplay=1`;
                        const modal = new bootstrap.Modal(trailerModal);
                        modal.show();
                        
                        // Clear iframe src when modal is closed
                        trailerModal.addEventListener('hidden.bs.modal', function() {
                            videoFrame.src = '';
                        });
                    }
                }
            }
        });
    });
    
    // Function to format currency (IDR)
    window.formatCurrency = function(amount) {
        return new Intl.NumberFormat('id-ID', { 
            style: 'currency', 
            currency: 'IDR',
            minimumFractionDigits: 0,
            maximumFractionDigits: 0
        }).format(amount);
    };
    
    // File input preview (for image uploads)
    const fileInputs = document.querySelectorAll('.custom-file-input');
    fileInputs.forEach(input => {
        input.addEventListener('change', function() {
            const fileName = this.files[0]?.name || 'No file chosen';
            const label = this.nextElementSibling;
            if (label) {
                label.textContent = fileName;
            }
            
            // Preview image if it's an image file
            const previewElement = document.getElementById(`${this.id}-preview`);
            if (previewElement && this.files[0]) {
                const file = this.files[0];
                if (file.type.match('image.*')) {
                    const reader = new FileReader();
                    reader.onload = function(e) {
                        previewElement.src = e.target.result;
                        previewElement.classList.remove('d-none');
                    };
                    reader.readAsDataURL(file);
                }
            }
        });
    });
});