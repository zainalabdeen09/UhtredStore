from datetime import datetime, date


def generate_invoice_number(db=None) -> str:
    from models import Setting
    if db is None:
        return f"INV-{datetime.now().strftime('%Y%m%d-%H%M%S')}"

    setting = db.query(Setting).filter(Setting.key == "invoice_counter").first()
    if setting is None:
        counter = 1
        db.add(Setting(key="invoice_counter", value=str(counter), type="number"))
    else:
        counter = int(setting.value) + 1
        setting.value = str(counter)
    db.commit()
    return f"INV-{counter:05d}"


def format_currency(amount: float) -> str:
    return f"{amount:,.0f} د.ع"


def get_setting(db, key: str, default=""):
    from models import Setting
    setting = db.query(Setting).filter(Setting.key == key).first()
    if setting:
        return setting.value
    return default


def save_setting(db, key: str, value: str, type_: str = "text"):
    from models import Setting
    setting = db.query(Setting).filter(Setting.key == key).first()
    if setting:
        setting.value = value
    else:
        db.add(Setting(key=key, value=value, type=type_))
    db.commit()
