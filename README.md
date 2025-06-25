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

### Running the Application

1. Start the Flask development server:
```
python run_app.py
```

   **Alternative**: You can also run directly with `python app.py` (both commands work the same)

2. Open your browser to: `http://localhost:5000`

3. Login with admin credentials:
   - Username: `admin`
   - Password: `admin123`
   - **Important**: Change the default password after first login!

### Admin Access

Admin users are automatically redirected to the admin dashboard upon login. The admin panel allows you to:
- **Manage portfolio items** - Add, edit, and organize portfolio projects
- Manage service cards
- Add/edit FAQs
- Create quiz questions
- View user statistics

### Key Features

#### Portfolio Management
- **Dynamic Portfolio Display**: Portfolio page (`/portfolio`) displays real-time data from the database
- **Admin Dashboard**: Full CRUD operations for portfolio items at `/admin/portfolio`
- **Real-time Synchronization**: Changes in admin panel immediately appear on the portfolio page
- **Image Management**: Support for before/after transformation images
- **Category Filtering**: Dynamic category filters based on actual portfolio data
- **Featured Items**: Highlight specific portfolio projects

#### User Experience
- **Responsive Design**: Works seamlessly on desktop, tablet, and mobile devices
- **Interactive Elements**: Image hover effects, filtering, and dynamic loading
- **Professional Layout**: Clean, modern design suitable for interior design business


## Project Structure

```
Interior-Design-Website/
├── app.py                 # Main Flask application
├── models.py             # Database models
├── config.py             # Application configuration
├── run_app.py            # Application startup script
├── setup_admin.py        # Admin user setup
├── requirements.txt      # Python dependencies
├── templates/            # Jinja2 templates
│   ├── base.html        # Base template
│   ├── index.html       # Home page
│   ├── portfolio.html   # Portfolio display (connected to admin)
│   ├── admin/           # Admin dashboard templates
│   │   ├── dashboard.html
│   │   ├── portfolio.html    # Portfolio management
│   │   ├── add_portfolio.html
│   │   └── edit_portfolio.html
│   └── ...
├── static/              # Static assets
│   ├── styles/         # CSS files
│   │   ├── styles.css  # Main stylesheet
│   │   ├── portfolio.css
│   │   └── admin.css
│   ├── javascript/     # JavaScript files
│   │   ├── script.js
│   │   └── portfolio.js
│   └── images/         # Image assets
└── migrations/         # Database migrations
```

## Important URLs

- **Home Page**: `http://localhost:5000/`
- **Portfolio Page**: `http://localhost:5000/portfolio` (displays dynamic content)
- **Admin Dashboard**: `http://localhost:5000/admin`
- **Portfolio Management**: `http://localhost:5000/admin/portfolio`

## Database

The application uses SQLite database with the following key models:
- `User`: User accounts and authentication
- `AdminUser`: Admin user management
- `PortfolioItem`: Portfolio projects with full CRUD operations
- `Card`: Service cards
- `FAQ`: Frequently asked questions
- `QuizQuestion`: Quiz functionality

## Recent Updates

### Portfolio-Admin Connection (Latest)
- ✅ **Fixed**: Portfolio page now displays dynamic content from database
- ✅ **Connected**: Admin dashboard portfolio management to public portfolio page
- ✅ **Real-time**: Changes in admin panel immediately reflect on portfolio page
- ✅ **Enhanced**: Added error handling for missing images
- ✅ **Improved**: Better template structure with conditional content
- ✅ **Added**: `run_app.py` for easier application startup (both `python run_app.py` and `python app.py` work)


### Common Issues

1. **Portfolio page shows no items**: 
   - Ensure database is properly set up: `python setup_admin.py`
   - Add portfolio items via admin dashboard

2. **Images not loading**:
   - Check image URLs in admin dashboard
   - Placeholder images will show for missing/broken links

3. **Admin login issues**:
   - Default credentials: admin / admin123
   - Run `python setup_admin.py` to reset admin user

4. **Database errors**:
   - Delete `instance/` folder and re-run `python setup_admin.py`

