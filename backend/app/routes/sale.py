from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.product import Product
from app.models.customer import Customer
from app.models.sale import Sale, SaleItem
from app.models.inventory import StockMovement
from app.schemas.sale import SaleCreate
from app.services.dependencies import get_current_user


router = APIRouter(
    prefix="/sales",
    tags=["Sales"]
)


# ============================================================
# CREATE SALE
# ============================================================

@router.post("/")
def create_sale(
    sale_data: SaleCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    try:

        # ----------------------------------------------------
        # BASIC VALIDATION
        # ----------------------------------------------------

        if not sale_data.items:

            raise HTTPException(
                status_code=400,
                detail="Sale must contain at least one product"
            )


        # ----------------------------------------------------
        # PAYMENT METHOD
        # ----------------------------------------------------

        payment_method = (
            sale_data.payment_method or "Cash"
        ).strip()


        allowed_payment_methods = {
            "Cash",
            "UPI",
            "Card"
        }


        if payment_method not in allowed_payment_methods:

            raise HTTPException(
                status_code=400,
                detail="Invalid payment method. Use Cash, UPI, or Card."
            )


        # ----------------------------------------------------
        # CUSTOMER
        # ----------------------------------------------------

        if sale_data.customer_id is not None:

            customer = (
                db.query(Customer)
                .filter(
                    Customer.id ==
                    sale_data.customer_id
                )
                .first()
            )


            if not customer:

                raise HTTPException(
                    status_code=404,
                    detail="Customer not found"
                )


        # ----------------------------------------------------
        # DISCOUNT / TAX
        # ----------------------------------------------------

        discount = (
            Decimal(str(sale_data.discount or 0))
        )


        tax = (
            Decimal(str(sale_data.tax or 0))
        )


        if discount < 0:

            raise HTTPException(
                status_code=400,
                detail="Discount cannot be negative"
            )


        if tax < 0:

            raise HTTPException(
                status_code=400,
                detail="Tax cannot be negative"
            )


        # ----------------------------------------------------
        # COMBINE DUPLICATE PRODUCTS
        # ----------------------------------------------------

        product_quantities = {}


        for item in sale_data.items:

            if item.quantity <= 0:

                raise HTTPException(
                    status_code=400,
                    detail="Quantity must be greater than 0"
                )


            product_id = item.product_id


            if product_id in product_quantities:

                product_quantities[product_id] += (
                    item.quantity
                )

            else:

                product_quantities[product_id] = (
                    item.quantity
                )


        # ----------------------------------------------------
        # LOAD PRODUCTS
        # ----------------------------------------------------

        product_ids = list(
            product_quantities.keys()
        )


        product_rows = (
            db.query(Product)
            .filter(
                Product.id.in_(product_ids)
            )
            .all()
        )


        products_by_id = {
            product.id: product
            for product in product_rows
        }


        # ----------------------------------------------------
        # CHECK ALL PRODUCTS
        # ----------------------------------------------------

        for product_id in product_ids:

            if product_id not in products_by_id:

                raise HTTPException(
                    status_code=404,
                    detail=f"Product {product_id} not found"
                )


        # ----------------------------------------------------
        # PREPARE SALE ITEMS
        # ----------------------------------------------------

        subtotal = Decimal("0.00")

        prepared_items = []


        for product_id, quantity in product_quantities.items():

            product = products_by_id[
                product_id
            ]


            # ----------------------------------------------
            # STOCK CHECK
            # ----------------------------------------------

            if quantity > product.stock:

                raise HTTPException(
                    status_code=400,
                    detail=(
                        f"Not enough stock for "
                        f"{product.name}. "
                        f"Available: {product.stock}, "
                        f"Requested: {quantity}"
                    )
                )


            # ----------------------------------------------
            # IMPORTANT:
            # USE PRODUCT SELLING PRICE
            # ----------------------------------------------

            price = Decimal(
                str(product.selling or 0)
            )


            if price < 0:

                raise HTTPException(
                    status_code=400,
                    detail=(
                        f"Invalid selling price "
                        f"for {product.name}"
                    )
                )


            item_total = (
                price *
                quantity
            )


            subtotal += item_total


            prepared_items.append({

                "product": product,

                "quantity": quantity,

                "price": price,

                "cost": Decimal(
                    str(product.cost or 0)
                ),

                "total": item_total

            })


        # ----------------------------------------------------
        # DISCOUNT CHECK
        # ----------------------------------------------------

        if discount > subtotal:

            raise HTTPException(
                status_code=400,
                detail=(
                    "Discount cannot be greater "
                    "than subtotal"
                )
            )


        # ----------------------------------------------------
        # FINAL TOTAL
        # ----------------------------------------------------

        total = (
            subtotal -
            discount +
            tax
        )


        if total < 0:

            raise HTTPException(
                status_code=400,
                detail="Total cannot be negative"
            )


        # ----------------------------------------------------
        # ROUND MONEY VALUES
        # ----------------------------------------------------

        subtotal = subtotal.quantize(
            Decimal("0.01")
        )

        discount = discount.quantize(
            Decimal("0.01")
        )

        tax = tax.quantize(
            Decimal("0.01")
        )

        total = total.quantize(
            Decimal("0.01")
        )


        # ----------------------------------------------------
        # CREATE SALE
        # ----------------------------------------------------

        sale = Sale(

            customer_id=
                sale_data.customer_id,

            subtotal=
                subtotal,

            discount=
                discount,

            tax=
                tax,

            total=
                total,

            payment_method=
                payment_method,

            status=
                "Completed",

            invoice_number=
                "TEMP"

        )


        db.add(sale)

        db.flush()


        # ----------------------------------------------------
        # INVOICE NUMBER
        # ----------------------------------------------------

        sale.invoice_number = (
            f"INV-{sale.id:05d}"
        )


        # ----------------------------------------------------
        # REDUCE STOCK
        # CREATE SALE ITEMS
        # CREATE STOCK MOVEMENTS
        # ----------------------------------------------------

        for item in prepared_items:

            product = item["product"]

            quantity = item["quantity"]

            stock_before = product.stock

            stock_after = (
                stock_before -
                quantity
            )


            # ----------------------------------------------
            # FINAL STOCK SAFETY CHECK
            # ----------------------------------------------

            if stock_after < 0:

                raise HTTPException(
                    status_code=400,
                    detail=(
                        f"Stock cannot become negative "
                        f"for {product.name}"
                    )
                )


            product.stock = stock_after


            # ----------------------------------------------
            # SALE ITEM
            # ----------------------------------------------

            sale_item = SaleItem(

                sale_id=
                    sale.id,

                product_id=
                    product.id,

                quantity=
                    quantity,

                price=
                    item["price"],

                cost=
                    item["cost"],

                total=
                    item["total"]

            )


            db.add(
                sale_item
            )


            # ----------------------------------------------
            # STOCK MOVEMENT
            # ----------------------------------------------

            movement = StockMovement(

                product_id=
                    product.id,

                movement_type=
                    "OUT",

                quantity=
                    quantity,

                stock_before=
                    stock_before,

                stock_after=
                    stock_after,

                note=
                    f"Sale {sale.invoice_number}"

            )


            db.add(
                movement
            )


        # ----------------------------------------------------
        # SAVE EVERYTHING
        # ----------------------------------------------------

        db.commit()

        db.refresh(sale)


        # ----------------------------------------------------
        # RESPONSE
        # ----------------------------------------------------

        return {

            "message":
                "Sale completed successfully",

            "id":
                sale.id,

            "sale_id":
                sale.id,

            "invoice_number":
                sale.invoice_number,

            "subtotal":
                sale.subtotal,

            "discount":
                sale.discount,

            "tax":
                sale.tax,

            "total":
                sale.total,

            "payment_method":
                sale.payment_method,

            "status":
                sale.status

        }


    except HTTPException:

        db.rollback()

        raise


    except Exception as error:

        db.rollback()

        print(
            "SALE ERROR:",
            error
        )

        raise HTTPException(
            status_code=500,
            detail="Sale could not be completed"
        )


# ============================================================
# GET ALL SALES
# ============================================================

@router.get("/")
def get_sales(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    return (
        db.query(Sale)
        .order_by(
            Sale.id.desc()
        )
        .all()
    )


# ============================================================
# GET SINGLE SALE
# ============================================================

@router.get("/{sale_id}")
def get_sale(
    sale_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    sale = (
        db.query(Sale)
        .filter(
            Sale.id == sale_id
        )
        .first()
    )


    if not sale:

        raise HTTPException(
            status_code=404,
            detail="Sale not found"
        )


    items = (
        db.query(SaleItem)
        .filter(
            SaleItem.sale_id ==
            sale.id
        )
        .all()
    )


    return {

        "id":
            sale.id,

        "invoice_number":
            sale.invoice_number,

        "customer_id":
            sale.customer_id,

        "subtotal":
            sale.subtotal,

        "discount":
            sale.discount,

        "tax":
            sale.tax,

        "total":
            sale.total,

        "payment_method":
            sale.payment_method,

        "status":
            sale.status,

        "created_at":
            sale.created_at,

        "items":
            items

    }