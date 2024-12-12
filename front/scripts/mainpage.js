  // Function to render the hero section
  function renderHero() {
    document.getElementById("hero").innerHTML = `
      <h4>Don't throw away old tech!</h4>
      <h2>Find pieces of nostalgia!</h2>
      <h1>Guaranteed safe purchases!</h1>
      <p>Have a preview of what you might find!</p>
      <button>Shop Now</button>
    `;
  }
  
  // Function to render the feature section
  function renderFeature() {
    document.getElementById("feature").innerHTML = `
      <div class="fe-box">
          <img src="">
          <h6>Reliable Sellers</h6>
      </div>
      <div class="fe-box">
          <img src="">
          <h6>24/7 Customer Support</h6>
      </div>
      <div class="fe-box">
          <img src="">
          <h6>Reliable Sellers</h6>
      </div>
    `;
  }
  document.addEventListener("DOMContentLoaded", () => {
    renderHero();
    renderFeature();
  });