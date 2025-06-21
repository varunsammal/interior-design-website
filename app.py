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

# Import and initialize models
import models
models.db = db
models.bcrypt = bcrypt
models.init_models()
from models import User, Project, Design, DesignImage, Review, AdminUser, Card, FAQ, QuizQuestion, PortfolioItem
# Ensure the instance folder exists
try:
    os.makedirs(app.instance_path)
except OSError:
    pass

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

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
        
        # Add new columns to existing users table
        try:
            with db.engine.connect() as connection:
                inspector = db.inspect(db.engine)
                if 'users' in inspector.get_table_names():
                    columns = [col['name'] for col in inspector.get_columns('users')]
                    
                    if 'is_admin' not in columns:
                        with connection.begin() as transaction:
                            connection.execute(db.text('ALTER TABLE users ADD COLUMN is_admin BOOLEAN DEFAULT FALSE'))
                            print("Added 'is_admin' column to 'users' table.")
                            transaction.commit()
                    
                    if 'user_type' not in columns:
                        with connection.begin() as transaction:
                            connection.execute(db.text("ALTER TABLE users ADD COLUMN user_type VARCHAR(20) DEFAULT 'user'"))
                            print("Added 'user_type' column to 'users' table.")
                            transaction.commit()
                    
                    # Make username NOT NULL and add constraints if needed
                    if 'username' in columns:
                        with connection.begin() as transaction:
                            # First, set any NULL usernames to a default value
                            connection.execute(db.text("UPDATE users SET username = CONCAT('user_', id) WHERE username IS NULL"))
                            # Then make the column NOT NULL
                            connection.execute(db.text('ALTER TABLE users ALTER COLUMN username SET NOT NULL'))
                            print("Updated 'username' column constraints in 'users' table.")
                            transaction.commit()
                    
                    # Make email nullable
                    if 'email' in columns:
                        with connection.begin() as transaction:
                            connection.execute(db.text('ALTER TABLE users ALTER COLUMN email DROP NOT NULL'))
                            print("Made 'email' column nullable in 'users' table.")
                            transaction.commit()
        except Exception as e:
            print(f"Error updating users table schema: {e}")

        # Migrate existing admin users to the unified user system
        try:
            admin_users = AdminUser.query.all()
            for admin_user in admin_users:
                # Check if this admin user already exists in the unified users table
                existing_user = User.query.filter_by(username=admin_user.username).first()
                if not existing_user:
                    # Create a new user with admin privileges
                    unified_admin = User(
                        username=admin_user.username,
                        email=f"{admin_user.username}@admin.decorilla.com",  # Temporary email
                        is_admin=True,
                        user_type='admin'
                    )
                    # Copy the hashed password directly
                    unified_admin.password = admin_user.password
                    db.session.add(unified_admin)
                    print(f"Migrated admin user: {admin_user.username}")
                else:
                    # Update existing user to be admin
                    existing_user.is_admin = True
                    existing_user.user_type = 'admin'
                    print(f"Updated existing user to admin: {existing_user.username}")
            
            db.session.commit()
        except Exception as e:
            print(f"Error migrating admin users: {e}")
            db.session.rollback()

        # Create default admin user if none exists in the unified system
        if not User.query.filter_by(is_admin=True).first():
            admin = User(
                username='admin',
                email='admin@decorilla.com',
                password='admin123',
                is_admin=True,
                user_type='admin'
            )
            db.session.add(admin)
            try:
                db.session.commit()
                print("Created default admin user in unified system (username: admin, password: admin123)")
            except Exception as e:
                print(f"Error creating unified admin user: {e}")
        
        # Create sample service cards if none exist
        if not Card.query.filter_by(card_type='service').first():
            sample_cards = [
                Card(
                    title="Up to 45% off at +350 furniture stores",
                    description="Save thousands with our exclusive trade discounts at top furniture retailers worldwide.",
                    image_url="https://images.unsplash.com/photo-1555041469-a586c61ea9bc?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1770&q=80",
                    card_type="service",
                    page="index",
                    icon_class="fas fa-tag",
                    order_position=1
                ),
                Card(
                    title="Concepts from multiple top designers",
                    description="Choose from multiple design concepts created by our award-winning interior designers.",
                    image_url="https://images.unsplash.com/photo-1578662996442-48f60103fc96?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1770&q=80",
                    card_type="service",
                    page="index",
                    icon_class="fas fa-paint-brush",
                    order_position=2
                ),
                Card(
                    title="One-on-one interior design consultation",
                    description="Work directly with your designer through personalized consultations and feedback sessions.",
                    image_url="https://images.unsplash.com/photo-1560472354-b33ff0c44a43?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1826&q=80",
                    card_type="service",
                    page="index",
                    icon_class="fas fa-comments",
                    order_position=3
                ),
                Card(
                    title="3D model of your space",
                    description="Visualize your new space with detailed 3D renderings before making any purchases.",
                    image_url="https://images.unsplash.com/photo-1586023492125-27b2c045efd7?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1770&q=80",
                    card_type="service",
                    page="index",
                    icon_class="fas fa-cube",
                    order_position=4
                ),
                Card(
                    title="Color palette & floor plan",
                    description="Get professional color schemes and detailed floor plans tailored to your style and space.",
                    image_url="https://images.unsplash.com/photo-1513694203232-719a280e022f?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1769&q=80",
                    card_type="service",
                    page="index",
                    icon_class="fas fa-palette",
                    order_position=5
                )
            ]
            
            for card in sample_cards:
                db.session.add(card)
            
            try:
                db.session.commit()
                print("Created sample service cards")
            except Exception as e:
                print(f"Error creating sample cards: {e}")

