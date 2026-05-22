/**
 * CardNova - Main JavaScript
 * Handles: Auth Modal UI, Product Grid, Cart Interactions, CSRF Protection
 * Compatible with Django Templates & Session Auth
 */

// ============================================
// 🔐 CSRF Token Helper (Required for Django AJAX)
// ============================================
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
const csrftoken = getCookie('csrftoken');

// ============================================
// 🎯 DOM Elements Cache
// ============================================
const authModal = document.getElementById('authModal');
const authNavBtn = document.getElementById('authNavBtn');
const closeAuth = document.getElementById('closeAuthModal');
const loginForm = document.getElementById('loginForm');
const signupForm = document.getElementById('signupForm');
const showSignupLink = document.getElementById('showSignupLink');
const showLoginLink = document.getElementById('showLoginLink');
const loginAlert = document.getElementById('loginAlert');
const signupAlert = document.getElementById('signupAlert');
const productGrid = document.getElementById('productGrid');
const categoriesGrid = document.getElementById('categoriesGrid');
const shopNowBtn = document.getElementById('shopNowHeroBtn');
const exploreBtn = document.getElementById('exploreBtn');
const shopBanner = document.getElementById('shopBanner');

// ============================================
// 🔁 Modal UI Functions
// ============================================
function openAuthModal() {
    if (!authModal) return;
    // Reset to login view
    if (loginForm) loginForm.style.display = 'block';
    if (signupForm) signupForm.style.display = 'none';
    if (loginAlert) loginAlert.style.display = 'none';
    if (signupAlert) signupAlert.style.display = 'none';
    authModal.classList.add('active');
    document.body.style.overflow = 'hidden'; // Prevent background scroll
}

function closeAuthModalHandler() {
    if (!authModal) return;
    authModal.classList.remove('active');
    document.body.style.overflow = ''; // Restore scroll
}

function switchToSignup(e) {
    e.preventDefault();
    if (loginForm) loginForm.style.display = 'none';
    if (signupForm) signupForm.style.display = 'block';
    if (loginAlert) loginAlert.style.display = 'none';
    if (signupAlert) signupAlert.style.display = 'none';
}

function switchToLogin(e) {
    e.preventDefault();
    if (loginForm) loginForm.style.display = 'block';
    if (signupForm) signupForm.style.display = 'none';
    if (loginAlert) loginAlert.style.display = 'none';
    if (signupAlert) signupAlert.style.display = 'none';
}

function showAlert(element, message, type) {
    if (!element) return;
    element.textContent = message;
    element.className = `alert alert-${type}`;
    element.style.display = 'block';
    // Auto-hide after 4 seconds
    setTimeout(() => {
        element.style.display = 'none';
    }, 4000);
}

// ============================================
// 🛒 Product Grid Rendering (Django Fallback)
// ============================================
// This runs only if productGrid exists AND has no Django-rendered products
function renderProductGridFallback() {
    if (!productGrid || productGrid.children.length > 0) return;

    // Demo products (replace with real API call or Django template rendering)
    const demoProducts = [
        { id: 1, name: "Blue-Eyes White Dragon - Ultra Rare", price: 2499, salePrice: 1899, image: "https://placehold.co/400x400/1a1a1a/ff6b00?text=Blue-Eyes", inStock: true },
        { id: 2, name: "Dark Magician - Holographic", price: 2799, salePrice: 2199, image: "https://placehold.co/400x400/1a1a1a/ff6b00?text=Dark+Magician", inStock: true },
        { id: 3, name: "Exodia the Forbidden One - Complete Set", price: 4999, salePrice: 3999, image: "https://placehold.co/400x400/1a1a1a/ff6b00?text=Exodia+Set", inStock: false },
        { id: 4, name: "Red-Eyes Black Dragon - Limited Edition", price: 3299, salePrice: 2699, image: "https://placehold.co/400x400/1a1a1a/ff6b00?text=Red-Eyes", inStock: true },
        { id: 5, name: "Pokemon TCG - Charizard VMAX", price: 5499, salePrice: 4999, image: "https://placehold.co/400x400/1a1a1a/ff6b00?text=Charizard", inStock: true },
        { id: 6, name: "One Piece Card - Luffy Gear 5", price: 1899, salePrice: 1499, image: "https://placehold.co/400x400/1a1a1a/ff6b00?text=Luffy+G5", inStock: true }
    ];

    productGrid.innerHTML = demoProducts.map(product => `
        <div class="product-card">
            <img class="product-image" src="${product.image}" alt="${product.name}" loading="lazy">
            <div class="product-info">
                <div class="product-name">${product.name}</div>
                <div class="product-price">
                    <span class="regular-price">₹${product.price}</span>
                    ${product.salePrice ? `<span class="sale-price">₹${product.salePrice}</span>` : ''}
                </div>
                ${product.inStock 
                    ? `<button class="btn btn-small btn-primary add-to-cart" data-id="${product.id}" data-name="${product.name}">Add to Cart 🛒</button>` 
                    : `<div class="out-of-stock">Out of Stock</div>`
                }
            </div>
        </div>
    `).join('');

    // Attach cart event listeners
    attachCartListeners();
}

