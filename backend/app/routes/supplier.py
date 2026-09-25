from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.supplier import Supplier
from app.schemas.supplier import SupplierCreate, SupplierResponse
from app.services.dependencies import get_current_user


router = APIRouter(
    prefix="/suppliers",
    tags=["Suppliers"]
)


# CREATE
@router.post("/", response_model=SupplierResponse)
def create_supplier(
    supplier_data: SupplierCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    supplier = Supplier(
        name=supplier_data.name,
        phone=supplier_data.phone,
        email=supplier_data.email,
        address=supplier_data.address,
        notes=supplier_data.notes
    )

    db.add(supplier)
    db.commit()
    db.refresh(supplier)

    return supplier


# GET ALL
@router.get("/", response_model=list[SupplierResponse])
def get_suppliers(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    return db.query(Supplier).order_by(
        Supplier.id.asc()
    ).all()


# GET ONE
@router.get("/{supplier_id}", response_model=SupplierResponse)
def get_supplier(
    supplier_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    supplier = db.query(Supplier).filter(
        Supplier.id == supplier_id
    ).first()

    if not supplier:
        raise HTTPException(
            status_code=404,
            detail="Supplier not found"
        )

    return supplier


# UPDATE
@router.put("/{supplier_id}", response_model=SupplierResponse)
def update_supplier(
    supplier_id: int,
    supplier_data: SupplierCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    supplier = db.query(Supplier).filter(
        Supplier.id == supplier_id
    ).first()

    if not supplier:
        raise HTTPException(
            status_code=404,
            detail="Supplier not found"
        )

    supplier.name = supplier_data.name
    supplier.phone = supplier_data.phone
    supplier.email = supplier_data.email
    supplier.address = supplier_data.address
    supplier.notes = supplier_data.notes

    db.commit()
    db.refresh(supplier)

    return supplier


# DELETE
@router.delete("/{supplier_id}")
def delete_supplier(
    supplier_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    supplier = db.query(Supplier).filter(
        Supplier.id == supplier_id
    ).first()

    if not supplier:
        raise HTTPException(
            status_code=404,
            detail="Supplier not found"
        )

    db.delete(supplier)
    db.commit()

    return {
        "message": "Supplier deleted successfully"
    }