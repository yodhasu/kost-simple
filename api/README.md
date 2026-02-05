# Kost Simple API

A production-ready REST API for Kost Kostan Management System built with FastAPI.

## Features

- 🚀 **FastAPI** - High-performance async framework
- 📚 **Swagger UI** - Interactive API documentation at `/docs`
- 🔐 **JWT Authentication** - Secure token-based auth
- 🗃️ **SQLAlchemy** - Robust ORM with PostgreSQL support
- 🧩 **Feature-based Structure** - Clean, modular architecture

## Project Structure

```
api/
├── app/
│   ├── api/v1/           # API versioning
│   ├── core/             # Config, security, dependencies
│   ├── db/               # Database configuration
│   └── features/         # Feature modules
│       ├── auth/         # Authentication
│       ├── rooms/        # Room management
│       ├── tenants/      # Tenant management
│       └── payments/     # Payment tracking
├── .env.example
├── requirements.txt
└── README.md
```

## Quick Start

```bash
# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Copy and configure environment
copy .env.example .env

# Run development server
uvicorn app.main:app --reload
```

## API Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
