"""
BRD Test Executor - Phase 2
Flask server with UI and API endpoints
"""
import sys
import os
from flask import Flask
from flask_cors import CORS
from app.config import Config

# Import routes
from app.routes.executor_routes import executor_bp

def create_app():
    """Create and configure Flask application"""
    # IMPORTANT: Set template_folder and static_folder explicitly
    template_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'app', 'templates')
    static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'app', 'static')
    
    app = Flask(__name__, 
                template_folder=template_dir,
                static_folder=static_dir)
    
    # Load configuration
    app.config.from_object(Config)
    Config.init_app()
    
    # Enable CORS
    CORS(app)
    
    # Register blueprints
    app.register_blueprint(executor_bp)
    
    # Debug: Print template folder
    print(f"✓ Template folder: {app.template_folder}")
    print(f"✓ Static folder: {app.static_folder}")
    
    return app

def main():
    """Main entry point"""
    app = create_app()
    
    print("\n" + "="*70)
    print("🚀 BRD Test Executor - Phase 2")
    print("="*70)
    print(f"Server running on: http://{Config.FLASK_HOST}:{Config.FLASK_PORT}")
    print(f"Google Sheet: {Config.GOOGLE_SHEET_NAME}")
    print(f"Test Website: {Config.TEST_WEBSITE_URL}")
    print("="*70 + "\n")
    
    # Run Flask server
    app.run(
        host=Config.FLASK_HOST,
        port=Config.FLASK_PORT,
        debug=Config.DEBUG
    )

if __name__ == '__main__':
    sys.exit(main())
