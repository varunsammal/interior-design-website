from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# Home page route
@app.route('/')
def home():
    return render_template('index.html')

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

#Portfolio route
@app.route('/portfolio/')
def portfolio():
     # This is a placeholder - you'll create this template later
     return render_template('portfolio.html')  # For now, redirect to home



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
@app.route('/blog/')
def blog():
     # This is a placeholder - you'll create this template later
     return render_template('blog.html')  # For now, redirect to home

# # Contact form submission route - for static site, we'll make this a GET route
# @app.route('/contact/')
# def contact():
#     # For static site, we'll just show the home page
#     return render_template('contact.html')



if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
