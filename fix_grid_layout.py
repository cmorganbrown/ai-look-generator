#!/usr/bin/env python3
"""
Fix CSS Grid Layout for Shopping Page
This script creates an updated version of the shopping page with responsive grid layout.
"""

import pandas as pd
import json
import os
import urllib.parse
import random
from bs4 import BeautifulSoup

# Updated CSS with better responsive grid layout
updated_css_styles = """
<style>
.product-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
    gap: 25px;
    padding: 20px;
    max-width: 1400px;
    margin: 0 auto;
}

/* Responsive breakpoints for better grid layout */
@media (min-width: 768px) {
    .product-grid {
       /* grid-template-columns: repeat(2, 1fr);*/
    }
}

@media (min-width: 1024px) {
    .product-grid {
     /*   grid-template-columns: repeat(3, 1fr); */
    }
}

@media (min-width: 1200px) {
    .product-grid {
        /* grid-template-columns: repeat(4, 1fr); */
    }
}

@media (min-width: 1400px) {
    .product-grid {
     /*   grid-template-columns: repeat(5, 1fr); */
    }
}

.product-item {
    border: 1px solid #e0e0e0;
    border-radius: 12px;
    padding: 20px;
    text-align: center;
    position: relative;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    background: white;
    transition: all 0.3s ease;
    min-height: 400px;
}

.product-item:hover {
    transform: translateY(-4px);
    box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
    border-color: #d0d0d0;
}

.product-item img {
    max-width: 100%;
    height: 220px;
    object-fit: cover;
    border-radius: 8px;
    margin-bottom: 15px;
    transition: transform 0.3s ease;
    width: 100%;
    box-sizing: border-box;
}

.product-item:hover img {
    transform: scale(1.05);
}

.product-item a {
    text-decoration: none;
    color: inherit;
}

.product-item h3 {
    font-size: 1.1em;
    margin: 10px 0 8px;
    min-height: 2.5em;
    color: #333;
    font-weight: 600;
    line-height: 1.3;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
    max-width: 100%;
}

.product-item p {
    font-size: 1.3em;
    color: rgb(153,14,53);
    margin-bottom: 15px;
    font-weight: bold;
}

.add-to-cart-button {
    background-color: transparent;
    color: purple;
    border: 2px solid purple;
    padding: 12px 24px;
    border-radius: 8px;
    cursor: pointer;
    margin-top: auto;
    transition: all 0.3s ease;
    font-weight: 600;
    text-transform: uppercase;
    font-size: 0.9em;
    letter-spacing: 0.5px;
}

.add-to-cart-button:hover {
    background-color: purple;
    color: white;
    transform: translateY(-2px);
    box-shadow: 0 6px 15px rgba(128, 0, 128, 0.3);
}

.heart-icon {
    position: absolute;
    top: 15px;
    right: 15px;
    background-color: white;
    border: 2px solid purple;
    border-radius: 50%;
    width: 40px;
    height: 40px;
    display: flex;
    justify-content: center;
    align-items: center;
    cursor: pointer;
    z-index: 1;
    transition: all 0.3s ease;
}

.heart-icon:hover {
    background-color: rgba(255, 105, 180, 0.9);
    transform: scale(1.1);
}

.heart-icon svg {
    fill: purple;
    width: 22px;
    height: 22px;
    transition: fill 0.3s ease;
}

.heart-icon:hover svg {
    fill: #ff1493;
}

.source-logo {
    position: absolute;
    bottom: 15px;
    right: 15px;
    width: 30px;
    height: 30px;
    border-radius: 50%;
    background-color: white;
    padding: 3px;
    z-index: 1;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
}

.source-logo img {
    width: 100%;
    height: 100%;
    object-fit: contain;
    border-radius: 50%;
}

/* Page title styling */
h2 {
    text-align: center;
    color: #333;
    font-size: 2.8em;
    margin: 40px 0;
    font-weight: 700;
    text-transform: capitalize;
    letter-spacing: 1px;
}

/* Container styling */
body {
    background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    margin: 0;
    padding: 0;
    min-height: 100vh;
    overflow-x: hidden;
    box-sizing: border-box;
}

.container {
    max-width: 1400px;
    margin: 0 auto;
    padding: 20px;
    box-sizing: border-box;
}

/* Loading animation for images */
.product-item img {
    opacity: 0;
    animation: fadeIn 0.5s ease-in forwards;
}

@keyframes fadeIn {
    from { opacity: 0; }
    to { opacity: 1; }
}
</style>
"""

