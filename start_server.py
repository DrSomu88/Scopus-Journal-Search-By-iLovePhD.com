#!/usr/bin/env python3
"""
Scopus Journal Search Web Interface
Simple startup script for the Flask application
"""

import os
import sys
import webbrowser
from threading import Timer

def open_browser():
    """Open the web browser after a short delay."""
    webbrowser.open('http://localhost:5000')

def main():
    """Start the Flask server with automatic browser opening."""
    
    # Check if the search index exists
    if not os.path.exists('scopus_search_index.pkl'):
        print("❌ Error: Search index not found!")
        print("Please run 'python Step2_full_dataset.py' first to create the search index.")
        sys.exit(1)
    
    print("🚀 Starting Scopus Journal Search Web Interface...")
    print("📊 Search index found - ready to serve!")
    print("🌐 Server will start at: http://localhost:5000")
    print("🔍 You can search through 47,758+ academic journals")
    print("\nPress Ctrl+C to stop the server")
    print("="*60)
    
    # Open browser after 2 seconds
    Timer(2, open_browser).start()
    
    # Import and run the Flask app
    try:
        from app import app
        app.run(debug=False, host='0.0.0.0', port=5000, use_reloader=False)
    except KeyboardInterrupt:
        print("\n\n👋 Server stopped. Goodbye!")
    except Exception as e:
        print(f"\n❌ Error starting server: {e}")
        print("Make sure all required packages are installed.")

if __name__ == "__main__":
    main()
