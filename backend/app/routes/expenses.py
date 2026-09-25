from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.expense import Expense
from app.schemas.expense import ExpenseCreate, ExpenseResponse
from app.services.dependencies import get_current_user


router = APIRouter(
    prefix="/expenses",
    tags=["Expenses"]
)


# CREATE
@router.post("/", response_model=ExpenseResponse)
def create_expense(
    expense_data: ExpenseCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    if expense_data.amount <= 0:
        raise HTTPException(
            status_code=400,
            detail="Expense amount must be greater than 0"
        )

    expense = Expense(
        date=expense_data.date,
        category=expense_data.category,
        description=expense_data.description,
        amount=expense_data.amount,
        payment_method=expense_data.payment_method,
        notes=expense_data.notes
    )

    db.add(expense)
    db.commit()
    db.refresh(expense)

    return expense


# GET ALL
@router.get("/", response_model=list[ExpenseResponse])
def get_expenses(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    return db.query(Expense).order_by(
        Expense.id.desc()
    ).all()


# GET ONE
@router.get("/{expense_id}", response_model=ExpenseResponse)
def get_expense(
    expense_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    expense = db.query(Expense).filter(
        Expense.id == expense_id
    ).first()

    if not expense:
        raise HTTPException(
            status_code=404,
            detail="Expense not found"
        )

    return expense


# UPDATE
@router.put("/{expense_id}", response_model=ExpenseResponse)
def update_expense(
    expense_id: int,
    expense_data: ExpenseCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    expense = db.query(Expense).filter(
        Expense.id == expense_id
    ).first()

    if not expense:
        raise HTTPException(
            status_code=404,
            detail="Expense not found"
        )

    if expense_data.amount <= 0:
        raise HTTPException(
            status_code=400,
            detail="Expense amount must be greater than 0"
        )

    expense.date = expense_data.date
    expense.category = expense_data.category
    expense.description = expense_data.description
    expense.amount = expense_data.amount
    expense.payment_method = expense_data.payment_method
    expense.notes = expense_data.notes

    db.commit()
    db.refresh(expense)

    return expense


# DELETE
@router.delete("/{expense_id}")
def delete_expense(
    expense_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    expense = db.query(Expense).filter(
        Expense.id == expense_id
    ).first()

    if not expense:
        raise HTTPException(
            status_code=404,
            detail="Expense not found"
        )

    db.delete(expense)
    db.commit()

    return {
        "message": "Expense deleted successfully"
    }