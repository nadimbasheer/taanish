from logging.config import fileConfig

from alembic import context

from app.database import Base, engine

# Import all models so Alembic can see every table.
from app.models.product import Product
from app.models.inventory import StockMovement
from app.models.supplier import Supplier
from app.models.purchase import Purchase
from app.models.customer import Customer
from app.models.sale import Sale, SaleItem
from app.models.expense import Expense
from app.models.settings import ShopSettings
from app.models.user import User
from app.models.sale_return import SaleReturn


# Alembic Config object
config = context.config


# Configure Python logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)


# SQLAlchemy metadata
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations in offline mode."""

    url = config.get_main_option("sqlalchemy.url")

    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={
            "paramstyle": "named"
        },
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in online mode."""

    with engine.connect() as connection:

        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()