/**
 * Module de prévisualisation en temps réel pour les événements
 * Vanilla JavaScript - Pas de dépendances externes
 */

(function() {
    'use strict';

    /**
     * Initialise la prévisualisation des événements
     */
    function initEventPreview() {
        const form = document.getElementById('event-form');
        if (!form) return;

        // Éléments du formulaire
        const titleInput = document.getElementById('id_title');
        const descriptionInput = document.getElementById('id_description');
        const locationInput = document.getElementById('id_location');
        const cityInput = document.getElementById('id_city');
        const startInput = document.getElementById('id_start_datetime');
        const endInput = document.getElementById('id_end_datetime');
        const sectorSelect = document.getElementById('id_sector');
        const commBefore = document.getElementById('id_comm_before');
        const commDuring = document.getElementById('id_comm_during');
        const commAfter = document.getElementById('id_comm_after');
        const needsFilming = document.getElementById('id_needs_filming');
        const needsPoster = document.getElementById('id_needs_poster');

        // Éléments de prévisualisation
        const previewTitle = document.getElementById('preview-title');
        const previewDescription = document.getElementById('preview-description');
        const previewLocation = document.getElementById('preview-location');
        const previewDatetime = document.getElementById('preview-datetime');
        const previewSector = document.getElementById('preview-sector');
        const previewOptions = document.getElementById('preview-options');

        /**
         * Met à jour la prévisualisation
         */
        function updatePreview() {
            // Titre
            if (previewTitle) {
                previewTitle.textContent = titleInput?.value || 'Titre de l\'événement';
            }

            // Description
            if (previewDescription) {
                previewDescription.textContent = descriptionInput?.value || 'Description de l\'événement...';
            }

            // Lieu
            if (previewLocation) {
                const location = locationInput?.value;
                const city = cityInput?.value;
                if (location || city) {
                    previewLocation.innerHTML = `<strong>Lieu :</strong> ${location || ''}${location && city ? ', ' : ''}${city || ''}`;
                } else {
                    previewLocation.textContent = '';
                }
            }

            // Date et heure
            if (previewDatetime) {
                const start = startInput?.value;
                const end = endInput?.value;
                if (start) {
                    const startDate = new Date(start);
                    const formattedStart = startDate.toLocaleString('fr-FR', {
                        weekday: 'long',
                        year: 'numeric',
                        month: 'long',
                        day: 'numeric',
                        hour: '2-digit',
                        minute: '2-digit'
                    });
                    
                    let html = `<strong>Date :</strong> ${formattedStart}`;
                    
                    if (end) {
                        const endDate = new Date(end);
                        const formattedEnd = endDate.toLocaleString('fr-FR', {
                            weekday: 'long',
                            year: 'numeric',
                            month: 'long',
                            day: 'numeric',
                            hour: '2-digit',
                            minute: '2-digit'
                        });
                        html += `<br><strong>Fin :</strong> ${formattedEnd}`;
                    }
                    
                    previewDatetime.innerHTML = html;
                } else {
                    previewDatetime.textContent = '';
                }
            }

            // Secteur
            if (previewSector && sectorSelect) {
                const selectedOption = sectorSelect.options[sectorSelect.selectedIndex];
                if (selectedOption && selectedOption.value) {
                    previewSector.textContent = selectedOption.text;
                    // Récupérer la couleur depuis un attribut data ou utiliser une couleur par défaut
                    const colorCode = selectedOption.getAttribute('data-color') || '#6c757d';
                    previewSector.style.backgroundColor = colorCode;
                } else {
                    previewSector.textContent = '';
                }
            }

            // Options
            if (previewOptions) {
                let options = [];
                if (commBefore?.checked) options.push('Communication avant');
                if (commDuring?.checked) options.push('Communication pendant');
                if (commAfter?.checked) options.push('Communication après');
                if (needsFilming?.checked) options.push('Filmer');
                if (needsPoster?.checked) options.push('Affiche');

                if (options.length > 0) {
                    previewOptions.innerHTML = '<strong>Options :</strong><br>' + 
                        options.map(opt => `• ${opt}`).join('<br>');
                } else {
                    previewOptions.textContent = '';
                }
            }
        }

        // Ajouter les écouteurs d'événements
        const inputs = [titleInput, descriptionInput, locationInput, cityInput, 
                       startInput, endInput, sectorSelect];
        inputs.forEach(input => {
            if (input) {
                input.addEventListener('input', updatePreview);
                input.addEventListener('change', updatePreview);
            }
        });

        const checkboxes = [commBefore, commDuring, commAfter, needsFilming, needsPoster];
        checkboxes.forEach(checkbox => {
            if (checkbox) {
                checkbox.addEventListener('change', updatePreview);
            }
        });

        // Initialiser la prévisualisation
        updatePreview();
    }

    // Initialiser au chargement du DOM
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initEventPreview);
    } else {
        initEventPreview();
    }
})();
