from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os
from flask_bcrypt import Bcrypt
from flask_migrate import Migrate
from datetime import datetime
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

# Initialize extensions
db = SQLAlchemy(app)
migrate = Migrate(app, db)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Ensure the instance folder exists
try:
    os.makedirs(app.instance_path)
except OSError:
    pass

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Database Models
class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime, nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    address = db.Column(db.String(200))
    phone = db.Column(db.String(20))
    design_style = db.Column(db.String(50))
    projects = db.relationship('Project', backref='user', lazy=True)
    designs = db.relationship('DesignImage', backref='user', lazy='dynamic')

    def __init__(self, email, username=None, password=None, address=None, phone=None, design_style=None):
        self.email = email
        self.username = username
        self.address = address
        self.phone = phone
        self.design_style = design_style
        if password:
            self.password = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        if not self.password:
            return False
        return bcrypt.check_password_hash(self.password, password)

class Project(db.Model):
    __tablename__ = 'projects'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    budget = db.Column(db.Float, nullable=True)
    status = db.Column(db.String(20), default='pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    designs = db.relationship('Design', backref='project', lazy=True)

class Design(db.Model):
    __tablename__ = 'designs'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    image_url = db.Column(db.String(200), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)

class DesignImage(db.Model):
    __tablename__ = 'design_images'
    
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(100), nullable=False)
    filepath = db.Column(db.String(200), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    upload_date = db.Column(db.DateTime, default=db.func.current_timestamp())
    design_notes = db.Column(db.Text)

class Review(db.Model):
    __tablename__ = 'reviews'
    
    id = db.Column(db.Integer, primary_key=True)
    rating = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    design_id = db.Column(db.Integer, db.ForeignKey('designs.id'), nullable=False)
    
    # Relationships
    user = db.relationship('User', backref='reviews')
    design = db.relationship('Design', backref='reviews')

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Create database tables
def init_db():
    with app.app_context():
        db.create_all()
        print("Database initialized successfully!")

# Initialize database
init_db()

@app.route('/')
def home():
    designs = DesignImage.query.all()
    return render_template('index.html', designs=designs)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        address = request.form.get('address')
        phone = request.form.get('phone')
        design_style = request.form.get('design_style')
        
        # Check if email already exists
        if User.query.filter_by(email=email).first():
            flash('Email already registered', 'danger')
            return redirect(url_for('register'))
            
        # Create new user
        new_user = User(
            email=email,
            username=name,
            password=password,
            address=address,
            phone=phone,
            design_style=design_style
        )
        
        try:
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user)
            flash('Account created successfully! Welcome to Decorilla!', 'success')
            return redirect(url_for('home'))
        except Exception as e:
            db.session.rollback()
            flash('An error occurred during registration. Please try again.', 'danger')
            return redirect(url_for('register'))
            
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        
        if user and user.check_password(password):
            login_user(user)
            user.last_login = datetime.utcnow()
            db.session.commit()
            flash('Login successful!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Invalid email or password', 'danger')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out successfully', 'info')
    return redirect(url_for('home'))

@app.route('/profile')
@login_required
def profile():
    user = current_user
    projects = Project.query.filter_by(user_id=current_user.id).all()
    return render_template('profile.html', user=user, projects=projects)

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

@app.route('/how-it-works/')
def how_it_works():
    return render_template('how_it_works.html')

@app.route('/blog')
def blog():
    return render_template('blog.html')

@app.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    if request.method == 'POST':
        if 'design_image' not in request.files:
            flash('No file selected', 'danger')
            return redirect(request.url)
            
        file = request.files['design_image']
        design_notes = request.form.get('design_notes', '')
        
        if file.filename == '':
            flash('No file selected', 'danger')
            return redirect(request.url)
            
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            design = DesignImage(
                filename=filename,
                filepath=filepath,
                user_id=current_user.id,
                design_notes=design_notes
            )
            db.session.add(design)
            db.session.commit()
            
            flash('Design image uploaded successfully!', 'success')
            return redirect(url_for('upload'))
    
    # Get designs for the current user, ordered by upload date
    designs = DesignImage.query.filter_by(user_id=current_user.id).order_by(DesignImage.upload_date.desc()).all()
    return render_template('upload.html', designs=designs)

@app.route('/delete_design', methods=['POST'])
@login_required
def delete_design():
    design_id = request.form.get('design_id')
    if not design_id:
        flash('Design ID is required', 'danger')
        return redirect(url_for('upload'))
    
    design = DesignImage.query.get_or_404(design_id)
    
    # Check if the design belongs to the current user
    if design.user_id != current_user.id:
        flash('You do not have permission to delete this design', 'danger')
        return redirect(url_for('upload'))
    
    try:
        # Delete the file from the filesystem
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], design.filename)
        if os.path.exists(file_path):
            os.remove(file_path)
        
        # Delete the database record
        db.session.delete(design)
        db.session.commit()
        flash('Design deleted successfully', 'success')
    except Exception as e:
        db.session.rollback()
        flash('An error occurred while deleting the design', 'danger')
    
    return redirect(url_for('upload'))

@app.route('/design/<int:design_id>/reviews', methods=['GET', 'POST'])
@login_required
def design_reviews(design_id):
    design = Design.query.get_or_404(design_id)
    
    if request.method == 'POST':
        rating = request.form.get('rating')
        comment = request.form.get('comment')
        
        if not rating:
            flash('Please select a rating', 'danger')
            return redirect(url_for('design_reviews', design_id=design_id))
        
        # Check if user has already reviewed this design
        existing_review = Review.query.filter_by(
            user_id=current_user.id,
            design_id=design_id
        ).first()
        
        if existing_review:
            flash('You have already reviewed this design', 'warning')
            return redirect(url_for('design_reviews', design_id=design_id))
        
        review = Review(
            rating=int(rating),
            comment=comment,
            user_id=current_user.id,
            design_id=design_id
        )
        
        try:
            db.session.add(review)
            db.session.commit()
            flash('Your review has been submitted successfully!', 'success')
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while submitting your review', 'danger')
        
        return redirect(url_for('design_reviews', design_id=design_id))
    
    # Get all reviews for this design, ordered by creation date
    reviews = Review.query.filter_by(design_id=design_id).order_by(Review.created_at.desc()).all()
    
    return render_template('reviews.html', design=design, reviews=reviews)

@app.route('/pricing')
def pricing():
    return render_template('pricing.html')

@app.route('/faq')
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

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
