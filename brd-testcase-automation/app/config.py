"""
Configuration file for BRD Test Case Automation
Loads environment variables and provides configuration classes
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """Base configuration class"""

    # Flask Configuration
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    FLASK_ENV = os.getenv('FLASK_ENV', 'development')
    DEBUG = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'

    # Upload Configuration
    UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', 'uploads')
    MAX_CONTENT_LENGTH = int(os.getenv('MAX_CONTENT_LENGTH', 16777216))  # 16MB default
    ALLOWED_EXTENSIONS = set(os.getenv('ALLOWED_EXTENSIONS', 'pdf,docx').split(','))

    # OpenAI Configuration
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    OPENAI_MODEL = os.getenv('OPENAI_MODEL', 'gpt-4-turbo-preview')

    # Google Sheets Configuration
    GOOGLE_CREDENTIALS_FILE = os.getenv('GOOGLE_CREDENTIALS_FILE', 'credentials/service-account.json')
    GOOGLE_SHEET_NAME = os.getenv('GOOGLE_SHEET_NAME', 'BRD_TestCases_Output')

    # Test Case Configuration
    TEST_CASE_PREFIX = os.getenv('TEST_CASE_PREFIX', 'TC')
    COVERAGE_TARGET = int(os.getenv('COVERAGE_TARGET', 80))

    @staticmethod
    def init_app():
        """Initialize application configurations and validate"""
        # Ensure upload folder exists
        if not os.path.exists(Config.UPLOAD_FOLDER):
            os.makedirs(Config.UPLOAD_FOLDER)
            print(f"✓ Created upload folder: {Config.UPLOAD_FOLDER}")

        # Validate required configurations
        if not Config.OPENAI_API_KEY:
            print(" WARNING: OPENAI_API_KEY not set in .env file")

        if not os.path.exists(Config.GOOGLE_CREDENTIALS_FILE):
            print(f" WARNING: Google credentials file not found at {Config.GOOGLE_CREDENTIALS_FILE}")
            print("   Please follow GOOGLE_SETUP_GUIDE.md to set up credentials")
        else:
            print(f"✓ Google credentials file found: {Config.GOOGLE_CREDENTIALS_FILE}")

        print(f"✓ Configuration loaded successfully")
        print(f"  - Model: {Config.OPENAI_MODEL}")
        print(f"  - Google Sheet: {Config.GOOGLE_SHEET_NAME}")
        print(f"  - Coverage Target: {Config.COVERAGE_TARGET}%")


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    TESTING = False


class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    TESTING = False


class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    DEBUG = True


# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}


def get_config(config_name=None):
    """Get configuration by name"""
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'development')
    return config.get(config_name, config['default'])