# Initialize database
init_db()

@app.route('/')
def home():
    designs = DesignImage.query.all()
    # Get dynamic cards for homepage
    service_cards = Card.query.filter_by(
        page='index', 
        card_type='service', 
        is_active=True
    ).order_by(Card.order_position).all()
    
    return render_template('index.html', designs=designs, service_cards=service_cards)

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
        if email and User.query.filter_by(email=email).first():
            flash('Email already registered', 'danger')
            return redirect(url_for('register'))
        
        # Check if username already exists
        if User.query.filter_by(username=name).first():
            flash('Username already taken', 'danger')
            return redirect(url_for('register'))
            
        # Create new user
        new_user = User(
            username=name,
            email=email,
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
        # If already logged in and is admin, redirect to admin dashboard
        if current_user.is_admin:
            return redirect(url_for('admin_dashboard'))
        else:
            return redirect(url_for('home'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # Find user by username
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            login_user(user)
            user.last_login = datetime.utcnow()
            db.session.commit()
            
            if user.is_admin:
                # Set session variables for admin template compatibility
                session['admin_logged_in'] = True
                session['admin_id'] = user.id
                session['admin_username'] = user.username
                flash('Admin login successful! Welcome to the admin dashboard.', 'success')
                return redirect(url_for('admin_dashboard'))
            else:
                flash('Login successful! Welcome back.', 'success')
                next_page = request.args.get('next')
                return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Invalid username or password', 'danger')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    # Clear admin session variables if they exist
    session.pop('admin_logged_in', None)
    session.pop('admin_id', None)
    session.pop('admin_username', None)
    
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
    # Get active portfolio items
    portfolio_items = PortfolioItem.query.filter_by(is_active=True).order_by(PortfolioItem.order_position).all()
    
    # Get featured items
    featured_items = PortfolioItem.query.filter_by(is_active=True, is_featured=True).order_by(PortfolioItem.order_position).limit(6).all()
    
    # Get unique categories and styles for filtering
    categories = db.session.query(PortfolioItem.category).filter(PortfolioItem.is_active==True).distinct().all()
    styles = db.session.query(PortfolioItem.style).filter(PortfolioItem.is_active==True).distinct().all()
    
    return render_template('portfolio.html', 
                         portfolio_items=portfolio_items,
                         featured_items=featured_items,
                         categories=[c[0] for c in categories if c[0]],
                         styles=[s[0] for s in styles if s[0]])


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
    # Get active FAQs ordered by position
    faqs = FAQ.query.filter_by(is_active=True).order_by(FAQ.order_position).all()
    
    # Group FAQs by category
    categorized_faqs = {}
    for faq_item in faqs:
        category = faq_item.category or 'General'
        if category not in categorized_faqs:
            categorized_faqs[category] = []
        categorized_faqs[category].append(faq_item)
    
    return render_template('FAQ.html', categorized_faqs=categorized_faqs)

@app.route('/quiz')
def quiz():
    # Get active quiz questions ordered by position
    quiz_questions = QuizQuestion.query.filter_by(is_active=True).order_by(QuizQuestion.order_position).all()
    return render_template('Quiz.html', quiz_questions=quiz_questions)

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

# Admin Helper Functions
def is_admin():
    # Check both session-based and user-based admin status for compatibility
    return (current_user.is_authenticated and current_user.is_admin) or session.get('admin_logged_in', False)

def admin_required(f):
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Please log in to access this page', 'danger')
            return redirect(url_for('login'))
        if not current_user.is_admin:
            flash('Admin access required', 'danger')
            return redirect(url_for('home'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

# Admin Routes
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    # Redirect to unified login system
    return redirect(url_for('login'))

@app.route('/admin/logout')
@admin_required
def admin_logout():
    # Use the unified logout system
    return redirect(url_for('logout'))

@app.route('/admin')
@app.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    # Get statistics
    total_cards = Card.query.count()
    active_cards = Card.query.filter_by(is_active=True).count()
    total_users = User.query.count()
    total_reviews = Review.query.count()
    total_faqs = FAQ.query.count()
    active_faqs = FAQ.query.filter_by(is_active=True).count()
    total_portfolio = PortfolioItem.query.count()
    active_portfolio = PortfolioItem.query.filter_by(is_active=True).count()
    total_quiz = QuizQuestion.query.count()
    active_quiz = QuizQuestion.query.filter_by(is_active=True).count()
    
    # Get recent items
    recent_cards = Card.query.order_by(Card.created_at.desc()).limit(3).all()
    recent_faqs = FAQ.query.order_by(FAQ.created_at.desc()).limit(3).all()
    recent_portfolio = PortfolioItem.query.order_by(PortfolioItem.created_at.desc()).limit(3).all()
    
    stats = {
        'total_cards': total_cards,
        'active_cards': active_cards,
        'total_users': total_users,
        'total_reviews': total_reviews,
        'total_faqs': total_faqs,
        'active_faqs': active_faqs,
        'total_portfolio': total_portfolio,
        'active_portfolio': active_portfolio,
        'total_quiz': total_quiz,
        'active_quiz': active_quiz
    }
    
    return render_template('admin/dashboard.html', 
                         stats=stats, 
                         recent_cards=recent_cards,
                         recent_faqs=recent_faqs,
                         recent_portfolio=recent_portfolio)

@app.route('/admin/cards')
@admin_required
def admin_cards():
    page = request.args.get('page', 1, type=int)
    card_type = request.args.get('type', '')
    page_filter = request.args.get('page_filter', '')
    
    query = Card.query
    
    if card_type:
        query = query.filter(Card.card_type == card_type)
    if page_filter:
        query = query.filter(Card.page == page_filter)
    
    cards = query.order_by(Card.page, Card.order_position).paginate(
        page=page, per_page=10, error_out=False
    )
    
    # Get unique card types and pages for filters
    card_types = db.session.query(Card.card_type).distinct().all()
    pages = db.session.query(Card.page).distinct().all()
    
    return render_template('admin/cards.html', 
                         cards=cards, 
                         card_types=[ct[0] for ct in card_types],
                         pages=[p[0] for p in pages])

@app.route('/admin/cards/add', methods=['GET', 'POST'])
@admin_required
def admin_add_card():
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        image_url = request.form.get('image_url')
        card_type = request.form.get('card_type')
        page = request.form.get('page')
        price = request.form.get('price')
        features = request.form.get('features')
        button_text = request.form.get('button_text')
        button_link = request.form.get('button_link')
        icon_class = request.form.get('icon_class')
        order_position = int(request.form.get('order_position', 0))
        
        try:
            card = Card(
                title=title,
                description=description,
                image_url=image_url,
                card_type=card_type,
                page=page,
                price=price,
                features=features,
                button_text=button_text,
                button_link=button_link,
                icon_class=icon_class,
                order_position=order_position
            )
            
            db.session.add(card)
            db.session.commit()
            flash('Card added successfully!', 'success')
            return redirect(url_for('admin_cards'))
        
        except Exception as e:
            db.session.rollback()
            flash(f'Error adding card: {str(e)}', 'danger')
    
    return render_template('admin/add_card.html')

@app.route('/admin/cards/edit/<int:card_id>', methods=['GET', 'POST'])
@admin_required
def admin_edit_card(card_id):
    card = Card.query.get_or_404(card_id)
    
    if request.method == 'POST':
        card.title = request.form.get('title')
        card.description = request.form.get('description')
        card.image_url = request.form.get('image_url')
        card.card_type = request.form.get('card_type')
        card.page = request.form.get('page')
        card.price = request.form.get('price')
        card.features = request.form.get('features')
        card.button_text = request.form.get('button_text')
        card.button_link = request.form.get('button_link')
        card.icon_class = request.form.get('icon_class')
        card.order_position = int(request.form.get('order_position', 0))
        card.is_active = 'is_active' in request.form
        card.updated_at = datetime.utcnow()
        
        try:
            db.session.commit()
            flash('Card updated successfully!', 'success')
            return redirect(url_for('admin_cards'))
        
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating card: {str(e)}', 'danger')
    
    return render_template('admin/edit_card.html', card=card)

@app.route('/admin/cards/delete/<int:card_id>', methods=['POST'])
@admin_required
def admin_delete_card(card_id):
    card = Card.query.get_or_404(card_id)
    
    try:
        db.session.delete(card)
        db.session.commit()
        flash('Card deleted successfully!', 'success')
    
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting card: {str(e)}', 'danger')
    
    return redirect(url_for('admin_cards'))

@app.route('/admin/cards/toggle/<int:card_id>', methods=['POST'])
@admin_required
def admin_toggle_card(card_id):
    card = Card.query.get_or_404(card_id)
    card.is_active = not card.is_active
    
    try:
        db.session.commit()
        status = 'activated' if card.is_active else 'deactivated'
        flash(f'Card {status} successfully!', 'success')
    
    except Exception as e:
        db.session.rollback()
        flash(f'Error toggling card status: {str(e)}', 'danger')
    
    return redirect(url_for('admin_cards'))

# FAQ Admin Routes
@app.route('/admin/faqs')
@admin_required
def admin_faqs():
    page = request.args.get('page', 1, type=int)
    category = request.args.get('category', '')
    
    query = FAQ.query
    if category:
        query = query.filter(FAQ.category == category)
    
    faqs = query.order_by(FAQ.order_position).paginate(
        page=page, per_page=10, error_out=False
    )
    
    # Get unique categories for filters
    categories = db.session.query(FAQ.category).distinct().all()
    
    return render_template('admin/faqs.html', 
                         faqs=faqs, 
                         categories=[c[0] for c in categories if c[0]])

@app.route('/admin/faqs/add', methods=['GET', 'POST'])
@admin_required
def admin_add_faq():
    if request.method == 'POST':
        question = request.form.get('question')
        answer = request.form.get('answer')
        category = request.form.get('category')
        order_position = int(request.form.get('order_position', 0))
        
        try:
            faq = FAQ(
                question=question,
                answer=answer,
                category=category,
                order_position=order_position
            )
            db.session.add(faq)
            db.session.commit()
            flash('FAQ added successfully!', 'success')
            return redirect(url_for('admin_faqs'))
        
        except Exception as e:
            db.session.rollback()
            flash(f'Error adding FAQ: {str(e)}', 'danger')
    
    return render_template('admin/add_faq.html')

@app.route('/admin/faqs/edit/<int:faq_id>', methods=['GET', 'POST'])
@admin_required
def admin_edit_faq(faq_id):
    faq = FAQ.query.get_or_404(faq_id)
    
    if request.method == 'POST':
        faq.question = request.form.get('question')
        faq.answer = request.form.get('answer')
        faq.category = request.form.get('category')
        faq.order_position = int(request.form.get('order_position', 0))
        faq.is_active = 'is_active' in request.form
        faq.updated_at = datetime.utcnow()
        
        try:
            db.session.commit()
            flash('FAQ updated successfully!', 'success')
            return redirect(url_for('admin_faqs'))
        
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating FAQ: {str(e)}', 'danger')
    
    return render_template('admin/edit_faq.html', faq=faq)

@app.route('/admin/faqs/toggle/<int:faq_id>', methods=['POST'])
@admin_required
def admin_toggle_faq(faq_id):
    faq = FAQ.query.get_or_404(faq_id)
    
    try:
        faq.is_active = not faq.is_active
        db.session.commit()
        status = 'activated' if faq.is_active else 'deactivated'
        flash(f'FAQ {status} successfully!', 'success')
    
    except Exception as e:
        db.session.rollback()
        flash(f'Error toggling FAQ: {str(e)}', 'danger')
    
    return redirect(url_for('admin_faqs'))

@app.route('/admin/faqs/delete/<int:faq_id>', methods=['POST'])
@admin_required
def admin_delete_faq(faq_id):
    faq = FAQ.query.get_or_404(faq_id)
    
    try:
        db.session.delete(faq)
        db.session.commit()
        flash('FAQ deleted successfully!', 'success')
    
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting FAQ: {str(e)}', 'danger')
    
    return redirect(url_for('admin_faqs'))

# Portfolio Admin Routes
@app.route('/admin/portfolio')
@admin_required
def admin_portfolio():
    page = request.args.get('page', 1, type=int)
    category = request.args.get('category', '')
    style = request.args.get('style', '')
    
    query = PortfolioItem.query
    if category:
        query = query.filter(PortfolioItem.category == category)
    if style:
        query = query.filter(PortfolioItem.style == style)
    
    portfolio_items = query.order_by(PortfolioItem.order_position).paginate(
        page=page, per_page=10, error_out=False
    )
    
    # Get unique categories and styles for filters
    categories = db.session.query(PortfolioItem.category).distinct().all()
    styles = db.session.query(PortfolioItem.style).distinct().all()
    
    return render_template('admin/portfolio.html', 
                         portfolio_items=portfolio_items,
                         categories=[c[0] for c in categories if c[0]],
                         styles=[s[0] for s in styles if s[0]])

@app.route('/admin/portfolio/add', methods=['GET', 'POST'])
@admin_required
def admin_add_portfolio():
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        image_url = request.form.get('image_url')
        category = request.form.get('category')
        style = request.form.get('style')
        before_image = request.form.get('before_image')
        project_details = request.form.get('project_details')
        client_name = request.form.get('client_name')
        location = request.form.get('location')
        completion_date = request.form.get('completion_date')
        order_position = int(request.form.get('order_position', 0))
        
        # Parse date if provided
        parsed_date = None
        if completion_date:
            try:
                parsed_date = datetime.strptime(completion_date, '%Y-%m-%d').date()
            except ValueError:
                pass
        
        try:
            portfolio_item = PortfolioItem(
                title=title,
                description=description,
                image_url=image_url,
                category=category,
                style=style,
                before_image=before_image,
                project_details=project_details,
                client_name=client_name,
                location=location,
                completion_date=parsed_date,
                order_position=order_position
            )
            db.session.add(portfolio_item)
            db.session.commit()
            flash('Portfolio item added successfully!', 'success')
            return redirect(url_for('admin_portfolio'))
        
        except Exception as e:
            db.session.rollback()
            flash(f'Error adding portfolio item: {str(e)}', 'danger')
    
    return render_template('admin/add_portfolio.html')

@app.route('/admin/portfolio/edit/<int:item_id>', methods=['GET', 'POST'])
@admin_required
def admin_edit_portfolio(item_id):
    portfolio_item = PortfolioItem.query.get_or_404(item_id)
    
    if request.method == 'POST':
        portfolio_item.title = request.form.get('title')
        portfolio_item.description = request.form.get('description')
        portfolio_item.image_url = request.form.get('image_url')
        portfolio_item.category = request.form.get('category')
        portfolio_item.style = request.form.get('style')
        portfolio_item.before_image = request.form.get('before_image')
        portfolio_item.project_details = request.form.get('project_details')
        portfolio_item.client_name = request.form.get('client_name')
        portfolio_item.location = request.form.get('location')
        portfolio_item.order_position = int(request.form.get('order_position', 0))
        portfolio_item.is_featured = 'is_featured' in request.form
        portfolio_item.is_active = 'is_active' in request.form
        
        # Parse date if provided
        completion_date = request.form.get('completion_date')
        if completion_date:
            try:
                portfolio_item.completion_date = datetime.strptime(completion_date, '%Y-%m-%d').date()
            except ValueError:
                portfolio_item.completion_date = None
        else:
            portfolio_item.completion_date = None
        
        portfolio_item.updated_at = datetime.utcnow()
        
        try:
            db.session.commit()
            flash('Portfolio item updated successfully!', 'success')
            return redirect(url_for('admin_portfolio'))
        
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating portfolio item: {str(e)}', 'danger')
    
    return render_template('admin/edit_portfolio.html', portfolio_item=portfolio_item)

@app.route('/admin/portfolio/toggle/<int:item_id>', methods=['POST'])
@admin_required
def admin_toggle_portfolio(item_id):
    portfolio_item = PortfolioItem.query.get_or_404(item_id)
    
    try:
        portfolio_item.is_active = not portfolio_item.is_active
        db.session.commit()
        status = 'activated' if portfolio_item.is_active else 'deactivated'
        flash(f'Portfolio item {status} successfully!', 'success')
    
    except Exception as e:
        db.session.rollback()
        flash(f'Error toggling portfolio item: {str(e)}', 'danger')
    
    return redirect(url_for('admin_portfolio'))

@app.route('/admin/portfolio/delete/<int:item_id>', methods=['POST'])
@admin_required
def admin_delete_portfolio(item_id):
    portfolio_item = PortfolioItem.query.get_or_404(item_id)
    
    try:
        db.session.delete(portfolio_item)
        db.session.commit()
        flash('Portfolio item deleted successfully!', 'success')
    
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting portfolio item: {str(e)}', 'danger')
    
    return redirect(url_for('admin_portfolio'))

# Quiz Admin Routes
@app.route('/admin/quiz')
@admin_required
def admin_quiz():
    page = request.args.get('page', 1, type=int)
    question_type = request.args.get('type', '')
    
    query = QuizQuestion.query
    if question_type:
        query = query.filter(QuizQuestion.question_type == question_type)
    
    questions = query.order_by(QuizQuestion.order_position).paginate(
        page=page, per_page=10, error_out=False
    )
    
    # Get unique question types for filters
    question_types = db.session.query(QuizQuestion.question_type).distinct().all()
    
    return render_template('admin/quiz.html', 
                         questions=questions,
                         question_types=[qt[0] for qt in question_types if qt[0]])

@app.route('/admin/quiz/add', methods=['GET', 'POST'])
@admin_required
def admin_add_quiz():
    if request.method == 'POST':
        question_text = request.form.get('question_text')
        question_type = request.form.get('question_type')
        image_left = request.form.get('image_left')
        image_right = request.form.get('image_right')
        style_left = request.form.get('style_left')
        style_right = request.form.get('style_right')
        options = request.form.get('options')
        order_position = int(request.form.get('order_position', 0))
        
        try:
            quiz_question = QuizQuestion(
                question_text=question_text,
                question_type=question_type,
                image_left=image_left,
                image_right=image_right,
                style_left=style_left,
                style_right=style_right,
                options=options,
                order_position=order_position
            )
            db.session.add(quiz_question)
            db.session.commit()
            flash('Quiz question added successfully!', 'success')
            return redirect(url_for('admin_quiz'))
        
        except Exception as e:
            db.session.rollback()
            flash(f'Error adding quiz question: {str(e)}', 'danger')
    
    return render_template('admin/add_quiz.html')

@app.route('/admin/quiz/edit/<int:question_id>', methods=['GET', 'POST'])
@admin_required
def admin_edit_quiz(question_id):
    quiz_question = QuizQuestion.query.get_or_404(question_id)
    
    if request.method == 'POST':
        quiz_question.question_text = request.form.get('question_text')
        quiz_question.question_type = request.form.get('question_type')
        quiz_question.image_left = request.form.get('image_left')
        quiz_question.image_right = request.form.get('image_right')
        quiz_question.style_left = request.form.get('style_left')
        quiz_question.style_right = request.form.get('style_right')
        quiz_question.options = request.form.get('options')
        quiz_question.order_position = int(request.form.get('order_position', 0))
        quiz_question.is_active = 'is_active' in request.form
        quiz_question.updated_at = datetime.utcnow()
        
        try:
            db.session.commit()
            flash('Quiz question updated successfully!', 'success')
            return redirect(url_for('admin_quiz'))
        
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating quiz question: {str(e)}', 'danger')
    
    return render_template('admin/edit_quiz.html', quiz_question=quiz_question)

@app.route('/admin/quiz/toggle/<int:question_id>', methods=['POST'])
@admin_required
def admin_toggle_quiz(question_id):
    quiz_question = QuizQuestion.query.get_or_404(question_id)
    
    try:
        quiz_question.is_active = not quiz_question.is_active
        db.session.commit()
        status = 'activated' if quiz_question.is_active else 'deactivated'
        flash(f'Quiz question {status} successfully!', 'success')
    
    except Exception as e:
        db.session.rollback()
        flash(f'Error toggling quiz question: {str(e)}', 'danger')
    
    return redirect(url_for('admin_quiz'))

@app.route('/admin/quiz/delete/<int:question_id>', methods=['POST'])
@admin_required
def admin_delete_quiz(question_id):
    quiz_question = QuizQuestion.query.get_or_404(question_id)
    
    try:
        db.session.delete(quiz_question)
        db.session.commit()
        flash('Quiz question deleted successfully!', 'success')
    
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting quiz question: {str(e)}', 'danger')
    
    return redirect(url_for('admin_quiz'))


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
