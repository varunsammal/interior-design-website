import os
import shutil
import re
from urllib.parse import urljoin
from flask_frozen import Freezer
from app import app

# Configure Frozen-Flask
app.config['FREEZER_DESTINATION'] = 'build'
app.config['FREEZER_BASE_URL'] = 'https://abhii-04.github.io/Interior-Design-Website/'
app.config['FREEZER_RELATIVE_URLS'] = True
freezer = Freezer(app)

# Function to fix paths in HTML files
def fix_paths_in_html(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Fix CSS and JS paths
    content = content.replace('Interior-Design-Website/static/', 'static/')
    
    # Fix internal links
    content = content.replace('Interior-Design-Website/index.html', 'index.html')
    content = content.replace('Interior-Design-Website/how-it-works/', 'how-it-works/')
    content = content.replace('Interior-Design-Website/designers/', 'designers/')
    content = content.replace('Interior-Design-Website/portfolio/', 'portfolio/')
    content = content.replace('Interior-Design-Website/pricing/', 'pricing/')
    content = content.replace('Interior-Design-Website/reviews/', 'reviews/')
    content = content.replace('Interior-Design-Website/blog/', 'blog/')
    content = content.replace('Interior-Design-Website/contact/', 'contact/')
    
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(content)

# Run the freezer
if __name__ == '__main__':
    # Clean build directory if it exists
    if os.path.exists('build'):
        shutil.rmtree('build')
    
    # Create build directory
    os.makedirs('build')
    
    # Freeze the app
    freezer.freeze()
    
    # Fix paths in all HTML files
    for root, dirs, files in os.walk('build'):
        for file in files:
            if file.endswith('.html'):
                fix_paths_in_html(os.path.join(root, file))
    
    print("Static site generated in the 'build' directory with fixed paths")