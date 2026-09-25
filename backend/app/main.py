import os

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.database import engine

# Models
from app.models.user import User
from app.models.product import Product
from app.models.inventory import StockMovement
from app.models.supplier import Supplier
from app.models.purchase import Purchase
from app.models.customer import Customer
from app.models.sale import Sale, SaleItem
from app.models.sale_return import SaleReturn
from app.models.expense import Expense
from app.models.settings import ShopSettings

# Routes
from app.routes.products import router as products_router
from app.routes.inventory import router as inventory_router
from app.routes.supplier import router as supplier_router
from app.routes.purchase import router as purchase_router
from app.routes.customer import router as customer_router
from app.routes.sale import router as sale_router
from app.routes.reports import router as reports_router
from app.routes.expenses import router as expenses_router
from app.routes.dashboard import router as dashboard_router
from app.routes.settings import router as settings_router
from app.routes.users import router as users_router
from app.routes.auth import router as auth_router
from app.routes.sale_return import router as sale_return_router


# Load environment variables
load_dotenv()

FRONTEND_URL = os.getenv(
    "FRONTEND_URL",
    "http://127.0.0.1:5500"
)


# Create FastAPI application
app = FastAPI(
    title="TAANISH Fancy Shop Management System",
    version="1.0.0"
)


# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Register routes
app.include_router(products_router)
app.include_router(inventory_router)
app.include_router(supplier_router)
app.include_router(purchase_router)
app.include_router(customer_router)
app.include_router(sale_router)
app.include_router(reports_router)
app.include_router(expenses_router)
app.include_router(dashboard_router)
app.include_router(settings_router)
app.include_router(users_router)
app.include_router(auth_router)
app.include_router(sale_return_router)


# Home
@app.get("/")
def home():
    return {
        "message": "TAANISH Backend is running!"
    }


# Health check
@app.get("/health")
def health():
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))

        return {
            "status": "ok",
            "database": "connected"
        }

    except Exception as error:
        return {
            "status": "error",
            "database": "not connected",
            "message": str(error)
        }