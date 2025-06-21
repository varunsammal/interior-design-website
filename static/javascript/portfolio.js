document.addEventListener('DOMContentLoaded', function() {
    // Initialize all components
    initializeScrollProgress();
    initializeBackToTop();
    initializeFilters();
    initializeImageComparisons();
    initializeAnimations();
    initializeRoomSelect();
    initializeSmoothScrolling();

    // Filter functionality
    function initializeFilters() {
        const filterButtons = document.querySelectorAll('.filter-btn');
        const portfolioItems = document.querySelectorAll('.portfolio-item');
        const loadingState = document.getElementById('loadingState');
        const portfolioGrid = document.getElementById('portfolioGrid');

        filterButtons.forEach(button => {
            button.addEventListener('click', () => {
                // Show loading state
                if (loadingState) {
                    loadingState.style.display = 'flex';
                    portfolioGrid.style.opacity = '0.5';
                }

                // Remove active class from all buttons
                filterButtons.forEach(btn => btn.classList.remove('active'));
                // Add active class to clicked button
                button.classList.add('active');

                const filter = button.getAttribute('data-filter');

                // Simulate loading delay for better UX
                setTimeout(() => {
                    // Filter portfolio items
                    portfolioItems.forEach(item => {
                        if (filter === 'all' || item.getAttribute('data-category') === filter) {
                            item.style.display = 'block';
                            item.style.animation = 'fadeIn 0.6s ease-in-out';
                        } else {
                            item.style.display = 'none';
                        }
                    });

                    // Hide loading state
                    if (loadingState) {
                        loadingState.style.display = 'none';
                        portfolioGrid.style.opacity = '1';
                    }

                    // Scroll to portfolio grid
                    portfolioGrid.scrollIntoView({ 
                        behavior: 'smooth', 
                        block: 'start' 
                    });
                }, 300);
            });
        });
    }

    // Image comparison functionality
    function initializeImageComparisons() {
        const imageComparisons = document.querySelectorAll('.image-comparison');

        imageComparisons.forEach(comparison => {
            const beforeImage = comparison.querySelector('.before');
            const afterImage = comparison.querySelector('.after');

            if (beforeImage && afterImage) {
                // Set initial state
                beforeImage.style.opacity = '0';

                comparison.addEventListener('mouseenter', () => {
                    beforeImage.style.opacity = '1';
                    beforeImage.style.transition = 'opacity 0.4s ease';
                });

                comparison.addEventListener('mouseleave', () => {
                    beforeImage.style.opacity = '0';
                    beforeImage.style.transition = 'opacity 0.4s ease';
                });

                // Add click functionality for mobile
                comparison.addEventListener('click', () => {
                    if (window.innerWidth <= 768) {
                        if (beforeImage.style.opacity === '1') {
                            beforeImage.style.opacity = '0';
                        } else {
                            beforeImage.style.opacity = '1';
                        }
                    }
                });
            }
        });
    }

    // Room select dropdown functionality
    function initializeRoomSelect() {
        const roomSelect = document.querySelector('.room-select');
        if (roomSelect) {
            roomSelect.addEventListener('change', function() {
                const selectedRoom = this.value;
                
                if (selectedRoom) {
                    // Find and click the corresponding filter button
                    const filterButton = document.querySelector(`[data-filter="${selectedRoom}"]`);
                    if (filterButton) {
                        filterButton.click();
                    }
                } else {
                    // Show all projects
                    const allButton = document.querySelector('[data-filter="all"]');
                    if (allButton) {
                        allButton.click();
                    }
                }
            });
        }
    }

    // Scroll progress indicator
    function initializeScrollProgress() {
        const scrollProgress = document.getElementById('scrollProgress');
        
        if (scrollProgress) {
            window.addEventListener('scroll', () => {
                const scrollTop = window.pageYOffset;
                const docHeight = document.body.offsetHeight - window.innerHeight;
                const scrollPercent = (scrollTop / docHeight) * 100;
                
                scrollProgress.style.width = scrollPercent + '%';
            });
        }
    }

    // Back to top button
    function initializeBackToTop() {
        const backToTop = document.getElementById('backToTop');
        
        if (backToTop) {
            window.addEventListener('scroll', () => {
                if (window.pageYOffset > 300) {
                    backToTop.classList.add('visible');
                } else {
                    backToTop.classList.remove('visible');
                }
            });

            backToTop.addEventListener('click', () => {
                window.scrollTo({
                    top: 0,
                    behavior: 'smooth'
                });
            });
        }
    }

    // Smooth scrolling for anchor links
    function initializeSmoothScrolling() {
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', function(e) {
                const targetId = this.getAttribute('href');
                if (targetId === '#') return;
                
                const targetElement = document.querySelector(targetId);
                if (targetElement) {
                    e.preventDefault();
                    targetElement.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }
            });
        });
    }

    // Enhanced animations
    function initializeAnimations() {
        const observerOptions = {
            threshold: 0.1,
            rootMargin: '0px 0px -50px 0px'
        };

        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('animate');
                    entry.target.style.opacity = '1';
                    entry.target.style.transform = 'translateY(0)';
                }
            });
        }, observerOptions);

        // Observe all portfolio items
        const portfolioItems = document.querySelectorAll('.portfolio-item');
        portfolioItems.forEach(item => {
            item.style.opacity = '0';
            item.style.transform = 'translateY(30px)';
            item.style.transition = 'opacity 0.8s ease, transform 0.8s ease';
            observer.observe(item);
        });

        // Add hover effects to portfolio items
        portfolioItems.forEach(item => {
            item.addEventListener('mouseenter', () => {
                item.style.transform = 'translateY(-10px)';
                item.style.boxShadow = '0 20px 50px rgba(0, 0, 0, 0.15)';
            });

            item.addEventListener('mouseleave', () => {
                item.style.transform = 'translateY(0)';
                item.style.boxShadow = '0 8px 30px rgba(0, 0, 0, 0.1)';
            });
        });

        // Add stagger animation to filter buttons
        const filterButtons = document.querySelectorAll('.filter-btn');
        filterButtons.forEach((button, index) => {
            button.style.opacity = '0';
            button.style.transform = 'translateY(20px)';
            button.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
            
            setTimeout(() => {
                button.style.opacity = '1';
                button.style.transform = 'translateY(0)';
            }, index * 100);
        });
    }
});

