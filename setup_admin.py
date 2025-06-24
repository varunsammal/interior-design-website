#!/usr/bin/env python3
"""
Setup script for Interior Design Website
Creates database tables and admin user
"""

from app import app, db, User

def setup_database():
    """Create database tables and default admin user"""
    with app.app_context():
        print("Setting up database...")
        
        # Create all tables
        db.create_all()
        print("✓ Database tables created")
        
        # Create default admin user if it doesn't exist
        admin_user = User.query.filter_by(username='admin', is_admin=True).first()
        if not admin_user:
            admin_user = User(
                username='admin', 
                email='admin@decorilla.com',
                password='admin123',
                is_admin=True,
                user_type='admin'
            )
            db.session.add(admin_user)
            print("✓ Default admin user created (username: admin, password: admin123)")
        else:
            print("✓ Admin user already exists")
        
        try:
            db.session.commit()
            print("✓ Database setup completed successfully!")
        except Exception as e:
            db.session.rollback()
            print(f"✗ Error during setup: {e}")
            return False
        
        return True

def main():
    """Main setup function"""
    print("=" * 40)
    print("Interior Design Website Setup")
    print("=" * 40)
    
    success = setup_database()
    
    if success:
        print("\n🎉 Setup completed successfully!")
        print("\nAdmin Login:")
        print("  Username: admin")
        print("  Password: admin123")
        print("\n⚠️  Change the default password after first login!")
    else:
        print("\n❌ Setup failed. Check error messages above.")

if __name__ == '__main__':
    main()