# Finanzas App v2.0 - Personal Finance Manager

A refactored Flask-based personal finance management application with improved architecture, maintainability, and error handling.

## 🚀 Features

- **User Authentication**: Secure user registration and login
- **Financial Tracking**: Track income, expenses, and savings
- **Account Management**: Multiple account support with balance tracking
- **Category Analysis**: Expense categorization and analysis
- **Notes System**: Personal financial notes and reminders
- **Dashboard**: Comprehensive financial overview
- **API Endpoints**: RESTful API for data access

## 🏗️ Architecture Improvements

### Version 2.0 Refactoring Benefits:

1. **Modular Structure**: Separated concerns into distinct modules
2. **Service Layer**: Business logic abstracted from routes
3. **Database Layer**: Centralized database operations with connection pooling
4. **Configuration Management**: Environment-based configuration
5. **Error Handling**: Comprehensive error handling and logging
6. **Type Safety**: Added type hints throughout the codebase
7. **Validation**: Input validation and sanitization
8. **Security**: Improved security practices

### Project Structure:
```
finanzas-app/
├── app/
│   ├── __init__.py              # Application factory
│   ├── models/
│   │   └── models.py            # Data models
│   ├── database/
│   │   └── db_manager.py        # Database operations
│   ├── routes/
│   │   ├── auth.py              # Authentication routes
│   │   └── main.py              # Main application routes
│   ├── services.py              # Business logic layer
│   └── utils.py                 # Utility functions
├── config/
│   └── config.py                # Configuration classes
├── templates/                   # HTML templates (existing)
├── static/                      # Static files (existing)
├── logs/                        # Application logs
├── run.py                       # Application entry point
├── requirements.txt             # Dependencies
├── .env.example                 # Environment variables example
└── README.md                    # This file
```

## 🛠️ Installation & Setup

### Prerequisites
- Python 3.8+
- pip

### Installation Steps

1. **Clone or navigate to the project directory**
   ```bash
   cd your-project-directory
   ```

2. **Create a virtual environment** (recommended)
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Run the application**
   ```bash
   python run.py
   ```

## 🔧 Configuration

### Environment Variables

Create a `.env` file based on `.env.example`:

```env
FLASK_ENV=development          # development, production, testing
SECRET_KEY=your-secret-key     # Change this in production!
DATABASE_NAME=finanzas.db      # Database file name
DEBUG=True                     # Set to False in production
HOST=127.0.0.1                # Server host
PORT=5000                      # Server port
```

### Configuration Classes

- **DevelopmentConfig**: For local development
- **ProductionConfig**: For production deployment
- **TestingConfig**: For running tests

## 📊 Database Schema

### Tables:
- **users**: User accounts and authentication
- **movimientos**: Financial movements (income, expenses, savings)
- **notas**: User notes and reminders

### Improvements:
- Added proper constraints and foreign keys
- Created indexes for better performance
- Improved data validation

## 🔐 Security Features

- Password hashing with Werkzeug
- CSRF protection ready
- Input validation and sanitization
- SQL injection prevention
- Session management with Flask-Login

## 📝 API Endpoints

### Authentication
- `POST /register` - User registration
- `POST /login` - User login
- `GET /logout` - User logout

### Main Application
- `GET /` - Dashboard
- `GET|POST /movimientos` - Movements management
- `POST /borrar_movimiento/<id>` - Delete movement
- `GET|POST /notas` - Notes management

### API Endpoints
- `GET /api/financial-summary` - Financial summary data
- `GET /api/top-categories` - Top expense categories
- `GET /api/account-balances` - Account balances

## 🧪 Testing

Run tests with pytest:
```bash
pytest
```

## 📈 Performance Improvements

1. **Database Optimization**:
   - Connection pooling with context managers
   - Proper indexing
   - Optimized queries

2. **Code Efficiency**:
   - Reduced database calls
   - Better error handling
   - Caching where appropriate

3. **Memory Management**:
   - Proper resource cleanup
   - Context managers for database connections

## 🚀 Deployment

### Development
```bash
python run.py
```

### Production with Gunicorn
```bash
gunicorn -w 4 -b 0.0.0.0:5000 "app:create_app('production')"
```

### Environment Setup for Production
```env
FLASK_ENV=production
SECRET_KEY=your-very-secure-secret-key
DATABASE_NAME=/path/to/production/finanzas.db
DEBUG=False
HOST=0.0.0.0
PORT=5000
```

## 🔍 Monitoring & Logging

- Application logs are stored in `logs/finanzas.log`
- Health check endpoint: `GET /health`
- Structured logging with timestamps and context

## 🤝 Contributing

1. Follow the existing code structure
2. Add type hints to new functions
3. Include proper error handling
4. Write tests for new features
5. Update documentation

## 📋 Migration from v1.0

The refactored version maintains database compatibility with the original `app.py`. Your existing data will work without migration.

### Key Changes:
- Modular architecture
- Improved error handling
- Better security practices
- Enhanced logging
- Type safety
- Configuration management

## 🐛 Troubleshooting

### Common Issues:

1. **Database locked error**:
   - Ensure proper connection cleanup
   - Check file permissions

2. **Import errors**:
   - Verify virtual environment activation
   - Check Python path

3. **Configuration issues**:
   - Verify `.env` file exists and is properly formatted
   - Check environment variable names

## 📞 Support

For issues or questions:
1. Check the logs in `logs/finanzas.log`
2. Verify configuration in `.env`
3. Ensure all dependencies are installed

## 🎯 Future Enhancements

- [ ] Data export functionality
- [ ] Advanced reporting and charts
- [ ] Mobile-responsive design improvements
- [ ] Backup and restore features
- [ ] Multi-currency support
- [ ] Budget planning tools

---

**Version**: 2.0  
**License**: MIT  
**Python**: 3.8+  
**Framework**: Flask 2.3+