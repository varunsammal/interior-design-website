from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
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
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

# Configure upload folder and allowed extensions
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

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
    profile_image = db.Column(db.String(200), nullable=True)
    projects = db.relationship('Project', backref='user', lazy=True)
    designs = db.relationship('DesignImage', backref='user', lazy='dynamic')

    def __init__(self, email, username=None, password=None, address=None, phone=None, design_style=None, profile_image=None):

        self.email = email
        self.username = username
        self.address = address
        self.phone = phone
        self.design_style = design_style
        self.profile_image = profile_image

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
    design_id = db.Column(db.Integer, db.ForeignKey('design_images.id'), nullable=False)
    helpful_count = db.Column(db.Integer, default=0)
    
    # Relationships
    user = db.relationship('User', backref=db.backref('reviews', lazy=True))
    design = db.relationship('DesignImage', backref=db.backref('reviews', lazy=True))

    def __init__(self, rating, comment, user_id, design_id):
        self.rating = rating
        self.comment = comment
        self.user_id = user_id
        self.design_id = design_id

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Create database tables
def init_db():
    with app.app_context():

        # Create all tables
        db.create_all()
        
        # Check if 'profile_image' column exists in 'users' table, add if not
        try:
            with db.engine.connect() as connection:
                inspector = db.inspect(db.engine)
                if 'users' in inspector.get_table_names():
                    columns = [col['name'] for col in inspector.get_columns('users')]
                    if 'profile_image' not in columns:
                        with connection.begin() as transaction:
                            connection.execute(db.text('ALTER TABLE users ADD COLUMN profile_image VARCHAR(200)'))
                            print("Added 'profile_image' column to 'users' table.")
                            transaction.commit()
        except Exception as e:
            print(f"Error checking/adding profile_image column: {e}")
            
        # Update the reviews table if needed
        try:
            with db.engine.connect() as connection:
                inspector = db.inspect(db.engine)
                if 'reviews' in inspector.get_table_names():
                    columns = [col['name'] for col in inspector.get_columns('reviews')]
                    if 'helpful_count' not in columns:
                        with connection.begin() as transaction:
                            connection.execute(db.text('ALTER TABLE reviews ADD COLUMN helpful_count INTEGER DEFAULT 0'))
                            print("Added 'helpful_count' column to 'reviews' table.")
                            transaction.commit()
        except Exception as e:
            print(f"Error checking/adding helpful_count column: {e}")
            
        # Update the reviews table if needed
        try:
            # Check if the design_id column exists and points to the wrong table
            with db.engine.connect() as conn:
                result = conn.execute(db.text("""
                    SELECT column_name, data_type, is_nullable 
                    FROM information_schema.columns 
                    WHERE table_name = 'reviews' AND column_name = 'design_id'
                """)).fetchone()
                
                if result and 'designs' in str(result):
                    # Drop the existing foreign key constraint
                    conn.execute(db.text("""
                        ALTER TABLE reviews 
                        DROP CONSTRAINT IF EXISTS reviews_design_id_fkey
                    """))
                    
                    # Update the column to reference design_images
                    conn.execute(db.text("""
                        ALTER TABLE reviews 
                        ALTER COLUMN design_id TYPE INTEGER USING design_id::INTEGER,
                        ADD CONSTRAINT reviews_design_id_fkey 
                        FOREIGN KEY (design_id) 
                        REFERENCES design_images(id)
                    """))
                    
                    print("Successfully updated reviews table schema")
        except Exception as e:
            print(f"Error updating schema: {str(e)}")
            # Continue with the application even if schema update fails
            pass

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

    print(f"DEBUG: Profile image for user {current_user.id}: {current_user.profile_image}")
    projects = Project.query.filter_by(user_id=current_user.id).all()
    return render_template('profile.html', user=current_user, projects=projects, DesignImage=DesignImage)


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

@app.route('/portfolio')
def portfolio():
    return render_template('portfolio.html')


@app.route('/designers')
def designers():
    return render_template('designer.html')


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

        print(f"Error deleting design: {e}")

        flash('An error occurred while deleting the design', 'danger')
    
    return redirect(url_for('upload'))

