#!/usr/bin/env python3

from flask import Flask, render_template, request, redirect, url_for, flash, send_file, jsonify
import os
import json
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta
from trend_generator import TrendLandingPageGenerator
import glob
from look_generator import LookGenerator

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # Change this in production
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB limit for large JSON/HTML content
app.config['MAX_CONTENT_PATH'] = None  # No path length limit
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0  # Disable caching for development

# Configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'json', 'html'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure upload directory exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs('landing_pages', exist_ok=True)

# Initialize look generator
look_generator = LookGenerator()

@app.errorhandler(413)
def too_large(e):
    return "The data you're trying to paste is too large. Please try breaking it into smaller chunks or contact support if you need to handle very large datasets.", 413

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_landing_pages():
    """Get list of all generated landing pages"""
    pages = []
    for html_file in glob.glob('landing_pages/*.html'):
        filename = os.path.basename(html_file)
        name = filename.replace('.html', '').replace('-', ' ').title()
        size = os.path.getsize(html_file)
        modified = datetime.fromtimestamp(os.path.getmtime(html_file))
        
        pages.append({
            'filename': filename,
            'name': name,
            'size': size,
            'modified': modified,
            'url': f'/view/{filename}'
        })
    
    # Sort by modification date (newest first)
    pages.sort(key=lambda x: x['modified'], reverse=True)
    return pages

@app.context_processor
def inject_now():
    """Inject current datetime into template context"""
    return {'now': datetime.now(), 'timedelta': timedelta}

@app.route('/')
def home():
    """Home page with links to all landing pages and create new"""
    pages = get_landing_pages()
    return render_template('home.html', pages=pages)

@app.route('/create')
def create():
    """Create new landing page form"""
    return render_template('create.html')

@app.route('/upload', methods=['POST'])
def upload_and_generate():
    """Handle file uploads and pasted content for landing page generation"""
    try:
        search_term = request.form.get('search_term', '').strip()
        if not search_term:
            flash('Search term is required!', 'error')
            return redirect(url_for('create'))
        
        # Handle data sources
        pinterest_file = None
        google_file = None
        
        # Process Pinterest data (file upload takes priority)
        if 'pinterest_file' in request.files and request.files['pinterest_file'].filename:
            # File upload
            file = request.files['pinterest_file']
            if file and allowed_file(file.filename):
                filename = secure_filename(f"{search_term.lower().replace(' ', '_')}_pinterest.json")
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                pinterest_file = filepath
        elif request.form.get('pinterest_content', '').strip():
            # Pasted content
            pinterest_content = request.form.get('pinterest_content', '').strip()
            try:
                # Validate JSON format
                json.loads(pinterest_content)
                filename = f"{search_term.lower().replace(' ', '_')}_pinterest.json"
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(pinterest_content)
                pinterest_file = filepath
            except json.JSONDecodeError:
                flash('Invalid JSON format in Pinterest content. Please check your data.', 'error')
                return redirect(url_for('create'))
        
        # Process Google data (file upload takes priority)
        if 'google_file' in request.files and request.files['google_file'].filename:
            # File upload
            file = request.files['google_file']
            if file and allowed_file(file.filename):
                filename = secure_filename(f"{search_term.lower().replace(' ', '_')}_google.html")
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                google_file = filepath
        elif request.form.get('google_content', '').strip():
            # Pasted content
            google_content = request.form.get('google_content', '').strip()
            filename = f"{search_term.lower().replace(' ', '_')}_google.html"
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(google_content)
            google_file = filepath
        
        # Check if at least one data source is provided
        if not pinterest_file and not google_file:
            flash('Please provide at least Pinterest JSON or Google HTML data (via file upload or pasted content).', 'error')
            return redirect(url_for('create'))
        
        # Generate landing page
        generator = TrendLandingPageGenerator()
        result = generator.create_landing_page(search_term, pinterest_file, google_file)
        
        if result:
            flash(f'Successfully created landing page for "{search_term}"!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Error creating landing page. Please check your data.', 'error')
            return redirect(url_for('create'))
            
    except Exception as e:
        flash(f'Error: {str(e)}', 'error')
        return redirect(url_for('create'))

@app.route('/view/<filename>')
def view_page(filename):
    """View a specific landing page"""
    filepath = os.path.join('landing_pages', filename)
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        return content
    else:
        flash('Page not found!', 'error')
        return redirect(url_for('home'))

@app.route('/download/<filename>')
def download_page(filename):
    """Download a landing page HTML file"""
    filepath = os.path.join('landing_pages', filename)
    if os.path.exists(filepath):
        return send_file(filepath, as_attachment=True)
    else:
        flash('File not found!', 'error')
        return redirect(url_for('home'))

