import os
import shutil
from urllib.parse import urljoin
from flask_frozen import Freezer
from app import app

# Configure Frozen-Flask
app.config['FREEZER_DESTINATION'] = 'build'
app.config['FREEZER_BASE_URL'] = 'https://abhii-04.github.io/Interior-Design-Website/'
app.config['FREEZER_RELATIVE_URLS'] = True
freezer = Freezer(app)

# Run the freezer
if __name__ == '__main__':
    # Clean build directory if it exists
    if os.path.exists('build'):
        shutil.rmtree('build')
    
    # Create build directory
    os.makedirs('build')
    
    # Freeze the app
    freezer.freeze()
    
    print("Static site generated in the 'build' directory")