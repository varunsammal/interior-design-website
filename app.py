<<<<<<< HEAD
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# Home page route
=======
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_bcrypt import Bcrypt
from flask_migrate import Migrate
import os
from datetime import datetime
from config import Config
import requests
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
from google_auth_oauthlib.flow import Flow

app = Flask(__name__)
app.config.from_object(Config)

# Ensure the instance folder exists
try:
    os.makedirs(app.instance_path)
except OSError:
    pass

db = SQLAlchemy(app)
migrate = Migrate(app, db)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Database Models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=True)
    google_id = db.Column(db.String(100), unique=True, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime, nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    projects = db.relationship('Project', backref='user', lazy=True)

    def __init__(self, email, username=None, password=None, google_id=None):
        self.email = email
        self.username = username
        if password:
            self.password = bcrypt.generate_password_hash(password).decode('utf-8')
        self.google_id = google_id

    def check_password(self, password):
        if not self.password:
            return False
        return bcrypt.check_password_hash(self.password, password)

class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    budget = db.Column(db.Float, nullable=True)
    status = db.Column(db.String(20), default='pending')  # pending, in_progress, completed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    designs = db.relationship('Design', backref='project', lazy=True)

class Design(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    image_url = db.Column(db.String(200), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

# Create database tables
def init_db():
    with app.app_context():
        # Drop all tables
        db.drop_all()
        # Create all tables
        db.create_all()
        print("Database initialized successfully!")

# Initialize the database
init_db()

# Routes
>>>>>>> main
@app.route('/')
def home():
    return render_template('index.html')

<<<<<<< HEAD
# # How It Works route
# @app.route('/how-it-works/')
# def how_it_works():
#     # This is a placeholder - you'll create this template later
#     return render_template('how_it_works.html')  # For now, redirect to home

# # Designers route
# @app.route('/designers/')
# def designers():
#     # This is a placeholder - you'll create this template later
#     return render_template('designers.html')  # For now, redirect to home

# # Portfolio route
# @app.route('/portfolio/')
# def portfolio():
#     # This is a placeholder - you'll create this template later
#     return render_template('portfolio.html')  # For now, redirect to home

# # Pricing route
# @app.route('/pricing/')
# def pricing():
#     # This is a placeholder - you'll create this template later
#     return render_template('pricing.html')  # For now, redirect to home

# # Reviews route
# @app.route('/reviews/')
# def reviews():
#     # This is a placeholder - you'll create this template later
#     return render_template('reviews.html')  # For now, redirect to home

# # Blog route
# @app.route('/blog/')
# def blog():
#     # This is a placeholder - you'll create this template later
#     return render_template('blog.html')  # For now, redirect to home

# # Contact form submission route - for static site, we'll make this a GET route
# @app.route('/contact/')
# def contact():
#     # For static site, we'll just show the home page
#     return render_template('contact.html')


=======
# Google Sign-In route
@app.route('/google-login')
def google_login():
    flow = Flow.from_client_config(
        {
            "web": {
                "client_id": app.config['GOOGLE_CLIENT_ID'],
                "client_secret": app.config['GOOGLE_CLIENT_SECRET'],
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
            }
        },
        scopes=["openid", "https://www.googleapis.com/auth/userinfo.email", "https://www.googleapis.com/auth/userinfo.profile"]
    )
    flow.redirect_uri = url_for('google_callback', _external=True)
    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true'
    )
    session['state'] = state
    return redirect(authorization_url)

# Google callback route
@app.route('/google-callback')
def google_callback():
    flow = Flow.from_client_config(
        {
            "web": {
                "client_id": app.config['GOOGLE_CLIENT_ID'],
                "client_secret": app.config['GOOGLE_CLIENT_SECRET'],
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
            }
        },
        scopes=["openid", "https://www.googleapis.com/auth/userinfo.email", "https://www.googleapis.com/auth/userinfo.profile"],
        state=session['state']
    )
    flow.redirect_uri = url_for('google_callback', _external=True)
    
    authorization_response = request.url
    flow.fetch_token(authorization_response=authorization_response)
    
    credentials = flow.credentials
    request_session = requests.session()
    token_request = google_requests.Request(session=request_session)
    
    id_info = id_token.verify_oauth2_token(
        id_token=credentials._id_token,
        request=token_request,
        audience=app.config['GOOGLE_CLIENT_ID']
    )
    
    # Check if user exists
    user = User.query.filter_by(google_id=id_info['sub']).first()
    if not user:
        # Check if email exists
        user = User.query.filter_by(email=id_info['email']).first()
        if user:
            # Link Google account to existing user
            user.google_id = id_info['sub']
            flash('Your Google account has been linked to your existing account.', 'success')
        else:
            # Create new user from Google info
            username = id_info.get('name', '').replace(' ', '_').lower()
            # Ensure username is unique
            base_username = username
            counter = 1
            while User.query.filter_by(username=username).first():
                username = f"{base_username}_{counter}"
                counter += 1
            
            user = User(
                email=id_info['email'],
                username=username,
                google_id=id_info['sub']
            )
            db.session.add(user)
            flash('Account created successfully with Google!', 'success')
    
    user.last_login = datetime.utcnow()
    db.session.commit()
    login_user(user)
    
    return redirect(url_for('profile'))

# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            login_user(user)
            user.last_login = datetime.utcnow()
            db.session.commit()
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login unsuccessful. Please check username and password', 'danger')
    
    return render_template('login.html')

# Register route
@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        
        if User.query.filter_by(username=username).first():
            flash('Username already exists', 'danger')
            return redirect(url_for('register'))
        
        if User.query.filter_by(email=email).first():
            flash('Email already registered', 'danger')
            return redirect(url_for('register'))
        
        new_user = User(email=email, username=username, password=password)
        db.session.add(new_user)
        db.session.commit()
        
        flash('Account created successfully! Please login.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

# Logout route
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

# Profile route
@app.route('/profile')
@login_required
def profile():
    projects = Project.query.filter_by(user_id=current_user.id).all()
    return render_template('profile.html', projects=projects)

# Project routes
@app.route('/projects/new', methods=['GET', 'POST'])
@login_required
def new_project():
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        budget = request.form.get('budget')
        
        project = Project(
            title=title,
            description=description,
            budget=float(budget) if budget else None,
            user_id=current_user.id
        )
        db.session.add(project)
        db.session.commit()
        
        flash('Project created successfully!', 'success')
        return redirect(url_for('profile'))
    
    return render_template('new_project.html')
>>>>>>> main

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
