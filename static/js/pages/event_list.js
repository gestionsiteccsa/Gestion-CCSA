/**
 * Gestionnaire de la page Event List
 * Gère le scroll horizontal de la timeline et l'accessibilité
 */

class EventListPage {
    constructor() {
        this.container = document.getElementById('timelineContainer');
        this.scrollLeft = document.getElementById('scrollLeft');
        this.scrollRight = document.getElementById('scrollRight');
        
        this.scrollAmount = 350;
        
        this.init();
    }
    
    init() {
        if (!this.container || !this.scrollLeft || !this.scrollRight) {
            return;
        }
        
        this.bindEvents();
        this.updateArrows();
    }
    
    bindEvents() {
        // Clic sur les flèches
        this.scrollLeft.addEventListener('click', () => this.scroll(-this.scrollAmount));
        this.scrollRight.addEventListener('click', () => this.scroll(this.scrollAmount));
        
        // Navigation au clavier
        this.container.addEventListener('keydown', (e) => this.handleKeydown(e));
        
        // Mise à jour des flèches au scroll
        this.container.addEventListener('scroll', () => this.updateArrows());
    }
    
    scroll(amount) {
        this.container.scrollBy({
            left: amount,
            behavior: 'smooth'
        });
    }
    
    handleKeydown(event) {
        if (event.key === 'ArrowLeft') {
            event.preventDefault();
            this.scroll(-this.scrollAmount);
        } else if (event.key === 'ArrowRight') {
            event.preventDefault();
            this.scroll(this.scrollAmount);
        }
    }
    
    updateArrows() {
        const canScrollLeft = this.container.scrollLeft > 0;
        const canScrollRight = this.container.scrollLeft < (this.container.scrollWidth - this.container.clientWidth);
        
        this.scrollLeft.style.opacity = canScrollLeft ? '1' : '0.3';
        this.scrollRight.style.opacity = canScrollRight ? '1' : '0.3';
    }
}

// Initialisation au chargement du DOM
document.addEventListener('DOMContentLoaded', () => {
    new EventListPage();
});
