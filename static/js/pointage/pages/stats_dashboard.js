/**
 * Dashboard de statistiques de pointage
 * @module StatsDashboard
 */

(function () {
    "use strict";

    let statsChart = null;
    let currentPeriod = "day";

    /**
     * Initialise le dashboard de statistiques
     */
    function init() {
        const chartCanvas = document.getElementById("statsChart");
        if (!chartCanvas) return;

        // Initialiser Chart.js
        initChart(chartCanvas);

        // Configurer les sélecteurs de période
        setupPeriodSelectors();

        // Configurer le sélecteur de date
        setupDateSelector();

        // Charger les données initiales
        loadStatsData();
    }

    /**
     * Initialise le graphique Chart.js
     * @param {HTMLCanvasElement} canvas - Élément canvas
     */
    function initChart(canvas) {
        const ctx = canvas.getContext("2d");

        statsChart = new Chart(ctx, {
            type: "line",
            data: {
                labels: [],
                datasets: [],
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                interaction: {
                    mode: "index",
                    intersect: false,
                },
                plugins: {
                    title: {
                        display: true,
                        text: "Statistiques de pointage",
                        font: {
                            size: 18,
                            weight: "bold",
                        },
                    },
                    legend: {
                        position: "top",
                    },
                    tooltip: {
                        mode: "index",
                        intersect: false,
                    },
                },
                scales: {
                    x: {
                        display: true,
                        title: {
                            display: true,
                            text: "Date",
                        },
                    },
                    y: {
                        display: true,
                        title: {
                            display: true,
                            text: "Nombre",
                        },
                        beginAtZero: true,
                    },
                },
            },
        });
    }

    /**
     * Configure les sélecteurs de période
     */
    function setupPeriodSelectors() {
        const buttons = document.querySelectorAll(".btn-period");

        buttons.forEach((button) => {
            button.addEventListener("click", function () {
                // Retirer la classe active de tous les boutons
                buttons.forEach((btn) => btn.classList.remove("active"));

                // Ajouter la classe active au bouton cliqué
                this.classList.add("active");

                // Mettre à jour la période courante
                currentPeriod = this.dataset.period;

                // Recharger les données
                loadStatsData();
            });
        });
    }

    /**
     * Configure le sélecteur de date
     */
    function setupDateSelector() {
        const dateInput = document.getElementById("stats-date");

        if (dateInput) {
            dateInput.addEventListener("change", loadStatsData);
        }
    }

    /**
     * Charge les données statistiques depuis l'API
     */
    async function loadStatsData() {
        const dateInput = document.getElementById("stats-date");
        const selectedDate = dateInput ? dateInput.value : new Date().toISOString().split("T")[0];

        try {
            const response = await fetch(
                `/pointage/stats/data/?period=${currentPeriod}&date=${selectedDate}`
            );

            if (!response.ok) {
                throw new Error("Erreur lors du chargement des données");
            }

            const data = await response.json();

            // Mettre à jour le graphique
            updateChart(data);

            // Mettre à jour le résumé
            updateSummary(data);
        } catch (error) {
            console.error("Erreur:", error);
            showNotification("Erreur lors du chargement des statistiques", "error");
        }
    }

    /**
     * Met à jour le graphique avec les nouvelles données
     * @param {Object} data - Données statistiques
     */
    function updateChart(data) {
        if (!statsChart) return;

        statsChart.data.labels = data.labels;
        statsChart.data.datasets = data.datasets;
        statsChart.update();
    }

    /**
     * Met à jour le résumé des statistiques
     * @param {Object} data - Données statistiques
     */
    function updateSummary(data) {
        const summaryGrid = document.getElementById("summary-grid");
        if (!summaryGrid) return;

        summaryGrid.innerHTML = "";

        // Calculer les totaux par section
        data.datasets.forEach((dataset) => {
            const total = dataset.data.reduce((sum, value) => sum + value, 0);
            const average = total / dataset.data.length;

            const card = document.createElement("div");
            card.className = "summary-card";
            card.style.borderTop = `4px solid ${dataset.borderColor}`;

            card.innerHTML = `
                <h3>${dataset.label}</h3>
                <div class="value">${total}</div>
                <small>Moyenne: ${average.toFixed(1)}/jour</small>
            `;

            summaryGrid.appendChild(card);
        });
    }

    /**
     * Affiche une notification
     * @param {string} message - Message à afficher
     * @param {string} type - Type de notification
     */
    function showNotification(message, type = "info") {
        const notification = document.createElement("div");
        notification.className = `notification notification-${type}`;
        notification.textContent = message;

        notification.style.cssText = `
            position: fixed;
            top: 1rem;
            right: 1rem;
            padding: 1rem 1.5rem;
            border-radius: 0.5rem;
            color: white;
            font-weight: 500;
            z-index: 9999;
            background-color: ${type === "error" ? "#ef4444" : "#3b82f6"};
        `;

        document.body.appendChild(notification);

        setTimeout(() => {
            notification.remove();
        }, 3000);
    }

    // Initialiser au chargement du DOM
    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", init);
    } else {
        init();
    }
})();
