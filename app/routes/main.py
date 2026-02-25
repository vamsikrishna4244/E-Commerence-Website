from flask import Blueprint, render_template, request, jsonify, session, flash, redirect, url_for
from app import db
from flask_login import current_user, login_required

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
@main_bp.route('/home')
def home():
    # Fetch featured products from Firestore
    products_ref = db.collection('products').limit(8).get()
    products = []
    for p in products_ref:
        prod = p.to_dict()
        prod['id'] = p.id
        products.append(prod)
    return render_template('index.html', products=products)

@main_bp.route('/products')
def product_list():
    category = request.args.get('category')
    search_query = request.args.get('q')
    
    query = db.collection('products')
    
    if category:
        query = query.where('category', '==', category)
    
    products_ref = query.get()
    products = []
    for p in products_ref:
        prod = p.to_dict()
        prod['id'] = p.id
        # Simple search filter (client-side or here)
        if search_query and search_query.lower() not in prod['name'].lower():
            continue
        products.append(prod)
        
    return render_template('product_list.html', products=products)

@main_bp.route('/product/<product_id>')
def product_detail(product_id):
    product_ref = db.collection('products').document(product_id).get()
    if not product_ref.exists:
        return render_template('errors/404.html'), 404
    product = product_ref.to_dict()
    product['id'] = product_ref.id
    return render_template('product_detail.html', product=product)

@main_bp.route('/cart')
def view_cart():
    cart = session.get('cart', {})
    # Fetch product details for items in cart
    cart_items = []
    total = 0
    for product_id, quantity in cart.items():
        p_ref = db.collection('products').document(product_id).get()
        if p_ref.exists:
            p_data = p_ref.to_dict()
            p_data['id'] = p_ref.id
            p_data['quantity'] = quantity
            p_data['subtotal'] = p_data['price'] * quantity
            total += p_data['subtotal']
            cart_items.append(p_data)
            
    return render_template('cart.html', cart_items=cart_items, total=total)

@main_bp.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    product_id = request.form.get('product_id')
    quantity = int(request.form.get('quantity', 1))
    
    cart = session.get('cart', {})
    cart[product_id] = cart.get(product_id, 0) + quantity
    session['cart'] = cart
    
    return jsonify({
        'status': 'success',
        'cart_count': sum(cart.values()),
        'message': 'Product added to cart!'
    })

@main_bp.route('/update_cart', methods=['POST'])
def update_cart():
    product_id = request.form.get('product_id')
    action = request.form.get('action') # 'increase', 'decrease', 'remove'
    
    cart = session.get('cart', {})
    if product_id in cart:
        if action == 'increase':
            cart[product_id] += 1
        elif action == 'decrease':
            cart[product_id] -= 1
            if cart[product_id] <= 0:
                del cart[product_id]
        elif action == 'remove':
            del cart[product_id]
            
    session['cart'] = cart
    return jsonify({
        'status': 'success',
        'cart_count': sum(cart.values())
    })

from app.forms import CheckoutForm
import datetime

@main_bp.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    cart = session.get('cart', {})
    if not cart:
        flash('Your cart is empty!', 'warning')
        return redirect(url_for('main.product_list'))

    form = CheckoutForm()
    # Fetch cart details for summary
    cart_items = []
    total = 0
    for product_id, quantity in cart.items():
        p_ref = db.collection('products').document(product_id).get()
        if p_ref.exists:
            p_data = p_ref.to_dict()
            p_data['price'] = float(p_data['price'])
            total += p_data['price'] * quantity
            cart_items.append({
                'id': product_id, 
                'name': p_data['name'], 
                'price': p_data['price'], 
                'quantity': quantity,
                'image_url': p_data.get('image_url')
            })

    if form.validate_on_submit():
        # Create order in Firestore
        order_data = {
            'user_id': current_user.id,
            'items': cart_items,
            'total': total,
            'status': 'Processing',
            'shipping_info': {
                'name': form.full_name.data,
                'address': form.address.data,
                'city': form.city.data,
                'zip': form.zip_code.data
            },
            'created_at': datetime.datetime.now()
        }
        db.collection('orders').add(order_data)
        
        # Send Order Confirmation Email
        try:
            from app.utils import send_email
            send_email(
                f'Order Confirmation - EShop Pro #{datetime.datetime.now().strftime("%Y%m%d%H%M")}',
                sender=None,
                recipients=[current_user.email],
                text_body=f"Hi {form.full_name.data},\n\nThank you for your order! We've received your order and are processing it.\n\nTotal: ${total:.2f}\n\nBest regards,\nThe EShop Pro Team",
                html_body=render_template('email/order_confirmation.html', order=order_data, user=current_user)
            )
        except Exception as e:
            print(f"Failed to send order confirmation email: {e}")

        # Clear cart
        session.pop('cart', None)
        flash('Order placed successfully! Thank you for shopping with us.', 'success')
        return redirect(url_for('main.dashboard'))
        
    return render_template('checkout.html', form=form, total=total, cart_items=cart_items)

@main_bp.route('/dashboard')
@login_required
def dashboard():
    # Fetch user orders from Firestore
    orders_ref = db.collection('orders').where('user_id', '==', current_user.id).get()
    orders = []
    for o in orders_ref:
        order = o.to_dict()
        order['id'] = o.id
        orders.append(order)
    return render_template('dashboard.html', user=current_user, orders=orders)

@main_bp.route('/hello')
def hello():
    return render_template('hello.html')
