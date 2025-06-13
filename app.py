from flask import Flask, render_template, request, redirect, url_for, flash,session
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
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///uploads.db'  # SQLite database
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = os.path.join(os.getcwd(), 'static/uploads')
app.config['ALLOWED_EXTENSIONS'] = {'jpg', 'jpeg', 'png'}

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
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
# How It Works route
@app.route('/how-it-works/')
def how_it_works():
    # This is a placeholder - you'll create this template later
    return render_template('how_it_works.html')  # For now, redirect to home

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
@app.route('/blog')
def blog():
    # This is a placeholder - you'll create this template later
    return render_template('blog.html')  # For now, redirect to home

# # Contact form submission route - for static site, we'll make this a GET route
# @app.route('/contact/')
# def contact():
#     # For static site, we'll just show the home page
#     return render_template('contact.html')




# @app.route('/upload', methods=['GET', 'POST'])
# def upload():
#     if request.method == 'POST':
#         file = request.files['file']
#         if file:
#             filename = secure_filename(file.filename)
#             file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
#             new_file = File(filename=filename)
#             db.session.add(new_file)
#             db.session.commit()
#             return redirect(url_for('downloads'))
#     return render_template('upload.html')

upload_folder="static/uploads/"

class UploadedImage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(100), nullable=False)
    filepath = db.Column(db.String(200), nullable=False)
    upload_date = db.Column(db.DateTime, default=db.func.current_timestamp())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('images', lazy=True))
    
    def delete(self):
        """Delete the image record and the associated file"""
        try:
            # Remove the file from filesystem
            if os.path.exists(self.filepath):
                os.remove(self.filepath)
            # Remove the record from database
            db.session.delete(self)
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            print(f"Error deleting image: {e}")
            return False

    def __repr__(self):
        return f'<UploadedImage {self.filename}>'
    
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
# Create database tables
with app.app_context():
    db.create_all()

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


@app.route('/delete/<int:image_id>', methods=['POST'])
def delete_image(image_id):
    image = UploadedImage.query.get_or_404(image_id)
    if image.delete():
        flash('Image successfully deleted', 'success')
    else:
        flash('Error deleting image', 'danger')
    return redirect(url_for('upload'))

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
    
    designs = current_user.designs.order_by(DesignImage.upload_date.desc()).all()
    return render_template('upload.html', designs=designs)



class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(200))
    phone = db.Column(db.String(20))
    design_style = db.Column(db.String(50))
    
    def set_password(self, password):
        self.password = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password, password)
    
class DesignImage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(100), nullable=False)
    filepath = db.Column(db.String(200), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    upload_date = db.Column(db.DateTime, default=db.func.current_timestamp())
    design_notes = db.Column(db.Text)

    user = db.relationship('User', backref=db.backref('designs', lazy=True))



@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        address = request.form['address']
        phone = request.form['phone']
        design_style = request.form['design_style']
        
        if User.query.filter_by(email=email).first():
            flash('Email already registered', 'danger')
            return redirect(url_for('register'))
            
        user = User(
            name=name,
            email=email,
            address=address,
            phone=phone,
            design_style=design_style
        )
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        login_user(user)
        flash('Registration successful!', 'success')
        return redirect(url_for('upload'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        
        if user and user.check_password(password):
            login_user(user)
            flash('Login successful', 'success')
            return redirect(url_for('upload'))
        else:
            flash('Invalid email or password', 'danger')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out', 'info')
    return redirect(url_for('home'))
    


if __name__ == '__main__':
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    app.run(debug=True)