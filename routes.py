from flask import Blueprint, render_template, redirect, url_for, request, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required, current_user
from models import db, User, Restaurant, MenuItem, CartItem, Order

main = Blueprint('main', __name__)

@main.route('/')
def index():
    restaurants = Restaurant.query.all()
    return render_template('index.html', restaurants=restaurants)

@main.route('/restaurant/<int:restaurant_id>')
def restaurant_detail(restaurant_id):
    restaurant = Restaurant.query.get_or_404(restaurant_id)
    return render_template('restaurant.html', restaurant=restaurant)

@main.route('/add_to_cart/<int:item_id>', methods=['POST'])
@login_required
def add_to_cart(item_id):
    cart_item = CartItem.query.filter_by(user_id=current_user.id, menu_item_id=item_id).first()
    if cart_item:
        cart_item.quantity += 1
    else:
        new_item = CartItem(user_id=current_user.id, menu_item_id=item_id, quantity=1)
        db.session.add(new_item)
    db.session.commit()
    flash('Item added to cart!')
    return redirect(request.referrer or url_for('main.index'))

@main.route('/cart')
@login_required
def view_cart():
    cart_items = CartItem.query.filter_by(user_id=current_user.id).all()
    total = sum(item.menu_item.price * item.quantity for item in cart_items)
    return render_template('cart.html', cart_items=cart_items, total=total)

@main.route('/clear_cart')
@login_required
def clear_cart():
    CartItem.query.filter_by(user_id=current_user.id).delete()
    db.session.commit()
    flash('Cart cleared.')
    return redirect(url_for('main.view_cart'))

@main.route('/checkout', methods=['POST'])
@login_required
def checkout():
    cart_items = CartItem.query.filter_by(user_id=current_user.id).all()
    if not cart_items:
        flash('Your cart is empty.')
        return redirect(url_for('main.view_cart'))
    
    total = sum(item.menu_item.price * item.quantity for item in cart_items)
    new_order = Order(user_id=current_user.id, total=total)
    db.session.add(new_order)
    
    CartItem.query.filter_by(user_id=current_user.id).delete()
    db.session.commit()
    
    flash('Order placed successfully!')
    return redirect(url_for('main.index'))

@main.route('/orders')
@login_required
def view_orders():
    user_orders = Order.query.filter_by(user_id=current_user.id).all()
    return render_template('orders.html', orders=user_orders)

@main.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        
        user_exists = User.query.filter_by(email=email).first()
        if user_exists:
            flash('Email address already exists.')
            return redirect(url_for('main.register'))
            
        new_user = User(
            username=username,
            email=email,
            password=generate_password_hash(password, method='pbkdf2:sha256')
        )
        db.session.add(new_user)
        db.session.commit()
        
        flash('Registration successful! Please login.')
        return redirect(url_for('main.login'))
        
    return render_template('register.html')

@main.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('main.index'))
        else:
            flash('Check your login details and try again.')
            
    return render_template('login.html')

@main.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))
