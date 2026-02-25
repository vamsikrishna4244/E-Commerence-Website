from flask import Blueprint, render_template, url_for, flash, redirect, request
from app import db
from app.forms import ProductForm
from app.utils import admin_required
import datetime

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/dashboard')
@admin_required
def dashboard():
    # Admin overview: counts of products and orders
    products_count = len(db.collection('products').get())
    orders_ref = db.collection('orders').order_by('created_at', direction='DESCENDING').get()
    orders = []
    for o in orders_ref:
        order = o.to_dict()
        order['id'] = o.id
        orders.append(order)
    
    return render_template('admin/dashboard.html', products_count=products_count, orders=orders)

@admin_bp.route('/products')
@admin_required
def manage_products():
    products_ref = db.collection('products').get()
    products = []
    for p in products_ref:
        prod = p.to_dict()
        prod['id'] = p.id
        products.append(prod)
    return render_template('admin/products.html', products=products)

@admin_bp.route('/product/new', methods=['GET', 'POST'])
@admin_required
def new_product():
    form = ProductForm()
    if form.validate_on_submit():
        product_data = {
            'name': form.name.data,
            'description': form.description.data,
            'price': float(form.price.data),
            'category': form.category.data,
            'image_url': form.image_url.data,
            'created_at': datetime.datetime.now()
        }
        db.collection('products').add(product_data)
        flash('Product created successfully!', 'success')
        return redirect(url_for('admin.manage_products'))
    return render_template('admin/product_form.html', title='New Product', form=form)

@admin_bp.route('/product/<product_id>/edit', methods=['GET', 'POST'])
@admin_required
def edit_product(product_id):
    product_ref = db.collection('products').document(product_id).get()
    if not product_ref.exists:
        flash('Product not found.', 'danger')
        return redirect(url_for('admin.manage_products'))
    
    product = product_ref.to_dict()
    form = ProductForm()
    if form.validate_on_submit():
        update_data = {
            'name': form.name.data,
            'description': form.description.data,
            'price': float(form.price.data),
            'category': form.category.data,
            'image_url': form.image_url.data
        }
        db.collection('products').document(product_id).update(update_data)
        flash('Product updated successfully!', 'success')
        return redirect(url_for('admin.manage_products'))
    elif request.method == 'GET':
        form.name.data = product['name']
        form.description.data = product['description']
        form.price.data = product['price']
        form.category.data = product['category']
        form.image_url.data = product.get('image_url', '')
        
    return render_template('admin/product_form.html', title='Edit Product', form=form)

@admin_bp.route('/product/<product_id>/delete', methods=['POST'])
@admin_required
def delete_product(product_id):
    db.collection('products').document(product_id).delete()
    flash('Product deleted.', 'info')
    return redirect(url_for('admin.manage_products'))
