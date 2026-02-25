from flask import Flask, session
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from flask_mail import Mail
from authlib.integrations.flask_client import OAuth
import firebase_admin
from firebase_admin import credentials, firestore
from config import Config
import os

# Initialize Flask extensions
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message_category = 'info'
csrf = CSRFProtect()
mail = Mail()
oauth = OAuth()

db = None

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions with app
    login_manager.init_app(app)
    csrf.init_app(app)
    mail.init_app(app)
    oauth.init_app(app)

    # Register Google OAuth
    oauth.register(
        name='google',
        client_id=app.config['GOOGLE_CLIENT_ID'],
        client_secret=app.config['GOOGLE_CLIENT_SECRET'],
        server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
        client_kwargs={
            'scope': 'openid email profile'
        }
    )

    # Initialize Firebase
    global db
    if not firebase_admin._apps:
        # Check if service account file exists or use credentials from env
        service_account_path = app.config.get('FIREBASE_SERVICE_ACCOUNT')
        if service_account_path and os.path.exists(service_account_path):
            cred = credentials.Certificate(service_account_path)
            firebase_admin.initialize_app(cred)
        else:
            # Fallback to default or raise alert if in production
            # In a real scenario, we'd use environment variables for keys
            try:
                firebase_admin.initialize_app()
            except Exception as e:
                app.logger.error(f"Failed to initialize Firebase: {e}")
    
    db = firestore.client()

    # Register blueprints
    from app.routes.main import main_bp
    from app.routes.auth import auth_bp
    from app.routes.admin import admin_bp
    from app.routes.errors import errors_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(errors_bp)

    @app.context_processor
    def inject_cart_count():
        cart = session.get('cart', {})
        return dict(cart_count=sum(cart.values()))

    return app
