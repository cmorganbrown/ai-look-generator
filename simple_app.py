#!/usr/bin/env python3
"""
Simple Flask app without AI features for testing
"""

from flask import Flask, render_template, request, redirect, url_for, flash, send_file, jsonify
import os
import json
from datetime import datetime, timedelta
from werkzeug.utils import secure_filename
from trend_generator import TrendLandingPageGenerator
import glob
import requests
from bs4 import BeautifulSoup
import re
import openai
import base64
import io

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'

# Configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'json', 'html', 'txt'}

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs('landing_pages', exist_ok=True)
os.makedirs('looks', exist_ok=True)
os.makedirs('looks/images', exist_ok=True)

@app.errorhandler(413)
def too_large(e):
    return "File too large", 413

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_landing_pages():
    """Get list of all landing pages"""
    pages = []
    if os.path.exists('landing_pages'):
        for file in os.listdir('landing_pages'):
            if file.endswith('.html'):
                filepath = os.path.join('landing_pages', file)
                stat = os.stat(filepath)
                # Convert filename to display name
                name = file.replace('.html', '').replace('-', ' ').title()
                pages.append({
                    'filename': file,
                    'name': name,
                    'size': stat.st_size,
                    'modified': datetime.fromtimestamp(stat.st_mtime),
                    'url': f'/view/{file}'
                })
    return sorted(pages, key=lambda x: x['modified'], reverse=True)

def get_looks():
    """Get list of all generated looks"""
    looks = []
    looks_file = os.path.join('looks', 'looks.json')
    if os.path.exists(looks_file):
        try:
            with open(looks_file, 'r', encoding='utf-8') as f:
                looks = json.load(f)
        except:
            looks = []
    return looks

@app.context_processor
def inject_now():
    return {
        'now': datetime.now(),
        'timedelta': timedelta
    }

@app.route('/')
def home():
    """Home page showing all landing pages"""
    pages = get_landing_pages()
    return render_template('home.html', pages=pages)

@app.route('/create')
def create():
    """Create new landing page"""
    return render_template('create.html')

@app.route('/upload', methods=['POST'])
def upload_and_generate():
    """Handle file upload and generate landing page"""
    try:
        search_term = request.form.get('search_term', '').strip()
        if not search_term:
            flash('Search term is required', 'error')
            return redirect(url_for('create'))
        
        # Handle file uploads
        pinterest_file = None
        google_file = None
        
        if 'pinterest_file' in request.files and request.files['pinterest_file'].filename:
            file = request.files['pinterest_file']
            if file.filename.endswith('.json') or file.filename.endswith('.html'):
                pinterest_filename = f"{search_term.lower().replace(' ', '_')}_pinterest{os.path.splitext(file.filename)[1]}"
                pinterest_file = os.path.join('uploads', pinterest_filename)
                file.save(pinterest_file)
        
        if 'google_file' in request.files and request.files['google_file'].filename:
            file = request.files['google_file']
            if file.filename.endswith('.html'):
                google_filename = f"{search_term.lower().replace(' ', '_')}_google.html"
                google_file = os.path.join('uploads', google_filename)
                file.save(google_file)
        
        # Generate landing page
        generator = TrendLandingPageGenerator()
        result = generator.create_landing_page(search_term, pinterest_file, google_file)
        
        if result:
            flash(f'Successfully created landing page for "{search_term}"!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Error creating landing page. Please check your data files.', 'error')
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

@app.route('/view_with_looks/<filename>')
def view_with_looks(filename):
    """View a landing page with product selection for creating looks"""
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
        
        # Add source logos to products
        for product in products:
            if product.get('source') == 'Pinterest':
                product['source_logo'] = 'https://1000logos.net/wp-content/uploads/2018/03/Pinterest-Logo-2011-2016.png'
            elif product.get('source') == 'Google':
                product['source_logo'] = 'https://www.google.com/images/branding/googlelogo/1x/googlelogo_color_272x92dp.png'
            else:
                product['source_logo'] = 'https://via.placeholder.com/30x30/cccccc/666666?text=?'
        
        return render_template('view_with_looks.html', 
                             products=products, 
                             page_title=search_term.title())
        
    except Exception as e:
        flash(f'Error loading page: {str(e)}', 'error')
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

@app.route('/edit/<filename>')
def edit_page(filename):
    """Edit an existing landing page"""
    try:
        # Load existing data
        pinterest_file = f'uploads/{filename.replace(".html", "_pinterest.json")}'
        google_file = f'uploads/{filename.replace(".html", "_google.html")}'
        
        pinterest_data = ""
        google_data = ""
        
        if os.path.exists(pinterest_file):
            with open(pinterest_file, 'r', encoding='utf-8') as f:
                pinterest_data = f.read()
        
        if os.path.exists(google_file):
            with open(google_file, 'r', encoding='utf-8') as f:
                google_data = f.read()
        
        return render_template('edit.html', 
                             filename=filename,
                             pinterest_data=pinterest_data,
                             google_data=google_data)
    except Exception as e:
        flash(f'Error loading edit page: {str(e)}', 'error')
        return redirect(url_for('home'))

