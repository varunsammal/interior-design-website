from flask import Flask, render_template, request, redirect, url_for,flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
import os


import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///uploads.db'  # SQLite database
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = os.path.join(os.getcwd(), 'static/uploads')
app.config['ALLOWED_EXTENSIONS'] = {'jpg', 'jpeg', 'png'}

db = SQLAlchemy(app)

# Home page route
@app.route('/')
def home():
    return render_template('index.html')

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
def upload():
    if request.method == 'POST':
        # Check if the post request has the file part
        if 'image_file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        
        file = request.files['image_file']
        
        # If user does not select file, browser submits empty file
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            # Save to database
            new_image = UploadedImage(filename=filename, filepath=filepath)
            db.session.add(new_image)
            db.session.commit()
            
            flash('Image successfully uploaded and saved to database')
            return redirect(url_for('upload'))
    
    # Get all uploaded images from database
    images = UploadedImage.query.order_by(UploadedImage.upload_date.desc()).all()
    return render_template('upload.html', images=images)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
