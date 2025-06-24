#!/usr/bin/env python3
"""
Development server runner
Sets environment to development and runs the Flask application
"""
import os
from app import app

if __name__ == '__main__':
    # Set environment to development
    os.environ['FLASK_ENV'] = 'development'
    
    # Run development server
    app.run(host='0.0.0.0', port=5000, debug=True)