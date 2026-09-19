# Expense Tracker API

A production-oriented expense tracker REST API built with FastAPI, SQLAlchemy 2,
SQLite, and JWT authentication.

## Quick start

Requires Python 3.10 or newer.

```bash
python -m venv .venv
# macOS/Linux: source .venv/bin/activate
# Windows: .venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env       # Windows (use cp on macOS/Linux)
uvicorn app.main:app --app-dir src --reload
```

Interactive API documentation is available at `http://localhost:8000/docs`.
Set a strong, random `JWT_SECRET_KEY` before deploying. `DATABASE_URL` defaults
to a local SQLite file and can be changed in `.env`.

## API

All versioned endpoints use the `/api/v1` prefix:

* `POST /api/v1/auth/register` — create an account (`email`, `password`, minimum 8 characters)
* `POST /api/v1/auth/login` — OAuth2 form login (`username` is the email and `password`); returns a bearer token
* `GET /api/v1/auth/me` — current authenticated user
* `POST /api/v1/expenses` — create an expense (`amount`, `category`, `expense_date`, optional `description`)
* `GET /api/v1/expenses` — list the current user's expenses with `page`, `page_size`, `category`, `start_date`, and `end_date` filters
* `GET /api/v1/expenses/{id}`, `PATCH /api/v1/expenses/{id}`, `DELETE /api/v1/expenses/{id}` — protected CRUD
* `GET /api/v1/expenses/summary` — total, count, and totals grouped by category (supports date filters)

Use the `Authorize` button in Swagger after logging in, or send
`Authorization: Bearer <access_token>`. Expense records are always scoped to
the authenticated user. `GET /health` is an unauthenticated readiness check.

## Tests

```bash
pytest
```

The test suite covers health, registration/login, protected expense CRUD,
filtering, and summary behavior. The SQLite database file is created
automatically on first run.
