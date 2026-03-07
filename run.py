"""
Movie Magic - Smart Movie Ticket Booking System
Main application entry point
"""

import os
from application import app

if __name__ == '__main__':
    # Run the application
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', 'True').lower() == 'true'
    
    print(f"Starting Movie Magic on port {port}...")
    print("=" * 50)
    print("Movie Magic - Smart Movie Ticket Booking")
    print("=" * 50)
    print(f"Debug mode: {debug}")
    print(f"Server running at: http://localhost:{port}")
    print("=" * 50)
    
    app.run(host='0.0.0.0', port=port, debug=debug)

