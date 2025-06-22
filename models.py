from flask_login import UserMixin
from datetime import datetime

# This will be set by app.py
db = None
bcrypt = None

def init_models():
    """Initialize models after db and bcrypt are set"""
    
    class User(UserMixin, db.Model):
        __tablename__ = 'users'
        
        id = db.Column(db.Integer, primary_key=True)
        username = db.Column(db.String(80), unique=True, nullable=False)
        email = db.Column(db.String(120), unique=True, nullable=True)
        password = db.Column(db.String(60), nullable=True)
        created_at = db.Column(db.DateTime, default=datetime.utcnow)
        last_login = db.Column(db.DateTime, nullable=True)
        is_active = db.Column(db.Boolean, default=True)
        is_admin = db.Column(db.Boolean, default=False)
        user_type = db.Column(db.String(20), default='user')  # 'user' or 'admin'
        address = db.Column(db.String(200))
        phone = db.Column(db.String(20))
        design_style = db.Column(db.String(50))
        profile_image = db.Column(db.String(200), nullable=True)
        projects = db.relationship('Project', backref='user', lazy=True)
        designs = db.relationship('DesignImage', backref='user', lazy='dynamic')

        def __init__(self, username, email=None, password=None, address=None, phone=None, design_style=None, profile_image=None, is_admin=False, user_type='user'):
            self.username = username
            self.email = email
            self.address = address
            self.phone = phone
            self.design_style = design_style
            self.profile_image = profile_image
            self.is_admin = is_admin
            self.user_type = user_type

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

    # Admin Models for Dynamic Content Management
    class AdminUser(db.Model):
        __tablename__ = 'admin_users'
        
        id = db.Column(db.Integer, primary_key=True)
        username = db.Column(db.String(80), unique=True, nullable=False)
        password = db.Column(db.String(60), nullable=False)
        created_at = db.Column(db.DateTime, default=datetime.utcnow)
        is_active = db.Column(db.Boolean, default=True)

        def __init__(self, username, password):
            self.username = username
            self.password = bcrypt.generate_password_hash(password).decode('utf-8')

        def check_password(self, password):
            return bcrypt.check_password_hash(self.password, password)

    class Card(db.Model):
        __tablename__ = 'cards'
        
        id = db.Column(db.Integer, primary_key=True)
        title = db.Column(db.String(200), nullable=False)
        description = db.Column(db.Text)
        image_url = db.Column(db.String(500))
        card_type = db.Column(db.String(50), nullable=False)  # service, portfolio, designer, pricing, etc.
        page = db.Column(db.String(50), nullable=False)  # index, portfolio, pricing, etc.
        order_position = db.Column(db.Integer, default=0)
        is_active = db.Column(db.Boolean, default=True)
        created_at = db.Column(db.DateTime, default=datetime.utcnow)
        updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
        
        # Additional fields for different card types
        price = db.Column(db.String(50))  # For pricing cards
        features = db.Column(db.Text)  # JSON string for features list
        button_text = db.Column(db.String(100))
        button_link = db.Column(db.String(200))
        icon_class = db.Column(db.String(100))  # For FontAwesome icons
        
        def __init__(self, title, description, card_type, page, image_url=None, price=None, 
                     features=None, button_text=None, button_link=None, icon_class=None, order_position=0):
            self.title = title
            self.description = description
            self.image_url = image_url
            self.card_type = card_type
            self.page = page
            self.price = price
            self.features = features
            self.button_text = button_text
            self.button_link = button_link
            self.icon_class = icon_class
            self.order_position = order_position

    class FAQ(db.Model):
        __tablename__ = 'faqs'
        
        id = db.Column(db.Integer, primary_key=True)
        question = db.Column(db.Text, nullable=False)
        answer = db.Column(db.Text, nullable=False)
        category = db.Column(db.String(100))  # general, pricing, design, etc.
        order_position = db.Column(db.Integer, default=0)
        is_active = db.Column(db.Boolean, default=True)
        created_at = db.Column(db.DateTime, default=datetime.utcnow)
        updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
        
        def __init__(self, question, answer, category=None, order_position=0):
            self.question = question
            self.answer = answer
            self.category = category
            self.order_position = order_position

    class QuizQuestion(db.Model):
        __tablename__ = 'quiz_questions'
        
        id = db.Column(db.Integer, primary_key=True)
        question_text = db.Column(db.Text, nullable=False)
        question_type = db.Column(db.String(50), nullable=False)  # image_comparison, multiple_choice, etc.
        image_left = db.Column(db.String(500))  # For image comparison questions
        image_right = db.Column(db.String(500))
        style_left = db.Column(db.String(100))  # Style name for left image
        style_right = db.Column(db.String(100))  # Style name for right image
        options = db.Column(db.Text)  # JSON string for multiple choice options
        order_position = db.Column(db.Integer, default=0)
        is_active = db.Column(db.Boolean, default=True)
        created_at = db.Column(db.DateTime, default=datetime.utcnow)
        updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
        
        def __init__(self, question_text, question_type, order_position=0, image_left=None, 
                     image_right=None, style_left=None, style_right=None, options=None):
            self.question_text = question_text
            self.question_type = question_type
            self.image_left = image_left
            self.image_right = image_right
            self.style_left = style_left
            self.style_right = style_right
            self.options = options
            self.order_position = order_position

    class PortfolioItem(db.Model):
        __tablename__ = 'portfolio_items'
        
        id = db.Column(db.Integer, primary_key=True)
        title = db.Column(db.String(200), nullable=False)
        description = db.Column(db.Text)
        image_url = db.Column(db.String(500), nullable=False)
        category = db.Column(db.String(100))  # living_room, bedroom, kitchen, etc.
        style = db.Column(db.String(100))  # modern, traditional, contemporary, etc.
        before_image = db.Column(db.String(500))  # Before image URL for transformations
        project_details = db.Column(db.Text)  # JSON string for project details
        client_name = db.Column(db.String(100))
        location = db.Column(db.String(100))
        completion_date = db.Column(db.Date)
        order_position = db.Column(db.Integer, default=0)
        is_featured = db.Column(db.Boolean, default=False)
        is_active = db.Column(db.Boolean, default=True)
        created_at = db.Column(db.DateTime, default=datetime.utcnow)
        updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
        
        def __init__(self, title, description, image_url, category=None, style=None, 
                     before_image=None, project_details=None, client_name=None, 
                     location=None, completion_date=None, order_position=0):
            self.title = title
            self.description = description
            self.image_url = image_url
            self.category = category
            self.style = style
            self.before_image = before_image
            self.project_details = project_details
            self.client_name = client_name
            self.location = location
            self.completion_date = completion_date
            self.order_position = order_position

    # Store the classes in the module's globals
    globals()['User'] = User
    globals()['Project'] = Project
    globals()['Design'] = Design
    globals()['DesignImage'] = DesignImage
    globals()['Review'] = Review
    globals()['AdminUser'] = AdminUser
    globals()['Card'] = Card
    globals()['FAQ'] = FAQ
    globals()['QuizQuestion'] = QuizQuestion
    globals()['PortfolioItem'] = PortfolioItem
    
    return {
        'User': User,
        'Project': Project,
        'Design': Design,
        'DesignImage': DesignImage,
        'Review': Review,
        'AdminUser': AdminUser,
        'Card': Card,
        'FAQ': FAQ,
        'QuizQuestion': QuizQuestion,
        'PortfolioItem': PortfolioItem
    }