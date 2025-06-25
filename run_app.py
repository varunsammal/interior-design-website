#!/usr/bin/env python3
"""
Script to run the Flask application
"""

import os
from app import app

if __name__ == '__main__':
    print("Starting Interior Design Website...")
    print("=" * 50)
    print("Portfolio page: http://localhost:5000/portfolio")
    print("Admin dashboard: http://localhost:5000/admin")
    print("Admin login: admin / admin123")
    print("=" * 50)
    print("The portfolio page is now connected to the admin dashboard!")
    print("Changes made in admin will appear on the portfolio page.")
    
    app.run(debug=True, host='0.0.0.0', port=5000)