@app.route('/design/<int:design_id>/reviews', methods=['GET', 'POST'])
@login_required
def design_reviews(design_id):

    try:
        design = DesignImage.query.get_or_404(design_id)
        
        if request.method == 'POST':
            rating = request.form.get('rating')
            comment = request.form.get('comment', '').strip()
            
            if not rating:
                flash('Please select a rating', 'danger')
                return redirect(url_for('design_reviews', design_id=design_id))
            
            try:
                rating = int(rating)
                if rating < 1 or rating > 5:
                    flash('Rating must be between 1 and 5', 'danger')
                    return redirect(url_for('design_reviews', design_id=design_id))
            except ValueError:
                flash('Invalid rating value', 'danger')
                return redirect(url_for('design_reviews', design_id=design_id))
            
            # Check if user has already reviewed this design
            existing_review = Review.query.filter_by(
                user_id=current_user.id,
                design_id=design_id
            ).first()
            
            if existing_review:
                flash('You have already reviewed this design', 'warning')
                return redirect(url_for('design_reviews', design_id=design_id))
            
            try:
                review = Review(
                    rating=rating,
                    comment=comment,
                    user_id=current_user.id,
                    design_id=design_id
                )
                db.session.add(review)
                db.session.commit()
                flash('Your review has been submitted successfully!', 'success')
            except Exception as e:
                db.session.rollback()
                print(f"Error submitting review: {str(e)}")
                flash('An error occurred while submitting your review. Please try again.', 'danger')
            
            return redirect(url_for('design_reviews', design_id=design_id))
        
        # Get all reviews for this design, ordered by creation date
        reviews = Review.query.filter_by(design_id=design_id).order_by(Review.created_at.desc()).all()
        
        # Initialize rating_distribution
        rating_distribution = {}
        for i in range(1, 6):
            count = Review.query.filter(Review.rating == i).count()
            percentage = (count / (len(reviews) if len(reviews) > 0 else 1)) * 100
            rating_distribution[i] = round(percentage, 1)

        return render_template('reviews.html', design=design, reviews=reviews, rating_distribution=rating_distribution)
    except Exception as e:
        print(f"Error in design_reviews route: {str(e)}")
        flash('An error occurred. Please try again later.', 'danger')
        return redirect(url_for('upload'))

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


def generate_sample_reviews():
    sample_reviews = [
        {
            'username': 'Sarah Johnson',
            'rating': 5,
            'comment': 'Absolutely love how my living room turned out! The designer perfectly captured my vision of a modern yet cozy space. The color scheme and furniture choices are exactly what I was looking for.',
            'created_at': datetime(2024, 2, 15),
            'helpful_count': 12
        },
        {
            'username': 'Michael Chen',
            'rating': 4,
            'comment': 'Great experience working with the design team. They transformed my small apartment into a functional and stylish space. The only reason for 4 stars is that the project took a bit longer than expected.',
            'created_at': datetime(2024, 2, 10),
            'helpful_count': 8
        },
        {
            'username': 'Emma Rodriguez',
            'rating': 5,
            'comment': 'The attention to detail in my kitchen redesign is incredible! Every element works together harmoniously, and the storage solutions are both practical and beautiful. Couldn\'t be happier with the results!',
            'created_at': datetime(2024, 2, 5),
            'helpful_count': 15
        },
        {
            'username': 'David Kim',
            'rating': 5,
            'comment': 'Professional, creative, and responsive team. They helped me achieve the perfect balance between contemporary and traditional styles in my home office. The lighting solutions are particularly impressive.',
            'created_at': datetime(2024, 1, 28),
            'helpful_count': 10
        },
        {
            'username': 'Lisa Thompson',
            'rating': 4,
            'comment': 'The bedroom redesign exceeded my expectations! The color palette creates such a peaceful atmosphere. The only minor issue was with the delivery timing of some furniture pieces.',
            'created_at': datetime(2024, 1, 20),
            'helpful_count': 7
        }
    ]
    return sample_reviews

