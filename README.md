# TrendScraper

A Flask web application that scrapes product data from Pinterest and Google Shopping, creates curated landing pages, and generates AI-powered "looks" with hero images.

## Features

- **Product Scraping**: Automatically scrapes products from Pinterest and Google Shopping based on search terms
- **Landing Pages**: Creates beautiful, responsive landing pages showcasing scraped products
- **Product Selection**: Interactive product selection with checkboxes and floating selection tray
- **AI Look Generation**: Creates curated "looks" from selected products with AI-generated hero images
- **Look Gallery**: Browse and manage all created looks
- **CSV Export**: Export product data for further analysis

## Tech Stack

- **Backend**: Python Flask
- **Frontend**: HTML, CSS, JavaScript
- **AI**: OpenAI GPT-4.1 for image generation
- **Deployment**: Railway.app (recommended)

## Quick Start

### Local Development

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd TrendScraper
   ```

2. **Set up virtual environment**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set environment variables**
   ```bash
   export OPENAI_API_KEY="your-openai-api-key-here"
   ```

5. **Run the application**
   ```bash
   python3 simple_app.py
   ```

6. **Access the app**
   - Open http://localhost:3000 in your browser

### Deployment to Railway

1. **Push to GitHub**
   ```bash
   git add .
   git commit -m "Initial commit"
   git push origin main
   ```

2. **Deploy to Railway**
   - Go to [railway.app](https://railway.app)
   - Sign up with GitHub
   - Create new project from GitHub repo
   - Add `OPENAI_API_KEY` environment variable
   - Deploy!

## Usage

1. **Create a Landing Page**
   - Go to "Create Landing Page"
   - Enter a search term (e.g., "nancy meyers bedroom aesthetic")
   - Upload Pinterest/Google Shopping data or use auto-scrape
   - Generate the landing page

2. **Select Products**
   - View the landing page
   - Use checkboxes to select products
   - Click "Create Look" when ready

3. **Generate AI Look**
   - The app will automatically generate a hero image using the selected products
   - View your look in the gallery

## Project Structure

```
TrendScraper/
├── simple_app.py          # Main Flask application
├── requirements.txt       # Python dependencies
├── wsgi.py               # WSGI entry point for production
├── gunicorn.conf.py      # Gunicorn configuration
├── templates/            # HTML templates
├── static/               # CSS, JS, images
├── uploads/              # Scraped data storage
├── landing_pages/        # Generated landing pages
├── looks/                # Generated looks
└── generated_images/     # AI-generated hero images
```

## Environment Variables

- `OPENAI_API_KEY`: Your OpenAI API key for image generation

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

MIT License - see LICENSE file for details

## 🚀 Features

- **Web UI**: User-friendly interface for non-technical users
- **File Upload**: Drag-and-drop support for Pinterest JSON and Google HTML files
- **Landing Page Generation**: Automatic creation of responsive product grids
- **Dashboard**: View, download, and manage all created landing pages
- **Statistics**: Track page creation and usage metrics
- **Responsive Design**: Modern, mobile-friendly interface

## 📋 Prerequisites

- Python 3.7+
- Virtual environment (recommended)

## 🛠️ Installation

1. **Clone or navigate to the project directory:**
   ```bash
   cd TrendScraper
   ```

2. **Create and activate virtual environment:**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip3 install -r requirements.txt
   ```

## 🎯 Quick Start

### Option 1: Web UI (Recommended)

1. **Start the web application:**
   ```bash
   python3 app.py
   ```

2. **Open your browser:**
   Navigate to `http://localhost:5000`

3. **Create your first landing page:**
   - Click "Create New Page"
   - Enter a search term/trend name
   - Upload Pinterest JSON and/or Google HTML files
   - Click "Generate Landing Page"

### Option 2: Command Line

1. **Generate a landing page directly:**
   ```bash
   python3 trend_generator.py "Your Search Term"
   ```

2. **Use existing data files:**
   ```bash
   python3 trend_generator.py "Storage Hacks" "scraped_data/storage_hacks_output.json" "scraped_data/storage_hacks_google.html"
   ```

## 📁 File Structure

```
TrendScraper/
├── app.py                 # Flask web application
├── trend_generator.py     # Core landing page generator
├── templates/             # HTML templates
│   ├── base.html         # Base template with styling
│   ├── home.html         # Dashboard/home page
│   └── create.html       # Create new page form
├── landing_pages/         # Generated HTML files
├── uploads/              # Uploaded data files
├── scraped_data/         # Sample data files
└── requirements.txt      # Python dependencies
```

## 📊 How to Get Data Files

### Pinterest Data (JSON)

1. **Search for your trend on Pinterest**
2. **Open browser developer tools** (F12)
3. **Go to Network tab** and filter by "json"
4. **Scroll through Pinterest results** to trigger API calls
5. **Find and download** the JSON response containing product data
6. **Save as** `your_trend_pinterest.json`

### Google Shopping Data (HTML)

1. **Search for your trend on Google Shopping**
2. **Right-click and "View Page Source"**
3. **Save the page as HTML file**
4. **Or use browser developer tools** to copy HTML content
5. **Save as** `your_trend_google.html`

## 🎨 Web UI Features

### Dashboard
- **Statistics**: Total pages, recent activity
- **Page Management**: View, download, delete pages
- **Quick Actions**: Create new pages, view existing ones

### Create Page Form
- **Search Term Input**: Name your trend/landing page
- **File Upload**: Drag-and-drop support for data files
- **Instructions**: Step-by-step guide for getting data files
- **Validation**: Ensures required fields are completed

### Page Viewer
- **Direct Viewing**: View generated pages in browser
- **Download**: Get HTML files for external hosting
- **Responsive**: Works on desktop and mobile

## 🔧 Configuration

### Flask Settings
- **Port**: Default 5000 (change in `app.py`)
- **Debug**: Enabled for development
- **Secret Key**: Change in production

### File Upload
- **Allowed Extensions**: `.json`, `.html`
- **Upload Directory**: `uploads/`
- **File Naming**: Automatic based on search term

## 🚀 Deployment

### Local Development
```bash
python3 app.py
```

### Production (using Gunicorn)
```