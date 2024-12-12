// cart.js

// Store products list globally
const products = [
    {
        img: "images/products/p1.png",
        brand: "Nintendo",
        name: "GameBoy Advance SP Tribal Special Edition AGS-001",
        condition: "Used",
        stars: 1,
        price: 127,
    },
    // ... rest of your products array
];

class SimpleCart {
    constructor() {
        this.items = JSON.parse(localStorage.getItem('cartItems')) || [];
        this.createCartStructure();
        this.initializeCart();
    }

    createCartStructure() {
        const cartSection = document.createElement('section');
        cartSection.id = 'cart';
        
        cartSection.innerHTML = `
            <table>
                <thead>
                    <tr>
                        <th>Product</th>
                        <th>Brand</th>
                        <th>Condition</th>
                        <th>Price</th>
                        <th>Quantity</th>
                        <th>Total</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody>
                </tbody>
            </table>
            <h2>Cart Total: $0.00</h2>
            <button onclick="location.href='checkout.html'">Proceed to Checkout</button>
            <button onclick="cart.clearCart()">Clear Cart</button>
        `;

        const footer = document.querySelector('#footer');
        if (footer) {
            footer.parentNode.insertBefore(cartSection, footer);
        } else {
            document.body.appendChild(cartSection);
        }
    }

    initializeCart() {
        this.updateDisplay();
        this.setupEventListeners();
    }

    setupEventListeners() {
        const quantityInputs = document.querySelectorAll('#cart input[type="number"]');
        quantityInputs.forEach(input => {
            input.addEventListener('change', (e) => {
                const row = e.target.closest('tr');
                const productName = row.dataset.productName;
                this.updateQuantity(productName, parseInt(e.target.value));
            });
        });

        const removeButtons = document.querySelectorAll('#cart .remove-button');
        removeButtons.forEach(button => {
            button.addEventListener('click', (e) => {
                const row = e.target.closest('tr');
                const productName = row.dataset.productName;
                this.removeItem(productName);
            });
        });
    }

    updateDisplay() {
        const tbody = document.querySelector('#cart tbody');
        tbody.innerHTML = '';

        this.items.forEach(item => {
            const row = document.createElement('tr');
            row.dataset.productName = item.name;
            row.innerHTML = `
                <td>
                    <div class="product-info">
                        <img src="${item.img}" alt="${item.name}" width="50">
                        <span>${item.name}</span>
                    </div>
                </td>
                <td>${item.brand}</td>
                <td>${item.condition}</td>
                <td>$${item.price}</td>
                <td><input type="number" value="${item.quantity}" min="1"></td>
                <td>$${(item.price * item.quantity).toFixed(2)}</td>
                <td><button class="remove-button">Remove</button></td>
            `;
            tbody.appendChild(row);
        });

        this.updateTotal();
        this.setupEventListeners();
    }

    updateTotal() {
        const total = this.items.reduce((sum, item) => sum + (item.price * item.quantity), 0);
        document.querySelector('#cart h2').textContent = `Cart Total: $${total.toFixed(2)}`;
    }

    addItem(productName) {
        // Find product in products list
        const product = products.find(p => p.name === productName);
        if (!product) return;

        const existingItem = this.items.find(item => item.name === productName);
        
        if (existingItem) {
            existingItem.quantity += 1;
        } else {
            this.items.push({
                ...product,
                quantity: 1
            });
        }

        localStorage.setItem('cartItems', JSON.stringify(this.items));
        this.updateDisplay();
    }

    removeItem(productName) {
        this.items = this.items.filter(item => item.name !== productName);
        localStorage.setItem('cartItems', JSON.stringify(this.items));
        this.updateDisplay();
    }

    updateQuantity(productName, quantity) {
        const item = this.items.find(item => item.name === productName);
        if (item) {
            item.quantity = Math.max(1, quantity);
            localStorage.setItem('cartItems', JSON.stringify(this.items));
            this.updateDisplay();
        }
    }

    clearCart() {
        this.items = [];
        localStorage.setItem('cartItems', JSON.stringify(this.items));
        this.updateDisplay();
    }
}

// Initialize cart when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    const cart = new SimpleCart();
    window.cart = cart;

    // Add "Add to Cart" buttons to product list
    const productContainer = document.querySelector('#pro-container'); // Adjust selector as needed
    if (productContainer) {
        const addToCartButtons = document.querySelectorAll('.add-to-cart-btn');
        addToCartButtons.forEach(button => {
            button.addEventListener('click', (e) => {
                const productName = e.target.dataset.productName;
                cart.addItem(productName);
            });
        });
    }
});

// Helper function to add items from anywhere
function addToCart(productName) {
    cart.addItem(productName);
}