// Get query parameters from the URL
const params = new URLSearchParams(window.location.search);
const index = params.get("index");

// Your products array
const products = [
  {
    img: "images/products/p1.png",
    brand: "Nintendo",
    name: "GameBoy Advance SP Tribal Special Edition AGS-001",
    condition: "Used",
    stars: 1,
    price: 127,
    description: "A rare and collectible handheld gaming console, featuring a tribal design. Perfect for nostalgic gaming enthusiasts.",
  },
  {
    img: "images/products/p2.png",
    brand: "Sony",
    name: "OEM 8GB Memory Card for Sony PlayStation PS Vita",
    condition: "Used",
    stars: 1,
    price: 12,
    description: "This OEM memory card is compatible with Sony PlayStation PS Vita, offering reliable storage for your games and data.",
  },
  {
    img: "images/products/p3.png",
    brand: "Sony",
    name: "Walkman WM-AF54 Sports Yellow Cassette Player",
    condition: "Used",
    stars: 1,
    price: 90,
    description: "The classic Walkman WM-AF54 sports cassette player with a vibrant yellow design. Ideal for retro music lovers.",
  },
];

// Get the selected product
const product = products[index];

if (product) {
  // Render the product details
  const productDetailsContainer = document.getElementById("productDetails");
  productDetailsContainer.innerHTML = `
    <div class="pro-details">
      <img src="${product.img}" alt="${product.name}">
      <div class="details">
        <h1>${product.name}</h1>
        <h3>Brand: ${product.brand}</h3>
        <h4>Condition: ${product.condition}</h4>
        <h4>Price: $${product.price}</h4>
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
        <p>${product.description}</p> 
      </div>
    </div>
  `;
} else {
  // Handle invalid product index
  document.getElementById("productDetails").innerHTML = "<h1>Product not found!</h1>";
}