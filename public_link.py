"""
Script to generate public link for Movie Magic using ngrok
"""
import os
import sys
import time
import threading

# Change to app directory
os.chdir(os.path.dirname(os.path.abspath(__file__)))

def start_flask():
    """Start Flask application in a separate thread"""
    from application import app
    app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)

def start_ngrok():
    """Start ngrok tunnel"""
    from pyngrok import ngrok
    
    # Set your ngrok authtoken here (get it from https://dashboard.ngrok.com/auth)
    # Or set it via: ngrok config add-authtoken YOUR_TOKEN
    NGROK_TOKEN = None  # Set your token here if needed
    
    if NGROK_TOKEN:
        ngrok.set_auth_token(NGROK_TOKEN)
    
    # Create tunnel
    public_url = ngrok.connect(5000, "http")
    print(f"\n" + "="*50)
    print(f"MOVIE MAGIC IS NOW LIVE!")
    print(f"="*50)
    print(f"Public URL: {public_url}")
    print(f"="*50)
    print(f"\nShare this link with others!")
    print(f"Press Ctrl+C to stop the server\n")
    
    return public_url

if __name__ == '__main__':
    print("Starting Movie Magic...")
    
    # Start Flask in background
    flask_thread = threading.Thread(target=start_flask, daemon=True)
    flask_thread.start()
    
    # Wait for Flask to start
    time.sleep(2)
    
    try:
        start_ngrok()
    except Exception as e:
        print(f"\nError: {e}")
        print("\nTo get a public link, you need to:")
        print("1. Sign up at https://ngrok.com")
        print("2. Get your authtoken")
        print("3. Run: ngrok config add-authtoken YOUR_TOKEN")
        print("\nOr try Render.com for permanent hosting:")
        print("https://render.com")

