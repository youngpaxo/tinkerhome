#!/usr/bin/env python3
"""
Finanzas Application - Refactored Version 2.0

A Flask-based personal finance management application with improved
architecture, error handling, and maintainability.

Features:
- User authentication and authorization
- Income, expense, and savings tracking
- Financial summaries and reporting
- Notes management
- Account balance tracking
- Category-based expense analysis

Author: Refactored for better maintainability
Version: 2.0
"""

import os
from app import create_app

# Create application instance
app = create_app()

if __name__ == "__main__":
    # Get configuration from environment or use defaults
    host = app.config.get('HOST', '127.0.0.1')
    port = app.config.get('PORT', 5000)
    debug = app.config.get('DEBUG', True)
    
    print(f"""
    ╔══════════════════════════════════════════════════════════════╗
    ║                    Finanzas App v2.0                         ║
    ║                  Personal Finance Manager                    ║
    ╠══════════════════════════════════════════════════════════════╣
    ║  🚀 Starting server on http://{host}:{port}                 ║
    ║  🔧 Debug mode: {'ON' if debug else 'OFF'}                                           ║
    ║  📊 Database: {app.config.get('DATABASE_NAME', 'finanzas.db')}                                    ║
    ║  🌍 Environment: {os.environ.get('FLASK_ENV', 'development')}                                 ║
    ╚══════════════════════════════════════════════════════════════╝
    """)
    
    try:
        app.run(
            host=host,
            port=port,
            debug=debug,
            threaded=True
        )
    except KeyboardInterrupt:
        print("\n👋 Shutting down gracefully...")
    except Exception as e:
        print(f"❌ Error starting application: {e}")
        exit(1)