@app.route('/reviews')
def reviews():
    # Get query parameters
    page = request.args.get('page', 1, type=int)
    per_page = 10
    search_query = request.args.get('search', '')
    rating_filter = request.args.get('rating', type=int)
    sort_by = request.args.get('sort', 'recent')

    # Get all reviews
    reviews_query = Review.query

    # Apply filters
    if search_query:
        reviews_query = reviews_query.filter(Review.comment.ilike(f'%{search_query}%'))
    if rating_filter:
        reviews_query = reviews_query.filter(Review.rating == rating_filter)

    # Apply sorting
    if sort_by == 'rating':
        reviews_query = reviews_query.order_by(Review.rating.desc())
    elif sort_by == 'helpful':
        reviews_query = reviews_query.order_by(Review.helpful_count.desc())
    else:  # recent
        reviews_query = reviews_query.order_by(Review.created_at.desc())

    # Get paginated reviews
    reviews = reviews_query.paginate(page=page, per_page=per_page, error_out=False)
    
    # If no reviews exist, use sample reviews
    if not reviews.items and page == 1:
        sample_reviews = generate_sample_reviews()
        # Calculate average rating and distribution
        total_rating = sum(review['rating'] for review in sample_reviews)
        average_rating = total_rating / len(sample_reviews)
        rating_distribution = {
            i: sum(1 for r in sample_reviews if r['rating'] == i) / len(sample_reviews) * 100
            for i in range(1, 6)
        }
        return render_template('reviews.html',
                             reviews=sample_reviews,
                             average_rating=round(average_rating, 1),
                             total_reviews=len(sample_reviews),
                             rating_distribution=rating_distribution,
                             current_page=page,
                             total_pages=1,
                             has_prev=False,
                             has_next=False)
    
    # Calculate average rating and distribution for real reviews
    all_reviews = Review.query.all()
    if all_reviews:
        total_rating = sum(review.rating for review in all_reviews)
        average_rating = total_rating / len(all_reviews)
        rating_distribution = {
            i: sum(1 for r in all_reviews if r.rating == i) / len(all_reviews) * 100
            for i in range(1, 6)
        }
    else:
        average_rating = 0
        rating_distribution = {i: 0 for i in range(1, 6)}

    return render_template('reviews.html',
                         reviews=reviews.items,
                         average_rating=round(average_rating, 1),
                         total_reviews=len(all_reviews),
                         rating_distribution=rating_distribution,
                         current_page=page,
                         total_pages=reviews.pages,
                         has_prev=reviews.has_prev,
                         has_next=reviews.has_next)

@app.route('/api/reviews/<int:review_id>/helpful', methods=['POST'])
@login_required
def mark_review_helpful(review_id):
    review = Review.query.get_or_404(review_id)
    review.helpful_count += 1
    db.session.commit()
    return jsonify({'success': True})

@app.route('/api/reviews/<int:review_id>', methods=['PUT'])
@login_required
def update_review(review_id):
    review = Review.query.get_or_404(review_id)
    
    # Check if user is the review author
    if review.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403

    data = request.get_json()
    review.rating = data.get('rating')
    review.comment = data.get('comment')
    db.session.commit()
    return jsonify({'success': True})

@app.route('/api/reviews/<int:review_id>', methods=['DELETE'])
@login_required
def delete_review(review_id):
    review = Review.query.get_or_404(review_id)
    
    # Check if user is the review author
    if review.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403

    db.session.delete(review)
    db.session.commit()
    return jsonify({'success': True})

@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    user = current_user
    if request.method == 'POST':
        user.username = request.form.get('username')
        user.email = request.form.get('email')
        user.address = request.form.get('address')
        user.phone = request.form.get('phone')
        user.design_style = request.form.get('design_style')

        # Handle profile image removal
        remove_image = request.form.get('remove_profile_image')
        if remove_image == '1' and user.profile_image:
            try:
                # Construct the full path to the profile picture
                profile_pic_path = os.path.join(app.config['UPLOAD_FOLDER'], user.profile_image)
                # Delete the user-specific folder if it's empty after deletion
                user_specific_folder = os.path.dirname(profile_pic_path)
                if os.path.exists(profile_pic_path):
                    os.remove(profile_pic_path)
                    print(f"Deleted profile picture: {profile_pic_path}")
                
                # Check if the user-specific folder is empty and remove it
                if os.path.exists(user_specific_folder) and not os.listdir(user_specific_folder):
                    os.rmdir(user_specific_folder)
                    print(f"Removed empty user folder: {user_specific_folder}")

                user.profile_image = None # Clear the profile image from the database
                flash('Profile picture removed successfully!', 'success')
            except Exception as e:
                print(f"Error removing profile picture: {e}")
                flash(f'An error occurred while removing profile picture: {e}', 'danger')

        # Handle profile image upload (if a new file is provided)
        if 'profile_image' in request.files and request.files['profile_image'].filename != '':
            file = request.files['profile_image']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                # Create user-specific folder if it doesn't exist
                user_folder = os.path.join(app.config['UPLOAD_FOLDER'], str(user.id))
                os.makedirs(user_folder, exist_ok=True)
                
                filepath = os.path.join(user_folder, filename)
                file.save(filepath)
                user.profile_image = os.path.join(str(user.id), filename).replace('\\', '/') # Store relative path with forward slashes
                flash('Profile picture updated successfully!', 'success')
            else:
                flash('Invalid file type for profile image. Allowed types are png, jpg, jpeg, gif.', 'danger')
                return redirect(url_for('edit_profile'))

        try:
            db.session.commit()
            print("Database commit successful.")
            flash('Your profile has been updated successfully!', 'success')
            return redirect(url_for('profile'))
        except Exception as e:
            db.session.rollback()
            print(f"Database commit failed: {e}")
            flash(f'An error occurred while updating your profile: {e}', 'danger')

    return render_template('edit_profile.html', user=user)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
