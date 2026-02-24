/**
 * Gestion du pointage journalier
 * @module DailyTracking
 */

(function () {
    "use strict";

    /**
     * Initialise le module de pointage
     */
    function init() {
        const container = document.querySelector(".pointage-container");
        if (!container) return;

        const csrfToken = container.dataset.csrfToken;

        // Gestion des boutons de compteur
        setupCounterButtons(csrfToken);

        // Gestion du changement de date
        setupDateForm();
    }

    /**
     * Configure les boutons d'incrémentation/décrémentation
     * @param {string} csrfToken - Token CSRF pour les requêtes
     */
    function setupCounterButtons(csrfToken) {
        const buttons = document.querySelectorAll(".btn-counter");

        buttons.forEach((button) => {
            button.addEventListener("click", async function () {
                const delta = parseInt(this.dataset.delta, 10);
                const trackingId = this.dataset.trackingId;
                const counterElement = document.querySelector(
                    `[data-tracking-id="${trackingId}"].counter-value`
                );

                if (!counterElement) return;

                try {
                    const response = await fetch(
                        `/pointage/update/${trackingId}/`,
                        {
                            method: "POST",
                            headers: {
                                "Content-Type": "application/json",
                                "X-CSRFToken": csrfToken,
                                "X-Requested-With": "XMLHttpRequest",
                            },
                            body: JSON.stringify({ delta: delta }),
                        }
                    );

                    if (response.ok) {
                        const data = await response.json();
                        counterElement.textContent = data.new_count;

                        // Animation visuelle
                        counterElement.classList.add("counter-updated");
                        setTimeout(() => {
                            counterElement.classList.remove("counter-updated");
                        }, 300);
                    } else {
                        const error = await response.json();
                        showNotification(error.error || "Erreur lors de la mise à jour", "error");
                    }
                } catch (error) {
                    console.error("Erreur:", error);
                    showNotification("Erreur de connexion", "error");
                }
            });
        });
    }

    /**
     * Configure le formulaire de changement de date
     */
    function setupDateForm() {
        const dateForm = document.getElementById("date-form");
        const dateInput = document.getElementById("date-input");

        if (!dateForm || !dateInput) return;

        dateForm.addEventListener("submit", function (e) {
            e.preventDefault();

            const selectedDate = dateInput.value;
            const action = dateForm.action.replace("0000-00-00", selectedDate);

            window.location.href = action;
        });
    }

    /**
     * Affiche une notification
     * @param {string} message - Message à afficher
     * @param {string} type - Type de notification (success, error, info)
     */
    function showNotification(message, type = "info") {
        // Créer l'élément de notification
        const notification = document.createElement("div");
        notification.className = `notification notification-${type}`;
        notification.textContent = message;

        // Styles de base
        notification.style.cssText = `
            position: fixed;
            top: 1rem;
            right: 1rem;
            padding: 1rem 1.5rem;
            border-radius: 0.5rem;
            color: white;
            font-weight: 500;
            z-index: 9999;
            animation: slideIn 0.3s ease;
        `;

        // Couleur selon le type
        const colors = {
            success: "#22c55e",
            error: "#ef4444",
            info: "#3b82f6",
        };
        notification.style.backgroundColor = colors[type] || colors.info;

        // Ajouter au DOM
        document.body.appendChild(notification);

        // Supprimer après 3 secondes
        setTimeout(() => {
            notification.style.animation = "slideOut 0.3s ease";
            setTimeout(() => notification.remove(), 300);
        }, 3000);
    }

    // Initialiser au chargement du DOM
    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", init);
    } else {
        init();
    }
})();
