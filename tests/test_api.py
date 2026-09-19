import os

os.environ["DATABASE_URL"] = "sqlite:///./test_expenses.db"
os.environ["JWT_SECRET_KEY"] = "test-only-secret"

from fastapi.testclient import TestClient

from app.database import Base, engine
from app.main import app

Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)
client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_register_login_and_expense_crud():
    registered = client.post("/api/v1/auth/register", json={"email": "test@example.com", "password": "password123"})
    assert registered.status_code == 201
    assert registered.json()["email"] == "test@example.com"

    login = client.post("/api/v1/auth/login", data={"username": "test@example.com", "password": "password123"})
    assert login.status_code == 200
    token = login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    created = client.post("/api/v1/expenses", headers=headers, json={
        "amount": "12.50", "category": "food", "description": "Lunch", "expense_date": "2026-01-02"
    })
    assert created.status_code == 201
    expense_id = created.json()["id"]

    listing = client.get("/api/v1/expenses?category=food", headers=headers)
    assert listing.status_code == 200
    assert listing.json()["total"] == 1
    assert listing.json()["items"][0]["amount"] == "12.50"

    summary = client.get("/api/v1/expenses/summary", headers=headers)
    assert summary.status_code == 200
    assert summary.json()["count"] == 1
    assert summary.json()["by_category"]["food"] == "12.50"

    updated = client.patch(f"/api/v1/expenses/{expense_id}", headers=headers, json={"category": "dining"})
    assert updated.status_code == 200
    assert updated.json()["category"] == "dining"

    deleted = client.delete(f"/api/v1/expenses/{expense_id}", headers=headers)
    assert deleted.status_code == 204


def test_input_normalization_and_date_range_validation():
    registered = client.post("/api/v1/auth/register", json={
        "email": "  normalized@example.com ",
        "password": "password123",
    })
    assert registered.status_code == 201
    assert registered.json()["email"] == "normalized@example.com"

    login = client.post("/api/v1/auth/login", data={
        "username": "NORMALIZED@EXAMPLE.COM",
        "password": "password123",
    })
    headers = {"Authorization": f"Bearer {login.json()['access_token']}"}
    created = client.post("/api/v1/expenses", headers=headers, json={
        "amount": "8.00",
        "category": "  transport  ",
        "description": "  Bus fare  ",
        "expense_date": "2026-02-01",
    })
    assert created.status_code == 201
    assert created.json()["category"] == "transport"
    assert created.json()["description"] == "Bus fare"

    invalid = client.get(
        "/api/v1/expenses?start_date=2026-03-01&end_date=2026-02-01",
        headers=headers,
    )
    assert invalid.status_code == 400


def test_expenses_are_isolated_between_users():
    first = client.post("/api/v1/auth/register", json={
        "email": "first@example.com",
        "password": "password123",
    })
    second = client.post("/api/v1/auth/register", json={
        "email": "second@example.com",
        "password": "password123",
    })
    first_login = client.post("/api/v1/auth/login", data={
        "username": "first@example.com",
        "password": "password123",
    })
    second_login = client.post("/api/v1/auth/login", data={
        "username": "second@example.com",
        "password": "password123",
    })
    first_headers = {"Authorization": f"Bearer {first_login.json()['access_token']}"}
    second_headers = {"Authorization": f"Bearer {second_login.json()['access_token']}"}
    expense = client.post("/api/v1/expenses", headers=first_headers, json={
        "amount": "25.00",
        "category": "utilities",
        "expense_date": "2026-02-02",
    })

    assert client.get("/api/v1/expenses", headers=second_headers).json()["total"] == 0
    assert client.get(f"/api/v1/expenses/{expense.json()['id']}", headers=second_headers).status_code == 404
