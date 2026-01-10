/**
 * Dark Mode Toggle
 *
 * Manages dark mode state and persistence
 */

class DarkModeManager {
    constructor() {
        this.storageKey = 'dms-theme';
        this.theme = this.getSavedTheme() || this.getSystemTheme();
        this.init();
    }

    init() {
        // Apply saved theme
        this.applyTheme(this.theme);

        // Create toggle button
        this.createToggleButton();

        // Listen for system theme changes
        this.watchSystemTheme();
    }

    getSavedTheme() {
        try {
            return localStorage.getItem(this.storageKey);
        } catch (e) {
            console.warn('localStorage not available:', e);
            return null;
        }
    }

    getSystemTheme() {
        if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
            return 'dark';
        }
        return 'light';
    }

    saveTheme(theme) {
        try {
            localStorage.setItem(this.storageKey, theme);
        } catch (e) {
            console.warn('Could not save theme preference:', e);
        }
    }

    applyTheme(theme) {
        this.theme = theme;
        document.documentElement.setAttribute('data-theme', theme);
        this.updateToggleButton();
        this.saveTheme(theme);

        // Dispatch event for other components
        window.dispatchEvent(new CustomEvent('themechange', {
            detail: { theme: theme }
        }));
    }

    toggleTheme() {
        const newTheme = this.theme === 'dark' ? 'light' : 'dark';
        this.applyTheme(newTheme);
    }

    createToggleButton() {
        // Check if button already exists
        if (document.getElementById('dark-mode-toggle')) {
            return;
        }

        const button = document.createElement('button');
        button.id = 'dark-mode-toggle';
        button.className = 'dark-mode-toggle';
        button.setAttribute('aria-label', 'Toggle dark mode');
        button.setAttribute('title', 'Toggle dark mode');

        button.innerHTML = '<i class="bi bi-moon-stars-fill"></i>';

        button.addEventListener('click', () => {
            this.toggleTheme();
        });

        document.body.appendChild(button);
    }

    updateToggleButton() {
        const button = document.getElementById('dark-mode-toggle');
        if (button) {
            if (this.theme === 'dark') {
                button.innerHTML = '<i class="bi bi-sun-fill"></i>';
                button.setAttribute('title', 'Switch to light mode');
            } else {
                button.innerHTML = '<i class="bi bi-moon-stars-fill"></i>';
                button.setAttribute('title', 'Switch to dark mode');
            }
        }
    }

    watchSystemTheme() {
        if (window.matchMedia) {
            const darkModeQuery = window.matchMedia('(prefers-color-scheme: dark)');

            // Modern browsers
            if (darkModeQuery.addEventListener) {
                darkModeQuery.addEventListener('change', (e) => {
                    // Only auto-switch if user hasn't manually set a preference
                    if (!this.getSavedTheme()) {
                        this.applyTheme(e.matches ? 'dark' : 'light');
                    }
                });
            }
            // Legacy browsers
            else if (darkModeQuery.addListener) {
                darkModeQuery.addListener((e) => {
                    if (!this.getSavedTheme()) {
                        this.applyTheme(e.matches ? 'dark' : 'light');
                    }
                });
            }
        }
    }

    // Public API
    getCurrentTheme() {
        return this.theme;
    }

    isDarkMode() {
        return this.theme === 'dark';
    }

    setTheme(theme) {
        if (theme === 'dark' || theme === 'light') {
            this.applyTheme(theme);
        }
    }
}

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        window.darkMode = new DarkModeManager();
    });
} else {
    window.darkMode = new DarkModeManager();
}

// Keyboard shortcut: Ctrl/Cmd + Shift + D
document.addEventListener('keydown', (e) => {
    if ((e.ctrlKey || e.metaKey) && e.shiftKey && e.key === 'D') {
        e.preventDefault();
        if (window.darkMode) {
            window.darkMode.toggleTheme();
        }
    }
});

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = DarkModeManager;
}