@app.route('/download_csv/<filename>')
def download_csv(filename):
    """Download product data as CSV"""
    try:
        # Extract search term from filename
        search_term = filename.replace('.html', '').replace('-', ' ')
        
        # Find corresponding data files
        pinterest_file = os.path.join('uploads', f"{search_term.lower().replace(' ', '_')}_pinterest.json")
        google_file = os.path.join('uploads', f"{search_term.lower().replace(' ', '_')}_google.html")
        
        # Generate the product data
        generator = TrendLandingPageGenerator()
        products = generator.get_product_data(search_term, pinterest_file, google_file)
        
        if not products:
            flash('No product data found!', 'error')
            return redirect(url_for('home'))
        
        # Create CSV content
        import csv
        from io import StringIO
        
        output = StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow(['Title', 'Price', 'Image URL', 'Product URL', 'Source', 'Description'])
        
        # Write product data
        for product in products:
            writer.writerow([
                product.get('title', ''),
                product.get('price', ''),
                product.get('image_url', ''),
                product.get('url', ''),
                product.get('source', ''),
                product.get('description', '')
            ])
        
        output.seek(0)
        csv_content = output.getvalue()
        
        # Create response
        from flask import Response
        response = Response(csv_content, mimetype='text/csv')
        response.headers['Content-Disposition'] = f'attachment; filename={search_term.replace(" ", "_")}_products.csv'
        
        return response
        
    except Exception as e:
        flash(f'Error generating CSV: {str(e)}', 'error')
        return redirect(url_for('home'))

@app.route('/delete/<filename>')
def delete_page(filename):
    """Delete a landing page"""
    filepath = os.path.join('landing_pages', filename)
    if os.path.exists(filepath):
        os.remove(filepath)
        flash(f'Successfully deleted {filename}', 'success')
    else:
        flash('File not found!', 'error')
    return redirect(url_for('home'))

@app.route('/api/pages')
def api_pages():
    """API endpoint to get all pages (for AJAX)"""
    pages = get_landing_pages()
    return jsonify(pages)

@app.route('/auto_scrape', methods=['GET', 'POST'])
def auto_scrape():
    """Automated scraping using Selenium"""
    if request.method == 'GET':
        return render_template('auto_scrape.html')
    
    try:
        search_term = request.form.get('search_term', '').strip()
        if not search_term:
            flash('Search term is required!', 'error')
            return redirect(url_for('auto_scrape'))
        
        # Import Selenium scraper
        from selenium_scraper import SeleniumTrendScraper
        
        print(f"🤖 Starting automated scraping for '{search_term}'...")
        
        # Initialize scraper
        scraper = SeleniumTrendScraper(output_dir="uploads", headless=False)  # Set headless=False to see the browser
        
        try:
            # Scrape data
            pinterest_data = scraper.scrape_pinterest(search_term, max_results=30)
            google_data = scraper.scrape_google_shopping(search_term, max_results=30)
            
            # Check if we got any data
            total_products = len(pinterest_data) + len(google_data)
            if total_products == 0:
                flash(f'❌ No products found for "{search_term}". This could be due to: 1) Search term not returning results, 2) Website blocking automated access, 3) Page structure changes. Try using the manual upload method instead.', 'error')
                return redirect(url_for('auto_scrape'))
            
            print(f"📊 Found {len(pinterest_data)} Pinterest products and {len(google_data)} Google products")
            
            # Save data
            scraper.save_data(search_term, pinterest_data, google_data)
            
            # Get file paths
            pinterest_file = os.path.join('uploads', f"{search_term.lower().replace(' ', '_')}_pinterest.json")
            google_file = os.path.join('uploads', f"{search_term.lower().replace(' ', '_')}_google.html")
            
            # Generate landing page
            generator = TrendLandingPageGenerator()
            result = generator.create_landing_page(search_term, pinterest_file, google_file)
            
            if result:
                flash(f'✅ Successfully scraped and created landing page for "{search_term}" with {total_products} products!', 'success')
                return redirect(url_for('home'))
            else:
                flash('❌ Error creating landing page from scraped data. Please try the manual upload method.', 'error')
                return redirect(url_for('auto_scrape'))
                
        finally:
            # Always close the browser
            scraper.close()
            
    except Exception as e:
        flash(f'❌ Error during automated scraping: {str(e)}', 'error')
        return redirect(url_for('auto_scrape'))

