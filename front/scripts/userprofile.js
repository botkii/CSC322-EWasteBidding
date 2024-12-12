// Sample user data
const userData = {
    username: "JohnDoe",
    email: "john@example.com",
    status: "member",
    balance: 1250.75,  // Added balance field
    listings: [
        {
            id: 1,
            title: "OEM 8GB Memory Card for Sony PlayStation PS Vita",
            price: 299.99,
            description: "Classic 1960s camera in excellent condition",
            status: "active"
        },
        {
            id: 2,
            title: "OEM 8GB Memory Card for Sony PlayStation PS Vita",
            price: 850.00,
            description: "Barely used, great for trails",
            status: "pending"
        }
    ],
    ratings: 3.0,
};

// Function to generate profile HTML
function generateProfileHTML(userData) {
    document.getElementById("profile-container").innerHTML = `
        <div class="profile-header">
            <h2>User Profile</h2>
            <span class="status-badge ${userData.status}">
                ${userData.status}
            </span>
        </div>

        <!-- User Information -->
        <div class="user-info">
            <div class="info-group">
                <label>Username</label>
                <p>${userData.username}</p>
            </div>

            <div class="info-group">
                <label>Email</label>
                <p>${userData.email}</p>
            </div>
            <div class="info-group">
                <label>Balance</label>
                <p>$${userData.balance.toFixed(2)}</p>
            </div>
        </div>

         <!-- Listings Section -->
        <div class="listings-section">
            <div class="listings-header">
                <h3>My Listings</h3>
                <button class="add-listing-btn" onclick="toggleListingForm()">Add New Listing</button>
            </div>

            <!-- New Listing Form (hidden by default) -->
            <form id="new-listing-form" class="listing-form" style="display: none;" onsubmit="handleNewListing(event)">
                <h4>Create New Listing</h4>
                <div class="form-group">
                    <label for="title">Title</label>
                    <input type="text" id="title" required>
                </div>
                <div class="form-group">
                    <label for="price">Price ($)</label>
                    <input type="number" id="price" step="0.01" required>
                </div>
                <div class="form-group">
                    <label for="description">Description</label>
                    <textarea id="description" required></textarea>
                </div>
                <div class="form-buttons">
                    <button type="submit" class="submit-btn">Create Listing</button>
                    <button type="button" class="cancel-btn" onclick="toggleListingForm()">Cancel</button>
                </div>
            </form>

            <!-- Current Listings -->
            <div class="listings-grid">
                ${generateListingsHTML(userData.listings)}
            </div>
        </div>
    `;
}

function generateListingsHTML(listings) {
    if (!listings.length) {
        return '<p class="no-listings">No listings yet</p>';
    }

    return listings.map(listing => `
        <div class="listing-card">
            <div class="listing-header">
                <h4>${listing.title}</h4>
                <span class="listing-status ${listing.status}">${listing.status}</span>
            </div>
            <p class="listing-price">$${listing.price.toFixed(2)}</p>
            <p class="listing-description">${listing.description}</p>
            <div class="listing-actions">
                <button onclick="editListing(${listing.id})">Edit</button>
                <button onclick="deleteListing(${listing.id})">Delete</button>
            </div>
        </div>
    `).join('');
}


// Toggle new listing form visibility
function toggleListingForm() {
    const form = document.getElementById('new-listing-form');
    form.style.display = form.style.display === 'none' ? 'block' : 'none';
}

// Handle new listing submission
function handleNewListing(event) {
    event.preventDefault();
    
    const newListing = {
        id: Date.now(), // Simple way to generate unique ID
        title: document.getElementById('title').value,
        price: parseFloat(document.getElementById('price').value),
        description: document.getElementById('description').value,
        status: 'pending'
    };

    userData.listings.push(newListing);
    generateProfileHTML(userData);
    toggleListingForm();
}

// Edit listing (placeholder function)
function editListing(id) {
    console.log(`Edit listing ${id}`);
    // Add your edit logic here
}

// Delete listing
function deleteListing(id) {
    userData.listings = userData.listings.filter(listing => listing.id !== id);
    generateProfileHTML(userData);
}


// Initialize profile when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    const profileContainer = document.getElementById("profile-container");
    
    if (profileContainer) {
        generateProfileHTML(userData);
    }
});