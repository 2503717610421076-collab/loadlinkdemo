from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from models import db, Order, Driver

driver_bp = Blueprint('driver', __name__)

@driver_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        phone = request.form.get('phone')
        driver = Driver.query.filter_by(phone=phone).first()
        if driver:
            session['driver_id'] = driver.id
            return redirect(url_for('driver.dashboard'))
        flash('Driver not found. Please register.')
        return redirect(url_for('driver.register'))
    return render_template('driver/login.html')

@driver_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        driver = Driver(
            name=request.form.get('name'),
            phone=request.form.get('phone'),
            dob=request.form.get('dob'),
            address=request.form.get('address'),
            city=request.form.get('city'),
            license_number=request.form.get('license_number'),
            vehicle_brand=request.form.get('vehicle_brand'),
            vehicle_model=request.form.get('vehicle_model'),
            vehicle_capacity=float(request.form.get('vehicle_capacity'))
        )
        db.session.add(driver)
        db.session.commit()
        session['driver_id'] = driver.id
        flash('Successfully Registered!')
        return redirect(url_for('driver.dashboard'))
        
    return render_template('driver/register.html')

@driver_bp.route('/dashboard')
def dashboard():
    driver_id = session.get('driver_id')
    if not driver_id:
        return redirect(url_for('driver.login'))
        
    driver = Driver.query.get(driver_id)
    
    search_terms = []
    if driver.city: search_terms.append(driver.city)
    if driver.address:
        search_terms.extend([p.strip() for p in driver.address.split(',') if p.strip()])
    
    # Match the order's pickup address against the driver's city or any part of their address (area names)
    if search_terms:
        conditions = [Order.pickup_address.ilike(f'%{term}%') for term in set(search_terms)]
        available_orders = Order.query.filter(
            Order.status == 'Placed',
            db.or_(*conditions)
        ).all()
    else:
        available_orders = Order.query.filter_by(status='Placed').all()
    
    # Driver's current active orders
    my_orders = Order.query.filter(Order.driver_id == driver_id, Order.status.in_(['Accepted', 'In Transit'])).all()
    
    return render_template('driver/dashboard.html', driver=driver, orders=available_orders, my_orders=my_orders)

@driver_bp.route('/accept_order/<int:order_id>', methods=['POST'])
def accept_order(order_id):
    driver_id = session.get('driver_id')
    if not driver_id: return redirect(url_for('driver.login'))
        
    order = Order.query.get_or_404(order_id)
    order.status = 'Accepted'
    order.driver_id = driver_id
    db.session.commit()
    return redirect(url_for('driver.dashboard'))

@driver_bp.route('/update_status/<int:order_id>', methods=['POST'])
def update_status(order_id):
    driver_id = session.get('driver_id')
    if not driver_id: return redirect(url_for('driver.login'))
        
    order = Order.query.get_or_404(order_id)
    # Ensure this driver owns the order
    if order.driver_id != driver_id: return redirect(url_for('driver.dashboard'))
    
    new_status = request.form.get('new_status')
    if new_status in ['In Transit', 'Delivered']:
        order.status = new_status
        db.session.commit()
        
    return redirect(url_for('driver.dashboard'))

import math

def get_distance(lat1, lon1, lat2, lon2):
    """Calculate distance using Haversine formula (in km)"""
    R = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

@driver_bp.route('/api/route_orders')
def api_route_orders():
    p_lat = request.args.get('p_lat', type=float)
    p_lng = request.args.get('p_lng', type=float)
    d_lat = request.args.get('d_lat', type=float)
    d_lng = request.args.get('d_lng', type=float)
    
    if None in [p_lat, p_lng, d_lat, d_lng]:
        return {'orders': []}
        
    all_placed = Order.query.filter_by(status='Placed').all()
    orders_data = []
    
    for o in all_placed:
        # Distance from routed start to order's pickup
        dist_pickup = get_distance(p_lat, p_lng, o.pickup_lat, o.pickup_lng)
        # Distance from routed end to order's dropoff
        dist_dropoff = get_distance(d_lat, d_lng, o.dropoff_lat, o.dropoff_lng)
        
        # If the order is starting within 20km of the origin OR ending within 20km of destination
        if dist_pickup <= 20.0 or dist_dropoff <= 20.0:
            orders_data.append({
                'id': o.id,
                'tracking_id': o.tracking_id,
                'fare': o.fare,
                'pickup': o.pickup_address,
                'dropoff': o.dropoff_address,
                'weight': o.weight,
                'category': o.load_category,
                'type': o.delivery_type,
                'p_lat': o.pickup_lat,
                'p_lng': o.pickup_lng,
                'd_lat': o.dropoff_lat,
                'd_lng': o.dropoff_lng
            })
        
    return {'orders': orders_data}
