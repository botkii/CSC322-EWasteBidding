const products = [
  {
    img: "images/products/p1.png",
    brand: "Nintendo",
    name: "GameBoy Advance SP Tribal Special Edition AGS-001",
    condition: "Used",
    stars: 1,
    price: 127,
  },
  {
    img: "images/products/p2.png",
    brand: "Sony",
    name: "OEM 8GB Memory Card for Sony PlayStation PS Vita",
    condition: "Used",
    stars: 1,
    price: 12,
  },
  {
    img: "images/products/p3.png",
    brand: "Sony",
    name: "Walkman WM-AF54 Sports Yellow Cassette Player",
    condition: "Used",
    stars: 1,
    price: 90,
  },
  {
    img: "images/products/p4.png",
    brand: "Cybiko",
    name: "Vintage PDA Wireless Entertainment System *RARE* CLEAR PURPLE",
    condition: "Used",
    stars: 1,
    price: 137,
  },
  {
    img: "images/products/p1.png",
    brand: "Nintendo",
    name: "GameBoy Advance SP Tribal Special Edition AGS-001",
    condition: "Used",
    stars: 1,
    price: 127,
  },
  {
    img: "images/products/p1.png",
    brand: "Nintendo",
    name: "GameBoy Advance SP Tribal Special Edition AGS-001",
    condition: "Used",
    stars: 1,
    price: 127,
  },
  {
    img: "images/products/p1.png",
    brand: "Nintendo",
    name: "GameBoy Advance SP Tribal Special Edition AGS-001",
    condition: "Used",
    stars: 1,
    price: 127,
  },
  {
    img: "images/products/p1.png",
    brand: "Nintendo",
    name: "GameBoy Advance SP Tribal Special Edition AGS-001",
    condition: "Used",
    stars: 1,
    price: 127,
  },
  {
    img: "images/products/p1.png",
    brand: "Nintendo",
    name: "GameBoy Advance SP Tribal Special Edition AGS-001",
    condition: "Used",
    stars: 1,
    price: 127,
  },
  {
    img: "images/products/p1.png",
    brand: "Nintendo",
    name: "GameBoy Advance SP Tribal Special Edition AGS-001",
    condition: "Used",
    stars: 1,
    price: 127,
  },
  {
    img: "images/products/p1.png",
    brand: "Nintendo",
    name: "GameBoy Advance SP Tribal Special Edition AGS-001",
    condition: "Used",
    stars: 1,
    price: 127,
  },
  {
    img: "images/products/p1.png",
    brand: "Nintendo",
    name: "GameBoy Advance SP Tribal Special Edition AGS-001",
    condition: "Used",
    stars: 1,
    price: 127,
  },
];

const productContainer = document.getElementById("productContainer");
if (productContainer) {
  products.forEach((product, index) => {
    const productHTML = `
      <div class="pro" data-index="${index}">
        <img src="${product.img}" alt="${product.name}">
        <div class="des">
          <span>${product.brand}</span>
          <h5>${product.name}</h5>
          <h5>Condition: ${product.condition}</h5>
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
          <h4>$${product.price}</h4>
        </div>
        <a href="#" class="cart"><i class="fal fa-shopping-cart"></i></a>
      </div>
    `;
    productContainer.insertAdjacentHTML("beforeend", productHTML);
  });

  // Delegate click events
  productContainer.addEventListener("click", (event) => {
    const card = event.target.closest(".pro");
    if (card) {
      const index = card.getAttribute("data-index");
      window.location.href = `listing_item.html?index=${index}`;
    }

    if (event.target.classList.contains("cart")) {
      event.preventDefault();
      alert("Added to cart!");
    }
  });
}
