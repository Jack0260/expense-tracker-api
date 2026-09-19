# Expense Tracker API

A secure FastAPI REST API for tracking personal or team expenses. It includes JWT-based authentication, SQLite persistence, and a clean REST interface for managing transactions, categories, and users.

## Features

- User registration and login with JWT authentication
- Secure password hashing using bcrypt or passlib
- Create, read, update, and delete expense records
- Filter expenses by category, date, and user
- SQLite database for simple local development and deployment
- FastAPI automatic API documentation via Swagger UI and ReDoc
- Structured error handling and validation

## Tech Stack

- Python 3.11+
- FastAPI
- SQLAlchemy
- SQLite
- PyJWT
- Pydantic
- Passlib

## Project Structure

```text
expense-tracker-api/
├── app/
│   ├── api/
│   ├── core/
│   ├── db/
│   ├── models/
│   ├── schemas/
│   ├── services/
│   └── main.py
├── requirements.txt
├── .env.example
├── README.md
└── .gitignore
```

## Getting Started

### Prerequisites

- Python 3.11 or newer
- pip
- Virtual environment tool such as venv

### Installation

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Environment Variables

Create a `.env` file based on `.env.example`:

```env
SECRET_KEY=your-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
DATABASE_URL=sqlite:///./app.db
```

### Run the API

```bash
uvicorn app.main:app --reload
```

The API will be available at:

- http://127.0.0.1:8000
- Swagger UI: http://127.0.0.1:8000/docs
- ReDoc: http://127.0.0.1:8000/redoc

## API Overview

### Auth

- `POST /register` — Create a new user account
- `POST /login` — Authenticate a user and return a JWT

### Expenses

- `GET /expenses` — List expenses
- `POST /expenses` — Create an expense
- `GET /expenses/{id}` — Fetch a specific expense
- `PUT /expenses/{id}` — Update an expense
- `DELETE /expenses/{id}` — Delete an expense

## Security Notes

This project is designed with security in mind:

- Passwords are hashed before storage
- JWT tokens are used for protected routes
- Secrets should be stored in environment variables, not in source control
- Database credentials and tokens must never be committed to Git

## License

This project is provided as-is for learning and development purposes.

## Contributing

Contributions are welcome. Please open an issue or submit a pull request with a clear explanation of the change.

