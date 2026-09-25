from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import get_db
from app.models.product import Product
from app.models.sale import Sale
from app.models.purchase import Purchase
from app.models.expense import Expense
from app.models.user import User
from app.services.dependencies import get_current_user


router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"]
)


@router.get("/summary")
def get_dashboard_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    total_products = db.query(
        func.count(Product.id)
    ).scalar()

    total_stock = db.query(
        func.coalesce(
            func.sum(Product.stock),
            0
        )
    ).scalar()

    total_sales = db.query(
        func.coalesce(
            func.sum(Sale.total),
            0
        )
    ).scalar()

    total_purchases = db.query(
        func.coalesce(
            func.sum(Purchase.total),
            0
        )
    ).scalar()

    total_expenses = db.query(
        func.coalesce(
            func.sum(Expense.amount),
            0
        )
    ).scalar()

    return {
        "total_products": total_products,
        "total_stock_units": total_stock,
        "total_sales": total_sales,
        "total_purchases": total_purchases,
        "total_expenses": total_expenses
    }