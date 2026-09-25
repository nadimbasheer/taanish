from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import get_db
from app.models.sale import Sale, SaleItem
from app.models.purchase import Purchase
from app.models.product import Product
from app.models.expense import Expense
from app.services.dependencies import get_current_user


router = APIRouter(
    prefix="/reports",
    tags=["Reports"]
)


@router.get("/summary")
def get_report_summary(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    total_sales = db.query(
        func.coalesce(func.sum(Sale.total), 0)
    ).scalar()

    total_purchases = db.query(
        func.coalesce(func.sum(Purchase.total), 0)
    ).scalar()

    total_products = db.query(
        func.count(Product.id)
    ).scalar()

    total_stock = db.query(
        func.coalesce(func.sum(Product.stock), 0)
    ).scalar()

    gross_profit = db.query(
        func.coalesce(
            func.sum(
                (SaleItem.price - SaleItem.cost)
                * SaleItem.quantity
            ),
            0
        )
    ).scalar()

    total_expenses = db.query(
        func.coalesce(func.sum(Expense.amount), 0)
    ).scalar()

    net_profit = gross_profit - total_expenses

    return {
        "total_sales": total_sales,
        "total_purchases": total_purchases,
        "total_products": total_products,
        "total_stock_units": total_stock,
        "gross_profit": gross_profit,
        "total_expenses": total_expenses,
        "net_profit": net_profit
    }