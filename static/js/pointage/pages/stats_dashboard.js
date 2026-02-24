/**
 * Dashboard de statistiques de pointage
 * @module StatsDashboard
 */

(function () {
    "use strict";

    let statsChart = null;
    let currentPeriod = "day";
    let currentStats = null;

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
                    legend: {
                        position: "top",
                        labels: {
                            usePointStyle: true,
                            padding: 20,
                            font: {
                                size: 12,
                            }
                        }
                    },
                    tooltip: {
                        mode: "index",
                        intersect: false,
                        backgroundColor: 'rgba(255, 255, 255, 0.95)',
                        titleColor: '#1e293b',
                        bodyColor: '#475569',
                        borderColor: '#e2e8f0',
                        borderWidth: 1,
                        padding: 12,
                        displayColors: true,
                        callbacks: {
                            label: function(context) {
                                return context.dataset.label + ': ' + context.parsed.y + ' personnes';
                            }
                        }
                    },
                },
                scales: {
                    x: {
                        display: true,
                        grid: {
                            display: false,
                        },
                        ticks: {
                            font: {
                                size: 11,
                            },
                            color: '#64748b',
                        }
                    },
                    y: {
                        display: true,
                        beginAtZero: true,
                        grid: {
                            color: '#f1f5f9',
                        },
                        ticks: {
                            font: {
                                size: 11,
                            },
                            color: '#64748b',
                            callback: function(value) {
                                return value + ' pers.';
                            }
                        }
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
                // Retirer la classe active et réinitialiser les styles de tous les boutons
                buttons.forEach((btn) => {
                    btn.classList.remove("active", "text-white");
                    btn.classList.add("text-slate-700", "bg-white");
                });

                // Ajouter la classe active et le style au bouton cliqué
                this.classList.add("active", "text-white");
                this.classList.remove("text-slate-700", "bg-white");

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

        // Afficher l'état de chargement
        showLoadingState();

        try {
            const response = await fetch(
                `/pointage/stats/data/?period=${currentPeriod}&date=${selectedDate}`
            );

            if (!response.ok) {
                throw new Error("Erreur lors du chargement des données");
            }

            const data = await response.json();
            currentStats = data.stats;
            
            // Debug: afficher les données reçues
            console.log("Données reçues:", data);
            console.log("Stats:", data.stats);

            // Mettre à jour le graphique
            updateChart(data);

            // Mettre à jour le résumé
            updateSummary(data);

            // Mettre à jour les stats globales
            if (data.stats) {
                updateGlobalStats(data.stats);
            } else {
                console.error("Pas de données stats reçues");
            }

            // Mettre à jour les KPI cards
            updateKpiCards(data.stats);

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
        if (!summaryGrid || !data.stats) return;

        summaryGrid.innerHTML = "";

        // Mettre à jour les cards de sections
        data.stats.sections.forEach((section, index) => {
            const card = createSectionCard(section, index);
            summaryGrid.appendChild(card);
        });
    }

    /**
     * Crée une card pour une section
     * @param {Object} section - Données de la section
     * @param {number} index - Index pour l'animation
     * @returns {HTMLElement}
     */
    function createSectionCard(section, index) {
        const card = document.createElement("div");
        card.className = "kpi-card bg-white rounded-xl shadow-sm border border-slate-200 p-5 animate-scale-in";
        card.style.animationDelay = `${index * 100}ms`;
        card.style.borderLeft = `4px solid ${section.color}`;

        card.innerHTML = `
            <div class="flex items-start justify-between">
                <div>
                    <div class="flex items-center gap-2 mb-2">
                        <div class="w-3 h-3 rounded-full" style="background-color: ${section.color}"></div>
                        <h3 class="font-medium text-slate-900">${section.name}</h3>
                    </div>
                    
                    <p class="text-3xl font-bold text-slate-900">${section.total.toLocaleString()}</p>
                    <p class="text-sm text-slate-500 mt-1">personnes</p>
                </div>
                
                <div class="w-10 h-10 rounded-lg flex items-center justify-center" style="background-color: ${section.color}15;">
                    <svg class="w-5 h-5" style="color: ${section.color}" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"/>
                    </svg>
                </div>
            </div>
            
            <div class="mt-4 pt-4 border-t border-slate-100 space-y-2">
                <div class="flex items-center justify-between text-sm">
                    <span class="text-slate-500">Moyenne/jour</span>
                    <span class="font-medium text-slate-900">${section.average}</span>
                </div>
                <div class="flex items-center justify-between text-sm">
                    <span class="text-slate-500">Maximum</span>
                    <span class="font-medium text-slate-900">${section.max}</span>
                </div>
                <div class="flex items-center justify-between text-sm">
                    <span class="text-slate-500">Minimum</span>
                    <span class="font-medium text-slate-900">${section.min}</span>
                </div>
            </div>
        `;

        return card;
    }

    /**
     * Met à jour les statistiques globales
     * @param {Object} stats - Données statistiques
     */
    function updateGlobalStats(stats) {
        console.log("updateGlobalStats appelé avec:", stats);
        
        if (!stats) {
            console.error("stats est null ou undefined");
            return;
        }

        // Mettre à jour le total général
        const totalElement = document.getElementById("total-count");
        if (totalElement) {
            animateNumber(totalElement, stats.total_general);
        }

        // Mettre à jour la moyenne par jour
        const avgElement = document.getElementById("avg-per-day");
        if (avgElement) {
            animateNumber(avgElement, stats.avg_per_day);
        }

        // Mettre à jour le jour max
        const maxDayElement = document.getElementById("max-day");
        const maxDayDateElement = document.getElementById("max-day-date");
        if (maxDayElement && stats.max_day) {
            maxDayElement.textContent = stats.max_day.value.toLocaleString();
            if (maxDayDateElement) {
                maxDayDateElement.textContent = stats.max_day.date;
            }
        }

        // Mettre à jour le jour min
        const minDayElement = document.getElementById("min-day");
        const minDayDateElement = document.getElementById("min-day-date");
        if (minDayElement && stats.min_day) {
            minDayElement.textContent = stats.min_day.value.toLocaleString();
            if (minDayDateElement) {
                minDayDateElement.textContent = stats.min_day.date;
            }
        }

        // Mettre à jour la section la plus populaire
        const topSectionElement = document.getElementById("top-section");
        const topSectionCountElement = document.getElementById("top-section-count");
        if (topSectionElement && stats.top_section) {
            topSectionElement.textContent = stats.top_section.name;
            topSectionElement.style.color = stats.top_section.color;
            if (topSectionCountElement) {
                topSectionCountElement.textContent = `${stats.top_section.total.toLocaleString()} personnes`;
            }
        }

        // Mettre à jour l'évolution
        const evolutionElement = document.getElementById("evolution");
        const evolutionArrowElement = document.getElementById("evolution-arrow");
        if (evolutionElement && stats.evolution !== undefined) {
            const isPositive = stats.evolution >= 0;
            evolutionElement.textContent = `${Math.abs(stats.evolution)}%`;
            evolutionElement.className = `text-2xl font-bold ${isPositive ? 'text-green-600' : 'text-red-600'}`;
            
            if (evolutionArrowElement) {
                evolutionArrowElement.innerHTML = isPositive 
                    ? '<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6"/></svg>'
                    : '<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 17h8m0 0V9m0 8l-8-8-4 4-6-6"/></svg>';
                evolutionArrowElement.className = `w-10 h-10 rounded-full flex items-center justify-center ${isPositive ? 'bg-green-100 text-green-600' : 'bg-red-100 text-red-600'}`;
            }
        }

        // Mettre à jour le nombre de jours
        const daysElement = document.getElementById("stats-days");
        if (daysElement && stats.num_days) {
            daysElement.textContent = stats.num_days === 1 
                ? '1 jour' 
                : `${stats.num_days} jours`;
        }
    }

    /**
     * Met à jour les cards KPI
     * @param {Object} stats - Données statistiques
     */
    function updateKpiCards(stats) {
        // Cette fonction peut être utilisée pour mettre à jour d'autres éléments si nécessaire
    }

    /**
     * Affiche l'état de chargement
     */
    function showLoadingState() {
        const summaryGrid = document.getElementById("summary-grid");
        if (summaryGrid) {
            summaryGrid.innerHTML = `
                <div class="col-span-full flex items-center justify-center py-12">
                    <svg class="w-8 h-8 animate-spin text-primary-600" fill="none" viewBox="0 0 24 24">
                        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    <span class="ml-2 text-slate-600">Chargement des statistiques...</span>
                </div>
            `;
        }
    }

    /**
     * Anime un nombre
     * @param {HTMLElement} element - Élément à animer
     * @param {number} target - Valeur cible
     */
    function animateNumber(element, target) {
        const duration = 1000;
        const start = 0;
        const startTime = performance.now();

        function update(currentTime) {
            const elapsed = currentTime - startTime;
            const progress = Math.min(elapsed / duration, 1);

            // Easing function
            const easeOutQuart = 1 - Math.pow(1 - progress, 4);
            const current = Math.floor(start + (target - start) * easeOutQuart);

            element.textContent = current.toLocaleString();

            if (progress < 1) {
                requestAnimationFrame(update);
            }
        }

        requestAnimationFrame(update);
    }

    /**
     * Affiche une notification
     * @param {string} message - Message à afficher
     * @param {string} type - Type de notification
     */
    function showNotification(message, type = "info") {
        const notification = document.createElement("div");
        notification.className = `fixed top-4 right-4 px-6 py-3 rounded-lg text-white font-medium z-50 animate-fade-in`;
        
        const colors = {
            success: "bg-green-600",
            error: "bg-red-600",
            warning: "bg-amber-600",
            info: "bg-blue-600",
        };
        
        notification.classList.add(colors[type] || colors.info);
        notification.textContent = message;

        document.body.appendChild(notification);

        setTimeout(() => {
            notification.style.opacity = "0";
            notification.style.transition = "opacity 0.3s ease";
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
