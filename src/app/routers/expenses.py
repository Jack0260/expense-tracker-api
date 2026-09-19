from datetime import date, datetime, time, timezone
from decimal import Decimal
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ..database import get_db
from ..dependencies import get_current_user
from ..models import Expense, User
from ..schemas import ExpenseCreate, ExpensePage, ExpenseRead, ExpenseSummary, ExpenseUpdate

router = APIRouter(prefix="/expenses", tags=["expenses"])


def _date_time(value: date) -> datetime:
    return datetime.combine(value, time.min, tzinfo=timezone.utc)


def _date_filters(start_date: date | None, end_date: date | None) -> list:
    if start_date and end_date and start_date > end_date:
        raise HTTPException(status_code=400, detail="start_date must be on or before end_date")
    filters = []
    if start_date:
        filters.append(Expense.expense_date >= _date_time(start_date))
    if end_date:
        filters.append(Expense.expense_date < _date_time(end_date.fromordinal(end_date.toordinal() + 1)))
    return filters


def _owned(db: Session, user: User, expense_id: int) -> Expense:
    expense = db.scalar(select(Expense).where(Expense.id == expense_id, Expense.owner_id == user.id))
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")
    return expense


@router.post("", response_model=ExpenseRead, status_code=status.HTTP_201_CREATED)
def create_expense(payload: ExpenseCreate, db: Annotated[Session, Depends(get_db)],
                   user: Annotated[User, Depends(get_current_user)]):
    expense = Expense(owner_id=user.id, amount=payload.amount, category=payload.category,
                      description=payload.description, expense_date=_date_time(payload.expense_date))
    db.add(expense)
    db.commit()
    db.refresh(expense)
    return expense


@router.get("", response_model=ExpensePage)
def list_expenses(db: Annotated[Session, Depends(get_db)], user: Annotated[User, Depends(get_current_user)],
                  page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=100),
                  category: str | None = None, start_date: date | None = None, end_date: date | None = None):
    filters = [Expense.owner_id == user.id]
    if category:
        filters.append(Expense.category == category.strip())
    filters.extend(_date_filters(start_date, end_date))
    total = db.scalar(select(func.count()).select_from(Expense).where(*filters)) or 0
    items = db.scalars(select(Expense).where(*filters).order_by(Expense.expense_date.desc(), Expense.id.desc())
                       .offset((page - 1) * page_size).limit(page_size)).all()
    return ExpensePage(items=items, total=total, page=page, page_size=page_size)


@router.get("/summary", response_model=ExpenseSummary)
def summary(db: Annotated[Session, Depends(get_db)], user: Annotated[User, Depends(get_current_user)],
            start_date: date | None = None, end_date: date | None = None):
    filters = [Expense.owner_id == user.id]
    filters.extend(_date_filters(start_date, end_date))
    total = db.scalar(select(func.coalesce(func.sum(Expense.amount), 0)).where(*filters)) or Decimal("0")
    count = db.scalar(select(func.count()).select_from(Expense).where(*filters)) or 0
    rows = db.execute(select(Expense.category, func.sum(Expense.amount)).where(*filters).group_by(Expense.category)).all()
    return ExpenseSummary(total_amount=total, count=count, by_category={category: amount for category, amount in rows})


@router.get("/{expense_id}", response_model=ExpenseRead)
def get_expense(expense_id: int, db: Annotated[Session, Depends(get_db)],
                user: Annotated[User, Depends(get_current_user)]):
    return _owned(db, user, expense_id)


@router.patch("/{expense_id}", response_model=ExpenseRead)
def update_expense(expense_id: int, payload: ExpenseUpdate, db: Annotated[Session, Depends(get_db)],
                   user: Annotated[User, Depends(get_current_user)]):
    expense = _owned(db, user, expense_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(expense, field, _date_time(value) if field == "expense_date" else value)
    db.commit()
    db.refresh(expense)
    return expense


@router.delete("/{expense_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_expense(expense_id: int, db: Annotated[Session, Depends(get_db)],
                   user: Annotated[User, Depends(get_current_user)]):
    expense = _owned(db, user, expense_id)
    db.delete(expense)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
