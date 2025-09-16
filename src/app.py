"""
Virtual Try-On Flask Application
Main application entry point
"""

from flask import Flask, render_template, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_cors import CORS
from flask_socketio import SocketIO
import os
import logging
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Import configuration
from config.app_config import config

# Initialize extensions
db = SQLAlchemy()
login_manager = LoginManager()
socketio = SocketIO(cors_allowed_origins="*")

def create_app(config_name=None):
    """Application factory pattern."""
    
    if config_name is None:
        config_name = os.environ.get('FLASK_CONFIG', 'default')
    
    app = Flask(__name__, 
                template_folder='../frontend/templates',
                static_folder='../frontend/static')
    
    # Load configuration
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    socketio.init_app(app)
    
    # Configure CORS
    CORS(app, origins=app.config['CORS_ORIGINS'])
    
    # Configure login manager
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'
    
    # Configure logging
    setup_logging(app)
    
    # Register blueprints
    register_blueprints(app)
    
    # Register error handlers
    register_error_handlers(app)
    
    # Create database tables
    with app.app_context():
        db.create_all()
    
    return app

def setup_logging(app):
    """Configure application logging."""
    
    if not app.debug and not app.testing:
        if not os.path.exists('logs'):
            os.mkdir('logs')
        
        file_handler = logging.FileHandler('logs/virtual_tryon.log')
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        
        app.logger.setLevel(logging.INFO)
        app.logger.info('Virtual Try-On application startup')

def register_blueprints(app):
    """Register application blueprints."""
    
    # Import clothing API blueprint
    from api.clothing import clothing_bp
    
    # Register clothing blueprint
    app.register_blueprint(clothing_bp, url_prefix='/api/clothing')
    
    # TODO: Import other blueprints when API modules are created
    # from api.auth import auth_bp
    # from api.pose_detection import pose_bp
    # from api.size_estimation import size_bp
    # from api.virtual_tryon import tryon_bp
    # from api.user import user_bp
    
    # TODO: Register other blueprints when API modules are created
    # app.register_blueprint(auth_bp, url_prefix='/api/auth')
    # app.register_blueprint(pose_bp, url_prefix='/api/pose')
    # app.register_blueprint(size_bp, url_prefix='/api/size')
    # app.register_blueprint(tryon_bp, url_prefix='/api/tryon')
    # app.register_blueprint(user_bp, url_prefix='/api/user')

def register_error_handlers(app):
    """Register error handlers."""
    
    @app.errorhandler(404)
    def not_found_error(error):
        return jsonify({'error': 'Resource not found'}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return jsonify({'error': 'Internal server error'}), 500
    
    @app.errorhandler(413)
    def too_large(error):
        return jsonify({'error': 'File too large'}), 413

# User loader for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    # TODO: Import User model when it's created
    # from models.user import User
    # return User.query.get(int(user_id))
    return None

# Create Flask app
app = create_app()

# Main routes
@app.route('/')
def index():
    """Main application page."""
    return render_template('index.html')

@app.route('/tryon')
def virtual_tryon():
    """Virtual try-on page."""
    return render_template('tryon.html')

@app.route('/catalog')
def clothing_catalog():
    """Clothing catalog page."""
    return render_template('catalog.html')

@app.route('/profile')
def user_profile():
    """User profile page."""
    return render_template('profile.html')

@app.route('/health')
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'version': '1.0.0'
    })

# SocketIO events for real-time communication
@socketio.on('connect')
def handle_connect():
    """Handle client connection."""
    app.logger.info('Client connected')

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection."""
    app.logger.info('Client disconnected')

@socketio.on('pose_data')
def handle_pose_data(data):
    """Handle real-time pose data from client."""
    # Process pose data and emit back results
    # This will be implemented in the pose detection module
    pass

if __name__ == '__main__':
    # Development server
    socketio.run(app, 
                debug=app.config['DEBUG'],
                host='0.0.0.0',
                port=5000,
                allow_unsafe_werkzeug=True)
