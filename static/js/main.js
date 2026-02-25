/**
 * Main JavaScript file for Gestion-CCSA
 * Handles mobile menu, dropdowns, and accordions
 */

(function () {
  "use strict";

  // Mobile menu toggle
  function initMobileMenu() {
    const mobileMenuButton = document.getElementById("mobile-menu-button");
    const mobileMenu = document.getElementById("mobile-menu");
    const menuOpenIcon = document.getElementById("menu-open-icon");
    const menuCloseIcon = document.getElementById("menu-close-icon");

    if (mobileMenuButton && mobileMenu) {
      mobileMenuButton.addEventListener("click", () => {
        mobileMenu.classList.toggle("hidden");
        if (menuOpenIcon) menuOpenIcon.classList.toggle("hidden");
        if (menuCloseIcon) menuCloseIcon.classList.toggle("hidden");
      });
    }
  }

  // Dropdown menus manager
  function initDropdownMenus() {
    const menus = [
      { button: "user-menu-button", menu: "user-menu" },
      {
        button: "communication-nav-menu-button",
        menu: "communication-nav-menu",
      },
      { button: "tools-nav-menu-button", menu: "tools-nav-menu" },
      { button: "pointage-nav-menu-button", menu: "pointage-nav-menu" },
    ];

    // Function to close all menus except the specified one
    function closeAllMenusExcept(exceptMenuId) {
      menus.forEach(({ menu }) => {
        if (menu !== exceptMenuId) {
          const menuEl = document.getElementById(menu);
          if (menuEl) {
            menuEl.classList.add("hidden");
          }
        }
      });
    }

    // Initialize each menu
    menus.forEach(({ button, menu }) => {
      const buttonEl = document.getElementById(button);
      const menuEl = document.getElementById(menu);

      if (buttonEl && menuEl) {
        buttonEl.addEventListener("click", (e) => {
          e.stopPropagation();
          const isHidden = menuEl.classList.contains("hidden");

          // Close all other menus first
          closeAllMenusExcept(menu);

          // Toggle the clicked menu
          if (isHidden) {
            menuEl.classList.remove("hidden");
          } else {
            menuEl.classList.add("hidden");
          }
        });
      }
    });

    // Close all menus when clicking elsewhere
    document.addEventListener("click", (e) => {
      menus.forEach(({ button, menu }) => {
        const buttonEl = document.getElementById(button);
        const menuEl = document.getElementById(menu);

        if (buttonEl && menuEl) {
          if (!buttonEl.contains(e.target) && !menuEl.contains(e.target)) {
            menuEl.classList.add("hidden");
          }
        }
      });
    });
  }

  // Administration accordion
  function initAdminAccordion() {
    document.querySelectorAll(".admin-accordion-toggle").forEach((toggle) => {
      toggle.addEventListener("click", (e) => {
        e.stopPropagation();
        const accordion = toggle.closest(".admin-accordion");
        const content = accordion.querySelector(".admin-accordion-content");
        const icon = toggle.querySelector(".admin-accordion-icon");

        if (content && icon) {
          if (content.classList.contains("hidden")) {
            content.classList.remove("hidden");
            icon.classList.add("rotate-180");
          } else {
            content.classList.add("hidden");
            icon.classList.remove("rotate-180");
          }
        }
      });
    });
  }

  // Initialize all components when DOM is ready
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", function () {
      initMobileMenu();
      initDropdownMenus();
      initAdminAccordion();
    });
  } else {
    // DOM already loaded
    initMobileMenu();
    initDropdownMenus();
    initAdminAccordion();
  }
})();
