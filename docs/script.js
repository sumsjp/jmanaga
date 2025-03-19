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

document.addEventListener('DOMContentLoaded', function() {
    const mainContent = document.getElementById('main-content');
    const genreContent = document.getElementById('genre-content');
    const genreDetail = document.getElementById('genre-detail');
    const backButton = document.getElementById('back-to-genres');
    const scrollTopButton = document.getElementById('scroll-top');

    // 返回按鈕處理
    backButton.addEventListener('click', function() {
        genreContent.style.display = 'none';
        mainContent.style.display = 'block';
        window.scrollTo(0, 0);
    });

    // 回到頂部按鈕處理
    scrollTopButton.addEventListener('click', function() {
        window.scrollTo({
            top: 0,
            behavior: 'smooth'
        });
    });

    // 顯示/隱藏回到頂部按鈕
    window.addEventListener('scroll', function() {
        if (window.pageYOffset > 100) {
            scrollTopButton.style.display = 'block';
        } else {
            scrollTopButton.style.display = 'none';
        }
    });
});
