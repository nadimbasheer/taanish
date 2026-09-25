from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.sale import Sale, SaleItem
from app.models.product import Product
from app.models.sale_return import SaleReturn
from app.models.inventory import StockMovement
from app.schemas.sale_return import (
    SaleReturnCreate,
    SaleReturnResponse
)
from app.services.dependencies import get_current_user


router = APIRouter(
    prefix="/sales-returns",
    tags=["Sales Returns"]
)


@router.post(
    "/",
    response_model=SaleReturnResponse
)
def create_sale_return(
    return_data: SaleReturnCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    # Check sale
    sale = db.query(Sale).filter(
        Sale.id == return_data.sale_id
    ).first()

    if not sale:
        raise HTTPException(
            status_code=404,
            detail="Sale not found"
        )

    # Check product
    product = db.query(Product).filter(
        Product.id == return_data.product_id
    ).first()

    if not product:
        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )

    # Validate quantity
    if return_data.quantity <= 0:
        raise HTTPException(
            status_code=400,
            detail="Quantity must be greater than 0"
        )

    # Find product in original sale
    sale_item = db.query(SaleItem).filter(
        SaleItem.sale_id == return_data.sale_id,
        SaleItem.product_id == return_data.product_id
    ).first()

    if not sale_item:
        raise HTTPException(
            status_code=400,
            detail="This product was not part of the sale"
        )

    # Check previous returns
    previous_returns = db.query(
        SaleReturn
    ).filter(
        SaleReturn.sale_id == return_data.sale_id,
        SaleReturn.product_id == return_data.product_id
    ).all()

    already_returned = sum(
        item.quantity for item in previous_returns
    )

    remaining_quantity = (
        sale_item.quantity - already_returned
    )

    if return_data.quantity > remaining_quantity:
        raise HTTPException(
            status_code=400,
            detail=f"Only {remaining_quantity} item(s) can be returned"
        )

    # Validate refund amount
    if return_data.refund_amount < 0:
        raise HTTPException(
            status_code=400,
            detail="Refund amount cannot be negative"
        )

    # Add returned product back to stock
    stock_before = product.stock

    product.stock += return_data.quantity

    stock_after = product.stock

    # Record stock movement
    movement = StockMovement(
        product_id=product.id,
        movement_type="IN",
        quantity=return_data.quantity,
        stock_before=stock_before,
        stock_after=stock_after,
        note=f"Sales return for sale #{sale.id}"
    )

    db.add(movement)

    # Record return
    sale_return = SaleReturn(
        sale_id=return_data.sale_id,
        product_id=return_data.product_id,
        quantity=return_data.quantity,
        refund_amount=return_data.refund_amount,
        reason=return_data.reason,
        refund_method=return_data.refund_method
    )

    db.add(sale_return)

    db.commit()
    db.refresh(sale_return)

    return sale_return


@router.get("/")
def get_sale_returns(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    returns = db.query(
        SaleReturn
    ).order_by(
        SaleReturn.id.desc()
    ).all()

    result = []

    for item in returns:

        sale = db.query(Sale).filter(
            Sale.id == item.sale_id
        ).first()

        product = db.query(Product).filter(
            Product.id == item.product_id
        ).first()

        result.append({
            "id": item.id,
            "sale_id": item.sale_id,
            "invoice_number": sale.invoice_number if sale else None,
            "product_id": item.product_id,
            "product_name": product.name if product else None,
            "quantity": item.quantity,
            "refund_amount": item.refund_amount,
            "reason": item.reason,
            "refund_method": item.refund_method,
            "created_at": item.created_at
        })

    return result