#!/usr/bin/env python3
"""
Automated Trend Scraper
Fetches product data from Pinterest and Google Shopping for any search term.
"""

import requests
import json
import time
import random
import os
from urllib.parse import quote, urlencode
from bs4 import BeautifulSoup
import re
from datetime import datetime

class AutomatedTrendScraper:
    def __init__(self, output_dir="scraped_data"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        
        # Session with realistic headers
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Cache-Control': 'max-age=0'
        })
    
    def scrape_pinterest(self, search_term, max_results=50):
        """Scrape Pinterest for products related to search term"""
        print(f"🔍 Scraping Pinterest for '{search_term}'...")
        
        # Pinterest search URL
        encoded_term = quote(search_term)
        url = f"https://www.pinterest.com/search/pins/?q={encoded_term}&rs=typed"
        
        try:
            # Add Pinterest-specific headers
            headers = {
                'Referer': 'https://www.pinterest.com/',
                'X-Requested-With': 'XMLHttpRequest',
                'Accept': 'application/json, text/javascript, */*; q=0.01'
            }
            
            response = self.session.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            
            # Extract JSON data from Pinterest response
            # Pinterest loads data dynamically, so we need to look for JSON in the HTML
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Look for JSON data in script tags
            json_data = None
            for script in soup.find_all('script'):
                if script.string and 'window.__INITIAL_STATE__' in script.string:
                    # Extract JSON from the script
                    json_str = script.string.split('window.__INITIAL_STATE__ = ')[1].split(';</script>')[0]
                    json_data = json.loads(json_str)
                    break
            
            if not json_data:
                print("❌ Could not find Pinterest data in page")
                return []
            
            # Extract products from Pinterest data structure
            products = []
            # This is a simplified extraction - Pinterest's structure can be complex
            # You might need to adjust based on the actual response structure
            
            print(f"✅ Found Pinterest data structure")
            return products
            
        except Exception as e:
            print(f"❌ Error scraping Pinterest: {e}")
            return []
    
    def scrape_google_shopping(self, search_term, max_results=50):
        """Scrape Google Shopping for products related to search term"""
        print(f"🔍 Scraping Google Shopping for '{search_term}'...")
        
        # Google Shopping search URL
        encoded_term = quote(search_term)
        url = f"https://www.google.com/search?tbm=shop&q={encoded_term}&hl=en"
        
        try:
            # Add Google-specific headers
            headers = {
                'Referer': 'https://www.google.com/',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            }
            
            response = self.session.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract product data from Google Shopping
            products = []
            product_containers = soup.select('.pla-unit-container')
            
            for container in product_containers[:max_results]:
                try:
                    product = self.extract_google_product(container)
                    if product:
                        products.append(product)
                except Exception as e:
                    print(f"❌ Error extracting Google product: {e}")
                    continue
            
            print(f"✅ Found {len(products)} Google Shopping products")
            return products
            
        except Exception as e:
            print(f"❌ Error scraping Google Shopping: {e}")
            return []
    
    def extract_google_product(self, container):
        """Extract product data from Google Shopping container"""
        try:
            # Extract title
            title_elem = container.select_one('.bXPcId')
            title = title_elem.get('aria-label') if title_elem else ''
            
            # Extract price
            price_elem = container.select_one('.dOp6Sc')
            price = price_elem.get('aria-label') if price_elem else ''
            
            # Extract image
            img_elem = container.select_one('img')
            image_url = img_elem['src'] if img_elem and img_elem.has_attr('src') else ''
            
            # Extract link
            link_elem = container.select_one('a.pla-unit')
            link = link_elem.get('adurl') or link_elem.get('href') if link_elem else ''
            
            if title and link:
                return {
                    'title': title,
                    'price': price,
                    'image_url': image_url,
                    'link': link,
                    'source': 'Google Shopping'
                }
        except Exception as e:
            print(f"❌ Error in extract_google_product: {e}")
        
        return None
    
    def save_data(self, search_term, pinterest_data, google_data):
        """Save scraped data to files"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        slug = re.sub(r'[^a-zA-Z0-9\s-]', '', search_term.lower())
        slug = re.sub(r'\s+', '-', slug.strip())
        
        # Save Pinterest data
        if pinterest_data:
            pinterest_file = os.path.join(self.output_dir, f"{slug}_pinterest_{timestamp}.json")
            with open(pinterest_file, 'w', encoding='utf-8') as f:
                json.dump(pinterest_data, f, indent=2, ensure_ascii=False)
            print(f"✅ Saved Pinterest data: {pinterest_file}")
        
        # Save Google data
        if google_data:
            google_file = os.path.join(self.output_dir, f"{slug}_google_{timestamp}.html")
            with open(google_file, 'w', encoding='utf-8') as f:
                f.write(google_data)
            print(f"✅ Saved Google data: {google_file}")
        
        return pinterest_file if pinterest_data else None, google_file if google_data else None
    
    def scrape_trend(self, search_term, max_results=50):
        """Main method to scrape both sources for a search term"""
        print(f"🚀 Starting automated scrape for: '{search_term}'")
        print("=" * 50)
        
        # Add random delay to avoid rate limiting
        delay = random.uniform(1, 3)
        print(f"⏳ Waiting {delay:.1f} seconds...")
        time.sleep(delay)
        
        # Scrape both sources
        pinterest_data = self.scrape_pinterest(search_term, max_results)
        google_data = self.scrape_google_shopping(search_term, max_results)
        
        # Save data
        pinterest_file, google_file = self.save_data(search_term, pinterest_data, google_data)
        
        print("=" * 50)
        print(f"✅ Scraping complete for '{search_term}'")
        print(f"📊 Pinterest products: {len(pinterest_data)}")
        print(f"📊 Google products: {len(google_data)}")
        
        return pinterest_file, google_file

def main():
    """Example usage"""
    scraper = AutomatedTrendScraper()
    
    # Example search terms
    search_terms = [
        "storage hacks",
        "dopamine decor",
        "kitchen organization",
        "minimalist bedroom"
    ]
    
    for term in search_terms:
        try:
            scraper.scrape_trend(term, max_results=30)
            print("\n" + "="*60 + "\n")
        except Exception as e:
            print(f"❌ Error processing '{term}': {e}")
            continue

if __name__ == "__main__":
    main() 