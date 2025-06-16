// Create floating particles
function createParticles() {
    const particleCount = 20;
    for (let i = 0; i < particleCount; i++) {
        const particle = document.createElement('div');
        particle.classList.add('particle');
        
        // Random properties
        const size = Math.random() * 10 + 5;
        const posX = Math.random() * 100;
        const duration = Math.random() * 30 + 20;
        const delay = Math.random() * 15;
        
        particle.style.width = `${size}px`;
        particle.style.height = `${size}px`;
        particle.style.left = `${posX}%`;
        particle.style.animationDuration = `${duration}s`;
        particle.style.animationDelay = `${delay}s`;
        
        document.body.appendChild(particle);
    }
}

// All available interior design images
const allImages = [
    "https://images.unsplash.com/photo-1618221195710-dd6b41faaea6",
    "https://images.unsplash.com/photo-1616486338812-3dadae4b4ace",
    "https://images.unsplash.com/photo-1586023492125-27b2c045efd7",
    "https://images.unsplash.com/photo-1513694203232-719a280e022f",
    "https://images.unsplash.com/photo-1556911220-bff31c812dba",
    "https://images.unsplash.com/photo-1583847268964-b28dc8f51f92",
    "https://images.unsplash.com/photo-1618220179428-22790b461013",
    "https://images.unsplash.com/photo-1493809842364-78817add7ffb",
    "https://images.unsplash.com/photo-1513519245088-0e12902e5a38",
    "https://images.unsplash.com/photo-1507652313519-d4e9174996dd"
].map(img => img + "?ixlib=rb-1.2.1&auto=format&fit=crop&w=800&h=800");

let selectedImages = [];
let availableImages = [...allImages];
const totalSelections = 10;

// Initialize
createParticles();
initializeDots();
loadNewPair();

function initializeDots() {
    const dotsContainer = document.getElementById('dotsContainer');
    dotsContainer.innerHTML = '';
    
    for (let i = 0; i < totalSelections; i++) {
        const dot = document.createElement('div');
        dot.className = 'dot';
        dot.onclick = function() {
            if (i < selectedImages.length) {
                showSelectedImage(i);
            }
        };
        dotsContainer.appendChild(dot);
    }
}

function loadNewPair() {
    if (availableImages.length < 2) {
        availableImages = [...allImages]; // Reset if running low
    }
    
    // Get two random unique images
    const randomIndex1 = Math.floor(Math.random() * availableImages.length);
    let randomIndex2;
    do {
        randomIndex2 = Math.floor(Math.random() * availableImages.length);
    } while (randomIndex2 === randomIndex1);
    
    document.getElementById('leftImage').src = availableImages[randomIndex1];
    document.getElementById('rightImage').src = availableImages[randomIndex2];
}

function selectImage(imgNumber) {
    const selectedImg = imgNumber === 1 
        ? document.getElementById('leftImage').src 
        : document.getElementById('rightImage').src;
    
    selectedImages.push(selectedImg);
    updateDots();
    
    // Remove selected image from available images
    availableImages = availableImages.filter(img => img !== selectedImg);
    
    if (selectedImages.length < totalSelections) {
        loadNewPair();
    } else {
        // All selections completed
        completeSelection();
    }
}

function updateDots() {
    const dots = document.querySelectorAll('.dots-container .dot');
    
    selectedImages.forEach((img, index) => {
        dots[index].style.backgroundImage = `url('${img}')`;
        dots[index].classList.add('selected');
    });
}

function showSelectedImage(index) {
    // Show the selected image in left position
    document.getElementById('leftImage').src = selectedImages[index];
    
    // Find a different image for right position
    let rightImage;
    do {
        const randomIndex = Math.floor(Math.random() * selectedImages.length);
        rightImage = selectedImages[randomIndex];
    } while (rightImage === selectedImages[index] && selectedImages.length > 1);
    
    document.getElementById('rightImage').src = rightImage;
}

function skipAll() {
    // Fill all remaining dots with random selections
    while (selectedImages.length < totalSelections) {
        const randomIndex = Math.floor(Math.random() * allImages.length);
        selectedImages.push(allImages[randomIndex]);
    }
    
    updateDots();
    completeSelection();
}

function completeSelection() {
    document.getElementById('comparisonContainer').style.display = 'none';
    document.querySelector('p').textContent = '';
    document.querySelector('h2').textContent = 'Your Style Preferences';
    
    // Add completion message
    const message = document.createElement('div');
    message.className = 'completion-message';
    message.textContent = 'Thank you for your selections!';
    document.querySelector('.header-container').appendChild(message);
    
    // Center dots vertically
    document.querySelector('.dots-container').style.margin = '40px auto';
    
    // Make skip button disappear
    document.querySelector('.skip-btn').style.display = 'none';
} 