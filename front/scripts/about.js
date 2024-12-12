function renderAbout() {
    document.getElementById("about-container").innerHTML = `
        <div class="about-header">
            <h1>About Us</h1>
        </div>
        
        <div class="story-section">
            <div class="story-box">
                <h2>Our Story</h2>
                <p>Greetings and welcome to the E-Waste Market. We are, quite literally, obsessed with the prospect of connecting people to products 
                that are truly one-of-a-kind and of the utmost quality. Whether you happen to be a collector, an aficionado, or simply someone in 
                search of something that might be described as "special," we are dedicated to making your experience that much more "you" and, ideally, enjoyable.</p>
            </div>
        </div>
    `;
}

// Initialize about page when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    const aboutContainer = document.getElementById("about-container");
    
    if (aboutContainer) {
        renderAbout();
    }
});

