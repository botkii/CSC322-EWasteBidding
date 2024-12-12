class AuthComponent {
    static render(containerId) {
        const container = document.getElementById("login-container");
        if (!container) return;

        const template = `
            <div class="auth-container">
                <div class="auth-wrapper">
                    <div class="back-button-container">
                        <button class="back-button" onclick="window.location.href='index.html'">
                            <i class="fas fa-arrow-left"></i> Back to Home
                        </button>
                    </div>
                    
                    <div class="tabs">
                        <button class="tab active" data-form="login">Login</button>
                        <button class="tab" data-form="signup">Sign Up</button>
                    </div>

                    <form id="login-form">
                        <div class="form-group">
                            <label for="login-email">Email</label>
                            <input type="email" id="login-email" required>
                            <div class="error-message" id="login-email-error"></div>
                        </div>
                        <div class="form-group">
                            <label for="login-password">Password</label>
                            <input type="password" id="login-password" required>
                            <div class="error-message" id="login-password-error"></div>
                        </div>
                        <button type="submit">
                            <i class="fas fa-sign-in-alt"></i> Login
                        </button>
                    </form>

                    <form id="signup-form">
                        <div class="form-group">
                            <label for="signup-name">Full Name</label>
                            <input type="text" id="signup-name" required>
                            <div class="error-message" id="signup-name-error"></div>
                        </div>
                        <div class="form-group">
                            <label for="signup-email">Email</label>
                            <input type="email" id="signup-email" required>
                            <div class="error-message" id="signup-email-error"></div>
                        </div>
                        <div class="form-group">
                            <label for="signup-password">Password</label>
                            <input type="password" id="signup-password" required>
                            <div class="error-message" id="signup-password-error"></div>
                        </div>
                        <div class="form-group">
                            <label for="signup-confirm-password">Confirm Password</label>
                            <input type="password" id="signup-confirm-password" required>
                            <div class="error-message" id="signup-confirm-password-error"></div>
                        </div>
                        <button type="submit">
                            <i class="fas fa-user-plus"></i> Sign Up
                        </button>
                    </form>
                </div>
            </div>
        `;

        container.innerHTML = template;
        this.initializeForms();
    }

    static initializeForms() {
        new TabManager();
        new LoginForm();
        new SignupForm();
    }
}


// Form validation utilities
const ValidationRules = {
    isValidEmail: (email) => email.includes('@'),
    isValidPassword: (password) => password.length >= 8,
    isValidName: (name) => name.length >= 2,
    doPasswordsMatch: (password, confirmPassword) => password === confirmPassword
};

class AuthForm {
    constructor(formId) {
        this.form = document.getElementById(formId);
        this.errors = {};
    }

    showError(fieldId, message) {
        const errorElement = document.getElementById(`${fieldId}-error`);
        errorElement.textContent = message;
        errorElement.style.display = 'block';
        this.errors[fieldId] = true;
    }

    clearErrors() {
        this.form.querySelectorAll('.error-message').forEach(error => {
            error.style.display = 'none';
        });
        this.errors = {};
    }

    isValid() {
        return Object.keys(this.errors).length === 0;
    }
}

class LoginForm extends AuthForm {
    constructor() {
        super('login-form');
        this.emailInput = document.getElementById('login-email');
        this.passwordInput = document.getElementById('login-password');
        this.setupEventListeners();
    }

    validate() {
        this.clearErrors();

        if (!ValidationRules.isValidEmail(this.emailInput.value)) {
            this.showError('login-email', 'Please enter a valid email address');
        }

        if (!this.passwordInput.value) {
            this.showError('login-password', 'Password is required');
        }

        return this.isValid();
    }

    handleSubmit(event) {
        event.preventDefault();
        
        if (this.validate()) {
            console.log('Login attempt:', {
                email: this.emailInput.value,
                password: this.passwordInput.value
            });
        }
    }

    setupEventListeners() {
        this.form.addEventListener('submit', (e) => this.handleSubmit(e));
    }
}

class SignupForm extends AuthForm {
    constructor() {
        super('signup-form');
        this.nameInput = document.getElementById('signup-name');
        this.emailInput = document.getElementById('signup-email');
        this.passwordInput = document.getElementById('signup-password');
        this.confirmPasswordInput = document.getElementById('signup-confirm-password');
        this.setupEventListeners();
    }

    validate() {
        this.clearErrors();

        if (!ValidationRules.isValidName(this.nameInput.value)) {
            this.showError('signup-name', 'Name must be at least 2 characters long');
        }

        if (!ValidationRules.isValidEmail(this.emailInput.value)) {
            this.showError('signup-email', 'Please enter a valid email address');
        }

        if (!ValidationRules.isValidPassword(this.passwordInput.value)) {
            this.showError('signup-password', 'Password must be at least 8 characters long');
        }

        if (!ValidationRules.doPasswordsMatch(this.passwordInput.value, this.confirmPasswordInput.value)) {
            this.showError('signup-confirm-password', 'Passwords do not match');
        }

        return this.isValid();
    }

    handleSubmit(event) {
        event.preventDefault();
        
        if (this.validate()) {
            console.log('Signup attempt:', {
                name: this.nameInput.value,
                email: this.emailInput.value,
                password: this.passwordInput.value
            });
        }
    }

    setupEventListeners() {
        this.form.addEventListener('submit', (e) => this.handleSubmit(e));
    }
}

class TabManager {
    constructor() {
        this.tabs = document.querySelectorAll('.tab');
        this.forms = document.querySelectorAll('form');
        this.setupEventListeners();
    }

    switchTab(tab) {
        const formToShow = tab.dataset.form;
        
        this.tabs.forEach(t => t.classList.remove('active'));
        tab.classList.add('active');
        
        this.forms.forEach(form => {
            form.style.display = form.id === `${formToShow}-form` ? 'block' : 'none';
        });
    }

    setupEventListeners() {
        this.tabs.forEach(tab => {
            tab.addEventListener('click', () => this.switchTab(tab));
        });
    }
}

document.addEventListener('DOMContentLoaded', () => {
    AuthComponent.render('login-container');
});