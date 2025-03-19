// Intersection Observer for lazy loading
const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            const loadingDiv = entry.target;
            const imgUrl = loadingDiv.dataset.img;
            
            const img = new Image();
            img.src = imgUrl;
            img.alt = "Manga Cover";
            img.onload = () => {
                loadingDiv.parentNode.replaceChild(img, loadingDiv);
            };
            img.onerror = () => {
                loadingDiv.textContent = 'Failed to load image';
            };
            
            observer.unobserve(loadingDiv);
        }
    });
}, {
    rootMargin: '50px 0px',
    threshold: 0.1
});

// Observe all loading divs
document.querySelectorAll('.loading').forEach(div => observer.observe(div));

// Scroll to top button
const scrollTopBtn = document.getElementById('scroll-top');

window.onscroll = () => {
    if (document.body.scrollTop > 500 || document.documentElement.scrollTop > 500) {
        scrollTopBtn.style.display = 'block';
    } else {
        scrollTopBtn.style.display = 'none';
    }
};

scrollTopBtn.onclick = () => {
    window.scrollTo({
        top: 0,
        behavior: 'smooth'
    });
};