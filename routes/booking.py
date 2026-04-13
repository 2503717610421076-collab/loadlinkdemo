from flask import Blueprint, render_template, request, redirect, url_for, session
from models import db, Order, User
import uuid
import random

booking_bp = Blueprint('booking', __name__)

@booking_bp.route('/step1', methods=['GET', 'POST'])
def step1():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('auth.google_login')) # Force login

    if request.method == 'POST':
        session['booking_step1'] = request.form.to_dict()
        return redirect(url_for('booking.step2'))
    
    return render_template('booking/step1.html')

@booking_bp.route('/step2', methods=['GET', 'POST'])
def step2():
    if 'booking_step1' not in session:
        return redirect(url_for('booking.step1'))

    if request.method == 'POST':
        session['booking_step2'] = request.form.to_dict()
        return redirect(url_for('booking.step3'))
        
    return render_template('booking/step2.html')

@booking_bp.route('/step3', methods=['GET', 'POST'])
def step3():
    if 'booking_step2' not in session:
        return redirect(url_for('booking.step2'))

    step1_data = session['booking_step1']
    step2_data = session['booking_step2']
    
    # Simple Mock Fare Logic based on weight and choices
    base_fare = float(step1_data.get('weight', 0)) * 20 # ₹20 per kg
    if step2_data.get('delivery_type') == 'fast':
        base_fare *= 1.5
    if step2_data.get('pooling_choice') == 'separate':
        base_fare += 500 # flat ₹500 separate vehicle fee
        
    fare = round(base_fare + random.uniform(100, 300), 2) # add a bit of distance factor mockup
    eta = "Within 2 Hours" if step2_data.get('delivery_type') == 'fast' else "Today"

    if request.method == 'POST':
        # Save order
        order = Order(
            tracking_id="LL-" + str(uuid.uuid4()).split('-')[0].upper(),
            user_id=session.get('user_id'),
            pickup_address=step1_data.get('pickup_address'),
            pickup_lat=float(step1_data.get('pickup_lat', 0)),
            pickup_lng=float(step1_data.get('pickup_lng', 0)),
            dropoff_address=step1_data.get('dropoff_address'),
            dropoff_lat=float(step1_data.get('dropoff_lat', 0)),
            dropoff_lng=float(step1_data.get('dropoff_lng', 0)),
            pickup_name=step1_data.get('pickup_name'),
            pickup_phone=step1_data.get('pickup_phone'),
            dropoff_name=step1_data.get('dropoff_name'),
            dropoff_phone=step1_data.get('dropoff_phone'),
            load_category=step1_data.get('load_category'),
            weight=float(step1_data.get('weight')),
            delivery_type=step2_data.get('delivery_type'),
            pooling_choice=step2_data.get('pooling_choice'),
            pickup_time=step2_data.get('pickup_time'),
            eta=eta,
            fare=fare
        )
        db.session.add(order)
        db.session.commit()
        
        # Clear booking session
        session.pop('booking_step1', None)
        session.pop('booking_step2', None)
        
        return render_template('booking/step3.html', order=order, success=True)

    return render_template('booking/step3.html', step1=step1_data, step2=step2_data, fare=fare, eta=eta, success=False)
