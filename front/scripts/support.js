
function renderSupport(targetElement) {
    const supportHTML = `
    <div class="about-header">
        <h1>Support</h1>
    </div>

    <div class="support-container">
    
        <div class="support-form">
                <form id="supportForm">
                <div class="form-group">
                    <label for="username">Username</label>
                    <input type="text" id="username" name="username" required>
                </div>

        <div class="form-group">
            <label for="email">Your Email</label>
            <input type="email" id="email" name="email" required>
        </div>

        <div class="form-group">
            <label for="message">Your Message</label>
            <textarea id="message" name="message" required></textarea>
        </div>

        <button type="submit" class="submit-btn">Submit</button>
    </form>
</div>
</div>
`;

// Set the HTML content
targetElement.innerHTML = supportHTML;

// Add form submission handler
const form = targetElement.querySelector('#supportForm');
form.addEventListener('submit', function(e) {
e.preventDefault();
const formData = new FormData(form);
const data = Object.fromEntries(formData.entries());
console.log('Form submitted:', data);
// Add your form submission logic here
});
}

document.addEventListener('DOMContentLoaded', () => {
    const container = document.getElementById('supportContainer');
    renderSupport(container);
});
