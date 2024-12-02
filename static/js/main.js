// Configuração inicial
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

// Funções principais
const app = {
    init: function() {
        this.setupLoadingSpinner();
        this.setupMessageHandlers();
        this.setupInputMasks();
        this.setupNavigationHandlers();
        this.setupAutoSave();
    },

    setupLoadingSpinner: function() {
        window.showLoading = function() {
            document.getElementById('loadingSpinner')?.classList.add('active');
        };

        window.hideLoading = function() {
            document.getElementById('loadingSpinner')?.classList.remove('active');
        };

        // Intercepta navegação para mostrar loading
        window.addEventListener('beforeunload', showLoading);
    },

    setupMessageHandlers: function() {
        const messages = document.querySelectorAll('.alert');
        messages.forEach(message => {
            setTimeout(() => {
                message.style.opacity = '0';
                setTimeout(() => message.remove(), 300);
            }, 5000);
        });
    },

    setupInputMasks: function() {
        // CNS Mask
        const cnsInput = document.getElementById('cns');
        if (cnsInput) {
            cnsInput.addEventListener('input', function(e) {
                let value = e.target.value.replace(/\D/g, '');
                if (value.length > 15) value = value.slice(0, 15);
                e.target.value = value;
            });
        }

        // Numeric inputs with decimal places
        const numericInputs = document.querySelectorAll('input[type="number"][step="0.01"]');
        numericInputs.forEach(input => {
            input.addEventListener('input', function(e) {
                const value = e.target.value;
                if (value && !isNaN(value)) {
                    e.target.value = parseFloat(value).toFixed(2);
                }
            });
        });
    },

    setupNavigationHandlers: function() {
        const menuToggle = document.getElementById('menuToggle');
        const menuItems = document.getElementById('menuItems');
        
        if (menuToggle && menuItems) {
            menuToggle.addEventListener('click', () => {
                menuItems.classList.toggle('active');
            });
        }
    },

    setupAutoSave: function() {
        const forms = document.querySelectorAll('form[data-autosave]');
        forms.forEach(form => {
            const inputs = form.querySelectorAll('input, select, textarea');
            inputs.forEach(input => {
                input.addEventListener('change', this.utils.debounce(() => {
                    this.utils.autoSave(form);
                }, 1000));
            });
        });
    },

    utils: {
        formatDate: function(date) {
            return new Date(date).toLocaleDateString('pt-BR');
        },
        
        formatCurrency: function(value) {
            return new Intl.NumberFormat('pt-BR', {
                style: 'currency',
                currency: 'BRL'
            }).format(value);
        },
        
        debounce: function(func, wait) {
            let timeout;
            return function(...args) {
                clearTimeout(timeout);
                timeout = setTimeout(() => func.apply(this, args), wait);
            };
        },

        autoSave: async function(form) {
            try {
                const formData = new FormData(form);
                const response = await fetch(form.action, {
                    method: 'POST',
                    body: formData
                });
                
                if (!response.ok) throw new Error('Erro ao salvar');
                
                const message = document.createElement('div');
                message.className = 'autosave-message';
                message.textContent = 'Salvo automaticamente';
                form.appendChild(message);
                
                setTimeout(() => message.remove(), 2000);
            } catch (error) {
                console.error('Erro no auto-save:', error);
            }
        }
    }
};

// Inicialização
function initializeApp() {
    app.init();
}

// Exporta utilidades
window.appUtils = app.utils;