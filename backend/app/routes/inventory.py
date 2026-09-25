from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.product import Product
from app.models.inventory import StockMovement
from app.schemas.inventory import StockMovementCreate
from app.services.dependencies import (
    get_current_user,
    require_role
)


router = APIRouter(
    prefix="/inventory",
    tags=["Inventory"]
)


# ============================================================
# CREATE STOCK MOVEMENT
# ============================================================

@router.post("/movement")
def create_stock_movement(
    movement_data: StockMovementCreate,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_role("admin", "manager")
    )
):

    try:

        # ----------------------------------------------------
        # FIND PRODUCT
        # ----------------------------------------------------

        product = (
            db.query(Product)
            .filter(
                Product.id ==
                movement_data.product_id
            )
            .first()
        )


        if not product:

            raise HTTPException(
                status_code=404,
                detail="Product not found"
            )


        # ----------------------------------------------------
        # VALIDATE MOVEMENT TYPE
        # ----------------------------------------------------

        allowed_types = {
            "IN",
            "OUT",
            "ADJUSTMENT"
        }


        if movement_data.movement_type not in allowed_types:

            raise HTTPException(
                status_code=400,
                detail=(
                    "Invalid movement type. "
                    "Use IN, OUT, or ADJUSTMENT."
                )
            )


        # ----------------------------------------------------
        # VALIDATE QUANTITY
        # ----------------------------------------------------

        if movement_data.quantity <= 0:

            raise HTTPException(
                status_code=400,
                detail="Quantity must be greater than 0"
            )


        stock_before = product.stock


        # ----------------------------------------------------
        # STOCK IN
        # ----------------------------------------------------

        if movement_data.movement_type == "IN":

            stock_after = (
                stock_before +
                movement_data.quantity
            )


        # ----------------------------------------------------
        # STOCK OUT
        # ----------------------------------------------------

        elif movement_data.movement_type == "OUT":

            if (
                movement_data.quantity >
                stock_before
            ):

                raise HTTPException(
                    status_code=400,
                    detail=(
                        f"Not enough stock. "
                        f"Available: {stock_before}"
                    )
                )


            stock_after = (
                stock_before -
                movement_data.quantity
            )


        # ----------------------------------------------------
        # STOCK ADJUSTMENT
        # ----------------------------------------------------

        else:

            # For ADJUSTMENT, quantity represents
            # the final physical stock count.

            stock_after = (
                movement_data.quantity
            )


        # ----------------------------------------------------
        # FINAL SAFETY CHECK
        # ----------------------------------------------------

        if stock_after < 0:

            raise HTTPException(
                status_code=400,
                detail="Stock cannot be negative"
            )


        # ----------------------------------------------------
        # UPDATE PRODUCT
        # ----------------------------------------------------

        product.stock = stock_after


        # ----------------------------------------------------
        # CREATE MOVEMENT HISTORY
        # ----------------------------------------------------

        movement = StockMovement(

            product_id=
                product.id,

            movement_type=
                movement_data.movement_type,

            quantity=
                movement_data.quantity,

            stock_before=
                stock_before,

            stock_after=
                stock_after,

            note=
                movement_data.note

        )


        db.add(
            movement
        )


        # ----------------------------------------------------
        # SAVE
        # ----------------------------------------------------

        db.commit()

        db.refresh(
            movement
        )


        # ----------------------------------------------------
        # RESPONSE
        # ----------------------------------------------------

        return {

            "message":
                "Stock movement recorded successfully",

            "product_id":
                product.id,

            "product_name":
                product.name,

            "movement_type":
                movement.movement_type,

            "quantity":
                movement.quantity,

            "stock_before":
                movement.stock_before,

            "stock_after":
                movement.stock_after

        }


    except HTTPException:

        db.rollback()

        raise


    except Exception as error:

        db.rollback()

        print(
            "INVENTORY ERROR:",
            error
        )

        raise HTTPException(
            status_code=500,
            detail="Stock movement could not be completed"
        )


# ============================================================
# GET STOCK MOVEMENTS
# ============================================================

@router.get("/movements")
def get_stock_movements(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    movements = (
        db.query(
            StockMovement
        )
        .order_by(
            StockMovement.id.desc()
        )
        .all()
    )


    return movements