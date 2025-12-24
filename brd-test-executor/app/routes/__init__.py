"""
Routes package for Phase 2
"""
from flask import Blueprint

# Create blueprint
executor_bp = Blueprint('executor', __name__)

# Import routes
from app.routes import executor_routes