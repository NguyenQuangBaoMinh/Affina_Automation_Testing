"""
Flask Application Factory
Initialize and configure Flask app
"""
from flask import Flask
from flask_cors import CORS
import os

from app.config import Config


def create_app(config_class=Config):
    """
    Create and configure Flask application

    Args:
        config_class: Configuration class to use

    Returns:
        Configured Flask app instance
    """
    # Initialize Flask app
    app = Flask(__name__)

    # Load configuration
    app.config.from_object(config_class)

    # Enable CORS (for API calls from different origins)
    CORS(app)

    # Initialize app configurations
    Config.init_app()

    # Register blueprints
    from app.routes.brd_routes import brd_bp
    app.register_blueprint(brd_bp)

    # Create upload folder if it doesn't exist
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    # Log app startup
    with app.app_context():
        print("\n" + "=" * 70)
        print("🚀 BRD Test Case Automation System")
        print("=" * 70)
        print(f"Environment: {app.config['FLASK_ENV']}")
        print(f"Debug Mode: {app.config['DEBUG']}")
        print(f"Upload Folder: {app.config['UPLOAD_FOLDER']}")
        print(f"Max File Size: {app.config['MAX_CONTENT_LENGTH'] / (1024 * 1024):.0f}MB")
        print(f"OpenAI Model: {app.config['OPENAI_MODEL']}")
        print(f"Google Sheet: {app.config['GOOGLE_SHEET_NAME']}")
        print(f"Coverage Target: {app.config['COVERAGE_TARGET']}%")
        print("=" * 70 + "\n")

    return app