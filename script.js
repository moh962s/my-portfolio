// 1. Lightbox functions (تكبير الصور)
function openLightbox(src) {
    const lightbox = document.getElementById('lightbox');
    const lightboxImg = document.getElementById('lightbox-img');
    lightboxImg.src = src;
    lightbox.classList.add('active');
    document.body.style.overflow = 'hidden'; // منع التمرير
}

function closeLightbox(event) {
    if (event) event.stopPropagation();
    const lightbox = document.getElementById('lightbox');
    lightbox.classList.remove('active');
    document.body.style.overflow = 'auto';
}

// 2. Change main image gallery function (تبديل الصورة الرئيسية)
function changeImage(projectId, imageIndex) {
    const mainImage = document.getElementById(`main-img-${projectId}`);
    const thumbnailsContainer = document.getElementById(`thumbnails-${projectId}`);
    const thumbnails = thumbnailsContainer.querySelectorAll('.thumbnail-img');

    if (imageIndex >= 0 && imageIndex < thumbnails.length) {
        const newSrc = thumbnails[imageIndex].src;

        mainImage.style.transform = 'scale(0.95)';
        mainImage.style.opacity = '0';
        setTimeout(() => {
            mainImage.src = newSrc;
            mainImage.style.transform = 'scale(1)';
            mainImage.style.opacity = '1';
        }, 200);

        thumbnails.forEach((thumb, index) => {
            thumb.classList.remove('active');
            if (index === imageIndex) { thumb.classList.add('active'); }
        });
    }
}

// 3. Dark Mode Logic (تبديل الوضع الداكن)
const themeToggle = document.getElementById('theme-toggle');
const body = document.body;
const icon = themeToggle.querySelector('i');

const currentTheme = localStorage.getItem('theme');
if (currentTheme === 'dark') {
    body.classList.add('dark-mode');
    icon.classList.replace('fa-moon', 'fa-sun');
} else if (currentTheme === 'light') {
    body.classList.remove('dark-mode');
    icon.classList.replace('fa-sun', 'fa-moon');
} else {
    if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
        body.classList.add('dark-mode');
        icon.classList.replace('fa-moon', 'fa-sun');
    }
}

themeToggle.addEventListener('click', () => {
    body.classList.toggle('dark-mode');
    if (body.classList.contains('dark-mode')) {
        icon.classList.replace('fa-moon', 'fa-sun');
        localStorage.setItem('theme', 'dark');
    } else {
        icon.classList.replace('fa-sun', 'fa-moon');
        localStorage.setItem('theme', 'light');
    }
});

// 4. Scroll Reveal (تأثيرات الظهور عند النزول للأسفل)
document.addEventListener("DOMContentLoaded", function () {
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('active');
            }
        });
    }, { threshold: 0.15 });

    const elements = document.querySelectorAll('.reveal');
    elements.forEach((el) => observer.observe(el));
});