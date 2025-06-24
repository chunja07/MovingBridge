#!/usr/bin/env python3
"""
Pre-deployment check script for Korean Job Community Platform
Verifies required environment variables and database connectivity before starting the app
"""

import os
import sys
import psycopg2
from dotenv import load_dotenv

def check_environment_variables():
    """Check if all required environment variables are set"""
    load_dotenv()
    
    required_vars = ['SESSION_SECRET']
    
    # Get environment
    flask_env = os.environ.get('FLASK_ENV', 'development')
    
    # Check if DATABASE_URL is set for production
    if flask_env == 'production':
        required_vars.append('DATABASE_URL')
    
    missing_vars = []
    for var in required_vars:
        if not os.environ.get(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Missing environment variables: {', '.join(missing_vars)}")
        return False
    
    print(f"✅ All required environment variables are set for {flask_env} environment")
    return True

def check_database_connectivity():
    """Check if database connection is working"""
    try:
        flask_env = os.environ.get('FLASK_ENV', 'development')
        database_url = os.environ.get('DATABASE_URL')
        
        if flask_env == 'production' and database_url and database_url.startswith('postgresql'):
            # Check PostgreSQL connection for production
            conn = psycopg2.connect(database_url)
            cur = conn.cursor()
            cur.execute('SELECT 1')
            cur.close()
            conn.close()
            print("✅ PostgreSQL database connection successful (production)")
        else:
            # Check SQLite connection for development
            import sqlite3
            db_file = 'movingbridge_dev.db' if flask_env == 'development' else 'movingbridge.db'
            conn = sqlite3.connect(db_file)
            cur = conn.cursor()
            cur.execute('SELECT 1')
            cur.close()
            conn.close()
            print(f"✅ SQLite database connection successful ({flask_env})")
        
        return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

def run_pre_deployment_checks():
    """Run all pre-deployment checks"""
    print("🔍 Running pre-deployment checks...")
    
    checks_passed = True
    
    # Check environment variables
    if not check_environment_variables():
        checks_passed = False
    
    # Check database connectivity
    if not check_database_connectivity():
        checks_passed = False
    
    if checks_passed:
        print("✅ All pre-deployment checks passed!")
        return True
    else:
        print("❌ Pre-deployment checks failed!")
        return False

if __name__ == "__main__":
    if not run_pre_deployment_checks():
        sys.exit(1)
    print("🚀 Ready for deployment!")