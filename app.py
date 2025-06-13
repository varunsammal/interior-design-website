from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_bcrypt import Bcrypt
from flask_migrate import Migrate
import os
from datetime import datetime
from config import Config

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
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime, nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    projects = db.relationship('Project', backref='user', lazy=True)

    def __init__(self, email, username=None, password=None):
        self.email = email
        self.username = username
        if password:
            self.password = bcrypt.generate_password_hash(password).decode('utf-8')

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
        db.drop_all()
        db.create_all()
        print("Database initialized successfully!")

init_db()

@app.route('/')
def home():
    return render_template('index.html')

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

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/profile')
@login_required
def profile():
    projects = Project.query.filter_by(user_id=current_user.id).all()
    return render_template('profile.html', projects=projects)

@app.route('/projects/new', methods=['GET', 'POST'])
@login_required
def new_project():
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        budget = request.form.get('budget')
        new_project = Project(
            title=title,
            description=description,
            budget=float(budget) if budget else None,
            user_id=current_user.id
        )
        db.session.add(new_project)
        db.session.commit()
        flash('Project created successfully!', 'success')
        return redirect(url_for('profile'))
    return render_template('new_project.html')

@app.route('/Pricing')
def pricing():
    return render_template('pricing.html')
@app.route('/Faq')
def faq():
    return render_template('FAQ.html')

@app.route('/quiz')
def quiz():
    return render_template('Quiz.html')

@app.route('/schedule-consultation', methods=['GET', 'POST'])
def schedule_consultation():
    if request.method == 'POST':
        # Process form data here
        first_name = request.form.get('firstName')
        zip_code = request.form.get('zipCode')
        phone = request.form.get('phone')
        budget = request.form.get('budget')
        source = request.form.get('source')
        description = request.form.get('description')
        
        # You can add code here to save the consultation request to the database
        # or send an email notification, etc.
        
        flash('Thank you for your consultation request! We will contact you shortly.', 'success')
        return redirect(url_for('home'))
    
    return render_template('schedule_consultation.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