// ============================================
// 🛒 Add to Cart Functionality
// ============================================
function attachCartListeners() {
    document.querySelectorAll('.add-to-cart').forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            
            const productId = this.dataset.id;
            const productName = this.dataset.name;
            
            // Check if user is logged in (Django passes this via data attribute on body)
            const isLoggedIn = document.body.dataset.userLoggedIn === 'true';
            
            if (!isLoggedIn) {
                // Show auth modal if guest
                openAuthModal();
                showAlert(loginAlert, 'Please login to add items to your cart', 'error');
                return;
            }
            
            // Demo: Show success message (replace with real AJAX to Django endpoint)
            showAlert(document.createElement('div'), `✨ "${productName}" added to cart!`, 'success');
            
            // Optional: Update cart count in navbar (if you add a cart counter element)
            // const cartCount = document.querySelector('.cart-count');
            // if (cartCount) cartCount.textContent = parseInt(cartCount.textContent) + 1;
            
            // Visual feedback on button
            const originalText = this.innerHTML;
            this.innerHTML = 'Added! ✓';
            this.disabled = true;
            setTimeout(() => {
                this.innerHTML = originalText;
                this.disabled = false;
            }, 1500);
        });
    });
}

// ============================================
// 📂 Categories Grid Interactions
// ============================================
function attachCategoryListeners() {
    if (!categoriesGrid) return;
    
    categoriesGrid.querySelectorAll('.category-card').forEach(card => {
        card.addEventListener('click', function() {
            const categoryName = this.querySelector('h3')?.textContent || 'Collection';
            // Scroll to products section and filter (demo)
            document.getElementById('productsSection')?.scrollIntoView({ behavior: 'smooth' });
            showAlert(document.createElement('div'), `🔍 Showing ${categoryName} collection...`, 'success');
        });
    });
}

// ============================================
// 🎨 Smooth Scroll & UI Enhancements
// ============================================
function attachScrollListeners() {
    if (shopNowBtn) {
        shopNowBtn.addEventListener('click', function(e) {
            e.preventDefault();
            document.getElementById('productsSection')?.scrollIntoView({ behavior: 'smooth' });
        });
    }
    
    if (exploreBtn) {
        exploreBtn.addEventListener('click', function(e) {
            e.preventDefault();
            showAlert(document.createElement('div'), '✨ Explore exclusive drops & limited editions coming soon! ✨', 'success');
        });
    }
    
    if (shopBanner) {
        shopBanner.addEventListener('click', function() {
            document.getElementById('productsSection')?.scrollIntoView({ behavior: 'smooth' });
        });
    }
}

// ============================================
// 🚀 Initialize Everything on DOM Ready
// ============================================
document.addEventListener('DOMContentLoaded', function() {
    // 1. Modal Event Listeners
    if (authNavBtn) authNavBtn.addEventListener('click', openAuthModal);
    if (closeAuth) closeAuth.addEventListener('click', closeAuthModalHandler);
    if (authModal) {
        authModal.addEventListener('click', function(e) {
            if (e.target === authModal) closeAuthModalHandler();
        });
    }
    
    // 2. Form Switching
    if (showSignupLink) showSignupLink.addEventListener('click', switchToSignup);
    if (showLoginLink) showLoginLink.addEventListener('click', switchToLogin);
    
    // 3. Render fallback products if Django didn't render any
    renderProductGridFallback();
    
    // 4. Attach cart & category listeners
    attachCartListeners();
    attachCategoryListeners();
    
    // 5. Smooth scroll interactions
    attachScrollListeners();
    
    // 6. Handle Django form submission messages (passed via template)
    // Django can inject alerts via template variables like {{ login_message }}
    // Example: if login failed, Django renders <div id="djangoAlert" class="alert alert-error">Invalid credentials</div>
    const djangoAlert = document.getElementById('djangoAlert');
    if (djangoAlert && djangoAlert.textContent.trim()) {
        const targetForm = djangoAlert.closest('#loginForm') ? loginAlert : signupAlert;
        if (targetForm) {
            targetForm.textContent = djangoAlert.textContent;
            targetForm.className = djangoAlert.className;
            targetForm.style.display = 'block';
            djangoAlert.remove(); // Clean up
        }
    }
    
    // 7. Auto-close modal after successful Django form submit (if redirected back with success param)
    const urlParams = new URLSearchParams(window.location.search);
    if (urlParams.get('auth_success') === '1' && authModal) {
        closeAuthModalHandler();
        showAlert(document.createElement('div'), '✅ Authentication successful! Welcome to CardNova.', 'success');
        // Clean URL
        window.history.replaceState({}, document.title, window.location.pathname);
    }
    
    console.log('✅ CardNova frontend initialized');
});

// ============================================
// 🌐 Optional: AJAX Helper for Future API Calls
// ============================================
// Example usage: fetchCartData(), addToCartAPI(productId), etc.
async function djangoFetch(url, options = {}) {
    const config = {
        headers: {
            'X-CSRFToken': csrftoken,
            'Content-Type': 'application/json',
            ...options.headers
        },
        credentials: 'same-origin', // Include cookies for session auth
        ...options
    };
    
    try {
        const response = await fetch(url, config);
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        return await response.json();
    } catch (error) {
        console.error('Fetch error:', error);
        showAlert(document.createElement('div'), '⚠️ Network error. Please try again.', 'error');
        throw error;
    }
}

// Export for module usage (optional)
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { djangoFetch, getCookie };
}