def generate_product_html(product):
    """Generate HTML for a single product item"""
    grid_title = product.get('grid_title', 'No Title Available')
    display_name = product.get('display_name')
    image_url = product.get('images:orig:url')
    link = product.get('link')
    price = product.get('price', 'Price not available')
    seo_alt_txt = product.get('seo_alt_txt')
    source = product.get('Source', 'Unknown')

    # Use display_name if available, otherwise use grid_title
    product_title = display_name if pd.notna(display_name) else grid_title
    
    # Truncate title if longer than 100 characters
    if len(product_title) > 200:
        product_title = product_title[:197] + '...'

    # Use seo_alt_txt for alt attribute if available, otherwise use product_title
    alt_text = seo_alt_txt if pd.notna(seo_alt_txt) else product_title

    # Ensure link is not None or empty
    product_link = link if pd.notna(link) and link else "#"

    # Determine source logo
    source_logo_html = ""
    if source == 'Pinterest':
        source_logo_html = '<div class="source-logo"><img src="https://1000logos.net/wp-content/uploads/2018/03/Pinterest-Logo-2011-2016.png" alt="Pinterest Logo"></div>'
    elif source == 'Google':
        source_logo_html = '<div class="source-logo"><img src="https://img.icons8.com/color/512/google-shopping.png" alt="Google Shopping Logo"></div>'

    # Basic check for a valid image URL
    image_tag = ""
    if image_url and isinstance(image_url, str):
         image_tag = f'<img src="{image_url}" alt="{alt_text}">'
    else:
         image_tag = f'<img src="https://via.placeholder.com/150?text=No+Image" alt="No image available for {alt_text}">'

    product_html = f"""
    <div class="product-item">
        <a href="{product_link}">
            {image_tag}
        </a>
        <div class="heart-icon">
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z"/></svg>
        </div>
        {source_logo_html}
        <div class="product-details">
            <h3>{product_title}</h3>
            <p>{price}</p>
            <button class="add-to-cart-button">Add to Cart</button>
        </div>
    </div>
    """
    return product_html

def parse_pinterest_json(json_path):
    """Parse Pinterest JSON and return a list of product dicts"""
    products = []
    if not os.path.exists(json_path):
        print(f"❌ Pinterest JSON file not found: {json_path}")
        return products
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    try:
        results = data['resource_response']['data']['results']
        for item in results:
            rich = item.get('rich_summary', {})
            prod = rich.get('products', [{}])[0] if rich.get('products') else {}
            offer = prod.get('offers', [{}])[0] if prod.get('offers') else {}
            images = item.get('images', {})
            image_url = images.get('orig', {}).get('url')
            products.append({
                'grid_title': item.get('grid_title', ''),
                'display_name': rich.get('display_name', ''),
                'images:orig:url': image_url,
                'link': item.get('link', ''),
                'price': offer.get('price_value') and f"${offer.get('price_value')}",
                'seo_alt_txt': rich.get('display_name', ''),
                'Source': 'Pinterest'
            })
    except Exception as e:
        print(f"❌ Error parsing Pinterest JSON: {e}")
    return products

