document.addEventListener('DOMContentLoaded', () => {
// پیدا کردن منوها
const links = document.querySelectorAll('.glass-container a');
const container = document.querySelector('.glass-container');
// تبدیل هر لینک به یک "سیاره" معلق
links.forEach((link, index) => {
link.style.position = 'absolute';
link.style.display = 'inline-block';
link.style.background = 'rgba(255, 255, 255, 0.1)';
link.style.padding = '20px';
link.style.borderRadius = '50%';
link.style.boxShadow = '0 0 20px rgba(0, 255, 204, 0.5)';
link.style.transition = 'transform 0.3s';

// پخش کردن آن‌ها در فضا
const angle = (index / links.length) * Math.PI * 2;
const radius = 150;
link.style.left = `calc(50% + ${Math.cos(angle) * radius}px)`;
link.style.top = `calc(50% + ${Math.sin(angle) * radius}px)`;
link.style.transform = 'translate(-50%, -50%)';

// افکت شناور بودن
link.addEventListener('mouseenter', () => {
link.style.transform = 'translate(-50%, -50%) scale(1.2)';
});
link.addEventListener('mouseleave', () => {
link.style.transform = 'translate(-50%, -50%) scale(1)';
});
});

// چرخش کل صفحه با حرکت موس
document.addEventListener('mousemove', (e) => {
if (!container) return;
const xAxis = (window.innerWidth / 2 - e.pageX) / 25;
const yAxis = (window.innerHeight / 2 - e.pageY) / 25;
container.style.transform = `rotateY(${xAxis}deg) rotateX(${yAxis}deg)`;
});
});
