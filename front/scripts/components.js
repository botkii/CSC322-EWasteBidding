// Function to render the header section
function renderHeader() {
    // Get the current page's filename
    const currentPage = window.location.pathname.split("/").pop();
  
    // Define the navbar HTML with dynamic active class
    document.getElementById("header").innerHTML = `
      <a href="#"><img src="images/logo.png" class="logo" alt=""></a>
      <ul id="navbar">
          <li><a href="index.html" ${currentPage === "index.html" ? 'class="active"' : ""}>Home</a></li>
          <li><a href="active_listing.html" ${currentPage === "active_listing.html" ? 'class="active"' : ""}>Active Listings</a></li>
          <li><a href="about.html" ${currentPage === "about.html" ? 'class="active"' : ""}>About</a></li>
          <li><a href="support.html" ${currentPage === "support.html" ? 'class="active"' : ""}>Support</a></li>
          <li><a href="user_profile.html" ${currentPage === "user_profile.html" ? 'class="active"' : ""}><i class="fas fa-user"></i></a></li>
          <li><a href="cart.html" ${currentPage === "cart.html" ? 'class="active"' : ""}><i class="far fa-shopping-bag"></i></a></li>
      </ul>
      <div id="mobile">
          <a href="cart.html"><i class="far fa-shopping-bag"></i></a>
          <i id="bar" class="fas fa-outdent"></i>
      </div>
    `;
  }

  function renderFooter() {
    document.getElementById("footer").innerHTML =  `
        <div class="col">
        <img class="logo" src="images/logo.png" alt="">
        <h4>Contact</h4>
        <p><strong>Address:</strong> 160 Convent Ave, New York, NY 10031</p>
        <div class="github">
            <h4>GitHub Repository</h4>
            <div class="icon">
                <i class="fab fa-github"></i>
            </div>
        </div>
    </div>

    <div class="col">
        <h4>About</h4>
        <a href="#">About Us</a>
    </div>

    <div class="col">
        <h4>My Account</h4>
        <a href="#">Sign In</a>
        <a href="#">View Cart</a>
        <a href="#">Support</a>
    </div>

    <div class="credits">
        <p>E-Waste Market - Group K: Mudassir Sami, Eduardo Torres, Kenneth Wong</p>
    </div>
    `
  }
  
  // Call functions to render sections
  document.addEventListener("DOMContentLoaded", () => {
    renderHeader();
    renderFooter();
  });
  