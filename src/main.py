"""
Opera PMS - MikroTik - FreeRADIUS Integration
Main application entry point
"""

import os
import sys
import logging
from pathlib import Path

from flask import Flask
from flask_restful import Api

from src.logger import setup_logger
from src.database import Database
from src.opera_connector import OperaConnector
from src.mikrotik_connector import MikroTikConnector
from src.radius_manager import RADIUSManager
from src.auth_handler import AuthHandler

# Setup logging
logger = setup_logger(__name__)

def create_app(config_path=None):
    """
    Create and configure Flask application
    
    Args:
        config_path: Path to configuration file
        
    Returns:
        Flask application instance
    """
    app = Flask(__name__)
    api = Api(app)
    
    # Load configuration
    if config_path is None:
        config_path = os.getenv('CONFIG_PATH', 'config/config.yaml')
    
    logger.info(f"Loading configuration from {config_path}")
    
    try:
        from src.config import Config
        config = Config(config_path)
        app.config.from_object(config)
    except Exception as e:
        logger.error(f"Failed to load configuration: {e}")
        sys.exit(1)
    
    # Initialize components
    try:
        logger.info("Initializing database connection...")
        db = Database(app.config)
        
        logger.info("Initializing Opera PMS connector...")
        opera = OperaConnector(app.config)
        
        logger.info("Initializing MikroTik connector...")
        mikrotik = MikroTikConnector(app.config)
        
        logger.info("Initializing FreeRADIUS manager...")
        radius = RADIUSManager(app.config)
        
        logger.info("Initializing authentication handler...")
        auth_handler = AuthHandler(opera, radius, mikrotik, db)
        
        # Store in app context
        app.db = db
        app.opera = opera
        app.mikrotik = mikrotik
        app.radius = radius
        app.auth_handler = auth_handler
        
    except Exception as e:
        logger.error(f"Failed to initialize components: {e}")
        sys.exit(1)
    
    # Register API routes
    register_routes(api, app)
    
    # Register error handlers
    register_error_handlers(app)
    
    # Start background tasks
    start_background_tasks(app)
    
    logger.info("Application initialized successfully")
    return app


def register_routes(api, app):
    """Register API routes"""
    
    @app.route('/health', methods=['GET'])
    def health_check():
        return {'status': 'healthy'}, 200
    
    @app.route('/api/v1/guests', methods=['GET'])
    def list_guests():
        try:
            guests = app.db.get_all_guests()
            return {'data': guests, 'status': 'success'}, 200
        except Exception as e:
            logger.error(f"Error listing guests: {e}")
            return {'error': str(e)}, 500
    
    @app.route('/api/v1/guests/<guest_id>', methods=['GET'])
    def get_guest(guest_id):
        try:
            guest = app.db.get_guest(guest_id)
            if guest:
                return {'data': guest, 'status': 'success'}, 200
            return {'error': 'Guest not found'}, 404
        except Exception as e:
            logger.error(f"Error getting guest: {e}")
            return {'error': str(e)}, 500
    
    @app.route('/api/v1/sync', methods=['POST'])
    def manual_sync():
        try:
            logger.info("Manual sync initiated")
            result = app.auth_handler.sync_all_users()
            return {'result': result, 'status': 'success'}, 200
        except Exception as e:
            logger.error(f"Sync error: {e}")
            return {'error': str(e)}, 500


def register_error_handlers(app):
    """Register global error handlers"""
    
    @app.errorhandler(404)
    def not_found(error):
        return {'error': 'Resource not found'}, 404
    
    @app.errorhandler(500)
    def internal_error(error):
        logger.error(f"Internal server error: {error}")
        return {'error': 'Internal server error'}, 500


def start_background_tasks(app):
    """Start background synchronization tasks"""
    import threading
    
    def sync_worker():
        logger.info("Starting background sync worker")
        try:
            sync_interval = app.config.get('opera', {}).get('sync_interval', 300)
            while True:
                try:
                    logger.debug("Running scheduled sync...")
                    app.auth_handler.sync_all_users()
                except Exception as e:
                    logger.error(f"Sync error: {e}")
                
                import time
                time.sleep(sync_interval)
        except Exception as e:
            logger.error(f"Background worker error: {e}")
    
    # Start sync worker in background thread
    if app.config.get('features', {}).get('auto_provisioning', True):
        sync_thread = threading.Thread(target=sync_worker, daemon=True)
        sync_thread.start()
        logger.info("Background sync worker started")


if __name__ == '__main__':
    app = create_app()
    
    # Get configuration
    config_path = os.getenv('CONFIG_PATH', 'config/config.yaml')
    from src.config import Config
    config = Config(config_path)
    
    api_config = config.config.get('api', {})
    host = api_config.get('host', '0.0.0.0')
    port = api_config.get('port', 5000)
    debug = api_config.get('debug', False)
    
    logger.info(f"Starting application on {host}:{port}")
    app.run(host=host, port=port, debug=debug)