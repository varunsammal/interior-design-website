# Interior Design Website with Flask

This is a Flask-based web application for an interior design service, inspired by Decorilla.

## Setup Instructions

### Prerequisites
- Python 3.x
- Virtual environment (recommended)

### Installation

1. Clone the repository:
```
git clone https://github.com/Abhii-04/Interior-Design-Website.git
cd Interior-Design-Website
```

2. Create and activate a virtual environment:
```
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install the required packages:
```
pip install -r requirements.txt
```

4. Set up the database and admin user:
```
python setup_admin.py
```

5. (Optional) Add sample data for demo purposes:
```
python add_sample_data.py
```

### Running the Application

1. Start the Flask development server:
```
python app.py
```

2. Open your browser to: `http://localhost:5000`

3. Login with admin credentials:
   - Username: `admin`
   - Password: `admin123`
   - **Important**: Change the default password after first login!

### Admin Access

Admin users are automatically redirected to the admin dashboard upon login. The admin panel allows you to:
- Manage service cards
- Add/edit FAQs
- Manage portfolio items
- Create quiz questions
- View user statistics


## Project Structure

- `app.py`: Main Flask application file
- `templates/`: HTML templates
  - `index.html`: Home page template
- `static/`: Static files (CSS, JavaScript, images)
  - `styles.css`: Main stylesheet
  - `script.js`: JavaScript functionality

