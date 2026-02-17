/**
 * Initialisation de FullCalendar pour le calendrier des événements
 * Utilise FullCalendar v6
 */

(function() {
    'use strict';

    /**
     * Initialise le calendrier
     */
    function initCalendar() {
        const calendarEl = document.getElementById('calendar');
        if (!calendarEl) return;

        // Récupérer les événements depuis la variable globale
        const events = window.calendarEvents || [];
        const initialDate = window.calendarInitialDate || new Date().toISOString().split('T')[0];

        const calendar = new FullCalendar.Calendar(calendarEl, {
            initialView: 'dayGridMonth',
            initialDate: initialDate,
            locale: 'fr',
            firstDay: 1, // Lundi
            headerToolbar: false, // On gère l'en-tête nous-mêmes
            events: events,
            eventClick: function(info) {
                if (info.event.url) {
                    window.location.href = info.event.url;
                }
            },
            eventMouseEnter: function(info) {
                info.el.style.cursor = 'pointer';
            },
            eventContent: function(arg) {
                return {
                    html: `
                        <div class="fc-event-title" style="font-size: 0.85em;">
                            ${arg.event.title}
                        </div>
                        <div class="fc-event-location" style="font-size: 0.75em; opacity: 0.8;">
                            ${arg.event.extendedProps.location || ''}
                        </div>
                    `
                };
            }
        });

        calendar.render();

        // Gérer la navigation avec les boutons personnalisés
        const prevBtn = document.querySelector('a[href*="prev_month"]');
        const nextBtn = document.querySelector('a[href*="next_month"]');

        if (prevBtn) {
            prevBtn.addEventListener('click', function(e) {
                e.preventDefault();
                calendar.prev();
                updateUrl(calendar.getDate());
            });
        }

        if (nextBtn) {
            nextBtn.addEventListener('click', function(e) {
                e.preventDefault();
                calendar.next();
                updateUrl(calendar.getDate());
            });
        }
    }

    /**
     * Met à jour l'URL sans recharger la page
     */
    function updateUrl(date) {
        const year = date.getFullYear();
        const month = date.getMonth() + 1;
        const newUrl = `/evenements/calendrier/${year}/${month}/`;
        
        // Mettre à jour l'historique sans recharger
        if (window.history.replaceState) {
            window.history.replaceState({}, '', newUrl);
        }

        // Mettre à jour les liens de navigation
        updateNavigationLinks(year, month);
    }

    /**
     * Met à jour les liens de navigation
     */
    function updateNavigationLinks(year, month) {
        // Calculer les mois précédent et suivant
        let prevYear = year;
        let prevMonth = month - 1;
        if (prevMonth === 0) {
            prevMonth = 12;
            prevYear--;
        }

        let nextYear = year;
        let nextMonth = month + 1;
        if (nextMonth === 13) {
            nextMonth = 1;
            nextYear++;
        }

        // Mettre à jour les liens
        const prevBtn = document.querySelector('a[href*="prev_month"]');
        const nextBtn = document.querySelector('a[href*="next_month"]');

        if (prevBtn) {
            prevBtn.href = `/evenements/calendrier/${prevYear}/${prevMonth}/`;
        }
        if (nextBtn) {
            nextBtn.href = `/evenements/calendrier/${nextYear}/${nextMonth}/`;
        }

        // Mettre à jour le titre
        const titleEl = document.querySelector('h2');
        if (titleEl) {
            const monthNames = [
                'Janvier', 'Février', 'Mars', 'Avril', 'Mai', 'Juin',
                'Juillet', 'Août', 'Septembre', 'Octobre', 'Novembre', 'Décembre'
            ];
            titleEl.textContent = `${monthNames[month - 1]} ${year}`;
        }
    }

    // Initialiser au chargement du DOM
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initCalendar);
    } else {
        initCalendar();
    }
})();
