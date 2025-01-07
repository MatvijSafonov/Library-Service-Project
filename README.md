# Library-service-project
We developed a special API for library services,
allowing the addition of authors, books linked to these authors to the database,
as well as borrowing these books from the library.

## Features
The Library Management System API provides the following features:

### Books Service
This service is responsible for managing the books inventory.

API:

- GET /books/: Get a list of all books.
- GET /books/<id>/: Get details about a specific book.
- POST /books/: Add a new book to the inventory.
- PUT /books/<id>/: Update an existing book's information.
- DELETE /books/<id>/: Delete a book from the inventory.
### Users Service
This service is responsible for managing the library customers.

API:

- POST /users/: Register a new user.
- POST /users/token/: Get a JWT token.
- POST /users/token/refresh/: Refresh a JWT token.
- GET /users/me/: Get the currently logged-in user's information.
- PUT /users/me/: Update the currently logged-in user's information.
### Borrowings Service
This service is responsible for managing the users' borrowings of books.

API:

- GET /borrowings/: Get a list of all borrowings.
- GET /borrowings/<id>/: Get details about a specific borrowing.
- POST /borrowings/: Add a new borrowing.
- PATCH /borrowings/<id>/: Update a borrowing's information.
- DELETE /borrowings/<id>/: Delete a borrowing.
### Payments Service
- This service is responsible for handling payments for book borrowings through the platform.

API:

- POST /payments/: Make a payment for a borrowing.
### Notifications Service (Telegram)
This service is responsible for sending notifications about new borrowing created, borrowings overdue, and successful payment. The notifications will be sent via Telegram.

## Installation
Follow these steps to set up and run the project locally:

### Local Setup
1. Clone the repository:
   ```bash
    git clone https://github.com/MatvijSafonov/Library-Service-Project.git
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

6. Create superuser:
   ```bash
   python manage.py createsuperuser
   # Or alternatively:
   make superuser
   ```

7. Run the development server:
   ```bash
   python manage.py runserver
   # Or alternatively:
   make run
   ```
The application will be available at:
- API: http://localhost:8000/api/
- Admin panel: http://localhost:8000/admin/
- API Documentation (swagger): http://localhost:8000/api/docs/swagger/
- API Documentation (redoc): http://localhost:8000/api/docs/redoc/

### Docker Setup

1. Clone the repository:
   ```bash
    git clone https://github.com/MatvijSafonov/Library-Service-Project.git
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
- API Documentation (swagger): http://localhost:8000/api/docs/swagger/
- API Documentation (redoc): http://localhost:8000/api/docs/redoc/
- pgAdmin: http://localhost:5050/
- RedisInsight: http://localhost:5540/
