document.addEventListener('DOMContentLoaded', function() {
    // Filter functionality
    const filterButtons = document.querySelectorAll('.filter-btn');
    const portfolioItems = document.querySelectorAll('.portfolio-item');

    filterButtons.forEach(button => {
        button.addEventListener('click', () => {
            // Remove active class from all buttons
            filterButtons.forEach(btn => btn.classList.remove('active'));
            // Add active class to clicked button
            button.classList.add('active');

            const filter = button.getAttribute('data-filter');

            // Filter portfolio items
            portfolioItems.forEach(item => {
                if (filter === 'all' || item.getAttribute('data-category') === filter) {
                    item.style.display = 'block';
                } else {
                    item.style.display = 'none';
                }
            });
        });
    });

    // Image comparison functionality
    const imageComparisons = document.querySelectorAll('.image-comparison');

    imageComparisons.forEach(comparison => {
        const beforeImage = comparison.querySelector('.before');
        const afterImage = comparison.querySelector('.after');

        comparison.addEventListener('mouseenter', () => {
            beforeImage.style.opacity = '1';
        });

        comparison.addEventListener('mouseleave', () => {
            beforeImage.style.opacity = '0';
        });
    });

    // Smooth scroll for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
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
});

function viewDetails(projectId) {
    // You can implement a modal or redirect to a detailed view page
    console.log('Viewing details for project:', projectId);
    // For now, we'll just show an alert
    alert('Project details will be shown here. Project ID: ' + projectId);
} 