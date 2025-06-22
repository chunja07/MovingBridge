#!/usr/bin/env python3
"""
Startup script that runs pre-deployment checks before starting the Flask application
"""

import sys
import subprocess
from pre_deploy_check import run_pre_deployment_checks

def start_application():
    """Start the application with pre-deployment checks"""
    print("Starting Korean Job Community Platform...")
    
    # Run pre-deployment checks
    if not run_pre_deployment_checks():
        print("Failed pre-deployment checks. Exiting...")
        sys.exit(1)
    
    # Start the application with gunicorn
    try:
        cmd = ["gunicorn", "--bind", "0.0.0.0:5000", "--reuse-port", "--reload", "main:app"]
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Failed to start application: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nApplication stopped by user")
        sys.exit(0)

if __name__ == "__main__":
    start_application()