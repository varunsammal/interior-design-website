document.addEventListener('DOMContentLoaded', function() {
    // Mobile Navigation Toggle
    const hamburger = document.querySelector('.hamburger');
    const navLinks = document.querySelector('.nav-links');

    hamburger.addEventListener('click', () => {
        hamburger.classList.toggle('active');
        navLinks.classList.toggle('active');
    });

    // Close mobile menu when clicking on a nav link
    document.querySelectorAll('.nav-links a').forEach(link => {
        link.addEventListener('click', () => {
            hamburger.classList.remove('active');
            navLinks.classList.remove('active');
        });
    });

    // Portfolio Thumbnails
    const thumbnails = document.querySelectorAll('.thumbnail');
    const portfolioImage = document.querySelector('.portfolio-image img');
    const portfolioTitle = document.querySelector('.portfolio-details h3');
    const portfolioChallenge = document.querySelector('.challenge p');
    const portfolioResult = document.querySelector('.result blockquote');
    const portfolioClient = document.querySelector('.client-name');

    // Sample portfolio data
    const portfolioData = [
        {
            image: 'https://cdn.decorilla.com/images/1200x740/e1f2922e-b95b-487e-b3ca-6d0fb1010ffa/Modern-Coastal-Living-Room-and-Bedroom-Online-and-AI-Interior-Design.jpg?cv=1',
            title: 'Modern Coastal Living Room and Bedroom Makeover',
            challenge: 'We would like a more minimal look with Feng Shui and natural elements that highlight our beautiful green view.',
            result: 'We got the relaxing dream home we always wanted. Wanda was fun to work with and paid attention to every single detail.',
            client: 'Kris'
        },
        {
            image: 'https://cdn.decorilla.com/images/1200x740/2d8bb3bd-f143-4d72-b9fb-f39b1b5a484e/Glam-Elegant-Home-Interior-Design-Rendering.jpg?cv=1',
            title: 'Glam & Elegant Home Interior Design',
            challenge: 'I want my space to feel luxurious and elegant without being too over the top.',
            result: 'The design exceeded my expectations! It\'s exactly the elegant look I was hoping for.',
            client: 'Jennifer'
        },
        {
            image: 'https://cdn.decorilla.com/images/1200x740/4b606d9a-94be-4e1e-b912-5e107b0ef3ed/Blue-White-Kitchen-Rustic-Home-Design-Rendering.jpg?cv=1',
            title: 'Blue & White Kitchen & Rustic Home Design',
            challenge: 'Our kitchen needs updating while maintaining a rustic charm that fits with the rest of our home.',
            result: 'The blue and white color scheme works perfectly with our rustic elements. We love cooking in our new kitchen!',
            client: 'Michael'
        },
        {
            image: 'https://cdn.decorilla.com/images/1200x740/fb9af78e-95bc-4eec-a185-ae1ade6894c6/Eclectic-Formal-Living-Room-Interior-Design-Rendering.jpg?cv=1',
            title: 'Eclectic Formal Living Room Interior Design',
            challenge: 'We want a formal living room that still feels inviting and showcases our eclectic taste.',
            result: 'Our designer created the perfect balance between formal and comfortable. It\'s now our favorite room!',
            client: 'Sarah'
        },
        {
            image: 'https://cdn.decorilla.com/images/1200x740/a6e50faf-b4b4-4636-ac9c-7336f3f74175/SpaInspired-Master-Bathroom-Design-Rendering.jpg?cv=1',
            title: 'Spa-Inspired Master Bathroom Design',
            challenge: 'We want our bathroom to feel like a luxury spa retreat within our own home.',
            result: 'Every morning feels like a spa day now. The design is calming, luxurious, and exactly what we wanted.',
            client: 'David'
        }
    ];

    // Set up thumbnail click events
    thumbnails.forEach((thumbnail, index) => {
        thumbnail.addEventListener('click', () => {
            // Update active thumbnail
            thumbnails.forEach(t => t.classList.remove('active'));
            thumbnail.classList.add('active');
            
            // Update portfolio content
            if (portfolioData[index]) {
                portfolioImage.src = portfolioData[index].image;
                portfolioTitle.textContent = portfolioData[index].title;
                portfolioChallenge.textContent = portfolioData[index].challenge;
                portfolioResult.textContent = portfolioData[index].result;
                portfolioClient.textContent = '- ' + portfolioData[index].client;
            }
        });
    });

    // Smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();
            
            const targetId = this.getAttribute('href');
            if (targetId === '#') return;
            
            const targetElement = document.querySelector(targetId);
            if (targetElement) {
                targetElement.scrollIntoView({
                    behavior: 'smooth'
                });
            }
        });
    });

    // Scroll animations
    const animateOnScroll = () => {
        const elements = document.querySelectorAll('.service-card, .testimonial-content, .portfolio-showcase, .gallery-item');
        
        elements.forEach(element => {
            const elementPosition = element.getBoundingClientRect().top;
            const screenPosition = window.innerHeight / 1.3;
            
            if (elementPosition < screenPosition) {
                element.style.opacity = '1';
                element.style.transform = 'translateY(0)';
            }
        });
    };

    // Set initial styles for animation
    document.querySelectorAll('.service-card, .testimonial-content, .portfolio-showcase, .gallery-item').forEach(element => {
        element.style.opacity = '0';
        element.style.transform = 'translateY(20px)';
        element.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
    });

    // Run animation on scroll
    window.addEventListener('scroll', animateOnScroll);
    
    // Run once on page load
    animateOnScroll();
});document.addEventListener('DOMContentLoaded', function() {
    // Mobile Navigation Toggle
    const hamburger = document.querySelector('.hamburger');
    const navLinks = document.querySelector('.nav-links');

    hamburger.addEventListener('click', () => {
        hamburger.classList.toggle('active');
        navLinks.classList.toggle('active');
    });

    // Close mobile menu when clicking on a nav link
    document.querySelectorAll('.nav-links a').forEach(link => {
        link.addEventListener('click', () => {
            hamburger.classList.remove('active');
            navLinks.classList.remove('active');
        });
    });

    // Portfolio Thumbnails
    const thumbnails = document.querySelectorAll('.thumbnail');
    const portfolioImage = document.querySelector('.portfolio-image img');
    const portfolioTitle = document.querySelector('.portfolio-details h3');
    const portfolioChallenge = document.querySelector('.challenge p');
    const portfolioResult = document.querySelector('.result blockquote');
    const portfolioClient = document.querySelector('.client-name');

    // Sample portfolio data
    const portfolioData = [
        {
            image: 'https://cdn.decorilla.com/images/1200x740/e1f2922e-b95b-487e-b3ca-6d0fb1010ffa/Modern-Coastal-Living-Room-and-Bedroom-Online-and-AI-Interior-Design.jpg?cv=1',
            title: 'Modern Coastal Living Room and Bedroom Makeover',
            challenge: 'We would like a more minimal look with Feng Shui and natural elements that highlight our beautiful green view.',
            result: 'We got the relaxing dream home we always wanted. Wanda was fun to work with and paid attention to every single detail.',
            client: 'Kris'
        },
        {
            image: 'https://cdn.decorilla.com/images/1200x740/2d8bb3bd-f143-4d72-b9fb-f39b1b5a484e/Glam-Elegant-Home-Interior-Design-Rendering.jpg?cv=1',
            title: 'Glam & Elegant Home Interior Design',
            challenge: 'I want my space to feel luxurious and elegant without being too over the top.',
            result: 'The design exceeded my expectations! It\'s exactly the elegant look I was hoping for.',
            client: 'Jennifer'
        },
        {
            image: 'https://cdn.decorilla.com/images/1200x740/4b606d9a-94be-4e1e-b912-5e107b0ef3ed/Blue-White-Kitchen-Rustic-Home-Design-Rendering.jpg?cv=1',
            title: 'Blue & White Kitchen & Rustic Home Design',
            challenge: 'Our kitchen needs updating while maintaining a rustic charm that fits with the rest of our home.',
            result: 'The blue and white color scheme works perfectly with our rustic elements. We love cooking in our new kitchen!',
            client: 'Michael'
        },
        {
            image: 'https://cdn.decorilla.com/images/1200x740/fb9af78e-95bc-4eec-a185-ae1ade6894c6/Eclectic-Formal-Living-Room-Interior-Design-Rendering.jpg?cv=1',
            title: 'Eclectic Formal Living Room Interior Design',
            challenge: 'We want a formal living room that still feels inviting and showcases our eclectic taste.',
            result: 'Our designer created the perfect balance between formal and comfortable. It\'s now our favorite room!',
            client: 'Sarah'
        },
        {
            image: 'https://cdn.decorilla.com/images/1200x740/a6e50faf-b4b4-4636-ac9c-7336f3f74175/SpaInspired-Master-Bathroom-Design-Rendering.jpg?cv=1',
            title: 'Spa-Inspired Master Bathroom Design',
            challenge: 'We want our bathroom to feel like a luxury spa retreat within our own home.',
            result: 'Every morning feels like a spa day now. The design is calming, luxurious, and exactly what we wanted.',
            client: 'David'
        }
    ];

    // Set up thumbnail click events
    thumbnails.forEach((thumbnail, index) => {
        thumbnail.addEventListener('click', () => {
            // Update active thumbnail
            thumbnails.forEach(t => t.classList.remove('active'));
            thumbnail.classList.add('active');
            
            // Update portfolio content
            if (portfolioData[index]) {
                portfolioImage.src = portfolioData[index].image;
                portfolioTitle.textContent = portfolioData[index].title;
                portfolioChallenge.textContent = portfolioData[index].challenge;
                portfolioResult.textContent = portfolioData[index].result;
                portfolioClient.textContent = '- ' + portfolioData[index].client;
            }
        });
    });

    // Smooth scrolling for anchor links
    ddocument.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function(e) {
        const targetId = this.getAttribute('href');

        // Only prevent if target exists on the page
        const targetElement = document.querySelector(targetId);
        if (targetElement) {
            e.preventDefault();
            targetElement.scrollIntoView({
                behavior: 'smooth'
            });
        }
    });
});

    // Scroll animations
    const animateOnScroll = () => {
        const elements = document.querySelectorAll('.service-card, .testimonial-content, .portfolio-showcase, .gallery-item');
        
        elements.forEach(element => {
            const elementPosition = element.getBoundingClientRect().top;
            const screenPosition = window.innerHeight / 1.3;
            
            if (elementPosition < screenPosition) {
                element.style.opacity = '1';
                element.style.transform = 'translateY(0)';
            }
        });
    };

    // Set initial styles for animation
    document.querySelectorAll('.service-card, .testimonial-content, .portfolio-showcase, .gallery-item').forEach(element => {
        element.style.opacity = '0';
        element.style.transform = 'translateY(20px)';
        element.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
    });

    // Run animation on scroll
    window.addEventListener('scroll', animateOnScroll);
    
    // Run once on page load
    animateOnScroll();
});