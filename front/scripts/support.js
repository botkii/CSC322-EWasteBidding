function renderAbout(){
    document.getElementById("support").innerHTML = `
            <h2>How Can We Help?</h2>
            <form action="support_submit.html" method="post">
            <label for="name">Username:</label>
            <input type="text" id="name" name="name" required>
            <label for="email">Your Email:</label>
            <input type="email" id="email" name="email" required>
            <label for="message">Your Message:</label>
            <textarea id="message" name="message" rows="4" required></textarea>
            <button type="submit">Submit</button>
            </form>
            <h2>Contact Information</h2>
            <p>Email: support@example.com</p>
            <p>Phone: +1 234 567 890</p>`
}

document.addEventListener("DOMContentLoaded", () =>{
    renderAbout();
});
    


