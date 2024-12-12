document.addEventListener('DOMContentLoaded', function() {
    // Get product ID from URL
    const urlParams = new URLSearchParams(window.location.search);
    const productId = parseInt(urlParams.get('id'));
    
    // Get product details
    const product = products[productId];

    

    if (product) {
        const prodetails = document.getElementById('prodetails');
        prodetails.innerHTML = `
            <div class="back-to-listings">
                <button onclick="window.location.href='active_listing.html'">
                     <i class="fas fa-arrow-left"></i> Back to Listings
                </button>
            </div>

            <div class="single-pro-image">
                <img src="${product.img}" width="100%" id="MainImg" alt="${product.name}">
            </div>

            <div class="single-pro-details">
                <h6>${product.brand}</h6>
                <h2>${product.name}</h2>
                <h3>$${product.price}</h3>
                <div class="product-details">
                    <span>Condition: ${product.condition}</span>
                    <div class="star">
                        ${Array(5)
                            .fill("")
                            .map((_, i) =>
                                i < product.stars
                                    ? '<i class="fas fa-star"></i>'
                                    : '<i class="far fa-star"></i>'
                            )
                            .join("")}
                    </div>
                </div>
                <div class="purchase-details">
                    <button onclick="addToCart('${product.name}', ${product.price})">
                        Add To Cart
                    </button>
                </div>
            </div>
        `;
    } else {
        window.location.href = 'index.html';
    }
});