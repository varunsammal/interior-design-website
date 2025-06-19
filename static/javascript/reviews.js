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
document.addEventListener('DOMContentLoaded', () => {
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