from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from config import DATABASE_URL

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


class Base(DeclarativeBase):
    pass


def init_db():
    from models import Base as ModelsBase
    ModelsBase.metadata.create_all(bind=engine)
    seed_initial_data()


def seed_initial_data():
    from models import Setting
    from sqlalchemy import inspect

    inspector = inspect(engine)
    if not inspector.has_table("settings"):
        return

    # Migrate: add image column to products if missing
    if inspector.has_table("products"):
        cols = [c["name"] for c in inspector.get_columns("products")]
        if "image" not in cols:
            from sqlalchemy import text
            with engine.connect() as conn:
                conn.execute(text("ALTER TABLE products ADD COLUMN image VARCHAR(500) DEFAULT ''"))
                conn.commit()

    # Migrate: add customer_address column if missing
    if inspector.has_table("invoices"):
        cols = [c["name"] for c in inspector.get_columns("invoices")]
        if "customer_address" not in cols:
            from sqlalchemy import text
            with engine.connect() as conn:
                conn.execute(text("ALTER TABLE invoices ADD COLUMN customer_address TEXT DEFAULT ''"))
                conn.commit()

    db = SessionLocal()
    try:
        if db.query(Setting).count() == 0:
            defaults = [
                Setting(key="store_name", value="Uhtred Store", type="text"),
                Setting(key="store_phone", value="", type="text"),
                Setting(key="store_address", value="", type="text"),
                Setting(key="store_note", value="شكراً لتسوقك من Uhtred Store", type="text"),
                Setting(key="tax_rate", value="0", type="number"),
            ]
            db.add_all(defaults)
            db.commit()
    finally:
        db.close()


def get_db():
    db = SessionLocal()
    try:
        return db
    finally:
        db.close()
