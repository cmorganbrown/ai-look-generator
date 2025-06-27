# TrendScraper Deployment Guide

## Prerequisites
- Python 3.8+ installed on server
- Apache web server
- Git access to your repository

## Step 1: Clone/Update the Repository
```bash
cd /path/to/your/web/root
git pull origin main  # or your branch name
cd TrendScraper
```

## Step 2: Set Up Python Environment
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## Step 3: Set Environment Variables
```bash
# Set your OpenAI API key
export OPENAI_API_KEY="your-api-key-here"

# For permanent storage, add to ~/.bashrc or /etc/environment
echo 'export OPENAI_API_KEY="your-api-key-here"' >> ~/.bashrc
```

## Step 4: Test the Application
```bash
# Test with Gunicorn
gunicorn -c gunicorn.conf.py wsgi:app
```

## Step 5: Configure Apache (mod_proxy)
Add this to your Apache virtual host configuration:

```apache
<VirtualHost *:80>
    ServerName yourdomain.com
    DocumentRoot /path/to/your/web/root
    
    # Proxy Flask app
    ProxyPreserveHost On
    ProxyPass / http://127.0.0.1:8000/
    ProxyPassReverse / http://127.0.0.1:8000/
    
    # Static files (if needed)
    Alias /static/ /path/to/your/web/root/TrendScraper/static/
    <Directory /path/to/your/web/root/TrendScraper/static>
        Require all granted
    </Directory>
</VirtualHost>
```

## Step 6: Set Up Systemd Service
Create `/etc/systemd/system/trendscraper.service`:

```ini
[Unit]
Description=TrendScraper Flask App
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/path/to/your/web/root/TrendScraper
Environment="PATH=/path/to/your/web/root/TrendScraper/venv/bin"
Environment="OPENAI_API_KEY=your-api-key-here"
ExecStart=/path/to/your/web/root/TrendScraper/venv/bin/gunicorn -c gunicorn.conf.py wsgi:app
Restart=always

[Install]
WantedBy=multi-user.target
```

## Step 7: Start the Service
```bash
sudo systemctl daemon-reload
sudo systemctl enable trendscraper
sudo systemctl start trendscraper
sudo systemctl status trendscraper
```

## Step 8: Restart Apache
```bash
sudo systemctl restart apache2
```

## Troubleshooting
- Check logs: `sudo journalctl -u trendscraper -f`
- Check Apache logs: `sudo tail -f /var/log/apache2/error.log`
- Test Gunicorn directly: `gunicorn -c gunicorn.conf.py wsgi:app`

## File Permissions
Make sure the web server can write to these directories:
```bash
sudo chown -R www-data:www-data /path/to/your/web/root/TrendScraper/uploads
sudo chown -R www-data:www-data /path/to/your/web/root/TrendScraper/landing_pages
sudo chown -R www-data:www-data /path/to/your/web/root/TrendScraper/looks
sudo chown -R www-data:www-data /path/to/your/web/root/TrendScraper/static
``` 