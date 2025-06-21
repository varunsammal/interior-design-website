// DOM Elements
const searchInput = document.getElementById('searchReviews');
const ratingFilter = document.getElementById('ratingFilter');
const sortFilter = document.getElementById('sortFilter');
const reviewsList = document.querySelector('.reviews-list');
const imageModal = document.getElementById('imageModal');
const modalImage = document.getElementById('modalImage');
const editReviewModal = document.getElementById('editReviewModal');
const editReviewForm = document.getElementById('editReviewForm');

// State
let currentReviews = [];
let filteredReviews = [];

// Initialize
document.addEventListener('DOMContentLoaded', function() {
    // Initialize all components
    initializeScrollProgress();
    initializeBackToTop();
    initializeSearchAndFilters();
    initializeReviewCards();
    initializeModals();
    initializeRatingBars();
    initializeAnimations();
    initializeHelpfulButtons();
    initializePagination();

    // Get all review cards
    currentReviews = Array.from(document.querySelectorAll('.review-card'));
    filteredReviews = [...currentReviews];

    // Add event listeners
    searchInput.addEventListener('input', handleSearch);
    ratingFilter.addEventListener('change', handleFilter);
    sortFilter.addEventListener('change', handleSort);

    // Add event listeners for helpful buttons
    document.querySelectorAll('.btn-helpful').forEach(btn => {
        btn.addEventListener('click', handleHelpful);
    });

    // Add event listeners for edit buttons
    document.querySelectorAll('.btn-edit').forEach(btn => {
        btn.addEventListener('click', handleEdit);
    });

    // Add event listeners for delete buttons
    document.querySelectorAll('.btn-delete').forEach(btn => {
        btn.addEventListener('click', handleDelete);
    });

    // Add event listener for edit review form
    editReviewForm.addEventListener('submit', handleEditSubmit);
});

// Search functionality
function handleSearch(e) {
    const searchTerm = e.target.value.toLowerCase();
    filterReviews(searchTerm, ratingFilter.value);
}

// Filter functionality
function handleFilter(e) {
    const rating = e.target.value;
    filterReviews(searchInput.value.toLowerCase(), rating);
}

// Sort functionality
function handleSort(e) {
    const sortBy = e.target.value;
    sortReviews(sortBy);
}

// Filter reviews based on search term and rating
function filterReviews(searchTerm, rating) {
    filteredReviews = currentReviews.filter(review => {
        const reviewText = review.querySelector('.review-content').textContent.toLowerCase();
        const reviewRating = review.dataset.rating;
        const matchesSearch = reviewText.includes(searchTerm);
        const matchesRating = !rating || reviewRating === rating;
        return matchesSearch && matchesRating;
    });

    sortReviews(sortFilter.value);
}

// Sort reviews based on selected option
function sortReviews(sortBy) {
    switch (sortBy) {
        case 'recent':
            filteredReviews.sort((a, b) => {
                const dateA = new Date(a.querySelector('.review-date').textContent);
                const dateB = new Date(b.querySelector('.review-date').textContent);
                return dateB - dateA;
            });
            break;
        case 'rating':
            filteredReviews.sort((a, b) => {
                return b.dataset.rating - a.dataset.rating;
            });
            break;
        case 'helpful':
            filteredReviews.sort((a, b) => {
                const helpfulA = parseInt(a.querySelector('.btn-helpful span').textContent.match(/\d+/)[0]);
                const helpfulB = parseInt(b.querySelector('.btn-helpful span').textContent.match(/\d+/)[0]);
                return helpfulB - helpfulA;
            });
            break;
    }

    updateReviewsList();
}

// Update the reviews list in the DOM
function updateReviewsList() {
    reviewsList.innerHTML = '';
    if (filteredReviews.length === 0) {
        reviewsList.innerHTML = `
            <div class="no-reviews">
                <i class="far fa-search"></i>
                <h2>No Reviews Found</h2>
                <p>Try adjusting your search or filters</p>
            </div>
        `;
    } else {
        filteredReviews.forEach(review => {
            reviewsList.appendChild(review.cloneNode(true));
        });
    }
}

