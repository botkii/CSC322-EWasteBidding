function renderAbout(){
    document.getElementById("about").innerHTML = `
            <h1>About Us</h1>
            <h2>Our Story</h2>
            <p>
            Greetings and welcome to the E-Waste Market. We are, quite literally, obsessed with the prospect of connecting people to products 
            that are truly one-of-a-kind and of the utmost quality. Whether you happen to be a collector, an aficionado, or simply someone in 
            search of something that might be described as "special," we are dedicated to making your experience that much more "you" and, ideally, enjoyable.
            </p>
            <h2>Contact Us</h2>
            <p>Have questions? Feel free to <a href="support.html">reach out to our support team</a>.</p>`
}

document.addEventListener("DOMContentLoaded", () =>{
    renderAbout();
});