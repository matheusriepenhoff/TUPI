// Sistema de validação de formulários
const validations = {
    // Regras de validação
    rules: {
        cns: {
            pattern: /^\d{15}$/,
            message: 'CNS deve conter exatamente 15 dígitos numéricos'
        },
        idade: {
            min: 0,
            max: 120,
            message: 'Idade deve estar entre 0 e 120 anos'
        },
        pressaoSistolica: {
            min: 0,
            max: 300,
            message: 'Pressão sistólica deve estar entre 0 e 300 mmHg'
        }
    },

    // Valida formulário completo
    validateForm: function(formElement) {
        const errors = [];
        let isValid = true;

        try {
            // Validar campos obrigatórios
            const requiredFields = formElement.querySelectorAll('[required]');
            requiredFields.forEach(field => {
                if (!field.value.trim()) {
                    errors.push(`Campo "${field.previousElementSibling?.textContent || field.name}" é obrigatório`);
                    isValid = false;
                    this.markFieldAsError(field);
                }
            });

            // Validar CNS
            const cns = formElement.querySelector('[name="cns"]');
            if (cns && !this.validateCNS(cns.value)) {
                errors.push(this.rules.cns.message);
                isValid = false;
                this.markFieldAsError(cns);
            }

            // Validar idade
            const idade = formElement.querySelector('[name="idade"]');
            if (idade && !this.validateRange(idade.value, this.rules.idade)) {
                errors.push(this.rules.idade.message);
                isValid = false;
                this.markFieldAsError(idade);
            }

            // Validar exames
            const examesValidation = this.validateExames(new FormData(formElement));
            if (!examesValidation.isValid) {
                errors.push(...examesValidation.messages);
                isValid = false;
            }

            // Validar pressão sistólica
            const pressaoSistolica = formElement.querySelector('[name="pressao_sistolica"]');
            if (pressaoSistolica && !this.validateRange(pressaoSistolica.value, this.rules.pressaoSistolica)) {
                errors.push(this.rules.pressaoSistolica.message);
                isValid = false;
                this.markFieldAsError(pressaoSistolica);
            }

            // Exibir erros se houver
            if (!isValid) {
                this.showErrors(errors);
            }

            return isValid;
        } catch (error) {
            console.error('Erro na validação:', error);
            this.showErrors(['Ocorreu um erro na validação do formulário']);
            return false;
        }
    },

    // Validações específicas
    validateCNS: function(cns) {
        return this.rules.cns.pattern.test(cns);
    },

    validateRange: function(value, rule) {
        const num = parseFloat(value);
        return !isNaN(num) && num >= rule.min && num <= rule.max;
    },

    validateExames: function(formData) {
        const errors = [];
        let isValid = true;

        const colesterolTotal = parseFloat(formData.get('colesterol_total'));
        const hdl = parseFloat(formData.get('hdl'));
        const pressaoSistolica = parseFloat(formData.get('pressao_sistolica'));
        const creatinina = parseFloat(formData.get('creatinina_serica'));

        if (hdl > colesterolTotal) {
            errors.push('HDL não pode ser maior que o Colesterol Total');
            isValid = false;
        }

        if (isNaN(colesterolTotal) || colesterolTotal <= 0) {
            errors.push('Colesterol Total inválido');
            isValid = false;
        }

        if (isNaN(hdl) || hdl <= 0) {
            errors.push('HDL inválido');
            isValid = false;
        }

        if (isNaN(pressaoSistolica) || pressaoSistolica <= 0 || pressaoSistolica > 300) {
            errors.push('Pressão Sistólica inválida');
            isValid = false;
        }

        if (isNaN(creatinina) || creatinina <= 0) {
            errors.push('Creatinina Sérica inválida');
            isValid = false;
        }

        return {
            isValid,
            messages: errors
        };
    },

    // Utilidades
    markFieldAsError: function(field) {
        field.classList.add('error');
        field.addEventListener('input', function() {
            this.classList.remove('error');
        }, { once: true });
    },

    showErrors: function(errors) {
        if (errors.length > 0) {
            const message = errors.join('\n');
            alert(message); // Pode ser substituído por uma solução mais elegante
        }
    },

    clearErrors: function(formElement) {
        formElement.querySelectorAll('.error').forEach(field => {
            field.classList.remove('error');
        });
    }
};

// Inicialização das validações
document.addEventListener('DOMContentLoaded', function() {
    // Adiciona validação apenas aos formulários que não são de visita
    const forms = document.querySelectorAll('form:not(.visita-form)');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            validations.clearErrors(this);
            if (!validations.validateForm(this)) {
                e.preventDefault();
            } else {
                showLoading();
            }
        });
    });
});

// Exporta o módulo de validações
window.validations = validations;