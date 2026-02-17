/**
 * Module de gestion des images avec drag & drop
 * Vanilla JavaScript - Pas de dépendances externes
 */

(function() {
    'use strict';

    const MAX_IMAGES = 10;
    const MAX_FILE_SIZE = 10 * 1024 * 1024; // 10 Mo
    const ALLOWED_TYPES = ['image/jpeg', 'image/png', 'image/webp'];

    /**
     * Initialise le gestionnaire d'images
     */
    function initImageUpload() {
        const uploadZone = document.getElementById('image-upload-zone');
        const imageInput = document.getElementById('image-input');
        const previewContainer = document.getElementById('image-preview');
        const existingImages = document.getElementById('existing-images');

        if (!uploadZone || !imageInput) return;

        let selectedFiles = [];
        let currentImageCount = existingImages ? existingImages.children.length : 0;

        /**
         * Ouvre le sélecteur de fichiers
         */
        function openFileSelector() {
            imageInput.click();
        }

        /**
         * Gère le glisser-déposer
         */
        function handleDragOver(e) {
            e.preventDefault();
            e.stopPropagation();
            uploadZone.classList.add('drag-over');
        }

        function handleDragLeave(e) {
            e.preventDefault();
            e.stopPropagation();
            uploadZone.classList.remove('drag-over');
        }

        function handleDrop(e) {
            e.preventDefault();
            e.stopPropagation();
            uploadZone.classList.remove('drag-over');

            const files = Array.from(e.dataTransfer.files);
            processFiles(files);
        }

        /**
         * Gère la sélection de fichiers
         */
        function handleFileSelect(e) {
            const files = Array.from(e.target.files);
            processFiles(files);
        }

        /**
         * Traite les fichiers sélectionnés
         */
        function processFiles(files) {
            const availableSlots = MAX_IMAGES - currentImageCount - selectedFiles.length;

            if (availableSlots <= 0) {
                alert(`Vous ne pouvez pas ajouter plus de ${MAX_IMAGES} images.`);
                return;
            }

            const filesToProcess = files.slice(0, availableSlots);

            filesToProcess.forEach(file => {
                // Vérifier le type
                if (!ALLOWED_TYPES.includes(file.type)) {
                    alert(`Le fichier "${file.name}" n'est pas une image valide. Types acceptés: JPG, PNG, WEBP`);
                    return;
                }

                // Vérifier la taille
                if (file.size > MAX_FILE_SIZE) {
                    alert(`Le fichier "${file.name}" dépasse la taille maximale de 10 Mo.`);
                    return;
                }

                selectedFiles.push(file);
                createPreview(file);
            });

            updateFileInput();
        }

        /**
         * Crée la prévisualisation d'une image
         */
        function createPreview(file) {
            const reader = new FileReader();

            reader.onload = function(e) {
                const div = document.createElement('div');
                div.className = 'position-relative';
                div.dataset.fileName = file.name;

                div.innerHTML = `
                    <img src="${e.target.result}" alt="" style="width: 100px; height: 100px; object-fit: cover;">
                    <button type="button" class="position-absolute top-0 end-0 btn btn-sm btn-danger remove-image">×</button>
                `;

                // Gérer la suppression
                div.querySelector('.remove-image').addEventListener('click', function() {
                    removeFile(file.name);
                    div.remove();
                });

                previewContainer.appendChild(div);
            };

            reader.readAsDataURL(file);
        }

        /**
         * Supprime un fichier de la liste
         */
        function removeFile(fileName) {
            selectedFiles = selectedFiles.filter(f => f.name !== fileName);
            updateFileInput();
        }

        /**
         * Met à jour l'input file avec les fichiers sélectionnés
         */
        function updateFileInput() {
            const dataTransfer = new DataTransfer();
            selectedFiles.forEach(file => {
                dataTransfer.items.add(file);
            });
            imageInput.files = dataTransfer.files;
        }

        /**
         * Initialise le drag & drop pour réordonner les images existantes
         */
        function initDragReorder() {
            if (!existingImages) return;

            let draggedElement = null;

            existingImages.addEventListener('dragstart', function(e) {
                draggedElement = e.target.closest('[data-image-id]');
                if (draggedElement) {
                    draggedElement.style.opacity = '0.5';
                    e.dataTransfer.effectAllowed = 'move';
                }
            });

            existingImages.addEventListener('dragend', function(e) {
                if (draggedElement) {
                    draggedElement.style.opacity = '1';
                    draggedElement = null;
                }
            });

            existingImages.addEventListener('dragover', function(e) {
                e.preventDefault();
                const target = e.target.closest('[data-image-id]');
                if (target && target !== draggedElement) {
                    const rect = target.getBoundingClientRect();
                    const midX = rect.left + rect.width / 2;
                    if (e.clientX < midX) {
                        target.parentNode.insertBefore(draggedElement, target);
                    } else {
                        target.parentNode.insertBefore(draggedElement, target.nextSibling);
                    }
                }
            });

            existingImages.addEventListener('drop', function(e) {
                e.preventDefault();
                saveImageOrder();
            });
        }

        /**
         * Sauvegarde l'ordre des images via AJAX
         */
        function saveImageOrder() {
            const images = existingImages.querySelectorAll('[data-image-id]');
            const imageIds = Array.from(images).map(img => img.dataset.imageId);

            // Récupérer le slug de l'événement depuis l'URL
            const pathMatch = window.location.pathname.match(/\/evenements\/([^\/]+)\/modifier\//);
            if (!pathMatch) return;

            const slug = pathMatch[1];

            fetch(`/evenements/${slug}/images/reorder/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCsrfToken(),
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
                body: `image_ids[]=${imageIds.join('&image_ids[]=')}`
            })
            .then(response => response.json())
            .then(data => {
                if (!data.success) {
                    console.error('Erreur lors de la réorganisation');
                }
            })
            .catch(error => console.error('Erreur:', error));
        }

        /**
         * Récupère le token CSRF
         */
        function getCsrfToken() {
            const name = 'csrftoken';
            let cookieValue = null;
            if (document.cookie && document.cookie !== '') {
                const cookies = document.cookie.split(';');
                for (let i = 0; i < cookies.length; i++) {
                    const cookie = cookies[i].trim();
                    if (cookie.substring(0, name.length + 1) === (name + '=')) {
                        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                        break;
                    }
                }
            }
            return cookieValue;
        }

        // Écouteurs d'événements
        uploadZone.addEventListener('click', openFileSelector);
        uploadZone.addEventListener('dragover', handleDragOver);
        uploadZone.addEventListener('dragleave', handleDragLeave);
        uploadZone.addEventListener('drop', handleDrop);
        imageInput.addEventListener('change', handleFileSelect);

        // Initialiser le réordonnement
        initDragReorder();
    }

    // Initialiser au chargement du DOM
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initImageUpload);
    } else {
        initImageUpload();
    }
})();
