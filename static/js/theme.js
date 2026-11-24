
(() => {
    "use strict";

    const THEME_KEY = "forex-journal-theme";
    const themeSelect = document.getElementById("theme-select");
    const root = document.documentElement;
    const systemPreference = window.matchMedia("(prefers-color-scheme: dark)");

    let savedTheme = "dark";

    function applyTheme(preference) {

        const effectiveTheme = preference === "system"
            ? (systemPreference.matches ? "dark" : "light")
            : preference;

        root.setAttribute("data-theme", effectiveTheme);

        if (themeSelect) {
            themeSelect.value = preference;
        }
    }

    try {
        const stored = localStorage.getItem(THEME_KEY);

        if (["dark", "light", "system"].includes(stored)) {
            savedTheme = stored;
        }

    } catch (error) {
        // Continue with dark mode.
    }

    applyTheme(savedTheme);

    if (themeSelect) {

        themeSelect.addEventListener("change", () => {

            const selected = themeSelect.value;

            if (!["dark", "light", "system"].includes(selected)) {
                return;
            }

            savedTheme = selected;

            try {
                localStorage.setItem(THEME_KEY, selected);
            } catch (error) {
                // Theme still works for this page.
            }

            applyTheme(savedTheme);
        });
    }

    if (typeof systemPreference.addEventListener === "function") {

        systemPreference.addEventListener("change", () => {

            if (savedTheme === "system") {
                applyTheme("system");
            }
        });
    }

})();
