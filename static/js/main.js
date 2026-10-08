/**
 * U KOST - Main Application JavaScript
 * Handles global interactions, state management, UI components,
 * wizard steps, favorites, comparison, and SPK simulation.
 */

// ============================================
// State Management & Storage Helpers
// ============================================
const Storage = {
    FAVORITES_KEY: 'ukost_favorites',
    COMPARE_KEY: 'ukost_compare',
    SEARCH_PREF_KEY: 'ukost_search_prefs',
    HISTORY_KEY: 'ukost_history',

    getFavorites() {
        try {
            return JSON.parse(localStorage.getItem(this.FAVORITES_KEY)) || [1, 4];
        } catch (e) {
            return [1, 4];
        }
    },

    saveFavorites(favorites) {
        localStorage.setItem(this.FAVORITES_KEY, JSON.stringify(favorites));
        App.updateBadges();
    },

    toggleFavorite(kostId) {
        let favorites = this.getFavorites();
        const id = parseInt(kostId);
        const index = favorites.indexOf(id);
        let added = false;

        if (index > -1) {
            favorites.splice(index, 1);
            Toast.show('Kost dihapus dari daftar Favorit', 'info');
        } else {
            favorites.push(id);
            added = true;
            Toast.show('Kost berhasil ditambahkan ke Favorit!', 'success');
        }

        this.saveFavorites(favorites);
        return added;
    },

    isFavorite(kostId) {
        return this.getFavorites().includes(parseInt(kostId));
    },

    getCompareList() {
        try {
            const raw = localStorage.getItem(this.COMPARE_KEY);
            if (raw !== null) {
                const parsed = JSON.parse(raw);
                if (Array.isArray(parsed)) return parsed;
            }
            return [1, 2];
        } catch (e) {
            return [1, 2];
        }
    },

    saveCompareList(list) {
        localStorage.setItem(this.COMPARE_KEY, JSON.stringify(list));
        App.updateBadges();
    },

    addToCompare(kostId) {
        let list = this.getCompareList();
        const id = parseInt(kostId);
        if (list.includes(id)) {
            Toast.show('Kost ini sudah ada di daftar perbandingan!', 'info');
            return false;
        }

        if (list.length >= 3) {
            // Replace the last item
            list[2] = id;
            this.saveCompareList(list);
            Toast.show('Slot ke-3 digantikan dengan kost pilihan!', 'success');
            return true;
        } else {
            list.push(id);
            this.saveCompareList(list);
            Toast.show('Kost berhasil ditambahkan ke perbandingan!', 'success');
            return true;
        }
    },

    removeFromCompare(kostId) {
        let list = this.getCompareList();
        const id = parseInt(kostId);
        const index = list.indexOf(id);
        if (index > -1) {
            list.splice(index, 1);
            this.saveCompareList(list);
            Toast.show('Kost dihapus dari perbandingan', 'info');
            return true;
        }
        return false;
    },

    toggleCompare(kostId) {
        let list = this.getCompareList();
        const id = parseInt(kostId);
        const index = list.indexOf(id);
        let added = false;

        if (index > -1) {
            list.splice(index, 1);
            Toast.show('Kost dihapus dari perbandingan', 'info');
        } else {
            if (list.length >= 3) {
                list[2] = id; // replace 3rd slot
                added = true;
                Toast.show('Slot ke-3 digantikan dengan kost pilihan!', 'success');
            } else {
                list.push(id);
                added = true;
                Toast.show('Kost ditambahkan ke perbandingan!', 'success');
            }
        }

        this.saveCompareList(list);
        return added;
    },

    isCompared(kostId) {
        return this.getCompareList().includes(parseInt(kostId));
    },

    getSearchPrefs() {
        try {
            return JSON.parse(localStorage.getItem(this.SEARCH_PREF_KEY)) || {
                campus: '1',
                faculty: '',
                room_type: 'Semua',
                max_price: 2000000,
                max_distance: 3.0,
                facilities: ['wifi', 'bathroom', 'ac'],
                priorities: {
                    harga: 4,
                    jarak: 5,
                    fasilitas: 4,
                    keamanan: 5,
                    kenyamanan: 3
                }
            };
        } catch (e) {
            return {};
        }
    },

    saveSearchPrefs(prefs) {
        const current = this.getSearchPrefs();
        const updated = { ...current, ...prefs };
        localStorage.setItem(this.SEARCH_PREF_KEY, JSON.stringify(updated));
    },

    addSearchHistory(searchRecord) {
        let history = [];
        try {
            history = JSON.parse(localStorage.getItem(this.HISTORY_KEY)) || [];
        } catch (e) {
            history = [];
        }
        history.unshift(searchRecord);
        if (history.length > 20) history.pop();
        localStorage.setItem(this.HISTORY_KEY, JSON.stringify(history));
    }
};

