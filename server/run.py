#!/usr/bin/env python3
"""
Development server for the IdiotsMS Account Management System
"""

import os
from app import app

if __name__ == '__main__':
    port = int(os.getenv('PORT', 3000))
    debug = os.getenv('NODE_ENV') == 'development'

    print(f"Starting Flask server on port {port}")
    print(f"Debug mode: {debug}")
    print(f"Environment: {os.getenv('NODE_ENV', 'development')}")

    app.run(host='0.0.0.0', port=port, debug=debug)