// Handle helpful button click
async function handleHelpful(e) {
    const button = e.currentTarget;
    const reviewId = button.dataset.reviewId;
    const countSpan = button.querySelector('span');
    const currentCount = parseInt(countSpan.textContent.match(/\d+/)[0]);

    try {
        const response = await fetch(`/api/reviews/${reviewId}/helpful`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });

        if (response.ok) {
            countSpan.textContent = `Helpful (${currentCount + 1})`;
            button.disabled = true;
            button.style.opacity = '0.5';
        }
    } catch (error) {
        console.error('Error marking review as helpful:', error);
    }
}

// Handle edit button click
function handleEdit(e) {
    const reviewId = e.currentTarget.dataset.reviewId;
    const reviewCard = e.currentTarget.closest('.review-card');
    const rating = reviewCard.dataset.rating;
    const comment = reviewCard.querySelector('.review-content p').textContent;

    // Set form values
    document.getElementById('editReviewId').value = reviewId;
    document.querySelector(`input[name="rating"][value="${rating}"]`).checked = true;
    document.getElementById('editComment').value = comment;

    // Show modal
    editReviewModal.style.display = 'flex';
}

// Handle edit form submission
async function handleEditSubmit(e) {
    e.preventDefault();
    const reviewId = document.getElementById('editReviewId').value;
    const rating = document.querySelector('input[name="rating"]:checked').value;
    const comment = document.getElementById('editComment').value;

    try {
        const response = await fetch(`/api/reviews/${reviewId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ rating, comment })
        });

        if (response.ok) {
            // Update the review card
            const reviewCard = document.querySelector(`.review-card[data-review-id="${reviewId}"]`);
            reviewCard.dataset.rating = rating;
            reviewCard.querySelector('.review-content p').textContent = comment;
            reviewCard.querySelector('.review-rating').innerHTML = generateStars(rating);

            // Close modal
            closeEditModal();
        }
    } catch (error) {
        console.error('Error updating review:', error);
    }
}

// Handle delete button click
async function handleDelete(e) {
    if (!confirm('Are you sure you want to delete this review?')) {
        return;
    }

    const reviewId = e.currentTarget.dataset.reviewId;
    try {
        const response = await fetch(`/api/reviews/${reviewId}`, {
            method: 'DELETE'
        });

        if (response.ok) {
            const reviewCard = e.currentTarget.closest('.review-card');
            reviewCard.remove();
            currentReviews = currentReviews.filter(review => review.dataset.reviewId !== reviewId);
            filterReviews(searchInput.value.toLowerCase(), ratingFilter.value);
        }
    } catch (error) {
        console.error('Error deleting review:', error);
    }
}

// Image modal functions
function openImageModal(src) {
    modalImage.src = src;
    imageModal.style.display = 'flex';
}

function closeImageModal() {
    imageModal.style.display = 'none';
}

function closeEditModal() {
    editReviewModal.style.display = 'none';
}

// Helper function to generate star HTML
function generateStars(rating) {
    let stars = '';
    for (let i = 0; i < 5; i++) {
        stars += `<i class="${i < rating ? 'fas' : 'far'} fa-star"></i>`;
    }
    return stars;
}

// Close modals when clicking outside
window.addEventListener('click', (e) => {
    if (e.target === imageModal) {
        closeImageModal();
    }
    if (e.target === editReviewModal) {
        closeEditModal();
    }
});

// Handle keyboard events
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
        closeImageModal();
        closeEditModal();
    }
});

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

// Search and filter functionality
function initializeSearchAndFilters() {
    const searchInput = document.getElementById('searchReviews');
    const ratingFilter = document.getElementById('ratingFilter');
    const sortFilter = document.getElementById('sortFilter');
    const reviewCards = document.querySelectorAll('.review-card');
    const loadingState = document.getElementById('loadingState');
    const reviewsList = document.getElementById('reviewsList');

    function filterReviews() {
        // Show loading state
        if (loadingState) {
            loadingState.style.display = 'flex';
            reviewsList.style.opacity = '0.5';
        }

        const searchTerm = searchInput.value.toLowerCase();
        const selectedRating = ratingFilter.value;
        const selectedSort = sortFilter.value;

        // Simulate loading delay for better UX
        setTimeout(() => {
            let visibleCount = 0;

            reviewCards.forEach(card => {
                const reviewText = card.querySelector('.review-content p').textContent.toLowerCase();
                const reviewerName = card.querySelector('.reviewer-details h3').textContent.toLowerCase();
                const cardRating = card.getAttribute('data-rating');
                
                let shouldShow = true;

                // Search filter
                if (searchTerm && !reviewText.includes(searchTerm) && !reviewerName.includes(searchTerm)) {
                    shouldShow = false;
                }

                // Rating filter
                if (selectedRating && cardRating !== selectedRating) {
                    shouldShow = false;
                }

                if (shouldShow) {
                    card.style.display = 'block';
                    card.style.animation = 'fadeIn 0.6s ease-in-out';
                    visibleCount++;
                } else {
                    card.style.display = 'none';
                }
            });

            // Sort reviews
            if (selectedSort) {
                const visibleCards = Array.from(reviewCards).filter(card => card.style.display !== 'none');
                
                visibleCards.sort((a, b) => {
                    switch (selectedSort) {
                        case 'rating':
                            return parseInt(b.getAttribute('data-rating')) - parseInt(a.getAttribute('data-rating'));
                        case 'recent':
                            // Assuming newer reviews come first in the DOM
                            return 0;
                        case 'helpful':
                            const aHelpful = parseInt(a.querySelector('.btn-helpful span').textContent.match(/\d+/)[0]);
                            const bHelpful = parseInt(b.querySelector('.btn-helpful span').textContent.match(/\d+/)[0]);
                            return bHelpful - aHelpful;
                        default:
                            return 0;
                    }
                });

                // Reorder in DOM
                const container = reviewsList;
                visibleCards.forEach(card => {
                    container.appendChild(card);
                });
            }

            // Hide loading state
            if (loadingState) {
                loadingState.style.display = 'none';
                reviewsList.style.opacity = '1';
            }

            // Show no results message if needed
            if (visibleCount === 0) {
                showNoResultsMessage();
            } else {
                hideNoResultsMessage();
            }
        }, 300);
    }

    // Event listeners
    if (searchInput) {
        searchInput.addEventListener('input', filterReviews);
    }
    if (ratingFilter) {
        ratingFilter.addEventListener('change', filterReviews);
    }
    if (sortFilter) {
        sortFilter.addEventListener('change', filterReviews);
    }
}

// Review cards functionality
function initializeReviewCards() {
    const reviewCards = document.querySelectorAll('.review-card');

    reviewCards.forEach(card => {
        // Add hover effects
        card.addEventListener('mouseenter', () => {
            card.style.transform = 'translateY(-8px)';
            card.style.boxShadow = '0 20px 50px rgba(0, 0, 0, 0.15)';
        });

        card.addEventListener('mouseleave', () => {
            card.style.transform = 'translateY(0)';
            card.style.boxShadow = '0 8px 30px rgba(0, 0, 0, 0.1)';
        });

        // Add click to expand functionality
        const reviewContent = card.querySelector('.review-content p');
        if (reviewContent && reviewContent.textContent.length > 200) {
            const originalText = reviewContent.textContent;
            const shortText = originalText.substring(0, 200) + '...';
            reviewContent.textContent = shortText;
            
            const expandButton = document.createElement('button');
            expandButton.textContent = 'Read More';
            expandButton.className = 'btn-expand';
            expandButton.style.cssText = `
                background: none;
                border: none;
                color: #d4af87;
                cursor: pointer;
                font-weight: 600;
                margin-top: 0.5rem;
                transition: all 0.3s ease;
            `;
            
            expandButton.addEventListener('click', (e) => {
                e.preventDefault();
                if (reviewContent.textContent === shortText) {
                    reviewContent.textContent = originalText;
                    expandButton.textContent = 'Read Less';
                } else {
                    reviewContent.textContent = shortText;
                    expandButton.textContent = 'Read More';
                }
            });
            
            card.querySelector('.review-content').appendChild(expandButton);
        }
    });
}

// Modal functionality
function initializeModals() {
    // Image modal
    window.openImageModal = function(imageSrc) {
        const modal = document.getElementById('imageModal');
        const modalImage = document.getElementById('modalImage');
        
        if (modal && modalImage) {
            modalImage.src = imageSrc;
            modal.style.display = 'flex';
            document.body.style.overflow = 'hidden';
        }
    };

    window.closeImageModal = function() {
        const modal = document.getElementById('imageModal');
        if (modal) {
            modal.style.display = 'none';
            document.body.style.overflow = 'auto';
        }
    };

    // Edit modal
    window.closeEditModal = function() {
        const modal = document.getElementById('editReviewModal');
        if (modal) {
            modal.style.display = 'none';
            document.body.style.overflow = 'auto';
        }
    };

    // Close modals on outside click
    document.addEventListener('click', (e) => {
        const modals = document.querySelectorAll('.modal');
        modals.forEach(modal => {
            if (e.target === modal) {
                modal.style.display = 'none';
                document.body.style.overflow = 'auto';
            }
        });
    });

    // Close modals on ESC key
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') {
            const modals = document.querySelectorAll('.modal');
            modals.forEach(modal => {
                if (modal.style.display === 'flex') {
                    modal.style.display = 'none';
                    document.body.style.overflow = 'auto';
                }
            });
        }
    });
}

// Rating bars animation
function initializeRatingBars() {
    const bars = document.querySelectorAll('.bar');
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const width = entry.target.getAttribute('data-width');
                entry.target.style.width = width + '%';
            }
        });
    }, { threshold: 0.5 });

    bars.forEach(bar => {
        observer.observe(bar);
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

    // Observe review cards
    const reviewCards = document.querySelectorAll('.review-card');
    reviewCards.forEach((card, index) => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(30px)';
        card.style.transition = 'opacity 0.8s ease, transform 0.8s ease';
        
        // Stagger animation
        setTimeout(() => {
            observer.observe(card);
        }, index * 100);
    });

    // Observe other elements
    const elementsToAnimate = document.querySelectorAll('.reviews-filters, .reviews-stats, .pagination');
    elementsToAnimate.forEach(element => {
        observer.observe(element);
    });
}

// Helpful button functionality
function initializeHelpfulButtons() {
    const helpfulButtons = document.querySelectorAll('.btn-helpful');

    helpfulButtons.forEach(button => {
        button.addEventListener('click', function() {
            const reviewId = this.getAttribute('data-review-id');
            const countSpan = this.querySelector('span');
            const icon = this.querySelector('i');
            
            // Update count
            const currentCount = parseInt(countSpan.textContent.match(/\d+/)[0]);
            const newCount = currentCount + 1;
            countSpan.textContent = `Helpful (${newCount})`;
            
            // Change icon and disable button
            icon.className = 'fas fa-thumbs-up';
            this.style.background = 'linear-gradient(135deg, #d4af87 0%, #c49a6b 100%)';
            this.style.color = 'white';
            this.style.borderColor = '#d4af87';
            this.disabled = true;
            
            // Add animation
            this.style.transform = 'scale(1.1)';
            setTimeout(() => {
                this.style.transform = 'scale(1)';
            }, 200);

            // Here you would typically send the data to the server
            console.log(`Marked review ${reviewId} as helpful`);
        });
    });
}

// Pagination functionality
function initializePagination() {
    const pageNumbers = document.querySelectorAll('.page-number');
    const prevButton = document.querySelector('.btn-prev');
    const nextButton = document.querySelector('.btn-next');

    pageNumbers.forEach(button => {
        button.addEventListener('click', function() {
            const page = this.getAttribute('data-page');
            
            // Remove active class from all buttons
            pageNumbers.forEach(btn => btn.classList.remove('active'));
            
            // Add active class to clicked button
            this.classList.add('active');
            
            // Here you would typically navigate to the page
            console.log(`Navigating to page ${page}`);
            
            // For demo purposes, scroll to top
            window.scrollTo({
                top: 0,
                behavior: 'smooth'
            });
        });
    });

    if (prevButton) {
        prevButton.addEventListener('click', function() {
            if (!this.disabled) {
                console.log('Navigate to previous page');
                window.scrollTo({
                    top: 0,
                    behavior: 'smooth'
                });
            }
        });
    }

    if (nextButton) {
        nextButton.addEventListener('click', function() {
            if (!this.disabled) {
                console.log('Navigate to next page');
                window.scrollTo({
                    top: 0,
                    behavior: 'smooth'
                });
            }
        });
    }
}

// Utility functions
function showNoResultsMessage() {
    const existingMessage = document.querySelector('.no-results-message');
    if (!existingMessage) {
        const message = document.createElement('div');
        message.className = 'no-results-message';
        message.innerHTML = `
            <div style="
                text-align: center;
                padding: 3rem 2rem;
                background: white;
                border-radius: 20px;
                box-shadow: 0 8px 30px rgba(0, 0, 0, 0.1);
                margin: 2rem 0;
            ">
                <i class="fas fa-search" style="
                    font-size: 3rem;
                    color: #d4af87;
                    margin-bottom: 1rem;
                    opacity: 0.7;
                "></i>
                <h3 style="
                    font-size: 1.5rem;
                    color: #2c2621;
                    margin-bottom: 0.5rem;
                    font-weight: 700;
                ">No Reviews Found</h3>
                <p style="
                    color: #6b6560;
                    margin: 0;
                    font-weight: 400;
                ">Try adjusting your search criteria or filters</p>
            </div>
        `;
        document.getElementById('reviewsList').appendChild(message);
    }
}

function hideNoResultsMessage() {
    const message = document.querySelector('.no-results-message');
    if (message) {
        message.remove();
    }
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
    
    .review-card {
        transition: transform 0.4s ease, box-shadow 0.4s ease, opacity 0.8s ease;
    }
    
    .review-card:nth-child(odd) {
        animation: slideInFromLeft 0.8s ease-out;
    }
    
    .review-card:nth-child(even) {
        animation: slideInFromRight 0.8s ease-out;
    }
    
    .btn-expand:hover {
        color: #c49a6b;
        transform: translateY(-1px);
    }
    
    .rating-stars i {
        transition: all 0.3s ease;
    }
    
    .review-card:hover .rating-stars i {
        transform: scale(1.1);
        filter: drop-shadow(0 2px 4px rgba(255, 215, 0, 0.4));
    }
    
    .design-thumbnail {
        transition: all 0.3s ease;
    }
    
    .design-thumbnail:hover {
        transform: scale(1.05);
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.2);
    }
    
    /* Enhanced hover effects */
    .review-card:hover .reviewer-avatar {
        transform: scale(1.1);
        box-shadow: 0 6px 20px rgba(212, 175, 135, 0.4);
    }
    
    .review-card:hover .reviewer-details h3 {
        color: #d4af87;
        transition: color 0.3s ease;
    }
    
    /* Loading animation */
    .loading-spinner {
        animation: spin 1s linear infinite;
    }
    
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    
    /* Mobile optimizations */
    @media (max-width: 768px) {
        .review-card {
            margin-bottom: 1.5rem;
        }
        
        .btn-expand {
            font-size: 0.9rem;
        }
    }
`;
document.head.appendChild(style);

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