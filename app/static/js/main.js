document.addEventListener('DOMContentLoaded', function () {
    // Page fade-in effect
    document.body.classList.add('page-fade-in');

    // Add to Cart AJAX
    const addToCartForms = document.querySelectorAll('.add-to-cart-form');
    addToCartForms.forEach(form => {
        form.addEventListener('submit', function (e) {
            e.preventDefault();
            const formData = new FormData(this);

            fetch('/add_to_cart', {
                method: 'POST',
                body: formData,
                headers: {
                    'X-CSRFToken': document.querySelector('meta[name="csrf-token"]')?.content || ''
                }
            })
                .then(response => response.json())
                .then(data => {
                    if (data.status === 'success') {
                        // Update cart count in nav
                        document.getElementById('cart-count').textContent = data.cart_count;

                        // Show toast notification
                        const toastMsg = document.getElementById('toast-message');
                        toastMsg.textContent = data.message;
                        const toastLiveExample = document.getElementById('liveToast');
                        const toast = new bootstrap.Toast(toastLiveExample);
                        toast.show();
                    }
                })
                .catch(error => console.error('Error:', error));
        });
    });

    // Update Cart Quantity AJAX
    const updateButtons = document.querySelectorAll('.update-cart-btn');
    updateButtons.forEach(btn => {
        btn.addEventListener('click', function () {
            const productId = this.dataset.productId;
            const action = this.dataset.action;

            const formData = new FormData();
            formData.append('product_id', productId);
            formData.append('action', action);

            fetch('/update_cart', {
                method: 'POST',
                body: formData,
                headers: {
                    'X-CSRFToken': document.querySelector('meta[name="csrf-token"]')?.content || ''
                }
            })
                .then(response => response.json())
                .then(data => {
                    if (data.status === 'success') {
                        // Reload page to reflect changes in cart items and total
                        location.reload();
                    }
                })
                .catch(error => console.error('Error:', error));
        });
    });

    // Micro-interactions for glass cards
    const glassCards = document.querySelectorAll('.glass-card');
    glassCards.forEach(card => {
        card.addEventListener('mouseenter', function () {
            this.style.transition = 'all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275)';
        });
    });
});
