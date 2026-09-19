from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: EmailStr) -> str:
        return str(value).strip().lower()


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: EmailStr
    created_at: datetime


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class ExpenseCreate(BaseModel):
    amount: Decimal = Field(gt=0, max_digits=12, decimal_places=2)
    category: str = Field(min_length=1, max_length=100)
    description: str | None = Field(default=None, max_length=2000)
    expense_date: date

    @field_validator("category")
    @classmethod
    def normalize_category(cls, value: str) -> str:
        return value.strip()

    @field_validator("description")
    @classmethod
    def normalize_description(cls, value: str | None) -> str | None:
        return value.strip() if value else None


class ExpenseUpdate(BaseModel):
    amount: Decimal | None = Field(default=None, gt=0, max_digits=12, decimal_places=2)
    category: str | None = Field(default=None, min_length=1, max_length=100)
    description: str | None = Field(default=None, max_length=2000)
    expense_date: date | None = None

    @field_validator("category")
    @classmethod
    def normalize_category(cls, value: str | None) -> str | None:
        return value.strip() if value else value

    @field_validator("description")
    @classmethod
    def normalize_description(cls, value: str | None) -> str | None:
        return value.strip() if value else value


class ExpenseRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    amount: Decimal
    category: str
    description: str | None
    expense_date: datetime
    created_at: datetime
    updated_at: datetime


class ExpensePage(BaseModel):
    items: list[ExpenseRead]
    total: int
    page: int
    page_size: int


class ExpenseSummary(BaseModel):
    total_amount: Decimal
    count: int
    by_category: dict[str, Decimal]