// Global function for room filtering (for the dropdown)
function filterProjects(roomType) {
    const filterButton = document.querySelector(`[data-filter="${roomType}"]`);
    if (filterButton) {
        filterButton.click();
    }
}

// Global function for viewing project details
function viewDetails(projectId) {
    // You can implement a modal or redirect to a detailed view page
    console.log('Viewing details for project:', projectId);
    
    // Create a simple modal for project details
    const modal = document.createElement('div');
    modal.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0, 0, 0, 0.8);
        display: flex;
        justify-content: center;
        align-items: center;
        z-index: 10000;
        opacity: 0;
        transition: opacity 0.3s ease;
    `;
    
    modal.innerHTML = `
        <div style="
            background: white;
            padding: 30px;
            border-radius: 20px;
            max-width: 500px;
            text-align: center;
            transform: scale(0.8);
            transition: transform 0.3s ease;
        ">
            <h3>Project Details</h3>
            <p>Detailed information for project ID: ${projectId}</p>
            <p>This feature can be expanded to show more detailed project information, additional images, specifications, and client testimonials.</p>
            <button onclick="this.parentElement.parentElement.remove()" style="
                background: #d4af87;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 25px;
                cursor: pointer;
                margin-top: 20px;
            ">Close</button>
        </div>
    `;
    
    document.body.appendChild(modal);
    
    // Animate in
    setTimeout(() => {
        modal.style.opacity = '1';
        modal.querySelector('div').style.transform = 'scale(1)';
    }, 10);
}

// Add enhanced CSS animations
const style = document.createElement('style');
style.textContent = `
    @keyframes fadeIn {
        from { 
            opacity: 0; 
            transform: translateY(30px); 
        }
        to { 
            opacity: 1; 
            transform: translateY(0); 
        }
    }
    
    @keyframes slideInFromLeft {
        from {
            opacity: 0;
            transform: translateX(-50px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }
    
    @keyframes slideInFromRight {
        from {
            opacity: 0;
            transform: translateX(50px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }
    
    .portfolio-item {
        transition: transform 0.4s ease, box-shadow 0.4s ease, opacity 0.8s ease;
    }
    
    .portfolio-item:nth-child(odd) {
        animation: slideInFromLeft 0.8s ease-out;
    }
    
    .portfolio-item:nth-child(even) {
        animation: slideInFromRight 0.8s ease-out;
    }
    
    .image-comparison {
        position: relative;
        overflow: hidden;
        border-radius: 20px 20px 0 0;
        cursor: pointer;
    }
    
    .image-comparison img {
        width: 100%;
        height: 100%;
        object-fit: cover;
        transition: all 0.4s ease;
    }
    
    .image-comparison .before {
        position: absolute;
        top: 0;
        left: 0;
        opacity: 0;
        z-index: 2;
    }
    
    .image-comparison .after {
        position: relative;
        z-index: 1;
    }
    
    .image-comparison:hover .before {
        opacity: 1;
    }
    
    .filter-btn {
        transition: all 0.4s ease;
    }
    
    .filter-btn:hover {
        transform: translateY(-3px) scale(1.05);
    }
    
    .portfolio-meta .testimonial {
        position: relative;
        overflow: hidden;
    }
    
    .portfolio-meta .testimonial::before {
        content: '"';
        position: absolute;
        top: -10px;
        left: -5px;
        font-size: 3rem;
        color: #d4af87;
        opacity: 0.3;
        font-family: serif;
    }
    
    /* Loading animation */
    .loading-spinner {
        animation: spin 1s linear infinite;
    }
    
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    
    /* Enhanced hover effects */
    .portfolio-item:hover .image-comparison img {
        transform: scale(1.05);
    }
    
    .portfolio-item:hover .portfolio-info h3 {
        color: #d4af87;
        transition: color 0.3s ease;
    }
    
    /* Mobile optimizations */
    @media (max-width: 768px) {
        .image-comparison {
            cursor: pointer;
        }
        
        .image-comparison::after {
            content: 'Tap to see Before/After';
            position: absolute;
            bottom: 10px;
            right: 10px;
            background: rgba(0, 0, 0, 0.8);
            color: white;
            padding: 5px 10px;
            border-radius: 15px;
            font-size: 0.7rem;
            z-index: 3;
        }
    }
`;
document.head.appendChild(style);

// Add keyboard navigation support
document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') {
        // Close any open modals
        const modals = document.querySelectorAll('[style*="position: fixed"]');
        modals.forEach(modal => modal.remove());
    }
});

// Add touch gesture support for mobile
let touchStartX = 0;
let touchEndX = 0;

document.addEventListener('touchstart', e => {
    touchStartX = e.changedTouches[0].screenX;
});

document.addEventListener('touchend', e => {
    touchEndX = e.changedTouches[0].screenX;
    handleSwipe();
});

function handleSwipe() {
    const swipeThreshold = 50;
    const difference = touchStartX - touchEndX;
    
    if (Math.abs(difference) > swipeThreshold) {
        // You can implement swipe navigation here
        console.log('Swipe detected:', difference > 0 ? 'left' : 'right');
    }
} 