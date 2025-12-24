"""
Configuration file for BRD Test Executor - Phase 2
Loads environment variables and provides configuration classes
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """Base configuration class"""

    # Flask Configuration
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-phase2')
    FLASK_ENV = os.getenv('FLASK_ENV', 'development')
    DEBUG = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    FLASK_HOST = os.getenv('FLASK_HOST', '0.0.0.0')
    FLASK_PORT = int(os.getenv('FLASK_PORT', 5002))

    # Google Sheets Configuration
    GOOGLE_CREDENTIALS_FILE = os.getenv('GOOGLE_CREDENTIALS_FILE', 'credentials/service-account.json')
    GOOGLE_SHEET_NAME = os.getenv('GOOGLE_SHEET_NAME', 'BRD_TestCases_Output')

    #Google drive upload Screenshot
    GOOGLE_DRIVE_FOLDER_ID = os.getenv('GOOGLE_DRIVE_FOLDER_ID', '')

    # Test Website & Credentials
    TEST_WEBSITE_URL = os.getenv('TEST_WEBSITE_URL', 'https://agency-uat.affina.com.vn/')
    TEST_USERNAME = os.getenv('TEST_USERNAME')
    TEST_PASSWORD = os.getenv('TEST_PASSWORD')

    # Azure OpenAI Configuration
    AZURE_OPENAI_ENDPOINT = os.getenv('AZURE_OPENAI_ENDPOINT')
    AZURE_OPENAI_API_KEY = os.getenv('AZURE_OPENAI_API_KEY')
    AZURE_OPENAI_DEPLOYMENT = os.getenv('AZURE_OPENAI_DEPLOYMENT')
    AZURE_OPENAI_API_VERSION = os.getenv('AZURE_OPENAI_API_VERSION', '2024-12-01-preview')

    # Playwright Configuration
    HEADLESS = os.getenv('HEADLESS', 'false').lower() == 'true'
    BROWSER = os.getenv('BROWSER', 'chromium')
    BROWSER_CHANNEL = os.getenv('BROWSER_CHANNEL', 'chrome')
    SLOW_MO = int(os.getenv('SLOW_MO', 500))
    TIMEOUT = int(os.getenv('TIMEOUT', 30000))

    # Screenshot Configuration
    SCREENSHOT_ON_FAILURE = os.getenv('SCREENSHOT_ON_FAILURE', 'true').lower() == 'true'
    SCREENSHOT_FOLDER = os.getenv('SCREENSHOT_FOLDER', 'screenshots/failures')

    # Logging Configuration
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = os.getenv('LOG_FILE', 'logs/test_execution.log')

    # Test Case Configuration
    TEST_CASE_PREFIX = os.getenv('TEST_CASE_PREFIX', 'TC')

    @staticmethod
    def init_app():
        """Initialize application configurations and validate"""
        # Ensure required folders exist
        folders = [
            'logs',
            Config.SCREENSHOT_FOLDER,
            'tests/generated'
        ]
        
        for folder in folders:
            if not os.path.exists(folder):
                os.makedirs(folder)
                print(f"✓ Created folder: {folder}")

        # Validate Google credentials
        if not os.path.exists(Config.GOOGLE_CREDENTIALS_FILE):
            print(f"⚠️  WARNING: Google credentials file not found at {Config.GOOGLE_CREDENTIALS_FILE}")
        else:
            print(f"✓ Google credentials file found")

        # Validate test credentials
        if not Config.TEST_USERNAME or not Config.TEST_PASSWORD:
            print("⚠️  WARNING: Test credentials not set (TEST_USERNAME, TEST_PASSWORD)")
        else:
            print(f"✓ Test credentials configured")
        
        # Validate Azure OpenAI
        if Config.AZURE_OPENAI_API_KEY:
            print(f"✓ Azure OpenAI configured: {Config.AZURE_OPENAI_DEPLOYMENT}")
        else:
            print("⚠️  WARNING: Azure OpenAI not configured")
        
        print(f"✓ Configuration loaded successfully")
        print(f"  - Google Sheet: {Config.GOOGLE_SHEET_NAME}")
        print(f"  - Test Website: {Config.TEST_WEBSITE_URL}")
        print(f"  - Browser: {Config.BROWSER}")


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