@app.route('/edit/<filename>')
def edit_page(filename):
    """Edit an existing landing page to add more products"""
    try:
        # Get the search term from the filename
        search_term = filename.replace('.html', '').replace('-', ' ')
        
        # Get existing data files for this search term
        data_dir = 'scraped_data'
        pinterest_file = None
        google_file = None
        
        if os.path.exists(data_dir):
            for file in os.listdir(data_dir):
                if file.startswith(search_term.lower().replace(' ', '_')):
                    if 'pinterest' in file:
                        pinterest_file = file
                    elif 'google' in file:
                        google_file = file
        
        return render_template('edit.html', 
                             search_term=search_term,
                             pinterest_file=pinterest_file,
                             google_file=google_file,
                             filename=filename)
    except Exception as e:
        flash(f'Error loading edit page: {str(e)}', 'error')
        return redirect(url_for('home'))

@app.route('/update/<filename>', methods=['POST'])
def update_page(filename):
    """Update an existing landing page with new data"""
    try:
        search_term = request.form.get('search_term', '').strip()
        if not search_term:
            flash('Search term is required', 'error')
            return redirect(url_for('edit_page', filename=filename))
        
        # Handle file uploads
        pinterest_file = None
        google_file = None
        
        if 'pinterest_file' in request.files and request.files['pinterest_file'].filename:
            file = request.files['pinterest_file']
            if file.filename.endswith('.json') or file.filename.endswith('.html'):
                pinterest_file = f"{search_term.lower().replace(' ', '_')}_pinterest{os.path.splitext(file.filename)[1]}"
                file.save(os.path.join('scraped_data', pinterest_file))
        
        if 'google_file' in request.files and request.files['google_file'].filename:
            file = request.files['google_file']
            if file.filename.endswith('.html'):
                google_file = f"{search_term.lower().replace(' ', '_')}_google.html"
                file.save(os.path.join('scraped_data', google_file))
        
        # Handle pasted content
        pinterest_content = request.form.get('pinterest_content', '').strip()
        google_content = request.form.get('google_content', '').strip()
        
        if pinterest_content:
            pinterest_file = f"{search_term.lower().replace(' ', '_')}_pinterest.json"
            with open(os.path.join('scraped_data', pinterest_file), 'w', encoding='utf-8') as f:
                f.write(pinterest_content)
        
        if google_content:
            google_file = f"{search_term.lower().replace(' ', '_')}_google.html"
            with open(os.path.join('scraped_data', google_file), 'w', encoding='utf-8') as f:
                f.write(google_content)
        
        # Generate updated landing page
        generator = TrendLandingPageGenerator()
        result = generator.create_landing_page(search_term, pinterest_file, google_file)
        
        if result:
            flash(f'Landing page updated successfully!', 'success')
            return redirect(url_for('view_page', filename=filename))
        else:
            flash('Failed to update landing page', 'error')
            return redirect(url_for('edit_page', filename=filename))
            
    except Exception as e:
        flash(f'Error updating page: {str(e)}', 'error')
        return redirect(url_for('edit_page', filename=filename))

@app.route('/looks')
def looks_gallery():
    """Gallery of all generated looks"""
    looks = look_generator.get_all_looks()
    return render_template('looks_gallery.html', looks=looks)

@app.route('/looks/<look_id>')
def view_look(look_id):
    """View a specific generated look"""
    look_data = look_generator.get_look_by_id(look_id)
    if not look_data:
        flash('Look not found!', 'error')
        return redirect(url_for('looks_gallery'))
    
    # Get all products from the original landing page
    generator = TrendLandingPageGenerator()
    landing_page_name = look_data.get('landing_page', '')
    if landing_page_name:
        search_term = landing_page_name.replace('.html', '').replace('-', ' ')
        all_products = generator.get_product_data(search_term)
    else:
        all_products = []
    
    return render_template('view_look.html', look=look_data, all_products=all_products)

@app.route('/generate_look', methods=['POST'])
def generate_look():
    """Generate a new look from selected products"""
    try:
        data = request.json
        selected_products = data.get('products', [])
        style_prompt = data.get('style_prompt', '')
        landing_page_name = data.get('landing_page_name', '')
        
        if len(selected_products) < 3:
            return jsonify({
                'success': False,
                'error': 'Please select at least 3 products to create a look'
            })
        
        # Generate the look
        result = look_generator.generate_shoppable_look(
            selected_products, 
            style_prompt, 
            landing_page_name
        )
        
        if result['success']:
            return jsonify({
                'success': True,
                'look_id': result['look_id'],
                'look_url': url_for('view_look', look_id=result['look_id']),
                'message': 'Look generated successfully!'
            })
        else:
            return jsonify({
                'success': False,
                'error': result.get('error', 'Failed to generate look')
            })
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/looks/images/<filename>')
def serve_look_image(filename):
    """Serve look images"""
    image_path = os.path.join('looks', 'images', filename)
    if os.path.exists(image_path):
        return send_file(image_path)
    else:
        return 'Image not found', 404

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=3000) 