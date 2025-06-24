#!/usr/bin/env python3
"""
Production server runner
Sets environment to production and runs with Gunicorn
"""
import os
import subprocess
import sys

if __name__ == '__main__':
    # Set environment to production
    os.environ['FLASK_ENV'] = 'production'
    
    # Run with Gunicorn for production
    cmd = [
        'gunicorn',
        '--bind', '0.0.0.0:5000',
        '--reuse-port',
        '--workers', '2',
        '--timeout', '30',
        'main:app'
    ]
    
    subprocess.run(cmd)