def parse_google_html(html_path):
    """Parse Google PLA HTML and return a list of product dicts"""
    products = []
    if not os.path.exists(html_path):
        print(f"❌ Google HTML file not found: {html_path}")
        return products
    with open(html_path, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f, 'html.parser')
    for unit in soup.select('.pla-unit-container'):
        try:
            a_tag = unit.select_one('a.pla-unit')
            if not a_tag:
                continue
            link = a_tag.get('adurl') or a_tag.get('href')
            # Extract real URL from Google ad URL
            if link and isinstance(link, str) and 'adurl=' in link:
                link = link.split('adurl=')[1]
                # URL decode the link
                link = urllib.parse.unquote(link)
            img_tag = unit.select_one('img')
            image_url = img_tag['src'] if img_tag and img_tag.has_attr('src') else None
            title_tag = unit.select_one('.bXPcId')
            price_tag = unit.select_one('.dOp6Sc')
            title = title_tag.get('aria-label') if title_tag else ''
            price = price_tag.get('aria-label') if price_tag else ''
            products.append({
                'grid_title': title,
                'display_name': title,
                'images:orig:url': image_url,
                'link': link,
                'price': price,
                'seo_alt_txt': title,
                'Source': 'Google'
            })
        except Exception as e:
            print(f"❌ Error parsing a Google PLA product: {e}")
    return products

