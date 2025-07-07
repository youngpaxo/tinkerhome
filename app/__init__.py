from flask import Flask, render_template
from flask_login import LoginManager
from config.config import config
from app.database.db_manager import DatabaseManager
from app.services import FinanceService, UserService, NotesService
from app.routes.auth import auth_bp, init_auth_routes
from app.routes.main import main_bp, init_main_routes
import logging
import os

# Try to load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # dotenv not installed, continue without it
    pass

def create_app(config_name=None):
    """Application factory pattern"""
    
    # Determine configuration
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'default')
    
    # Create Flask app with correct template and static folder paths
    # Since we're in app/__init__.py, we need to go up one level to find templates and static
    app = Flask(__name__, 
                template_folder='templates',
                static_folder='static')
    
    app.config.from_object(config[config_name])
    
    # Setup logging
    setup_logging(app)
    
    # Initialize database
    db_manager = DatabaseManager(app.config['DATABASE_NAME'])
    
    # Initialize services
    finance_service = FinanceService(db_manager)
    user_service = UserService(db_manager)
    notes_service = NotesService(db_manager)
    
    # Setup Flask-Login
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'
    login_manager.init_app(app)
    
    @login_manager.user_loader
    def load_user(user_id):
        return user_service.get_user_by_id(int(user_id))
    
    # Register blueprints
    auth_blueprint = init_auth_routes(user_service)
    main_blueprint = init_main_routes(finance_service, notes_service)
    
    app.register_blueprint(auth_blueprint)
    app.register_blueprint(main_blueprint)
    
    # Error handlers (only create templates if they don't exist)
    @app.errorhandler(404)
    def not_found_error(error):
        try:
            return render_template('errors/404.html'), 404
        except:
            return '<h1>404 - Page Not Found</h1><p>The page you are looking for does not exist.</p>', 404
    
    @app.errorhandler(500)
    def internal_error(error):
        app.logger.error(f'Server Error: {error}')
        try:
            return render_template('errors/500.html'), 500
        except:
            return '<h1>500 - Internal Server Error</h1><p>Something went wrong on our end.</p>', 500
    
    @app.errorhandler(403)
    def forbidden_error(error):
        try:
            return render_template('errors/403.html'), 403
        except:
            return '<h1>403 - Forbidden</h1><p>You do not have permission to access this resource.</p>', 403
    
    # Health check endpoint
    @app.route('/health')
    def health_check():
        return {'status': 'healthy', 'version': '2.0'}, 200
    
    return app

def setup_logging(app):
    """Setup application logging"""
    if not app.debug and not app.testing:
        # Production logging
        if not os.path.exists('logs'):
            os.mkdir('logs')
        
        file_handler = logging.FileHandler('logs/finanzas.log')
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        
        app.logger.setLevel(logging.INFO)
        app.logger.info('Finanzas application startup')
    else:
        # Development logging
        logging.basicConfig(
            level=logging.DEBUG,
            format='%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        )