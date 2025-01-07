# Library Service API

Global Flight Tracking System - RESTful API service for real-time flight monitoring and airport data management worldwide.

## 📋 Table of Contents
- [Overview](#-overview)
- [Features](#-features)
- [Tech Stack](#-tech-stack)
- [System Requirements](#-system-requirements)
- [Installation](#-installation)
  - [Local Setup](#local-setup)
  - [Docker Setup](#docker-setup)
- [Environment Variables](#-environment-variables)
- [API Documentation](#-api-documentation)
- [Makefile Commands](#-makefile-commands)
- [Database Structure](#-database-structure)
- [Testing](#-testing)
- [Troubleshooting](#-troubleshooting)
- [API Examples](#-api-examples)

## Overview

Airport API is a comprehensive flight management system that provides functionality for managing airports, airplanes, flights, crew members, and ticket bookings. The system allows users to track flights, manage airport resources, and handle ticket reservations efficiently.

## ✨ Features

### Airport Management
- Create and manage airports with location information
- Search airports by name or location

### Aircraft Operations
- Manage different types of aircraft
- Track airplane details including capacity and configuration
- Upload and manage aircraft images

### Flight Management
- Create and schedule flights
- Assign aircraft and crew to flights
- Search flights by various parameters (date, route, etc.)

### Crew Management
- Manage flight crew information

### Booking System
- User registration and authentication
- Ticket booking and management
- Order history tracking
- Seat selection functionality

### Additional Features
- JWT Authentication
- API throttling
- Caching with Redis
- Comprehensive API documentation
- Automated testing

## 🛠 Tech Stack

- **Python 3.12**
- **Django 5.1**
- **Django REST Framework**
- **PostgreSQL**
- **Redis**
- **Docker & Docker Compose**
- **Poetry (dependency management)**
- **Make**
- **JWT Authentication**
- **Swagger/Redoc Documentation**

## 💻 System Requirements

- Python 3.12+
- PostgreSQL 17+
- Redis 7+
- Docker & Docker Compose (for containerized setup)
- Make (optional, for using Makefile commands)

## 🚀 Installation

Follow these steps to set up and run the project locally:

### Local Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/vladyslav-tmf/airport-api.git
   cd airport-api
   ```

2. Create and activate virtual environment:
    - Linux/Mac:
      ```bash
      python3 -m venv venv
      source venv/bin/activate
      ```
    - Windows:
      ```bash
      python -m venv venv
      venv\Scripts\activate
      ```

3. Install Poetry and dependencies:
   ```bash
   pip install poetry
   poetry install
   ```

4. Create .env file:
   ```bash
   cp .env.sample .env
   # Edit .env file with your configurations
   ```

5. Apply database migrations:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   # Or alternatively:
   make migrate
   ```

6. Load sample data (optional):
   ```bash
   python manage.py loaddata airport_api_sample_data.json
   # Or alternatively:
   make load
   ```

7. Create superuser:
   ```bash
   python manage.py createsuperuser
   # Or alternatively:
   make superuser
   ```

8. Run the development server:
   ```bash
   python manage.py runserver
   # Or alternatively:
   make run
   ```
The application will be available at:
- API: http://localhost:8000/api/v1/
- Admin panel: http://localhost:8000/admin/
- API Documentation (swagger): http://localhost:8000/api/v1/docs/swagger/
- API Documentation (redoc): http://localhost:8000/api/v1/docs/redoc/

### Docker Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/airport-api.git
   cd airport-api
   ```

2. Create .env file:
   ```bash
   cp .env.sample .env
   # Edit .env file with your configurations
   ```

3. Build and run containers:
   ```bash
   docker-compose up --build
   ```

4. Create superuser in Docker:
   ```bash
   docker-compose exec app make superuser
   ```

The application will be available at:
- API: http://localhost:8000/api/v1/
- Admin panel: http://localhost:8000/admin/
- API Documentation (swagger): http://localhost:8000/api/v1/docs/swagger/
- API Documentation (redoc): http://localhost:8000/api/v1/docs/redoc/
- pgAdmin: http://localhost:5050/
- RedisInsight: http://localhost:5540/

## 🔐 Environment Variables

Create a `.env` file in the root directory with the following variables:

```env
# Database settings
POSTGRES_HOST=db
POSTGRES_PORT=5432
POSTGRES_DB=airport_db
POSTGRES_USER=airport_user
POSTGRES_PASSWORD=strong_password

# pgAdmin settings
PGADMIN_DEFAULT_EMAIL=admin@admin.com
PGADMIN_DEFAULT_PASSWORD=admin

# Django settings
SECRET_KEY=secret_key

```

## 📚 API Documentation

The API documentation is available in Swagger UI format at `/api/v1/docs/swagger/` and Redoc format at `/api/v1/docs/redoc/` when the server is running. It provides detailed information about:

- Available endpoints
- Request/Response formats
- Authentication methods
- API parameters

## 📦 Makefile Commands

The Makefile provides a set of commands for common tasks, such as running the server, applying database migrations, and loading sample data.

- `make install`: Install dependencies
- `make migrate`: Apply database migrations
- `make run`: Run the development server
- `make superuser`: Create superuser
- `make test`: Run tests
- `make load`: Load sample data
- `make setup`: Complete project setup

## 🗄 Database Structure

The project uses SQLite for local development and PostgreSQL for Docker setup, and includes the following main models:

- **User**: Manages user accounts
- **Airport**: Stores airport information
- **AirplaneType**: Defines different types of aircraft
- **Airplane**: Contains specific airplane details
- **Crew**: Manages crew member information
- **Route**: Defines flight routes between airports
- **Flight**: Manages flight schedules and details
- **Order**: Handles customer bookings
- **Ticket**: Manages individual tickets

## 🧪 Testing

The project includes comprehensive tests for models, views, serializers and admin panel functionality.

Run tests using:
```bash
# Local environment
python manage.py test
# Or alternatively:
make test

# Docker environment
docker-compose exec app make test
```

## 🔧 Troubleshooting

### Common Issues
1. **Database connection errors**
   - Check if PostgreSQL is running
   - Verify database credentials in .env file
   - Ensure database migrations are applied

2. **Redis connection issues**
   - Verify Redis service is running

## 📝 API Examples

### Authentication
```bash
# Get access token
curl -X POST http://localhost:8000/api/v1/user/token/ \
    -H "Content-Type: application/json" \
    -d '{"email": "user@example.com", "password": "password"}'
```

### Flights
```bash
# Get list of flights
curl -X GET http://localhost:8000/api/v1/flights/ \
    -H "Authorization: Bearer <your_token>"

# Create new flight (admin only)
curl -X POST http://localhost:8000/api/v1/flights/ \
    -H "Authorization: Bearer <your_token>" \
    -H "Content-Type: application/json" \
    -d '{
        "route": "uuid",
        "airplane": "uuid",
        "departure_time": "2024-01-01T10:00:00Z",
        "arrival_time": "2024-01-01T12:00:00Z"
    }'
```