@app.route('/update/<filename>', methods=['POST'])
def update_page(filename):
    """Update an existing landing page"""
    try:
        pinterest_data = request.form.get('pinterest_data', '')
        google_data = request.form.get('google_data', '')
        
        # Get search term from filename
        search_term = filename.replace('.html', '').replace('-', ' ')
        
        # Save the data
        pinterest_file = f'uploads/{filename.replace(".html", "_pinterest.json")}'
        google_file = f'uploads/{filename.replace(".html", "_google.html")}'
        
        if pinterest_data.strip():
            with open(pinterest_file, 'w', encoding='utf-8') as f:
                f.write(pinterest_data)
        
        if google_data.strip():
            with open(google_file, 'w', encoding='utf-8') as f:
                f.write(google_data)
        
        # Generate the landing page using the correct method
        generator = TrendLandingPageGenerator()
        result = generator.create_landing_page(search_term, pinterest_file, google_file)
        
        if result:
            flash(f'Landing page "{filename}" updated successfully!', 'success')
        else:
            flash('Failed to update landing page', 'error')
        
        return redirect(url_for('home'))
        
    except Exception as e:
        flash(f'Error updating page: {str(e)}', 'error')
        return redirect(url_for('edit_page', filename=filename))

@app.route('/looks')
def looks_gallery():
    """Show all generated looks"""
    try:
        looks = []
        looks_dir = 'looks'
        if os.path.exists(looks_dir):
            for filename in os.listdir(looks_dir):
                if filename.endswith('.json'):
                    look_file = os.path.join(looks_dir, filename)
                    with open(look_file, 'r') as f:
                        look_data = json.load(f)
                        looks.append(look_data)
        
        # Sort by creation date (newest first)
        looks.sort(key=lambda x: x.get('created_at', ''), reverse=True)
        return render_template('looks_gallery.html', looks=looks)
    except Exception as e:
        flash(f'Error loading looks: {str(e)}', 'error')
        return render_template('looks_gallery.html', looks=[])

@app.route('/view_look/<look_id>')
def view_look(look_id):
    """View a specific look"""
    try:
        look_file = f'looks/{look_id}.json'
        if os.path.exists(look_file):
            with open(look_file, 'r') as f:
                look_data = json.load(f)
            return render_template('view_look.html', look=look_data)
        else:
            flash('Look not found', 'error')
            return redirect(url_for('looks_gallery'))
    except Exception as e:
        flash(f'Error loading look: {str(e)}', 'error')
        return redirect(url_for('looks_gallery'))

@app.route('/generate_look', methods=['POST'])
def generate_look():
    """Generate a new look from selected products"""
    try:
        # Check if it's JSON data from the new frontend
        if request.is_json:
            data = request.get_json()
            products = data.get('products', [])
            page_title = data.get('page_title', 'Generated Look')
            created_at = data.get('created_at', datetime.now().isoformat())
        else:
            # Handle old form data format
            selected_products = request.form.getlist('selected_products')
            look_name = request.form.get('look_name', 'Generated Look')
            
            if len(selected_products) < 3:
                return jsonify({'success': False, 'error': 'Please select at least 3 products for a look'})
            
            # Convert old format to new format
            products = selected_products
            page_title = look_name
            created_at = datetime.now().isoformat()
        
        if len(products) < 3:
            return jsonify({'success': False, 'error': 'Please select at least 3 products for a look'})
        
        # Create look data
        look_id = f"look_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        look_data = {
            'id': look_id,
            'name': f"{page_title} Look",
            'landing_page': page_title,
            'products': products,
            'product_count': len(products),
            'created_at': created_at,
            'image_url': '/static/placeholder_look.jpg'  # Placeholder for simple version
        }
        
        # Save look
        os.makedirs('looks', exist_ok=True)
        look_file = f'looks/{look_id}.json'
        with open(look_file, 'w') as f:
            json.dump(look_data, f, indent=2)
        
        if request.is_json:
            return jsonify({
                'success': True, 
                'message': f'Look "{look_data["name"]}" created successfully!',
                'redirect_url': url_for('view_look', look_id=look_id)
            })
        else:
            flash(f'Look "{look_data["name"]}" created successfully!', 'success')
            return redirect(url_for('looks_gallery'))
        
    except Exception as e:
        error_msg = f'Error generating look: {str(e)}'
        if request.is_json:
            return jsonify({'success': False, 'error': error_msg})
        else:
            flash(error_msg, 'error')
            return redirect(request.referrer or url_for('home'))

@app.route('/looks/images/<filename>')
def serve_look_image(filename):
    """Serve look images"""
    image_path = os.path.join('looks', 'images', filename)
    if os.path.exists(image_path):
        return send_file(image_path)
    else:
        return 'Image not found', 404

@app.route('/auto_scrape')
def auto_scrape():
    """Auto scrape page - placeholder for now"""
    flash('Auto scrape functionality coming soon!', 'info')
    return redirect(url_for('home'))

