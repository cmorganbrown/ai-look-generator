#!/usr/bin/env python3
"""
Trend Landing Page Generator
This script creates landing pages for any search term using existing data files.
"""

import os
import json
import urllib.parse
import random
from bs4 import BeautifulSoup
from datetime import datetime
import re

class TrendLandingPageGenerator:
    def __init__(self, output_dir="landing_pages"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
    
    def generate_slug(self, search_term):
        """Convert search term to URL-friendly slug"""
        slug = re.sub(r'[^a-zA-Z0-9\s-]', '', search_term.lower())
        slug = re.sub(r'\s+', '-', slug.strip())
        return slug
    
    def create_landing_page(self, search_term, pinterest_file=None, google_file=None):
        """Create a landing page for a specific search term"""
        
        # Always look in uploads/ if only a filename is provided
        def resolve_path(file):
            if file and not os.path.isabs(file) and not os.path.exists(file):
                candidate = os.path.join('uploads', file)
                if os.path.exists(candidate):
                    return candidate
            return file
        
        pinterest_file = resolve_path(pinterest_file)
        google_file = resolve_path(google_file)
        
        # Generate URL slug
        slug = self.generate_slug(search_term)
        
        # Parse data sources
        pinterest_products = []
        google_products = []
        
        if pinterest_file and os.path.exists(pinterest_file):
            if pinterest_file.endswith('.html'):
                pinterest_products = self.parse_pinterest_html(pinterest_file)
            else:
                pinterest_products = self.parse_pinterest_json(pinterest_file)
            print(f"✅ Loaded {len(pinterest_products)} Pinterest products from {pinterest_file}")
        
        if google_file and os.path.exists(google_file):
            google_products = self.parse_google_html(google_file)
            print(f"✅ Loaded {len(google_products)} Google products from {google_file}")
        
        # Combine and randomize products
        all_products = pinterest_products + google_products
        random.shuffle(all_products)
        
        if not all_products:
            print(f"❌ No products found for '{search_term}'")
            return None
        
        # Generate HTML
        html_content = self.generate_html(search_term, all_products)
        
        # Save to file
        filename = f"{slug}.html"
        filepath = os.path.join(self.output_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"✅ Created landing page: {filepath}")
        print(f"📊 Total products: {len(all_products)}")
        print(f"🌐 URL: file://{os.path.abspath(filepath)}")
        
        return filepath
    
    def get_product_data(self, search_term, pinterest_file=None, google_file=None):
        """Get parsed product data without generating HTML"""
        
        # Always look in uploads/ if only a filename is provided
        def resolve_path(file):
            if file and not os.path.isabs(file) and not os.path.exists(file):
                candidate = os.path.join('uploads', file)
                if os.path.exists(candidate):
                    return candidate
            return file
        
        pinterest_file = resolve_path(pinterest_file)
        google_file = resolve_path(google_file)
        
        # Parse data sources
        pinterest_products = []
        google_products = []
        
        if pinterest_file and os.path.exists(pinterest_file):
            if pinterest_file.endswith('.html'):
                pinterest_products = self.parse_pinterest_html(pinterest_file)
            else:
                pinterest_products = self.parse_pinterest_json(pinterest_file)
        
        if google_file and os.path.exists(google_file):
            google_products = self.parse_google_html(google_file)
        
        # Combine products
        all_products = pinterest_products + google_products
        
        # Convert to standardized format for CSV
        standardized_products = []
        for product in all_products:
            standardized_products.append({
                'title': product.get('grid_title', ''),
                'price': product.get('price', ''),
                'image_url': product.get('images:orig:url', ''),
                'url': product.get('link', ''),
                'source': product.get('Source', ''),
                'description': product.get('seo_alt_txt', '')
            })
        
        return standardized_products
    
    def parse_pinterest_json(self, json_path):
        """Parse Pinterest JSON and return a list of product dicts"""
        products = []
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
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
    
    def parse_google_html(self, html_path):
        """Parse Google PLA HTML and return a list of product dicts"""
        products = []
        try:
            with open(html_path, 'r', encoding='utf-8') as f:
                soup = BeautifulSoup(f, 'html.parser')
            
            # First, try to find the main Google Shopping container
            main_containers = [
                '.top-pla-group-inner',
                '.pla-unit-container',
                '.sh-dgr__content',
                '.sh-dlr__list-result',
                '[data-docid]'
            ]
            
            # Look for any elements with data-docid (Google Shopping product IDs)
            docid_elements = soup.find_all(attrs={'data-docid': True})
            if docid_elements:
                print(f"✅ Found {len(docid_elements)} Google Shopping products with data-docid")
                
                for element in docid_elements:
                    try:
                        # Find wayfair links in this element or its children
                        all_links = element.find_all('a')
                        wayfair_links = [link for link in all_links if link.get('href') and 'wayfair.com' in str(link.get('href'))]
                        
                        if not wayfair_links:
                            continue
                        
                        link = wayfair_links[0].get('href')
                        
                        # Find images in this element
                        images = element.find_all('img')
                        image_url = ''
                        
                        # Prioritize base64 images, then gstatic.com
                        for img in images:
                            src = img.get('src', '')
                            if src.startswith('data:image'):
                                image_url = src
                                break
                        
                        if not image_url:
                            for img in images:
                                src = img.get('src', '')
                                if 'gstatic.com' in src and not src.startswith('data:'):
                                    image_url = src
                                    break
                        
                        if not image_url:
                            for img in images:
                                src = img.get('src', '')
                                if src and not src.startswith('data:') and 'gstatic.com' not in src:
                                    image_url = src
                                    break
                        
                        # Find title with multiple selectors
                        title = ''
                        title_selectors = [
                            '.bXPcId div',
                            '.bXPcId',
                            '[aria-label*="product"]',
                            'h3',
                            'h2',
                            '.title',
                            'span[aria-label]'
                        ]
                        
                        for selector in title_selectors:
                            title_elements = element.select(selector)
                            if title_elements:
                                title = title_elements[0].get_text(strip=True)
                                if not title:
                                    # Try aria-label attribute
                                    title = title_elements[0].get('aria-label', '')
                                if title:
                                    break
                        
                        # Find price with multiple selectors
                        price = ''
                        price_selectors = [
                            '.VbBaOe',
                            '.dOp6Sc',
                            '[aria-label*="price"]',
                            '.price',
                            '.cost',
                            'span[aria-label*="price"]'
                        ]
                        
                        for selector in price_selectors:
                            price_elements = element.select(selector)
                            if price_elements:
                                price = price_elements[0].get_text(strip=True)
                                if not price:
                                    # Try aria-label attribute
                                    price = price_elements[0].get('aria-label', '')
                                if price:
                                    break
                        
                        if title and link:
                            products.append({
                                'grid_title': title,
                                'display_name': title,
                                'images:orig:url': image_url,
                                'link': link,
                                'price': price,
                                'seo_alt_txt': title,
                                'Source': 'Google'
                            })
                            print(f"✅ Found Google product: {title[:50]}... - {price}")
                    except Exception as e:
                        print(f"❌ Error parsing Google product: {e}")
                        continue
            
            if not products:
                print("⚠️ No Google products found with data-docid")
                print("💡 This might mean:")
                print("   - The HTML structure has changed")
                print("   - No Wayfair products were found")
                print("   - The page didn't load properly")
                    
        except Exception as e:
            print(f"❌ Error parsing Google HTML: {e}")
        return products
    
    def parse_pinterest_html(self, html_path):
        """Parse Pinterest HTML and return a list of product dicts"""
        products = []
        try:
            with open(html_path, 'r', encoding='utf-8') as f:
                soup = BeautifulSoup(f, 'html.parser')
            
            # Look for Pinterest pins with multiple selectors
            pin_selectors = [
                '[data-test-id="pin"]',
                '[data-test-id="pinWrapper"]',
                '.pin',
                'a[href*="/pin/"]'
            ]
            
            found_pins = False
            for selector in pin_selectors:
                pins = soup.select(selector)
                if pins:
                    print(f"✅ Found {len(pins)} Pinterest pins with selector: {selector}")
                    found_pins = True
                    
                    for pin in pins:
                        try:
                            # Extract title with multiple selectors
                            title = ''
                            title_selectors = [
                                '[data-test-id="pinTitle"]',
                                '.pinTitle',
                                'h3',
                                'h2',
                                '.title',
                                '[aria-label*="product"]'
                            ]
                            
                            for title_selector in title_selectors:
                                title_elements = pin.select(title_selector)
                                if title_elements:
                                    title = title_elements[0].get_text(strip=True)
                                    if title:
                                        break
                            
                            # Extract image
                            image_url = ''
                            img_elements = pin.select('img')
                            for img in img_elements:
                                src = img.get('src', '')
                                if src and not src.startswith('data:'):
                                    image_url = src
                                    break
                            
                            # Extract link
                            link = ''
                            link_elements = pin.select('a')
                            for link_elem in link_elements:
                                href = link_elem.get('href', '')
                                if isinstance(href, list):
                                    href = href[0] if href else ''
                                if href and '/pin/' in str(href):
                                    link = str(href)
                                    if not str(link).startswith('http'):
                                        link = 'https://www.pinterest.com' + link
                                    break
                            
                            # Extract price (if available)
                            price = ''
                            price_selectors = [
                                '[data-test-id="price"]',
                                '.price',
                                '.cost'
                            ]
                            
                            for price_selector in price_selectors:
                                price_elements = pin.select(price_selector)
                                if price_elements:
                                    price = price_elements[0].get_text(strip=True)
                                    if price:
                                        break
                            
                            if title and link:  # Only add if we have at least title and link
                                products.append({
                                    'grid_title': title,
                                    'display_name': title,
                                    'images:orig:url': image_url,
                                    'link': link,
                                    'price': price,
                                    'seo_alt_txt': title,
                                    'Source': 'Pinterest'
                                })
                                print(f"✅ Found Pinterest product: {title[:50]}...")
                        except Exception as e:
                            print(f"❌ Error parsing a Pinterest pin: {e}")
                            continue
                    
                    # If we found products with this selector, break
                    if products:
                        break
            
            if not found_pins:
                print("⚠️ No Pinterest pins found with any selector")
                print("💡 This might mean:")
                print("   - The HTML structure has changed")
                print("   - No pins were found")
                print("   - The page didn't load properly")
                    
        except Exception as e:
            print(f"❌ Error parsing Pinterest HTML: {e}")
        return products
    
    def generate_html(self, search_term, products):
        """Generate the complete HTML page"""
        
        # CSS styles with product selection functionality
        css_styles = """
        <style>
        .product-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 25px;
            padding: 20px;
            max-width: 1400px;
            margin: 0 auto;
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
        }
        
        .product-item.selected {
            border-color: #667eea;
            box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3);
            transform: translateY(-4px);
        }
        
        .product-item img {
            max-width: 100%;
            height: 220px;
            object-fit: cover;
            border-radius: 8px;
            margin-bottom: 15px;
            transition: transform 0.3s ease;
            width: 100%;
        }
        
        .product-item:hover img {
            transform: scale(1.05);
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
        
        /* Product Selection Styles */
        .product-checkbox {
            position: absolute;
            top: 15px;
            left: 15px;
            width: 24px;
            height: 24px;
            cursor: pointer;
            z-index: 2;
            opacity: 0;
            transition: opacity 0.3s ease;
        }
        
        .product-item:hover .product-checkbox {
            opacity: 1;
        }
        
        .product-item.selected .product-checkbox {
            opacity: 1;
        }
        
        .selection-controls {
            position: fixed;
            bottom: 20px;
            right: 20px;
            background: white;
            padding: 20px;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            z-index: 1000;
            min-width: 300px;
        }
        
        .selection-counter {
            font-size: 1.1em;
            font-weight: 600;
            color: #333;
            margin-bottom: 15px;
            text-align: center;
        }
        
        .generate-look-btn {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 12px 24px;
            border: none;
            border-radius: 25px;
            cursor: pointer;
            font-weight: 600;
            font-size: 1em;
            transition: all 0.3s ease;
            width: 100%;
            margin-bottom: 10px;
        }
        
        .generate-look-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 20px rgba(102, 126, 234, 0.3);
        }
        
        .generate-look-btn:disabled {
            background: #ccc;
            cursor: not-allowed;
            transform: none;
            box-shadow: none;
        }
        
        .clear-selection-btn {
            background: #6c757d;
            color: white;
            padding: 8px 16px;
            border: none;
            border-radius: 20px;
            cursor: pointer;
            font-size: 0.9em;
            transition: all 0.3s ease;
            width: 100%;
        }
        
        .clear-selection-btn:hover {
            background: #545b62;
            transform: translateY(-1px);
        }
        
        .looks-link {
            position: fixed;
            top: 20px;
            right: 20px;
            background: rgba(255,255,255,0.9);
            color: #667eea;
            padding: 12px 20px;
            text-decoration: none;
            border-radius: 25px;
            backdrop-filter: blur(10px);
            transition: all 0.3s ease;
            font-weight: 600;
            z-index: 1000;
        }
        
        .looks-link:hover {
            background: rgba(255,255,255,1);
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }
        
        body {
            background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 0;
            min-height: 100vh;
            overflow-x: hidden;
        }
        
        .container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
        }
        </style>
        """
        
        # Wayfair logo
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
        title_filter_html = f'''<div style="text-align: center; padding: 30px 20px; background: white;">
            <h1 style="color: #7b189f; font-size: 3em; margin: 0 0 20px 0; font-weight: 700; text-transform: uppercase; letter-spacing: 2px;">{search_term.title()}</h1>
            <div style="margin-bottom: 20px;">
                <label for="sourceFilter" style="font-weight: 600; color: #333; margin-right: 10px;">Filter by Source:</label>
                <select id="sourceFilter" style="padding: 8px 16px; border: 2px solid #7b189f; border-radius: 6px; font-size: 16px; background: white; color: #333; cursor: pointer;">
                    <option value="all">All Sources</option>
                    <option value="Pinterest">Pinterest Only</option>
                    <option value="Google">Google Only</option>
                </select>
            </div>
        </div>'''
        
        # Generate products HTML with selection checkboxes
        products_html = ""
        for i, product in enumerate(products):
            source = product.get('Source', 'Unknown')
            product_html = self.generate_product_html(product)
            # Add checkbox and data attributes for selection
            checkbox_html = f'<input type="checkbox" class="product-checkbox" data-product-index="{i}">'
            product_html = product_html.replace('<div class="product-item">', 
                f'<div class="product-item" data-source="{source}" data-product-index="{i}">\n            {checkbox_html}')
            products_html += product_html
        
        # Selection controls
        selection_controls_html = '''
        <div class="selection-controls" id="selectionControls" style="display: none;">
            <div class="selection-counter" id="selectionCounter">0 products selected</div>
            <button class="generate-look-btn" id="generateLookBtn" disabled>Generate AI Look</button>
            <button class="clear-selection-btn" id="clearSelectionBtn">Clear Selection</button>
        </div>
        '''
        
        # Looks gallery link
        looks_link_html = '''
        <a href="/looks" class="looks-link">
            <i class="fas fa-magic"></i> View All Looks
        </a>
        '''
        
        # JavaScript for product selection and look generation
        js_code = f'''
        <script>
        let selectedProducts = [];
        const products = {json.dumps(products)};
        
        // Product selection functionality
        document.addEventListener('DOMContentLoaded', function() {{
            const checkboxes = document.querySelectorAll('.product-checkbox');
            const selectionControls = document.getElementById('selectionControls');
            const selectionCounter = document.getElementById('selectionCounter');
            const generateLookBtn = document.getElementById('generateLookBtn');
            const clearSelectionBtn = document.getElementById('clearSelectionBtn');
            const sourceFilter = document.getElementById('sourceFilter');
            
            // Handle checkbox changes
            checkboxes.forEach(checkbox => {{
                checkbox.addEventListener('change', function() {{
                    const productIndex = parseInt(this.dataset.productIndex);
                    const productItem = this.closest('.product-item');
                    
                    if (this.checked) {{
                        selectedProducts.push(productIndex);
                        productItem.classList.add('selected');
                    }} else {{
                        const index = selectedProducts.indexOf(productIndex);
                        if (index > -1) {{
                            selectedProducts.splice(index, 1);
                        }}
                        productItem.classList.remove('selected');
                    }}
                    
                    updateSelectionUI();
                }});
            }});
            
            // Update selection UI
            function updateSelectionUI() {{
                const count = selectedProducts.length;
                selectionCounter.textContent = `${{count}} product${{count !== 1 ? 's' : ''}} selected`;
                
                if (count >= 3) {{
                    selectionControls.style.display = 'block';
                    generateLookBtn.disabled = false;
                    generateLookBtn.textContent = `Generate AI Look (${{count}} products)`;
                }} else if (count > 0) {{
                    selectionControls.style.display = 'block';
                    generateLookBtn.disabled = true;
                    generateLookBtn.textContent = `Select at least 3 products (${{count}}/3)`;
                }} else {{
                    selectionControls.style.display = 'none';
                }}
            }}
            
            // Clear selection
            clearSelectionBtn.addEventListener('click', function() {{
                selectedProducts = [];
                checkboxes.forEach(checkbox => {{
                    checkbox.checked = false;
                }});
                document.querySelectorAll('.product-item').forEach(item => {{
                    item.classList.remove('selected');
                }});
                updateSelectionUI();
            }});
            
            // Generate look
            generateLookBtn.addEventListener('click', function() {{
                if (selectedProducts.length < 3) {{
                    alert('Please select at least 3 products to create a look');
                    return;
                }}
                
                const selectedProductData = selectedProducts.map(index => products[index]);
                
                // Show loading state
                generateLookBtn.textContent = 'Generating...';
                generateLookBtn.disabled = true;
                
                // Send to server
                fetch('/generate_look', {{
                    method: 'POST',
                    headers: {{
                        'Content-Type': 'application/json',
                    }},
                    body: JSON.stringify({{
                        products: selectedProductData,
                        landing_page_name: '{search_term.replace(" ", "-")}.html'
                    }})
                }})
                .then(response => response.json())
                .then(data => {{
                    if (data.success) {{
                        alert('Look generated successfully! Redirecting to view it...');
                        window.location.href = data.look_url;
                    }} else {{
                        alert('Error generating look: ' + data.error);
                        generateLookBtn.textContent = 'Generate AI Look';
                        generateLookBtn.disabled = false;
                    }}
                }})
                .catch(error => {{
                    console.error('Error:', error);
                    alert('Error generating look. Please try again.');
                    generateLookBtn.textContent = 'Generate AI Look';
                    generateLookBtn.disabled = false;
                }});
            }});
            
            // Source filter functionality
            sourceFilter.addEventListener('change', function() {{
                const selectedSource = this.value;
                const productItems = document.querySelectorAll('.product-item');
                
                productItems.forEach(item => {{
                    const source = item.dataset.source;
                    if (selectedSource === 'all' || source === selectedSource) {{
                        item.style.display = 'block';
                    }} else {{
                        item.style.display = 'none';
                    }}
                }});
            }});
        }});
        </script>
        '''
        
        # Complete HTML
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{search_term.title()} - Trend Landing Page</title>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    {css_styles}
</head>
<body>
    {looks_link_html}
    {logo_html}
    {title_filter_html}
    <div class="product-grid">
        {products_html}
    </div>
    {selection_controls_html}
    {js_code}
</body>
</html>"""
        
        return html
    
    def generate_product_html(self, product):
        """Generate HTML for a single product"""
        grid_title = product.get('grid_title', '')
        display_name = product.get('display_name', '')
        image_url = product.get('images:orig:url')
        link = product.get('link')
        price = product.get('price', 'Price not available')
        seo_alt_txt = product.get('seo_alt_txt')
        source = product.get('Source', 'Unknown')

        # Use display_name if available, otherwise use grid_title
        product_title = display_name if display_name else grid_title
        
        # Truncate title if longer than 100 characters
        if len(product_title) > 100:
            product_title = product_title[:97] + '...'

        # Use seo_alt_txt for alt attribute if available, otherwise use product_title
        alt_text = seo_alt_txt if seo_alt_txt else product_title

        # Ensure link is not None or empty
        product_link = link if link else "#"

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

def main():
    """Main function to demonstrate usage"""
    generator = TrendLandingPageGenerator()
    
    # Example: Create landing page for "storage hacks"
    print("🔄 Creating landing page for 'Storage Hacks'...")
    generator.create_landing_page(
        search_term="Storage Hacks",
        pinterest_file="storage_hacks_output.json",
        google_file="storage_hacks_google.html"
    )
    
    # Example: Create landing page for "dopamine decor" (existing data)
    print("\n🔄 Creating landing page for 'Dopamine Decor'...")
    generator.create_landing_page(
        search_term="Dopamine Decor",
        pinterest_file="trends_output.json",
        google_file="pla_output.html"
    )

if __name__ == "__main__":
    main() 