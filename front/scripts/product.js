document.addEventListener('DOMContentLoaded', function() {
    const urlParams = new URLSearchParams(window.location.search);
    const productId = parseInt(urlParams.get('id'));
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
                
                <!-- Bidding Section -->
                <div class="bidding-section">
                    <div class="current-bid-info">
                        <h4>Current Highest Bid</h4>
                        <p class="highest-bid">$${product.highestBid || product.price}</p>
                        <p class="bid-count">${product.bidCount || 0} bids</p>
                        <p class="time-remaining" id="countdown">Time remaining: Loading...</p>
                    </div>
                    
                    <div class="place-bid">
                        <h4>Place Your Bid</h4>
                        <div class="bid-input-group">
                            <span class="currency">$</span>
                            <input type="number" 
                                id="bidAmount" 
                                min="${(product.highestBid || product.price) + 1}" 
                                step="1" 
                                placeholder="Enter bid amount">
                        </div>
                        <p class="min-bid">Minimum bid: $${(product.highestBid || product.price) + 1}</p>
                        <button onclick="placeBid(${productId})" class="bid-button">
                            Place Bid
                        </button>
                    </div>
                    
                    <!-- Bid History -->
                    <div class="bid-history">
                        <h4>Bid History</h4>
                        <div class="bid-list" id="bidList">
                            ${generateBidHistory(product.bids || [])}
                        </div>
                    </div>
                </div>

                <div class="purchase-details">
                    <button onclick="addToCart('${product.name}', ${product.price})">
                        Buy Now: $${product.price}
                    </button>
                </div>
            </div>
        `;

        // Start countdown timer if there's an end date
        if (product.endDate) {
            startCountdown(product.endDate);
        }
    } else {
        window.location.href = 'index.html';
    }
});

// Helper function to generate bid history HTML
function generateBidHistory(bids) {
    if (!bids.length) {
        return '<p class="no-bids">No bids yet</p>';
    }

    return bids
        .sort((a, b) => b.amount - a.amount)
        .map(bid => `
            <div class="bid-item">
                <span class="bid-amount">$${bid.amount}</span>
                <span class="bid-user">${bid.username}</span>
                <span class="bid-time">${new Date(bid.time).toLocaleString()}</span>
            </div>
        `)
        .join('');
}

// Function to handle placing bids
function placeBid(productId) {
    const bidAmount = parseFloat(document.getElementById('bidAmount').value);
    const product = products[productId];
    const currentHighest = product.highestBid || product.price;

    if (bidAmount <= currentHighest) {
        alert('Bid must be higher than the current highest bid');
        return;
    }

    // Here you would typically make an API call to your backend
    // For now, we'll just update the frontend
    product.highestBid = bidAmount;
    product.bidCount = (product.bidCount || 0) + 1;
    product.bids = product.bids || [];
    product.bids.push({
        amount: bidAmount,
        username: 'Current User', // Replace with actual logged-in username
        time: new Date()
    });

    // Refresh the display
    document.querySelector('.highest-bid').textContent = `$${bidAmount}`;
    document.querySelector('.bid-count').textContent = `${product.bidCount} bids`;
    document.querySelector('.min-bid').textContent = `Minimum bid: $${bidAmount + 1}`;
    document.getElementById('bidAmount').min = bidAmount + 1;
    document.getElementById('bidList').innerHTML = generateBidHistory(product.bids);
}

// Function to handle countdown timer
function startCountdown(endDate) {
    const countdownElement = document.getElementById('countdown');
    const end = new Date(endDate).getTime();

    const timer = setInterval(() => {
        const now = new Date().getTime();
        const distance = end - now;

        const days = Math.floor(distance / (1000 * 60 * 60 * 24));
        const hours = Math.floor((distance % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
        const minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
        const seconds = Math.floor((distance % (1000 * 60)) / 1000);

        countdownElement.textContent = `Time remaining: ${days}d ${hours}h ${minutes}m ${seconds}s`;

        if (distance < 0) {
            clearInterval(timer);
            countdownElement.textContent = 'Auction ended';
            document.querySelector('.bid-button').disabled = true;
        }
    }, 1000);
}