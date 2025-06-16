document.addEventListener('DOMContentLoaded', function() {
    const dropZone = document.getElementById('dropZone');
    const fileInput = document.getElementById('design_image');
    const previewContainer = document.getElementById('previewContainer');
    const imagePreview = document.getElementById('imagePreview');
    const removePreview = document.getElementById('removePreview');
    const uploadForm = document.getElementById('uploadForm');

    // Drag and drop events
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, preventDefaults, false);
    });

    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    ['dragenter', 'dragover'].forEach(eventName => {
        dropZone.addEventListener(eventName, highlight, false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, unhighlight, false);
    });

    function highlight(e) {
        dropZone.classList.add('dragover');
    }

    function unhighlight(e) {
        dropZone.classList.remove('dragover');
    }

    dropZone.addEventListener('drop', handleDrop, false);

    function handleDrop(e) {
        const dt = e.dataTransfer;
        const files = dt.files;
        handleFiles(files);
    }

    fileInput.addEventListener('change', function() {
        handleFiles(this.files);
    });

    function handleFiles(files) {
        if (files.length > 0) {
            const file = files[0];
            if (file.type.startsWith('image/')) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    imagePreview.src = e.target.result;
                    previewContainer.style.display = 'block';
                }
                reader.readAsDataURL(file);
            }
        }
    }

    removePreview.addEventListener('click', function() {
        imagePreview.src = '';
        previewContainer.style.display = 'none';
        fileInput.value = '';
    });

    // Form submission
    uploadForm.addEventListener('submit', function(e) {
        if (!fileInput.files.length) {
            e.preventDefault();
            alert('Please select an image to upload');
        }
    });

    // Add double-click handler to all design images
    const designImages = document.querySelectorAll('.design-image');
    designImages.forEach(imageDiv => {
        imageDiv.addEventListener('dblclick', function() {
            const img = this.querySelector('img');
            if (img) {
                window.open(img.src, '_blank');
            }
        });
    });
});

function confirmDelete(designId) {
    const modal = document.getElementById('deleteModal');
    const deleteDesignId = document.getElementById('deleteDesignId');
    deleteDesignId.value = designId;
    modal.style.display = 'flex';
}

function closeModal() {
    const modal = document.getElementById('deleteModal');
    modal.style.display = 'none';
}

function viewDesign(imageUrl) {
    const modal = document.getElementById('imageModal');
    const modalImage = document.getElementById('modalImage');
    modalImage.src = imageUrl;
    modal.style.display = 'flex';
    
    // Reset zoom level
    modalImage.style.transform = 'scale(1)';
    
    // Add zoom functionality
    let isZoomed = false;
    modalImage.addEventListener('click', function() {
        isZoomed = !isZoomed;
        this.style.transform = isZoomed ? 'scale(1.5)' : 'scale(1)';
        this.style.cursor = isZoomed ? 'zoom-out' : 'zoom-in';
    });

    // Add double-click to open in new tab
    modalImage.addEventListener('dblclick', function() {
        window.open(imageUrl, '_blank');
    });
}

function closeImageModal() {
    const modal = document.getElementById('imageModal');
    const modalImage = document.getElementById('modalImage');
    modal.style.display = 'none';
    
    // Reset zoom level when closing
    modalImage.style.transform = 'scale(1)';
    modalImage.style.cursor = 'zoom-in';
}

// Close modals when clicking outside
window.onclick = function(event) {
    const deleteModal = document.getElementById('deleteModal');
    const imageModal = document.getElementById('imageModal');
    const modalImage = document.getElementById('modalImage');
    
    if (event.target === deleteModal) {
        closeModal();
    }
    if (event.target === imageModal) {
        closeImageModal();
    }
}

// Close modals with escape key
document.addEventListener('keydown', function(event) {
    if (event.key === 'Escape') {
        closeModal();
        closeImageModal();
    }
}); 