#!/usr/bin/env python3
"""
Trend Workflow Manager
Manages the complete workflow from search term to landing page generation.
"""

import os
import sys
import json
import re
from datetime import datetime
from trend_generator import TrendLandingPageGenerator

class TrendWorkflowManager:
    def __init__(self):
        self.generator = TrendLandingPageGenerator()
        self.data_dir = "scraped_data"
        self.landing_pages_dir = "landing_pages"
        
        # Ensure directories exist
        os.makedirs(self.data_dir, exist_ok=True)
        os.makedirs(self.landing_pages_dir, exist_ok=True)
    
    def list_existing_data(self):
        """List all existing data files"""
        print("📁 Existing data files:")
        print("-" * 40)
        
        if not os.path.exists(self.data_dir):
            print("No data directory found.")
            return []
        
        files = os.listdir(self.data_dir)
        data_files = []
        
        for file in files:
            if file.endswith(('.json', '.html')):
                filepath = os.path.join(self.data_dir, file)
                size = os.path.getsize(filepath)
                modified = datetime.fromtimestamp(os.path.getmtime(filepath))
                data_files.append({
                    'name': file,
                    'path': filepath,
                    'size': size,
                    'modified': modified
                })
        
        # Group by search term
        search_terms = {}
        for file in data_files:
            # Extract search term from filename
            # Format: term_source_timestamp.ext
            parts = file['name'].split('_')
            if len(parts) >= 3:
                search_term = ' '.join(parts[:-2])  # Everything except last 2 parts
                if search_term not in search_terms:
                    search_terms[search_term] = []
                search_terms[search_term].append(file)
        
        for term, files in search_terms.items():
            print(f"\n🔍 {term.title()}:")
            for file in files:
                print(f"  📄 {file['name']} ({file['size']} bytes, {file['modified'].strftime('%Y-%m-%d %H:%M')})")
        
        return data_files
    
    def find_data_for_term(self, search_term):
        """Find existing data files for a search term"""
        if not os.path.exists(self.data_dir):
            return None, None
        
        files = os.listdir(self.data_dir)
        pinterest_file = None
        google_file = None
        
        # Look for files matching the search term
        for file in files:
            if search_term.lower().replace(' ', '_') in file.lower():
                if file.endswith('.json') and 'pinterest' in file.lower():
                    pinterest_file = os.path.join(self.data_dir, file)
                elif file.endswith('.html') and 'google' in file.lower():
                    google_file = os.path.join(self.data_dir, file)
        
        return pinterest_file, google_file
    
    def create_landing_page(self, search_term, pinterest_file=None, google_file=None):
        """Create a landing page for a search term"""
        print(f"\n🎨 Creating landing page for '{search_term}'...")
        
        # Check if data files exist
        if not pinterest_file and not google_file:
            print("❌ No data files provided")
            return None
        
        if pinterest_file and not os.path.exists(pinterest_file):
            print(f"❌ Pinterest file not found: {pinterest_file}")
            pinterest_file = None
        
        if google_file and not os.path.exists(google_file):
            print(f"❌ Google file not found: {google_file}")
            google_file = None
        
        if not pinterest_file and not google_file:
            print("❌ No valid data files found")
            return None
        
        # Create landing page
        try:
            landing_page_path = self.generator.create_landing_page(
                search_term=search_term,
                pinterest_file=pinterest_file,
                google_file=google_file
            )
            
            if landing_page_path:
                print(f"✅ Landing page created successfully!")
                print(f"🌐 Open in browser: file://{os.path.abspath(landing_page_path)}")
                return landing_page_path
            else:
                print("❌ Failed to create landing page")
                return None
                
        except Exception as e:
            print(f"❌ Error creating landing page: {e}")
            return None
    
    def interactive_workflow(self):
        """Interactive workflow for creating landing pages"""
        print("🚀 Trend Landing Page Workflow")
        print("=" * 50)
        
        while True:
            print("\nOptions:")
            print("1. List existing data files")
            print("2. Create landing page from existing data")
            print("3. Create landing page with manual file selection")
            print("4. Exit")
            
            choice = input("\nEnter your choice (1-4): ").strip()
            
            if choice == "1":
                self.list_existing_data()
                
            elif choice == "2":
                self.create_from_existing_data()
                
            elif choice == "3":
                self.create_with_manual_files()
                
            elif choice == "4":
                print("👋 Goodbye!")
                break
                
            else:
                print("❌ Invalid choice. Please try again.")
    
    def create_from_existing_data(self):
        """Create landing page from existing data files"""
        print("\n📁 Available data:")
        data_files = self.list_existing_data()
        
        if not data_files:
            print("❌ No data files found. Please add some data files first.")
            return
        
        # Get search term from user
        search_term = input("\nEnter search term: ").strip()
        if not search_term:
            print("❌ Search term is required")
            return
        
        # Find data files for this term
        pinterest_file, google_file = self.find_data_for_term(search_term)
        
        if not pinterest_file and not google_file:
            print(f"❌ No data files found for '{search_term}'")
            return
        
        # Create landing page
        self.create_landing_page(search_term, pinterest_file, google_file)
    
    def create_with_manual_files(self):
        """Create landing page with manually specified files"""
        print("\n📁 Manual file selection:")
        
        # Get search term
        search_term = input("Enter search term: ").strip()
        if not search_term:
            print("❌ Search term is required")
            return
        
        # Get Pinterest file
        pinterest_file = input("Enter Pinterest JSON file path (or press Enter to skip): ").strip()
        if pinterest_file and not os.path.exists(pinterest_file):
            print(f"❌ File not found: {pinterest_file}")
            pinterest_file = None
        
        # Get Google file
        google_file = input("Enter Google HTML file path (or press Enter to skip): ").strip()
        if google_file and not os.path.exists(google_file):
            print(f"❌ File not found: {google_file}")
            google_file = None
        
        if not pinterest_file and not google_file:
            print("❌ At least one data file is required")
            return
        
        # Create landing page
        self.create_landing_page(search_term, pinterest_file, google_file)
    
    def batch_create_landing_pages(self, search_terms):
        """Create landing pages for multiple search terms"""
        print(f"🚀 Batch creating landing pages for {len(search_terms)} terms...")
        
        results = []
        for term in search_terms:
            print(f"\n{'='*50}")
            print(f"Processing: {term}")
            
            # Find existing data
            pinterest_file, google_file = self.find_data_for_term(term)
            
            if not pinterest_file and not google_file:
                print(f"❌ No data found for '{term}' - skipping")
                continue
            
            # Create landing page
            landing_page = self.create_landing_page(term, pinterest_file, google_file)
            results.append({
                'term': term,
                'landing_page': landing_page,
                'success': landing_page is not None
            })
        
        # Summary
        print(f"\n{'='*50}")
        print("📊 Batch Processing Summary:")
        successful = sum(1 for r in results if r['success'])
        print(f"✅ Successful: {successful}/{len(search_terms)}")
        
        for result in results:
            status = "✅" if result['success'] else "❌"
            print(f"{status} {result['term']}")
        
        return results

def main():
    """Main function"""
    manager = TrendWorkflowManager()
    
    # Check if command line arguments provided
    if len(sys.argv) > 1:
        if sys.argv[1] == "--batch" and len(sys.argv) > 2:
            # Batch mode
            search_terms = sys.argv[2:]
            manager.batch_create_landing_pages(search_terms)
        elif sys.argv[1] == "--list":
            # List existing data
            manager.list_existing_data()
        elif sys.argv[1] == "--create" and len(sys.argv) >= 3:
            # Create single landing page
            search_term = sys.argv[2]
            pinterest_file = sys.argv[3] if len(sys.argv) > 3 else None
            google_file = sys.argv[4] if len(sys.argv) > 4 else None
            manager.create_landing_page(search_term, pinterest_file, google_file)
        else:
            print("Usage:")
            print("  python workflow_manager.py --batch 'term1' 'term2' 'term3'")
            print("  python workflow_manager.py --list")
            print("  python workflow_manager.py --create 'search term' [pinterest_file] [google_file]")
            print("  python workflow_manager.py  # Interactive mode")
    else:
        # Interactive mode
        manager.interactive_workflow()

if __name__ == "__main__":
    main() 