#!/usr/bin/env python3

import subprocess
import sys
import os

def main():
    """Start the Flask web UI"""
    print("🚀 Starting Trend Landing Page Generator Web UI...")
    print("📱 Opening browser to http://localhost:5000")
    print("⏹️  Press Ctrl+C to stop the server")
    print()
    
    # Run the Flask app
    try:
        subprocess.run([sys.executable, "app.py"], check=True)
    except KeyboardInterrupt:
        print("\n👋 Web UI stopped. Goodbye!")
    except Exception as e:
        print(f"❌ Error starting web UI: {e}")

if __name__ == "__main__":
    main() 