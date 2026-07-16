// Auto-dismiss flash messages
document.addEventListener('DOMContentLoaded', () => {
    const flashes = document.querySelectorAll('.flash');
    flashes.forEach(f => {
        setTimeout(() => {
            f.style.opacity = '0';
            f.style.transition = 'opacity .5s ease';
            setTimeout(() => f.remove(), 500);
        }, 4000);
    });

    // Animate bar fills on load
    document.querySelectorAll('.bar-fill').forEach(bar => {
        const w = bar.style.width;
        bar.style.width = '0';
        setTimeout(() => { bar.style.width = w; }, 100);
    });
});