// ============================================
// Toast Notification Utility
// ============================================
const Toast = {
    show(message, type = 'info', duration = 3500) {
        const container = document.getElementById('toastContainer');
        if (!container) return;

        const icons = {
            success: 'fa-check-circle',
            warning: 'fa-exclamation-triangle',
            danger: 'fa-times-circle',
            info: 'fa-info-circle'
        };

        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        toast.innerHTML = `
            <i class="fas ${icons[type] || icons.info} toast-icon"></i>
            <div class="toast-content">
                <p class="toast-message">${message}</p>
            </div>
            <button class="toast-close" aria-label="Tutup"><i class="fas fa-times"></i></button>
        `;

        container.appendChild(toast);

        // Animate in
        requestAnimationFrame(() => {
            toast.classList.add('show');
        });

        const closeBtn = toast.querySelector('.toast-close');
        const dismiss = () => {
            toast.classList.remove('show');
            setTimeout(() => toast.remove(), 300);
        };

        closeBtn.addEventListener('click', dismiss);
        setTimeout(dismiss, duration);
    }
};

// ============================================
// Main Application Controller
// ============================================
const App = {
    init() {
        this.setupNavigation();
        this.setupUserDropdown();
        this.updateBadges();
        this.setupGlobalButtons();
        this.setupRangeSliders();
        this.highlightActiveFavorites();
    },

    setupNavigation() {
        const navToggle = document.getElementById('navToggle');
        const navMenu = document.getElementById('navMenu');

        if (navToggle && navMenu) {
            navToggle.addEventListener('click', () => {
                const expanded = navToggle.getAttribute('aria-expanded') === 'true';
                navToggle.setAttribute('aria-expanded', !expanded);
                navToggle.classList.toggle('active');
                navMenu.classList.toggle('active');
            });
        }

        // Close on clicking outside
        document.addEventListener('click', (e) => {
            if (navMenu && navMenu.classList.contains('active')) {
                if (!navMenu.contains(e.target) && !navToggle.contains(e.target)) {
                    navMenu.classList.remove('active');
                    navToggle.classList.remove('active');
                    navToggle.setAttribute('aria-expanded', 'false');
                }
            }
        });
    },

    setupUserDropdown() {
        const trigger = document.getElementById('userMenuTrigger');
        const dropdown = document.getElementById('userDropdown');

        if (trigger && dropdown) {
            trigger.addEventListener('click', (e) => {
                e.stopPropagation();
                dropdown.classList.toggle('active');
            });

            document.addEventListener('click', (e) => {
                if (!dropdown.contains(e.target) && !trigger.contains(e.target)) {
                    dropdown.classList.remove('active');
                }
            });
        }
    },

    updateBadges() {
        const compareBadge = document.getElementById('compareBadge');
        const favoriteBadge = document.getElementById('favoriteBadge');

        const compares = Storage.getCompareList();
        const favorites = Storage.getFavorites();

        if (compareBadge) {
            compareBadge.textContent = compares.length;
            compareBadge.style.display = compares.length > 0 ? 'inline-block' : 'none';
        }

        if (favoriteBadge) {
            favoriteBadge.textContent = favorites.length;
            favoriteBadge.style.display = favorites.length > 0 ? 'inline-block' : 'none';
        }
    },

    setupGlobalButtons() {
        // Delegate favorite button clicks
        document.addEventListener('click', (e) => {
            const favBtn = e.target.closest('.btn-favorite, [data-action="toggle-favorite"]');
            if (favBtn) {
                e.preventDefault();
                e.stopPropagation();
                const kostId = favBtn.dataset.kostId || favBtn.dataset.id;
                if (kostId) {
                    const isFav = Storage.toggleFavorite(kostId);
                    favBtn.classList.toggle('active', isFav);
                    const icon = favBtn.querySelector('i');
                    if (icon) {
                        icon.className = isFav ? 'fas fa-heart text-danger' : 'far fa-heart';
                    }
                }
            }

            // Delegate compare button clicks
            const compBtn = e.target.closest('.btn-compare, [data-action="toggle-compare"]');
            if (compBtn) {
                e.preventDefault();
                e.stopPropagation();
                const kostId = compBtn.dataset.kostId || compBtn.dataset.id;
                if (kostId) {
                    const isComp = Storage.toggleCompare(kostId);
                    compBtn.classList.toggle('active', isComp);
                }
            }
        });
    },

    highlightActiveFavorites() {
        const favs = Storage.getFavorites();
        document.querySelectorAll('.btn-favorite, [data-action="toggle-favorite"]').forEach(btn => {
            const id = parseInt(btn.dataset.kostId || btn.dataset.id);
            if (favs.includes(id)) {
                btn.classList.add('active');
                const icon = btn.querySelector('i');
                if (icon) {
                    icon.className = 'fas fa-heart text-danger';
                }
            }
        });
    },

    setupRangeSliders() {
        document.querySelectorAll('input[type="range"]').forEach(slider => {
            const display = document.getElementById(slider.id + '_display') ||
                            document.querySelector(`[data-slider-value="${slider.id}"]`);
            if (display) {
                const updateDisplay = () => {
                    const val = Number(slider.value);
                    if (slider.dataset.format === 'currency') {
                        display.textContent = 'Rp' + val.toLocaleString('id-ID');
                    } else if (slider.dataset.format === 'distance') {
                        display.textContent = val.toFixed(1) + ' km';
                    } else {
                        display.textContent = val;
                    }
                };
                slider.addEventListener('input', updateDisplay);
                updateDisplay();
            }
        });
    }
};

// Initialize on DOM ready
document.addEventListener('DOMContentLoaded', () => {
    App.init();
});