@app.route('/generate_hero_image', methods=['POST'])
def generate_hero_image():
    """Generate a hero image using ChatGPT API with selected products"""
    try:
        print("🔍 Starting hero image generation...")
        data = request.get_json()
        look_id = data.get('look_id')
        products = data.get('products', [])
        
        print(f"📋 Look ID: {look_id}")
        print(f"📦 Number of products: {len(products)}")
        
        if not look_id or len(products) < 3:
            return jsonify({'success': False, 'error': 'Need look ID and at least 3 products'})
        
        # Load the look data from individual file
        look_file = os.path.join('looks', f'{look_id}.json')
        if not os.path.exists(look_file):
            return jsonify({'success': False, 'error': 'Look file not found'})
        
        with open(look_file, 'r') as f:
            look = json.load(f)
        
        # Initialize OpenAI client (you'll need to set your API key)
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            return jsonify({'success': False, 'error': 'OpenAI API key not configured. Please set OPENAI_API_KEY environment variable.'})
        
        print("🔑 OpenAI API key found")
        client = openai.OpenAI(api_key=api_key)
        
        # Create the prompt
        product_names = [p['title'][:50] for p in products[:3]]
        prompt = f"""Create a beautiful, lifestyle shoppable scene that showcases these 3 products together in a cohesive, stylish look.

Products to include in the scene:
1. {product_names[0]}
2. {product_names[1]} 
3. {product_names[2]}

Style: The scene should look like a professional photo that would inspire someone to buy these products together. Use warm, inviting colors and create a sense of lifestyle and aspiration.

Requirements:
- High quality, photorealistic image
- Professional photography style
- Products should be naturally integrated into the scene
- Warm, inviting lighting
- Modern, elegant aesthetic
- 1:1 aspect ratio, landscape orientation"""
        
        print(f"📝 Generated prompt: {prompt[:200]}...")
        
        # Prepare the input content with reference images
        content = [
            {"type": "input_text", "text": prompt}
        ]
        
        # Add the reference images
        for i, product in enumerate(products[:3]):
            try:
                # Download and encode the image
                response = requests.get(product['image_url'])
                if response.status_code == 200:
                    # Convert to base64
                    image_data = base64.b64encode(response.content).decode('utf-8')
                    content.append({
                        "type": "input_image",
                        "image_url": f"data:image/jpeg;base64,{image_data}"
                    })
                    print(f"  ✅ Added reference image {i+1}")
                else:
                    print(f"  ❌ Failed to download image {i+1}: HTTP {response.status_code}")
            except Exception as e:
                print(f"  ❌ Error processing image {i+1}: {e}")
                continue
        
        print(f"🖼️ Prepared {len(content)-1} reference images")
        
        # Log the API call parameters
        print("🚀 API call parameters:")
        print(f"  Model: gpt-4.1")
        print(f"  Content items: {len(content)}")
        print(f"  Reference images: {len(content)-1}")
        
        # Generate the image using GPT-4.1 with reference images
        print("🎨 Calling OpenAI API...")
        response = client.responses.create(
            model="gpt-4.1",
            input=[
                {
                    "role": "user",
                    "content": content
                }
            ],
            tools=[{"type": "image_generation"}]
        )
        
        print("✅ API call successful!")
        
        # Extract the generated image
        image_generation_calls = [
            output
            for output in response.output
            if output.type == "image_generation_call"
        ]
        
        image_data = [output.result for output in image_generation_calls]
        
        if image_data:
            # Get the first generated image
            image_base64 = image_data[0]
            print(f"🖼️ Generated image received")
            
            # Create images directory if it doesn't exist
            os.makedirs('static/generated_images', exist_ok=True)
            
            # Save the image
            filename = f"hero_{look_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
            filepath = os.path.join('static/generated_images', filename)
            
            with open(filepath, 'wb') as f:
                f.write(base64.b64decode(image_base64))
            
            print(f"💾 Saved image to: {filepath}")
            
            # Update the look with the new image URL
            look['image_url'] = f'/static/generated_images/{filename}'
            
            # Save updated look
            with open(look_file, 'w') as f:
                json.dump(look, f, indent=2)
            
            print("✅ Hero image generation completed successfully!")
            return jsonify({
                'success': True, 
                'image_url': look['image_url'],
                'message': 'Hero image generated successfully!'
            })
        else:
            print(f"❌ No image generated: {response.output.content}")
            return jsonify({'success': False, 'error': 'No image was generated'})
            
    except Exception as e:
        print(f"❌ Error generating hero image: {e}")
        print(f"❌ Error type: {type(e)}")
        import traceback
        print(f"❌ Full traceback: {traceback.format_exc()}")
        return jsonify({'success': False, 'error': str(e)})

if __name__ == '__main__':
    print("🚀 Starting Simple Flask App...")
    print("📱 Access at: http://localhost:3000")
    print("✨ AI Look Generation: Coming Soon!")
    app.run(debug=True, host='0.0.0.0', port=3000) 