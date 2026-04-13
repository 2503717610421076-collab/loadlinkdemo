import os
from flask import Flask, render_template
from models import db
from routes.auth import auth_bp
from routes.booking import booking_bp
from routes.driver import driver_bp
from routes.user import user_bp
from dotenv import load_dotenv
import os
from extensions import oauth

load_dotenv()  # Load environment variables from .env file

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'default-secret-key-for-dev')
    
    # Configure OAuth Credentials
    app.config['GOOGLE_CLIENT_ID'] = os.environ.get('GOOGLE_CLIENT_ID')
    app.config['GOOGLE_CLIENT_SECRET'] = os.environ.get('GOOGLE_CLIENT_SECRET')
    
    # Configure SQLite Database
    basedir = os.path.abspath(os.path.dirname(__name__))
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'loadlink.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    
    # Init OAuth
    oauth.init_app(app)
    oauth.register(
        name='google',
        server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
        client_kwargs={
            'scope': 'openid email profile'
        }
    )

    # Register Blueprints
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(booking_bp, url_prefix='/booking')
    app.register_blueprint(driver_bp, url_prefix='/driver')
    app.register_blueprint(user_bp, url_prefix='/user')

    @app.route('/')
    def index():
        return render_template('index.html')

    @app.context_processor
    def inject_api_keys():
        return dict(GOOGLE_MAPS_API_KEY=os.environ.get('GOOGLE_MAPS_API_KEY', ''))

    # Create tables
    with app.app_context():
        db.create_all()

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=5000)
