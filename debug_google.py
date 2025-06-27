#!/usr/bin/env python3

from bs4 import BeautifulSoup

def debug_google_html():
    """Debug the Google HTML structure"""
    html_path = "scraped_data/storage_hacks_google.html"
    
    try:
        with open(html_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        print(f"File size: {len(content)} characters")
        
        soup = BeautifulSoup(content, 'html.parser')
        
        # Look for different possible selectors
        print("\n=== Testing different selectors ===")
        
        # Test .mnr-c.pla-unit
        pla_units = soup.select('.mnr-c.pla-unit')
        print(f"Found {len(pla_units)} .mnr-c.pla-unit elements")
        
        if pla_units:
            # Examine the first unit in detail
            first_unit = pla_units[0]
            print(f"\n=== First unit analysis ===")
            
            # Look for all img tags
            all_images = first_unit.select('img')
            print(f"Found {len(all_images)} img tags in first unit")
            
            for i, img in enumerate(all_images):
                src = img.get('src', '')
                alt = img.get('alt', '')
                print(f"  Image {i+1}: src='{src[:100]}...' alt='{alt[:50]}...'")
            
            # Look specifically for gstatic images
            gstatic_images = first_unit.select('img[src*="gstatic.com"]')
            print(f"Found {len(gstatic_images)} gstatic.com images")
            
            # Look for any images with wayfair in src
            wayfair_images = first_unit.select('img[src*="wayfair"]')
            print(f"Found {len(wayfair_images)} wayfair images")
            
            # Look for base64 images
            base64_images = first_unit.select('img[src*="data:image"]')
            print(f"Found {len(base64_images)} base64 images")
            
            # Look for any other image patterns
            print("\n=== All image sources in first unit ===")
            for img in all_images:
                src = img.get('src', '')
                if src:
                    print(f"  {src[:150]}...")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    debug_google_html() 