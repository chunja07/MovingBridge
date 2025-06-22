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
    
    required_vars = [
        'DATABASE_URL',
        'SESSION_SECRET'
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.environ.get(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Missing required environment variables: {', '.join(missing_vars)}")
        return False
    
    print("✅ All required environment variables are set")
    return True

def check_database_connectivity():
    """Check if database connection is working"""
    try:
        database_url = os.environ.get('DATABASE_URL')
        if not database_url:
            print("❌ DATABASE_URL not set")
            return False
        
        conn = psycopg2.connect(database_url)
        cur = conn.cursor()
        cur.execute('SELECT 1')
        cur.close()
        conn.close()
        
        print("✅ Database connection successful")
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