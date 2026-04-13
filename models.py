from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    google_id = db.Column(db.String(120), unique=True, nullable=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(20), nullable=True)
    address = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    orders = db.relationship('Order', backref='user', lazy=True)

class Driver(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    dob = db.Column(db.String(20), nullable=False)
    address = db.Column(db.String(255), nullable=False)
    city = db.Column(db.String(100), nullable=False)
    
    # Professional info
    license_number = db.Column(db.String(50), unique=True, nullable=False)
    vehicle_brand = db.Column(db.String(50), nullable=False)
    vehicle_model = db.Column(db.String(50), nullable=False)
    vehicle_capacity = db.Column(db.Float, nullable=False) # in kg
    
    # Status and Location
    is_active = db.Column(db.Boolean, default=False)
    current_lat = db.Column(db.Float, nullable=True)
    current_lng = db.Column(db.Float, nullable=True)
    
    orders = db.relationship('Order', backref='driver', lazy=True)

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tracking_id = db.Column(db.String(50), unique=True, nullable=False)
    
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    driver_id = db.Column(db.Integer, db.ForeignKey('driver.id'), nullable=True)
    
    # Addresses
    pickup_address = db.Column(db.String(255), nullable=False)
    pickup_lat = db.Column(db.Float, nullable=False)
    pickup_lng = db.Column(db.Float, nullable=False)
    dropoff_address = db.Column(db.String(255), nullable=False)
    dropoff_lat = db.Column(db.Float, nullable=False)
    dropoff_lng = db.Column(db.Float, nullable=False)
    
    # Contacts
    pickup_name = db.Column(db.String(100), nullable=False)
    pickup_phone = db.Column(db.String(20), nullable=False)
    dropoff_name = db.Column(db.String(100), nullable=False)
    dropoff_phone = db.Column(db.String(20), nullable=False)
    
    # Load Details
    load_category = db.Column(db.String(50), nullable=False)
    weight = db.Column(db.Float, nullable=False)
    
    # Preferences
    delivery_type = db.Column(db.String(20), nullable=False) # Ordinary / Fast
    pooling_choice = db.Column(db.String(20), nullable=False) # Combine / Separate
    pickup_time = db.Column(db.String(50), nullable=True)
    eta = db.Column(db.String(50), nullable=True)
    
    # Financials and Status
    fare = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default='Placed') # Placed, Accepted, In Transit, Delivered
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
