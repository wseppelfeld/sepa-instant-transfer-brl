# SEPA Instant Transfer BRL

A complete SEPA instant transfer system implementation adapted for Brazilian Real (BRL) with web interface.

## Features

### Backend Components
- **FastAPI REST API Server** with comprehensive endpoints
- **SQLAlchemy Database Models** with PostgreSQL support
- **JWT Authentication** and security features
- **Brazilian Compliance** (CPF/CNPJ validation, bank codes)
- **Instant Transfer Operations** with real-time balance updates
- **Transaction Management** with audit trails
- **SEPA/ISO 20022** message formatting compatibility
- **PIX Integration** ready architecture

### Frontend Components
- **Responsive Web Interface** with HTML/CSS/JavaScript
- **User Dashboard** with account overview
- **Transfer Forms** with Brazilian banking validation
- **Transaction History** with filtering and export
- **Real-time Balance Display**
- **QR Code Generation** for transfers

### Technical Features
- **Docker Containerization** with Docker Compose
- **Database Migrations** with Alembic
- **Comprehensive Testing** with pytest
- **API Documentation** with OpenAPI/Swagger
- **Brazilian Currency Formatting** (R$ 1.234,56)
- **Rate Limiting** and security middleware

## Quick Start

### Prerequisites
- Python 3.11+
- PostgreSQL 15+
- Docker and Docker Compose (optional)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/wseppelfeld/sepa-instant-transfer-brl.git
   cd sepa-instant-transfer-brl
   ```

2. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run with Docker Compose (Recommended)**
   ```bash
   docker-compose up -d
   ```

   **Or run manually:**
   ```bash
   # Start PostgreSQL database
   # Update DATABASE_URL in .env
   
   # Run database migrations
   alembic upgrade head
   
   # Start the application
   uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```

5. **Access the application**
   - Web Interface: http://localhost:8000
   - API Documentation: http://localhost:8000/docs
   - API Alternative Docs: http://localhost:8000/redoc

## Usage

### Web Interface

1. **Register a new user** with email, username, full name, and CPF
2. **Create bank accounts** with Brazilian bank codes and PIX keys
3. **Make instant transfers** between accounts or external recipients
4. **View transaction history** with filtering and CSV export
5. **Monitor account balances** in real-time

### API Endpoints

#### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - User login
- `GET /api/auth/me` - Get current user info

#### Account Management
- `POST /api/accounts/` - Create new account
- `GET /api/accounts/` - List user accounts
- `GET /api/accounts/{id}` - Get account details
- `PUT /api/accounts/{id}` - Update account
- `GET /api/accounts/{id}/balance` - Get account balance

#### Transfers
- `POST /api/transfers/instant` - Create instant transfer
- `GET /api/transfers/{id}` - Get transfer status
- `POST /api/transfers/{id}/cancel` - Cancel transfer

#### Transactions
- `GET /api/transactions/` - List transactions with filters
- `GET /api/transactions/{id}` - Get transaction details
- `GET /api/transactions/summary/monthly` - Monthly summary
- `GET /api/transactions/export/csv` - Export as CSV

## Development

### Running Tests
```bash
pytest tests/ -v
```

### Database Migrations
```bash
# Create new migration
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head

# Rollback migrations
alembic downgrade -1
```

### Code Structure
```
├── app/
│   ├── api/          # API route handlers
│   ├── core/         # Configuration and security
│   ├── db/           # Database configuration
│   ├── models/       # SQLAlchemy models
│   ├── schemas/      # Pydantic schemas
│   ├── services/     # Business logic
│   └── utils/        # Utility functions
├── static/           # Frontend assets
├── templates/        # HTML templates
├── tests/            # Test suite
├── alembic/          # Database migrations
└── docker-compose.yml
```

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://sepa_user:sepa_password@localhost:5432/sepa_brl_db` |
| `SECRET_KEY` | JWT secret key | `your-secret-key-here` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token expiration time | `30` |
| `RATE_LIMIT_PER_MINUTE` | API rate limit | `60` |
| `DEBUG` | Debug mode | `True` |

### Brazilian Banking Configuration

The system supports Brazilian banking standards:

- **Bank Codes**: 3-digit codes (001, 237, 341, etc.)
- **Branch Codes**: 4-digit agency codes
- **CPF Validation**: Individual taxpayer registry
- **CNPJ Validation**: Corporate taxpayer registry
- **PIX Keys**: Email, phone, CPF, or random keys
- **Currency Format**: R$ 1.234,56

## Security

- JWT-based authentication
- Password hashing with bcrypt
- API rate limiting
- Input validation and sanitization
- SQL injection prevention
- CORS configuration

## API Documentation

Full API documentation is available at:
- Swagger UI: `/docs`
- ReDoc: `/redoc`
- OpenAPI JSON: `/openapi.json`

## Testing

The project includes comprehensive tests:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app tests/

# Run specific test file
pytest tests/test_auth.py -v
```

## Deployment

### Docker Production Setup

1. Update environment variables in `.env`
2. Build and run with Docker Compose:
   ```bash
   docker-compose -f docker-compose.prod.yml up -d
   ```

### Manual Production Setup

1. Set up PostgreSQL database
2. Configure reverse proxy (nginx)
3. Set up SSL certificates
4. Configure environment variables
5. Run database migrations
6. Start application with production WSGI server

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run the test suite
6. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support, please open an issue on GitHub or contact the maintainers.

## Roadmap

- [ ] PIX integration with Brazilian Central Bank
- [ ] Multi-currency support
- [ ] Advanced fraud detection
- [ ] Mobile application
- [ ] Webhook notifications
- [ ] Advanced reporting and analytics
- [ ] SEPA network integration
- [ ] Blockchain settlement options
