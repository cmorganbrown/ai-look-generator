#!/usr/bin/env python3
"""
Selenium-based Trend Scraper
Uses Selenium WebDriver for better scraping of dynamic content.
"""

import time
import json
import os
import re
from datetime import datetime
from urllib.parse import quote, unquote
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import random

class SeleniumTrendScraper:
    def __init__(self, output_dir="scraped_data", headless=True):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        self.headless = headless
        self.driver = None
        
    def setup_driver(self):
        """Setup Chrome WebDriver with anti-detection measures"""
        chrome_options = Options()
        
        if self.headless:
            chrome_options.add_argument("--headless")
        
        # Anti-detection measures
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        # Random user agent
        user_agents = [
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        ]
        chrome_options.add_argument(f"--user-agent={random.choice(user_agents)}")
        
        # Window size
        chrome_options.add_argument("--window-size=1920,1080")
        
        self.driver = webdriver.Chrome(options=chrome_options)
        
        # Execute script to remove webdriver property
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        return self.driver
    
    def scrape_pinterest(self, search_term, max_results=50):
        """Scrape Pinterest using Selenium"""
        print(f"🔍 Scraping Pinterest for '{search_term}'...")
        
        if not self.driver:
            self.setup_driver()
        
        try:
            # Navigate to Pinterest search
            encoded_term = quote(search_term)
            url = f"https://www.pinterest.com/search/pins/?q={encoded_term}&rs=typed"
            
            print(f"🔗 Searching Pinterest for: {search_term}")
            self.driver.get(url)
            
            # Wait longer for page to load
            time.sleep(random.uniform(8, 12))
            
            # Try to apply product filter if available
            try:
                product_filter = WebDriverWait(self.driver, 5).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, '[data-test-id="product-filter"]'))
                )
                product_filter.click()
                print("✅ Applied product filter")
                time.sleep(2)
            except TimeoutException:
                print("ℹ️ No product filter found, continuing with all pins")
            
            # Print the first 1000 characters of the page source for debugging
            page_source = self.driver.page_source
            print("\n--- PINTEREST PAGE SOURCE (first 1000 chars) ---\n")
            print(page_source[:1000])
            print("\n--- END PAGE SOURCE ---\n")
            
            # Get the entire page HTML content
            html_content = page_source
            print(f"✅ Successfully extracted Pinterest HTML content ({len(html_content)} characters)")
            
            return html_content
            
        except Exception as e:
            print(f"❌ Error scraping Pinterest: {str(e)}")
            return None
    
    def extract_pinterest_pin(self, pin_element):
        """Extract data from a Pinterest pin element"""
        try:
            # Extract title
            title_elem = pin_element.find_element(By.CSS_SELECTOR, '[data-test-id="pinTitle"]')
            title = title_elem.text if title_elem else ''
            
            # Extract image
            img_elem = pin_element.find_element(By.CSS_SELECTOR, 'img')
            image_url = img_elem.get_attribute('src') if img_elem else ''
            
            # Extract link
            link_elem = pin_element.find_element(By.CSS_SELECTOR, 'a')
            link = link_elem.get_attribute('href') if link_elem else ''
            
            # Extract price (if available)
            price = ''
            try:
                price_elem = pin_element.find_element(By.CSS_SELECTOR, '[data-test-id="price"]')
                price = price_elem.text if price_elem else ''
            except NoSuchElementException:
                pass
            
            if title and link:
                return {
                    'grid_title': title,
                    'display_name': title,
                    'images:orig:url': image_url,
                    'link': link,
                    'price': price,
                    'seo_alt_txt': title,
                    'Source': 'Pinterest'
                }
        except Exception as e:
            print(f"❌ Error in extract_pinterest_pin: {e}")
        
        return None
    
    def scrape_google_shopping(self, search_term, max_results=50):
        """Scrape Google Shopping using Selenium"""
        print(f"🔍 Scraping Google Shopping for '{search_term}'...")
        
        if not self.driver:
            self.setup_driver()
        
        try:
            # Navigate to Google Shopping with "wayfair" prepended
            wayfair_search = f"wayfair {search_term}"
            encoded_term = quote(wayfair_search)
            url = f"https://www.google.com/search?tbm=shop&q={encoded_term}&hl=en"
            
            print(f"🔗 Searching for: {wayfair_search}")
            self.driver.get(url)
            
            # Wait even longer for page to load
            time.sleep(random.uniform(10, 15))
            
            # Scroll a bit to trigger dynamic loading
            self.driver.execute_script("window.scrollTo(0, 500);")
            time.sleep(2)
            
            # Print the first 1000 characters of the page source for debugging
            page_source = self.driver.page_source
            print("\n--- GOOGLE PAGE SOURCE (first 1000 chars) ---\n")
            print(page_source[:1000])
            print("\n--- END PAGE SOURCE ---\n")
            
            # Look for the top-pla-group-inner element
            try:
                pla_element = WebDriverWait(self.driver, 15).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, ".top-pla-group-inner"))
                )
                print("✅ Found top-pla-group-inner element")
                
                # Get the entire HTML content of this element and its children
                html_content = pla_element.get_attribute('outerHTML')
                print(f"✅ Successfully extracted HTML content ({len(html_content)} characters)")
                
                return html_content
                
            except TimeoutException:
                print("❌ Could not find .top-pla-group-inner element")
                # Let's see what elements are actually on the page
                try:
                    all_elements = self.driver.find_elements(By.CSS_SELECTOR, "*")
                    pla_elements = [elem for elem in all_elements if 'pla' in elem.get_attribute('class') or 'pla' in elem.get_attribute('id')]
                    print(f"ℹ️ Found {len(pla_elements)} elements with 'pla' in class or id")
                    
                    # Try to get the page source as fallback
                    page_source = self.driver.page_source
                    print(f"ℹ️ Page source length: {len(page_source)} characters")
                    
                    # Look for any wayfair links
                    wayfair_links = self.driver.find_elements(By.CSS_SELECTOR, "a[href*='wayfair.com']")
                    print(f"ℹ️ Found {len(wayfair_links)} wayfair.com links")
                    
                    return page_source
                except Exception as e:
                    print(f"❌ Debug info failed: {e}")
                    return None
                
        except Exception as e:
            print(f"❌ Error scraping Google Shopping: {str(e)}")
            return None
    
    def scroll_page(self, scroll_count=3):
        """Scroll page to load more content"""
        for i in range(scroll_count):
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(random.uniform(2, 4))
    
    def save_data(self, search_term, pinterest_data, google_data):
        """Save scraped data to files"""
        try:
            # Save Pinterest data
            if pinterest_data:
                pinterest_file = os.path.join(self.output_dir, f"{search_term.lower().replace(' ', '_')}_pinterest.html")
                
                # If pinterest_data is HTML content, save it directly
                if isinstance(pinterest_data, str):
                    with open(pinterest_file, 'w', encoding='utf-8') as f:
                        f.write(pinterest_data)
                    print(f"✅ Saved Pinterest HTML data to {pinterest_file}")
                else:
                    # If it's a list of products, convert to JSON
                    pinterest_json = {
                        "resource_response": {
                            "data": {
                                "results": pinterest_data
                            }
                        }
                    }
                    with open(pinterest_file.replace('.html', '.json'), 'w', encoding='utf-8') as f:
                        json.dump(pinterest_json, f, indent=2, ensure_ascii=False)
                    print(f"✅ Saved Pinterest JSON data to {pinterest_file.replace('.html', '.json')}")
            
            # Save Google data
            if google_data:
                google_file = os.path.join(self.output_dir, f"{search_term.lower().replace(' ', '_')}_google.html")
                
                # If google_data is HTML content, save it directly
                if isinstance(google_data, str):
                    with open(google_file, 'w', encoding='utf-8') as f:
                        f.write(google_data)
                    print(f"✅ Saved Google HTML data to {google_file}")
                else:
                    # If it's a list of products, convert to JSON
                    with open(google_file.replace('.html', '.json'), 'w', encoding='utf-8') as f:
                        json.dump(google_data, f, indent=2, ensure_ascii=False)
                    print(f"✅ Saved Google JSON data to {google_file.replace('.html', '.json')}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error saving data: {str(e)}")
            return False
    
    def generate_google_html(self, products):
        """Generate HTML file for Google products"""
        html = """<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Google Shopping Results</title>
</head>
<body>"""
        
        for product in products:
            html += f"""
    <div class="pla-unit-container">
        <a class="pla-unit" href="{product.get('link', '')}" adurl="{product.get('link', '')}">
            <img src="{product.get('images:orig:url', '')}" alt="{product.get('grid_title', '')}">
            <div class="bXPcId" aria-label="{product.get('grid_title', '')}"></div>
            <div class="dOp6Sc" aria-label="{product.get('price', '')}"></div>
        </a>
    </div>"""
        
        html += """
</body>
</html>"""
        return html
    
    def scrape_trend(self, search_term, max_results=50):
        """Scrape both Pinterest and Google Shopping for a search term"""
        print(f"🚀 Starting Selenium scrape for: '{search_term}'")
        print("=" * 50)
        
        try:
            # Scrape Pinterest
            pinterest_data = self.scrape_pinterest(search_term, max_results)
            
            # Scrape Google Shopping
            google_data = self.scrape_google_shopping(search_term, max_results)
            
            # Save data
            save_success = self.save_data(search_term, pinterest_data, google_data)
            
            print("=" * 50)
            print(f"✅ Scraping complete for '{search_term}'")
            print(f"📊 Pinterest products: {len(pinterest_data) if pinterest_data else 0}")
            print(f"📊 Google products: {len(google_data) if isinstance(google_data, list) else 'HTML content' if google_data else 0}")
            
            # Provide feedback on results
            if not pinterest_data and not google_data:
                print("⚠️  No data found from either source")
                print("💡 Suggestions:")
                print("   - Try a different search term")
                print("   - Check if the search term has available products")
                print("   - Verify internet connection")
                return False
            elif not pinterest_data:
                print("⚠️  No Pinterest data found, but Google data available")
            elif not google_data:
                print("⚠️  No Google data found, but Pinterest data available")
            
            if save_success:
                print("✅ Data saved successfully")
                return True
            else:
                print("❌ Failed to save data")
                return False
            
        except Exception as e:
            print(f"❌ Error in scrape_trend: {e}")
            return False
    
    def close(self):
        """Close the WebDriver"""
        if self.driver:
            self.driver.quit()

def main():
    """Example usage"""
    scraper = SeleniumTrendScraper(headless=False)  # Set to True for headless mode
    
    try:
        # Example search terms
        search_terms = [
            "storage hacks",
            "kitchen organization"
        ]
        
        for term in search_terms:
            try:
                scraper.scrape_trend(term, max_results=20)
                print("\n" + "="*60 + "\n")
                time.sleep(random.uniform(5, 10))  # Delay between searches
            except Exception as e:
                print(f"❌ Error processing '{term}': {e}")
                continue
    finally:
        scraper.close()

if __name__ == "__main__":
    main() 