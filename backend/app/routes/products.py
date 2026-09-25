from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.product import Product
from app.schemas.product import ProductCreate, ProductResponse
from app.services.dependencies import require_role

router = APIRouter(
    prefix="/products",
    tags=["Products"]
)


# =========================================================
# GET ALL PRODUCTS
# Admin + Cashier can view products
# =========================================================

@router.get("/", response_model=list[ProductResponse])
def get_products(
    db: Session = Depends(get_db),
    current_user=Depends(require_role("admin", "cashier"))
):
    return db.query(Product).order_by(Product.id.desc()).all()


# =========================================================
# GET SINGLE PRODUCT
# Admin + Cashier can view product
# =========================================================

@router.get("/{product_id}", response_model=ProductResponse)
def get_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_role("admin", "cashier"))
):
    product = db.query(Product).filter(
        Product.id == product_id
    ).first()

    if not product:
        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )

    return product


# =========================================================
# CREATE PRODUCT
# ADMIN ONLY
# =========================================================

@router.post("/", response_model=ProductResponse)
def create_product(
    product_data: ProductCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_role("admin"))
):

    if product_data.cost < 0:
        raise HTTPException(
            status_code=400,
            detail="Cost cannot be negative"
        )

    if product_data.mrp < 0:
        raise HTTPException(
            status_code=400,
            detail="MRP cannot be negative"
        )

    if product_data.selling < 0:
        raise HTTPException(
            status_code=400,
            detail="Selling price cannot be negative"
        )

    if product_data.stock < 0:
        raise HTTPException(
            status_code=400,
            detail="Stock cannot be negative"
        )

    if product_data.min_stock < 0:
        raise HTTPException(
            status_code=400,
            detail="Minimum stock cannot be negative"
        )

    if product_data.sku:

        existing_sku = db.query(Product).filter(
            Product.sku == product_data.sku
        ).first()

        if existing_sku:
            raise HTTPException(
                status_code=400,
                detail="SKU already exists"
            )

    if product_data.barcode:

        existing_barcode = db.query(Product).filter(
            Product.barcode == product_data.barcode
        ).first()

        if existing_barcode:
            raise HTTPException(
                status_code=400,
                detail="Barcode already exists"
            )

    product = Product(
        name=product_data.name,
        category=product_data.category,
        sku=product_data.sku,
        barcode=product_data.barcode,
        cost=product_data.cost,
        mrp=product_data.mrp,
        selling=product_data.selling,
        stock=product_data.stock,
        min_stock=product_data.min_stock
    )

    db.add(product)
    db.commit()
    db.refresh(product)

    return product


# =========================================================
# UPDATE PRODUCT
# ADMIN ONLY
# =========================================================

@router.put("/{product_id}", response_model=ProductResponse)
def update_product(
    product_id: int,
    product_data: ProductCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_role("admin"))
):

    product = db.query(Product).filter(
        Product.id == product_id
    ).first()

    if not product:
        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )

    if product_data.cost < 0:
        raise HTTPException(
            status_code=400,
            detail="Cost cannot be negative"
        )

    if product_data.mrp < 0:
        raise HTTPException(
            status_code=400,
            detail="MRP cannot be negative"
        )

    if product_data.selling < 0:
        raise HTTPException(
            status_code=400,
            detail="Selling price cannot be negative"
        )

    if product_data.stock < 0:
        raise HTTPException(
            status_code=400,
            detail="Stock cannot be negative"
        )

    if product_data.min_stock < 0:
        raise HTTPException(
            status_code=400,
            detail="Minimum stock cannot be negative"
        )

    if product_data.sku:

        existing_sku = db.query(Product).filter(
            Product.sku == product_data.sku,
            Product.id != product_id
        ).first()

        if existing_sku:
            raise HTTPException(
                status_code=400,
                detail="SKU already exists"
            )

    if product_data.barcode:

        existing_barcode = db.query(Product).filter(
            Product.barcode == product_data.barcode,
            Product.id != product_id
        ).first()

        if existing_barcode:
            raise HTTPException(
                status_code=400,
                detail="Barcode already exists"
            )

    product.name = product_data.name
    product.category = product_data.category
    product.sku = product_data.sku
    product.barcode = product_data.barcode
    product.cost = product_data.cost
    product.mrp = product_data.mrp
    product.selling = product_data.selling
    product.stock = product_data.stock
    product.min_stock = product_data.min_stock

    db.commit()
    db.refresh(product)

    return product


# =========================================================
# DELETE PRODUCT
# ADMIN ONLY
# =========================================================

@router.delete("/{product_id}")
def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_role("admin"))
):

    product = db.query(Product).filter(
        Product.id == product_id
    ).first()

    if not product:
        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )

    db.delete(product)
    db.commit()

    return {
        "message": "Product deleted successfully"
    }