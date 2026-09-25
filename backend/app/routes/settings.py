from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.settings import ShopSettings
from app.schemas.settings import SettingsUpdate, SettingsResponse
from app.services.dependencies import get_current_user


router = APIRouter(
    prefix="/settings",
    tags=["Settings"]
)


@router.get(
    "/",
    response_model=SettingsResponse
)
def get_settings(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    settings = db.query(
        ShopSettings
    ).first()

    if not settings:

        settings = ShopSettings(
            shop_name="Fancy Shop",
            currency="₹"
        )

        db.add(settings)
        db.commit()
        db.refresh(settings)

    return settings


@router.put(
    "/",
    response_model=SettingsResponse
)
def update_settings(
    settings_data: SettingsUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    settings = db.query(
        ShopSettings
    ).first()

    if not settings:

        settings = ShopSettings(
            shop_name=settings_data.shop_name,
            phone=settings_data.phone,
            email=settings_data.email,
            address=settings_data.address,
            currency=settings_data.currency
        )

        db.add(settings)

    else:

        settings.shop_name = settings_data.shop_name
        settings.phone = settings_data.phone
        settings.email = settings_data.email
        settings.address = settings_data.address
        settings.currency = settings_data.currency

    db.commit()
    db.refresh(settings)

    return settings