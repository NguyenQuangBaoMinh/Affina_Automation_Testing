"""
Entry point for BRD Test Case Automation System
Run Flask development server
"""
from app import create_app
from app.config import Config

# Create Flask app
app = create_app()

if __name__ == '__main__':
    # Run development server
    print("\n" + "=" * 70)
    print("Starting Flask Development Server...")
    print("=" * 70)
    print(f"Server will be available at: http://localhost:5001")
    print(f"API endpoint: http://localhost:5001/api/generate-testcases")
    print("=" * 70 + "\n")

    app.run(
        host='0.0.0.0',  # Listen on all network interfaces
        port=5001,  # Port number
        debug=Config.DEBUG  # Enable debug mode from config
    )