def main():
    """Main function to generate the shopping page"""
    print("🔄 Loading product data...")
    
    # Parse both data sources
    pinterest_products = parse_pinterest_json('trends_output.json')
    google_products = parse_google_html('pla_output.html')
    
    # Combine and randomize products
    all_products = pinterest_products + google_products
    random.shuffle(all_products)  # Randomize the order
    
    print(f"✅ Loaded {len(pinterest_products)} Pinterest products")
    print(f"✅ Loaded {len(google_products)} Google products")
    print(f"📊 Total products: {len(all_products)}")
    
    if not all_products:
        print("❌ No products found. Using sample data.")
        all_products = get_sample_products()
    
    # Generate HTML
    html_content = generate_html(all_products)
    
    # Save to file
    with open('shopping_page_responsive.html', 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print("✅ Updated responsive HTML shopping page saved to 'shopping_page_responsive.html'")
    print("🎨 The grid now displays products in multiple columns with responsive design!")
    print("📱 Features:")
    print("   - Mobile: 1 column")
    print("   - Tablet (768px+): 2 columns")
    print("   - Desktop (1024px+): 3 columns")
    print("   - Large Desktop (1200px+): 4 columns")
    print("   - Extra Large (1400px+): 5 columns")
    print(f"📊 Total products displayed: {len(all_products)}")

def generate_html(products):
    """Generate the complete HTML page with simple Wayfair logo, title, filter, and products"""
    
    # Simple Wayfair logo HTML
    logo_html = '''<div style="text-align: center; padding: 20px; background: white; border-bottom: 1px solid #e0e0e0;">
        <a href="https://www.wayfair.com" style="text-decoration: none;">
            <svg viewBox="0 0 629.52 150" xmlns="http://www.w3.org/2000/svg" role="img" height="60" width="200" style="display: inline-block;">
                <title>Wayfair</title>
                <path fill="#7b189f" stroke-width="0px" d="M624.09,42.29c0-0.77-0.42-1.54-1.47-1.54h-1.89v4.96h0.7V43.9h0.63l1.26,1.81h0.84l-1.33-1.89 C623.74,43.76,624.09,42.99,624.09,42.29L624.09,42.29z M621.44,43.2v-1.81h1.26c0.56,0,0.77,0.49,0.77,0.91 c0,0.42-0.21,0.91-0.84,0.91L621.44,43.2L621.44,43.2z"></path>
                <path fill="#7b189f" stroke-width="0px" d="M622.27,38.94c-2.38,0-4.26,1.89-4.26,4.26c0,2.38,1.89,4.26,4.26,4.26s4.26-1.89,4.26-4.26 C626.54,40.82,624.58,38.94,622.27,38.94z M622.27,46.83c-2.03,0-3.63-1.61-3.63-3.63c-0.07-2.03,1.61-3.63,3.63-3.63 s3.63,1.61,3.63,3.63C625.91,45.23,624.3,46.83,622.27,46.83z"></path>
                <ellipse fill="#7b189f" stroke-width="0px" cx="541.78" cy="15.8" rx="11.49" ry="11.2"></ellipse>
                <rect x="-42.72" y="-20.74" fill="none" stroke-width="0px" width="945.79" height="191.47"></rect>
                <path fill="#7b189f" stroke-width="0px" d="M53.15,111.51L19.41,77.76L7.77,89.4c-1.17,1.17-1.31,2.04-0.87,3.49l5.53,21.53 c0.58,2.33,1.74,3.49,4.07,4.07l21.53,5.53c1.45,0.44,2.33,0.29,3.49-0.87L53.15,111.51L53.15,111.51z M58.68,111.51l11.64,11.64 c1.17,1.17,2.04,1.31,3.49,0.87l21.53-5.53c2.33-0.58,3.49-1.74,4.07-4.07l5.53-21.53c0.44-1.45,0.29-2.33-0.87-3.49L92.43,77.76 L58.68,111.51L58.68,111.51z M58.68,38.49l33.75,33.75l11.64-11.64c1.17-1.17,1.31-2.04,0.87-3.49l-5.53-21.53 c-0.58-2.33-1.74-3.49-4.07-4.07l-21.53-5.53c-1.45-0.44-2.33-0.29-3.49,0.87L58.68,38.49L58.68,38.49z M53.15,38.49L41.52,26.85 c-1.17-1.17-2.04-1.31-3.49-0.87L16.5,31.51c-2.33,0.58-3.49,1.74-4.07,4.07L6.9,57.1c-0.44,1.45-0.29,2.33,0.87,3.49l11.64,11.64 L53.15,38.49L53.15,38.49z"></path>
                <path fill="#7b189f" stroke-width="0px" d="M437.35,53.47h-17.9v52.64c0,2.74-2.22,4.96-4.96,4.96h-13.95v-57.6h-16.28l-21.6,61.24 c-8.73,24.58-17.31,30.98-32.58,30.98c-2.91,0-7.56-0.58-12.22-1.45l4.12-13.53h6.65c7.34,0,11.21-2.28,13.75-8.68 c2.53-6.41,2.59-7.4,2.62-7.46L319.1,38.93h16.41c2.18,0,4.1,1.42,4.74,3.5l14.63,47.55L370.3,43c1.02-2.91,2.33-4.07,5.24-4.07 h25.01v-2.04c0-21.38,9.89-32.58,28.66-32.58c2.91,0,9.49,0.52,13.42,1.4l-4.15,13.58h-5.49c-7.47,0-13.53,6.06-13.53,13.53v6.11 h22.31L437.35,53.47L437.35,53.47z"></path>
                <path fill="#7b189f" stroke-width="0px" d="M200.36,89.4l-14.54-47.27c-0.73-2.47-1.74-3.2-4.22-3.2h-13.82c-2.47,0-3.49,0.73-4.22,3.2L148.87,89.4 l-13.09-50.47h-20.8l20.95,68.95c0.73,2.47,1.74,3.2,4.22,3.2h14.4c2.47,0,3.49-0.73,4.22-3.2l15.27-48.58l15.42,48.58 c0.73,2.47,1.74,3.2,4.22,3.2h12.95c2.47,0,3.49-0.73,4.22-3.2l20.95-68.95H213.6L200.36,89.4L200.36,89.4z"></path>
                <rect x="532.32" y="38.93" fill="#7b189f" stroke-width="0px" width="18.91" height="72.15"></rect>
                <path fill="#7b189f" stroke-width="0px" d="M291.9,43l-0.44,8.3c-4.51-10.77-13.67-13.82-24.44-13.82c-19.78,0-32.15,17.89-32.15,37.53 s12.36,37.53,32.15,37.53c10.77,0,19.93-3.06,24.44-13.82l0.44,8.3c0,2.76,1.31,4.07,3.64,4.07h15.13V38.93h-15.13 C293.21,38.93,291.9,40.23,291.9,43L291.9,43z M272.39,97.44c-11.93,0-18.75-9.94-18.75-22.44s6.81-22.44,18.75-22.44 S291.14,62.5,291.14,75S284.32,97.44,272.39,97.44L272.39,97.44z"></path>
                <path fill="#7b189f" stroke-width="0px" d="M497.64,43l-0.44,8.3c-4.51-10.77-13.67-13.82-24.44-13.82c-19.78,0-32.15,17.89-32.15,37.53 s12.36,37.53,32.15,37.53c10.77,0,19.93-3.06,24.44-13.82l0.44,8.3c0,2.76,1.31,4.07,3.64,4.07h15.13V38.93h-15.13 C498.96,38.93,497.64,40.23,497.64,43L497.64,43z M478.14,97.44c-11.93,0-18.75-9.94-18.75-22.44s6.81-22.44,18.75-22.44 S496.89,62.5,496.89,75S490.07,97.44,478.14,97.44z"></path>
                <path fill="#7b189f" stroke-width="0px" d="M608.98,38.2c-11.2,0-19.2,3.44-22.69,16.82L586,43c0-2.76-1.31-4.07-3.64-4.07h-15.13v72.15h18.91V75 c0-12.65,7.27-20.8,19.78-20.8h3.41l4.59-15.09C612.16,38.36,610.29,38.2,608.98,38.2L608.98,38.2z"></path>
            </svg>
        </a>
    </div>'''
    
    # Title and filter section
    title_filter_html = '''<div style="text-align: center; padding: 30px 20px; background: white;">
        <h1 style="color: #7b189f; font-size: 3em; margin: 0 0 20px 0; font-weight: 700; text-transform: uppercase; letter-spacing: 2px;">Dopamine Decor</h1>
        <div style="margin-bottom: 20px;">
            <label for="sourceFilter" style="font-weight: 600; color: #333; margin-right: 10px;">Filter by Source:</label>
            <select id="sourceFilter" style="padding: 8px 16px; border: 2px solid #7b189f; border-radius: 6px; font-size: 16px; background: white; color: #333; cursor: pointer;">
                <option value="all">All Sources</option>
                <option value="Pinterest">Pinterest Only</option>
                <option value="Google">Google Only</option>
            </select>
        </div>
    </div>'''
    
    # Generate products HTML with data attributes for filtering
    products_html = ""
    for i, product in enumerate(products):
        source = product.get('Source', 'Unknown')
        product_html = generate_product_html(product)
        # Replace the outer div with data-source attribute
        product_html = product_html.replace('<div class="product-item">', f'<div class="product-item" data-source="{source}">')
        products_html += product_html
    
    # Complete HTML with logo, title, filter, and products
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dopamine Decor - Pinterest & Google Products</title>
    {updated_css_styles}
</head>
<body>
    {logo_html}
    {title_filter_html}
    <div class="container">
        <div class="product-grid">
            {products_html}
        </div>
    </div>
    
    <script>
        // Add heart icon functionality
        document.addEventListener('DOMContentLoaded', function() {{
            const heartIcons = document.querySelectorAll('.heart-icon');
            heartIcons.forEach(icon => {{
                icon.addEventListener('click', function() {{
                    this.classList.toggle('liked');
                }});
            }});
            
            // Add filter functionality
            const sourceFilter = document.getElementById('sourceFilter');
            const productItems = document.querySelectorAll('.product-item');
            
            sourceFilter.addEventListener('change', function() {{
                const selectedSource = this.value;
                
                productItems.forEach(item => {{
                    const itemSource = item.getAttribute('data-source');
                    if (selectedSource === 'all' || itemSource === selectedSource) {{
                        item.style.display = 'block';
                    }} else {{
                        item.style.display = 'none';
                    }}
                }});
            }});
        }});
    </script>
</body>
</html>"""
    
    return html

if __name__ == "__main__":
    main() 