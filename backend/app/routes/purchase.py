from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.product import Product
from app.models.supplier import Supplier
from app.models.purchase import Purchase
from app.models.inventory import StockMovement
from app.schemas.purchase import PurchaseCreate
from app.services.dependencies import get_current_user


router = APIRouter(
    prefix="/purchases",
    tags=["Purchases"]
)


@router.post("/")
def create_purchase(
    purchase_data: PurchaseCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    # Find product
    product = db.query(Product).filter(
        Product.id == purchase_data.product_id
    ).first()

    if not product:
        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )

    # Check supplier if provided
    if purchase_data.supplier_id:

        supplier = db.query(Supplier).filter(
            Supplier.id == purchase_data.supplier_id
        ).first()

        if not supplier:
            raise HTTPException(
                status_code=404,
                detail="Supplier not found"
            )

    # Validate quantity
    if purchase_data.quantity <= 0:
        raise HTTPException(
            status_code=400,
            detail="Quantity must be greater than 0"
        )

    # Validate cost
    if purchase_data.cost_price < 0:
        raise HTTPException(
            status_code=400,
            detail="Cost price cannot be negative"
        )

    # Stock before purchase
    stock_before = product.stock

    # Add purchased quantity
    stock_after = (
        stock_before +
        purchase_data.quantity
    )

    # Calculate total
    total = (
        purchase_data.cost_price *
        purchase_data.quantity
    )

    # Update product stock
    product.stock = stock_after

    # Update product cost
    product.cost = purchase_data.cost_price

    # Create purchase record
    purchase = Purchase(
        product_id=purchase_data.product_id,
        supplier_id=purchase_data.supplier_id,
        quantity=purchase_data.quantity,
        cost_price=purchase_data.cost_price,
        total=total,
        invoice_number=purchase_data.invoice_number,
        note=purchase_data.note
    )

    db.add(purchase)

    # Create inventory movement
    movement = StockMovement(
        product_id=product.id,
        movement_type="IN",
        quantity=purchase_data.quantity,
        stock_before=stock_before,
        stock_after=stock_after,
        note="Purchase received"
    )

    db.add(movement)

    db.commit()

    db.refresh(purchase)

    return {
        "message": "Purchase recorded successfully",

        "purchase_id": purchase.id,

        "product_id": product.id,

        "product_name": product.name,

        "quantity": purchase.quantity,

        "cost_price": purchase.cost_price,

        "total": purchase.total,

        "stock_before": stock_before,

        "stock_after": stock_after
    }


@router.get("/")
def get_purchases(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    return db.query(
        Purchase
    ).order_by(
        Purchase.id.desc()
    ).all()


@router.get("/{purchase_id}")
def get_purchase(
    purchase_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    purchase = db.query(Purchase).filter(
        Purchase.id == purchase_id
    ).first()

    if not purchase:
        raise HTTPException(
            status_code=404,
            detail="Purchase not found"
        )

    return purchase