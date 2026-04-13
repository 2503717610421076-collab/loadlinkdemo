from flask import Blueprint, render_template, redirect, url_for, session, request
from models import db, User
from extensions import oauth

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/google_login')
def google_login():
    redirect_uri = url_for('auth.callback', _external=True)
    return oauth.google.authorize_redirect(redirect_uri)

@auth_bp.route('/callback')
def callback():
    token = oauth.google.authorize_access_token()
    user_info = token.get('userinfo')
    
    email = user_info.get('email')
    name = user_info.get('name')
    google_id = user_info.get('sub')
    
    user = User.query.filter_by(google_id=google_id).first()
    if not user:
        # Check by email in case user previously logged in without google ID tracked
        user = User.query.filter_by(email=email).first()
        if user:
            user.google_id = google_id
        else:
            user = User(name=name, email=email, google_id=google_id)
            db.session.add(user)
        db.session.commit()
    
    session['user_id'] = user.id 
    session['user_name'] = user.name
    
    return redirect(url_for('index'))

@auth_bp.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('user_name', None)
    return redirect(url_for('index'))
