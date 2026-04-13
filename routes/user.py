from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from models import db, User, Order

user_bp = Blueprint('user', __name__)

@user_bp.route('/profile', methods=['GET', 'POST'])
def profile():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('auth.google_login'))
        
    user = User.query.get(user_id)
    
    if request.method == 'POST':
        user.phone = request.form.get('phone')
        user.address = request.form.get('address')
        db.session.commit()
        flash('Profile updated successfully.')
        return redirect(url_for('user.profile'))
        
    # Get active and past orders
    active_orders = Order.query.filter(Order.user_id == user_id, Order.status.in_(['Placed', 'Accepted', 'In Transit'])).order_by(Order.created_at.desc()).all()
    past_orders = Order.query.filter(Order.user_id == user_id, Order.status == 'Delivered').order_by(Order.created_at.desc()).all()
    
    return render_template('user/profile.html', user=user, active_orders=active_orders, past_orders=past_orders)
