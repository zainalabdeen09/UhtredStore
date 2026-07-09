import json
import shutil
from datetime import date, datetime
from pathlib import Path
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    CommandHandler, CallbackQueryHandler, MessageHandler,
    ConversationHandler, filters, ContextTypes
)
from database import SessionLocal
from models import Product, Category, Invoice, InvoiceItem, Customer, StockMovement, Setting
from config import PRODUCT_IMAGES_DIR
from utils.helpers import generate_invoice_number

PER_PAGE = 8

# Conversation states
(PROD_NAME, PROD_CATEGORY, PROD_BUY, PROD_SELL, PROD_STOCK,
 PROD_MIN, PROD_IMAGE, PROD_SIZES, PROD_COLORS, PROD_PRINTS,
 PROD_NOTES, PROD_CONFIRM) = range(12)

(CUST_NAME, CUST_PHONE, CUST_ADDR) = range(12, 15)

(EDIT_FIELD, EDIT_VALUE) = range(15, 17)

(POS_QTY) = range(17, 18)


def get_db():
    return SessionLocal()


def escape_md(text):
    return str(text).replace("-", "\\-").replace(".", "\\.").replace("(", "\\(").replace(")", "\\)")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    from bot.keyboards import main_menu
    await update.message.reply_text(
        "🏪 *Uhtred Store* \\- نظام إدارة المبيعات\n"
        "اختر من القائمة أدناه:",
        reply_markup=main_menu()
    )


async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data.clear()
    from bot.keyboards import main_menu
    await query.edit_message_text(
        "🏪 *Uhtred Store* \\- نظام إدارة المبيعات\nاختر من القائمة:",
        reply_markup=main_menu()
    )


async def noop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()


# ─────────────────────── POS ───────────────────────

async def pos_categories(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    db = get_db()
    cats = db.query(Category).all()
    db.close()
    from bot.keyboards import categories_keyboard
    await query.edit_message_text("اختر الصنف:", reply_markup=categories_keyboard(cats))


async def pos_products(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    if data.startswith("cat_"):
        cat_id = int(data.split("_")[1])
        context.user_data["pos_cat"] = cat_id
        context.user_data["pos_page"] = 0
    page = context.user_data.get("pos_page", 0)

    db = get_db()
    q = db.query(Product).filter(Product.current_stock > 0)
    cat_id = context.user_data.get("pos_cat")
    if cat_id and cat_id != "all":
        q = q.filter(Product.category_id == cat_id)
    products = q.all()
    db.close()

    total_pages = max(1, (len(products) + PER_PAGE - 1) // PER_PAGE)
    page = min(page, total_pages - 1)
    context.user_data["pos_page"] = page
    start = page * PER_PAGE
    page_products = products[start:start + PER_PAGE]

    from bot.keyboards import products_keyboard
    await query.edit_message_text(f"اختر المنتج (صفحة {page+1}/{total_pages}):", reply_markup=products_keyboard(page_products, page, total_pages))


async def pos_product_select(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    pid = int(query.data.split("_")[1])
    context.user_data["pos_pid"] = pid

    db = get_db()
    p = db.query(Product).filter(Product.id == pid).first()
    db.close()

    if not p:
        await query.edit_message_text("المنتج غير موجود.")
        return

    text = (
        f"*{p.name}*\n"
        f"السعر: {p.sell_price:,.0f} د.ع\n"
        f"المخزون: {p.current_stock}\n"
    )

    # Show available options
    sizes = json.loads(p.sizes) if p.sizes else []
    colors = json.loads(p.colors) if p.colors else []
    prints = json.loads(p.print_locations) if p.print_locations else []
    if sizes:
        text += f"المقاسات: {', '.join(sizes)}\n"
    if colors:
        text += f"الألوان: {', '.join(colors)}\n"
    if prints:
        text += f"الطباعة: {', '.join(prints)}\n"

    context.user_data["pos_qty"] = 1

    from bot.keyboards import qty_keyboard
    img_path = PRODUCT_IMAGES_DIR / p.image if p.image else None
    if img_path and img_path.exists():
        with open(img_path, "rb") as f:
            await query.message.delete()
            msg = await context.bot.send_photo(
                chat_id=query.message.chat_id,
                photo=f,
                caption=text + f"\nالكمية: 1",
                reply_markup=qty_keyboard(pid)
            )
            context.user_data["pos_msg_id"] = msg.message_id
    else:
        await query.edit_message_text(
            text + f"\nالكمية: 1",
            reply_markup=qty_keyboard(pid)
        )


async def pos_qty_change(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    parts = query.data.split("_")
    pid = int(parts[2])
    qty = context.user_data.get("pos_qty", 1)
    if parts[1] == "up":
        qty += 1
    else:
        qty = max(1, qty - 1)
    context.user_data["pos_qty"] = qty

    db = get_db()
    p = db.query(Product).filter(Product.id == pid).first()
    db.close()
    qty = min(qty, p.current_stock)

    text = (
        f"*{p.name}*\n"
        f"السعر: {p.sell_price:,.0f} د.ع\n"
        f"المخزون: {p.current_stock}\n"
        f"الكمية: {qty}"
    )

    from bot.keyboards import qty_keyboard
    try:
        await query.edit_message_caption(caption=text, reply_markup=qty_keyboard(pid))
    except Exception:
        await query.edit_message_text(text, reply_markup=qty_keyboard(pid))


async def pos_add_to_cart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    pid = int(query.data.split("_")[1])
    qty = context.user_data.get("pos_qty", 1)

    db = get_db()
    p = db.query(Product).filter(Product.id == pid).first()
    db.close()

    if not p or qty > p.current_stock:
        await query.edit_message_text("الكمية غير متوفرة!")
        return

    cart = context.user_data.setdefault("cart", [])
    # Check if product already in cart
    for item in cart:
        if item["pid"] == pid:
            item["qty"] += qty
            item["total"] = item["qty"] * p.sell_price
            break
    else:
        cart.append({
            "pid": pid,
            "name": p.name,
            "price": p.sell_price,
            "qty": qty,
            "total": p.sell_price * qty,
        })

    from bot.keyboards import cart_keyboard
    await query.edit_message_text(f"✅ تمت إضافة {p.name} × {qty} للسلة!", reply_markup=cart_keyboard(cart))


async def pos_view_cart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    cart = context.user_data.get("cart", [])
    from bot.keyboards import cart_keyboard
    if not cart:
        await query.edit_message_text("السلة فارغة!", reply_markup=cart_keyboard(cart))
        return

    total = sum(item["total"] for item in cart)
    text = "🛒 *الفاتورة الحالية*\n\n"
    for i, item in enumerate(cart):
        text += f"{i+1}\\. {item['name']} × {item['qty']} = {item['total']:,.0f} د.ع\n"
    text += f"\n*الإجمالي: {total:,.0f} د.ع*"
    await query.edit_message_text(text, reply_markup=cart_keyboard(cart))


async def pos_remove_item(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    idx = int(query.data.split("_")[1])
    cart = context.user_data.get("cart", [])
    if 0 <= idx < len(cart):
        cart.pop(idx)
    await pos_view_cart(update, context)


async def pos_checkout(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    cart = context.user_data.get("cart", [])
    if not cart:
        await pos_view_cart(update, context)
        return

    total = sum(item["total"] for item in cart)
    text = "🧾 *تأكيد الفاتورة*\n\n"
    for item in cart:
        text += f"• {item['name']} × {item['qty']} = {item['total']:,.0f} د.ع\n"
    text += f"\n*الإجمالي: {total:,.0f} د.ع*"
    text += "\n\nالرجاء إرسال اسم العميل (أو أكتب /skip للتخطي):"

    context.user_data["checkout_step"] = "customer_name"
    from bot.keyboards import confirm_invoice_keyboard
    await query.edit_message_text(text, reply_markup=confirm_invoice_keyboard())


async def pos_confirm_invoice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    cart = context.user_data.get("cart", [])
    customer_name = context.user_data.get("customer_name", "نقدي")
    if not cart:
        return

    db = get_db()
    total = sum(item["total"] for item in cart)

    invoice = Invoice(
        invoice_number=generate_invoice_number(db),
        customer_name=customer_name,
        total=total,
        grand_total=total,
        invoice_date=date.today(),
    )
    db.add(invoice)
    db.flush()

    for item in cart:
        ii = InvoiceItem(
            invoice_id=invoice.id,
            product_id=item["pid"],
            product_name=item["name"],
            quantity=item["qty"],
            price=item["price"],
            total=item["total"],
        )
        db.add(ii)
        prod = db.query(Product).filter(Product.id == item["pid"]).first()
        if prod:
            prod.current_stock -= item["qty"]
            db.add(StockMovement(
                product_id=prod.id,
                type="out",
                quantity=-item["qty"],
                reference=invoice.invoice_number,
            ))

    db.commit()
    db.close()

    context.user_data.pop("cart", None)
    context.user_data.pop("customer_name", None)
    context.user_data.pop("checkout_step", None)

    from bot.keyboards import back_to_menu
    text = (
        f"✅ *تم حفظ الفاتورة!*\n\n"
        f"رقم: #{invoice.invoice_number}\n"
        f"العميل: {customer_name}\n"
        f"الإجمالي: {total:,.0f} د.ع"
    )
    await query.edit_message_text(text, reply_markup=back_to_menu())


async def pos_cancel_invoice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data.pop("cart", None)
    context.user_data.pop("customer_name", None)
    from bot.keyboards import main_menu
    await query.edit_message_text("❌ تم إلغاء الفاتورة", reply_markup=main_menu())


# ─────────────────────── PRODUCTS ───────────────────────

async def products_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    page = 0
    if data.startswith("prods_"):
        page = int(data.split("_")[1])

    db = get_db()
    products = db.query(Product).order_by(Product.id).all()
    db.close()

    total_pages = max(1, (len(products) + PER_PAGE - 1) // PER_PAGE)
    page = min(page, total_pages - 1)
    start = page * PER_PAGE
    page_products = products[start:start + PER_PAGE]

    from bot.keyboards import products_list_keyboard
    await query.edit_message_text(
        f"📦 *المنتجات* (صفحة {page+1}/{total_pages})",
        reply_markup=products_list_keyboard(page_products, page, total_pages)
    )


async def product_view(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    pid = int(query.data.split("_")[1])

    db = get_db()
    p = db.query(Product).filter(Product.id == pid).first()
    db.close()

    if not p:
        await query.edit_message_text("المنتج غير موجود.")
        return

    sizes = ", ".join(json.loads(p.sizes)) if p.sizes else "-"
    colors = ", ".join(json.loads(p.colors)) if p.colors else "-"
    prints = ", ".join(json.loads(p.print_locations)) if p.print_locations else "-"
    cat_name = p.category.name if p.category else "-"

    text = (
        f"*{p.name}*\n"
        f"الصنف: {cat_name}\n"
        f"سعر الشراء: {p.buy_price:,.0f} د.ع\n"
        f"سعر البيع: {p.sell_price:,.0f} د.ع\n"
        f"المخزون: {p.current_stock}\n"
        f"الحد الأدنى: {p.min_stock}\n"
        f"المقاسات: {sizes}\n"
        f"الألوان: {colors}\n"
        f"الطباعة: {prints}\n"
        f"ملاحظات: {p.notes or '-'}"
    )

    from bot.keyboards import product_view_keyboard
    img_path = PRODUCT_IMAGES_DIR / p.image if p.image else None
    if img_path and img_path.exists():
        with open(img_path, "rb") as f:
            await query.message.delete()
            await context.bot.send_photo(
                chat_id=query.message.chat_id,
                photo=f,
                caption=text,
                reply_markup=product_view_keyboard(pid)
            )
    else:
        await query.edit_message_text(text, reply_markup=product_view_keyboard(pid))


async def product_delete(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    pid = int(query.data.split("_")[1])

    db = get_db()
    p = db.query(Product).filter(Product.id == pid).first()
    if p:
        db.delete(p)
        db.commit()
    db.close()

    from bot.keyboards import back_to_menu
    await query.edit_message_text("✅ تم حذف المنتج", reply_markup=back_to_menu())


# ─── Add Product (Conversation) ───

async def prod_add_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data["new_prod"] = {}
    from bot.keyboards import add_prod_cancel
    await query.edit_message_text("أرسل اسم المنتج:", reply_markup=add_prod_cancel())
    return PROD_NAME


async def prod_add_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["new_prod"]["name"] = update.message.text
    db = get_db()
    cats = db.query(Category).all()
    db.close()
    from bot.keyboards import add_prod_cancel
    kb = [[InlineKeyboardButton(c.name, callback_data=f"pcat_{c.id}")] for c in cats]
    kb.append([InlineKeyboardButton("⏭️ بدون صنف", callback_data="pcat_none")])
    kb.append([InlineKeyboardButton("❌ إلغاء", callback_data="cancel")])
    await update.message.reply_text("اختر الصنف:", reply_markup=InlineKeyboardMarkup(kb))
    return PROD_CATEGORY


async def prod_add_category(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    if data.startswith("pcat_"):
        val = data.split("_")[1]
        context.user_data["new_prod"]["cat_id"] = None if val == "none" else int(val)
    from bot.keyboards import add_prod_cancel
    await query.edit_message_text("أرسل سعر الشراء:", reply_markup=add_prod_cancel())
    return PROD_BUY


async def prod_add_buy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        val = float(update.message.text)
    except ValueError:
        await update.message.reply_text("الرجاء إرسال رقم صحيح:")
        return PROD_BUY
    context.user_data["new_prod"]["buy_price"] = val
    from bot.keyboards import add_prod_cancel
    await update.message.reply_text("أرسل سعر البيع:", reply_markup=add_prod_cancel())
    return PROD_SELL


async def prod_add_sell(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        val = float(update.message.text)
    except ValueError:
        await update.message.reply_text("الرجاء إرسال رقم صحيح:")
        return PROD_SELL
    context.user_data["new_prod"]["sell_price"] = val
    from bot.keyboards import add_prod_cancel
    await update.message.reply_text("أرسل الكمية (المخزون الحالي):", reply_markup=add_prod_cancel())
    return PROD_STOCK


async def prod_add_stock(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        val = int(update.message.text)
    except ValueError:
        await update.message.reply_text("الرجاء إرسال رقم صحيح:")
        return PROD_STOCK
    context.user_data["new_prod"]["stock"] = val
    from bot.keyboards import add_prod_cancel
    await update.message.reply_text("أرسل الحد الأدنى للمخزون:", reply_markup=add_prod_cancel())
    return PROD_MIN


async def prod_add_min(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        val = int(update.message.text)
    except ValueError:
        await update.message.reply_text("الرجاء إرسال رقم صحيح:")
        return PROD_MIN
    context.user_data["new_prod"]["min_stock"] = val
    from bot.keyboards import skip_btn
    await update.message.reply_text(
        "أرسل صورة المنتج (أو اختر تخطي):",
        reply_markup=skip_btn("skip_image")
    )
    return PROD_IMAGE


async def prod_add_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Handle photo
    if update.message and update.message.photo:
        photo = update.message.photo[-1]
        file = await photo.get_file()
        ext = ".jpg"
        fname = f"prod_{datetime.now().strftime('%Y%m%d%H%M%S%f')}{ext}"
        fpath = PRODUCT_IMAGES_DIR / fname
        await file.download_to_drive(fpath)
        context.user_data["new_prod"]["image"] = fname
    else:
        context.user_data["new_prod"]["image"] = ""

    from bot.keyboards import skip_btn
    await update.message.reply_text(
        "أرسل المقاسات (مفصولة بفاصلة، مثال: S, M, L, XL) أو اختر تخطي:",
        reply_markup=skip_btn("skip_sizes")
    )
    return PROD_SIZES


async def prod_add_image_skip(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data["new_prod"]["image"] = ""
    from bot.keyboards import skip_btn
    await query.edit_message_text(
        "أرسل المقاسات (مفصولة بفاصلة) أو اختر تخطي:",
        reply_markup=skip_btn("skip_sizes")
    )
    return PROD_SIZES


async def prod_add_sizes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip() if update.message else ""
    context.user_data["new_prod"]["sizes"] = json.dumps([s.strip() for s in text.split(",") if s.strip()])
    from bot.keyboards import skip_btn
    await update.message.reply_text(
        "أرسل الألوان (مفصولة بفاصلة) أو اختر تخطي:",
        reply_markup=skip_btn("skip_colors")
    )
    return PROD_COLORS


async def prod_add_sizes_skip(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data["new_prod"]["sizes"] = "[]"
    from bot.keyboards import skip_btn
    await query.edit_message_text(
        "أرسل الألوان (مفصولة بفاصلة) أو اختر تخطي:",
        reply_markup=skip_btn("skip_colors")
    )
    return PROD_COLORS


async def prod_add_colors(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip() if update.message else ""
    context.user_data["new_prod"]["colors"] = json.dumps([c.strip() for c in text.split(",") if c.strip()])
    from bot.keyboards import skip_btn
    await update.message.reply_text(
        "أرسل أماكن الطباعة (مفصولة بفاصلة) أو اختر تخطي:",
        reply_markup=skip_btn("skip_prints")
    )
    return PROD_PRINTS


async def prod_add_colors_skip(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data["new_prod"]["colors"] = "[]"
    from bot.keyboards import skip_btn
    await query.edit_message_text(
        "أرسل أماكن الطباعة (مفصولة بفاصلة) أو اختر تخطي:",
        reply_markup=skip_btn("skip_prints")
    )
    return PROD_PRINTS


async def prod_add_prints(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip() if update.message else ""
    context.user_data["new_prod"]["prints"] = json.dumps([p.strip() for p in text.split(",") if p.strip()])
    from bot.keyboards import add_prod_cancel
    await update.message.reply_text("أرسل ملاحظات (أو اكتب /skip):", reply_markup=add_prod_cancel())
    return PROD_NOTES


async def prod_add_prints_skip(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data["new_prod"]["prints"] = "[]"
    from bot.keyboards import add_prod_cancel
    await query.edit_message_text("أرسل ملاحظات (أو اكتب /skip):", reply_markup=add_prod_cancel())
    return PROD_NOTES


async def prod_add_notes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip() if update.message else ""
    context.user_data["new_prod"]["notes"] = text if text != "/skip" else ""
    await prod_add_save(update, context)
    return ConversationHandler.END


async def prod_add_notes_skip(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data["new_prod"]["notes"] = ""
    await prod_add_save(update, context)
    return ConversationHandler.END


async def prod_add_save(update: Update, context: ContextTypes.DEFAULT_TYPE):
    d = context.user_data["new_prod"]
    db = get_db()

    p = Product(
        name=d.get("name", ""),
        category_id=d.get("cat_id"),
        buy_price=d.get("buy_price", 0),
        sell_price=d.get("sell_price", 0),
        current_stock=d.get("stock", 0),
        min_stock=d.get("min_stock", 5),
        image=d.get("image", ""),
        sizes=d.get("sizes", "[]"),
        colors=d.get("colors", "[]"),
        print_locations=d.get("prints", "[]"),
        notes=d.get("notes", ""),
    )
    db.add(p)
    if d.get("stock", 0) > 0:
        db.add(StockMovement(
            product=p, type="in", quantity=d["stock"],
            reference="telegram", notes="إضافة عن طريق البوت"
        ))
    db.commit()
    db.close()

    context.user_data.pop("new_prod", None)

    from bot.keyboards import back_to_menu
    msg = update.message or update.callback_query.message
    await msg.reply_text(f"✅ تمت إضافة المنتج {p.name}!", reply_markup=back_to_menu())
    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data.pop("new_prod", None)
    from bot.keyboards import main_menu
    await query.edit_message_text("❌ تم الإلغاء", reply_markup=main_menu())
    return ConversationHandler.END


# ─────────────────────── INVOICES ───────────────────────

async def invoices_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    page = 0
    if data.startswith("invs_"):
        page = int(data.split("_")[1])

    db = get_db()
    invoices = db.query(Invoice).order_by(Invoice.id.desc()).all()
    db.close()

    total_pages = max(1, (len(invoices) + PER_PAGE - 1) // PER_PAGE)
    page = min(page, total_pages - 1)
    start = page * PER_PAGE
    page_invs = invoices[start:start + PER_PAGE]

    from bot.keyboards import invoices_keyboard
    await query.edit_message_text(
        f"📋 *الفواتير* (صفحة {page+1}/{total_pages})",
        reply_markup=invoices_keyboard(page_invs, page, total_pages)
    )


async def invoice_detail(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    iid = int(query.data.split("_")[1])

    db = get_db()
    inv = db.query(Invoice).filter(Invoice.id == iid).first()
    db.close()

    if not inv:
        await query.edit_message_text("الفاتورة غير موجودة.")
        return

    items_text = ""
    for item in inv.items:
        items_text += f"• {item.product_name} × {item.quantity} = {item.total:,.0f} د.ع\n"

    text = (
        f"🧾 *فاتورة #{inv.invoice_number}*\n"
        f"التاريخ: {inv.invoice_date}\n"
        f"العميل: {inv.customer_name}\n"
        f"رقم الهاتف: {inv.customer_phone or '-'}\n\n"
        f"{items_text}\n"
        f"*الإجمالي: {inv.total:,.0f} د.ع*\n"
        f"الخصم: {inv.discount:,.0f}\n"
        f"الضريبة: {inv.tax:,.0f}\n"
        f"*الصافي: {inv.grand_total:,.0f} د.ع*"
    )

    from bot.keyboards import invoice_detail_keyboard
    await query.edit_message_text(text, reply_markup=invoice_detail_keyboard(iid))


# ─────────────────────── CUSTOMERS ───────────────────────

async def customers_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    page = 0
    if data.startswith("custs_"):
        page = int(data.split("_")[1])

    db = get_db()
    customers = db.query(Customer).order_by(Customer.id).all()
    db.close()

    total_pages = max(1, (len(customers) + PER_PAGE - 1) // PER_PAGE)
    page = min(page, total_pages - 1)
    start = page * PER_PAGE
    page_custs = customers[start:start + PER_PAGE]

    from bot.keyboards import customers_keyboard
    await query.edit_message_text(
        f"👤 *العملاء* (صفحة {page+1}/{total_pages})",
        reply_markup=customers_keyboard(page_custs, page, total_pages)
    )


async def customer_detail(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    cid = int(query.data.split("_")[1])

    db = get_db()
    c = db.query(Customer).filter(Customer.id == cid).first()
    db.close()

    if not c:
        await query.edit_message_text("العميل غير موجود.")
        return

    text = (
        f"*{c.name}*\n"
        f"الهاتف: {c.phone or '-'}\n"
        f"العنوان: {c.address or '-'}\n"
        f"ملاحظات: {c.notes or '-'}"
    )

    from bot.keyboards import customer_detail_keyboard
    await query.edit_message_text(text, reply_markup=customer_detail_keyboard(cid))


async def cust_add_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    from bot.keyboards import add_prod_cancel
    await query.edit_message_text("أرسل اسم العميل:", reply_markup=add_prod_cancel())
    return CUST_NAME


async def cust_add_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["new_cust"] = {"name": update.message.text}
    from bot.keyboards import skip_btn
    await update.message.reply_text("أرسل رقم الهاتف (أو اختر تخطي):", reply_markup=skip_btn("skip_phone"))
    return CUST_PHONE


async def cust_add_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["new_cust"]["phone"] = update.message.text
    from bot.keyboards import skip_btn
    await update.message.reply_text("أرسل العنوان (أو اختر تخطي):", reply_markup=skip_btn("skip_addr"))
    return CUST_ADDR


async def cust_add_phone_skip(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data["new_cust"]["phone"] = ""
    from bot.keyboards import skip_btn
    await query.edit_message_text("أرسل العنوان (أو اختر تخطي):", reply_markup=skip_btn("skip_addr"))
    return CUST_ADDR


async def cust_add_addr(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["new_cust"]["address"] = update.message.text
    await cust_add_save(update, context)
    return ConversationHandler.END


async def cust_add_addr_skip(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data["new_cust"]["address"] = ""
    await cust_add_save(update, context)
    return ConversationHandler.END


async def cust_add_save(update: Update, context: ContextTypes.DEFAULT_TYPE):
    d = context.user_data.get("new_cust", {})
    db = get_db()
    c = Customer(name=d.get("name", ""), phone=d.get("phone", ""), address=d.get("address", ""))
    db.add(c)
    db.commit()
    db.close()
    context.user_data.pop("new_cust", None)
    from bot.keyboards import back_to_menu
    await update.message.reply_text(f"✅ تمت إضافة العميل {c.name}!", reply_markup=back_to_menu())


# ─────────────────────── REPORTS ───────────────────────

async def reports_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    from bot.keyboards import reports_keyboard
    await query.edit_message_text("📊 *التقارير*", reply_markup=reports_keyboard())


async def report_today(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    db = get_db()
    today = date.today()
    invoices = db.query(Invoice).filter(Invoice.invoice_date == today).all()
    total_sales = sum(i.grand_total for i in invoices)
    count = len(invoices)
    db.close()

    text = (
        f"📅 *مبيعات اليوم ({today})*\n\n"
        f"عدد الفواتير: {count}\n"
        f"الإجمالي: {total_sales:,.0f} د.ع"
    )
    from bot.keyboards import back_to_menu
    await query.edit_message_text(text, reply_markup=back_to_menu())


async def report_month(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    db = get_db()
    today = date.today()
    month_start = today.replace(day=1)
    invoices = db.query(Invoice).filter(Invoice.invoice_date >= month_start).all()
    total_sales = sum(i.grand_total for i in invoices)
    count = len(invoices)
    db.close()

    text = (
        f"📆 *مبيعات شهر {today.strftime('%m/%Y')}*\n\n"
        f"عدد الفواتير: {count}\n"
        f"الإجمالي: {total_sales:,.0f} د.ع"
    )
    from bot.keyboards import back_to_menu
    await query.edit_message_text(text, reply_markup=back_to_menu())


async def report_low_stock(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    db = get_db()
    products = db.query(Product).filter(Product.current_stock <= Product.min_stock).all()
    db.close()

    if not products:
        text = "✅ لا توجد منتجات منخفضة المخزون."
    else:
        text = "⚠️ *المنتجات منخفضة المخزون:*\n\n"
        for p in products:
            text += f"• {p.name}: {p.current_stock} / {p.min_stock}\n"

    from bot.keyboards import back_to_menu
    await query.edit_message_text(text, reply_markup=back_to_menu())


# ─────────────────────── SETTINGS ───────────────────────

async def settings_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    db = get_db()
    settings = db.query(Setting).all()
    db.close()
    from bot.keyboards import settings_keyboard
    await query.edit_message_text("⚙️ *الإعدادات*", reply_markup=settings_keyboard(settings))


async def setting_edit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    sid = int(query.data.split("_")[1])
    context.user_data["edit_setting_id"] = sid

    db = get_db()
    s = db.query(Setting).filter(Setting.id == sid).first()
    db.close()

    if not s:
        await query.edit_message_text("الإعداد غير موجود.")
        return

    context.user_data["edit_setting_key"] = s.key
    await query.edit_message_text(f"أرسل القيمة الجديدة لـ `{s.key}`:", reply_markup=InlineKeyboardMarkup([
        [InlineKeyboardButton("❌ إلغاء", callback_data="menu")]
    ]))
    return EDIT_VALUE


async def setting_save(update: Update, context: ContextTypes.DEFAULT_TYPE):
    val = update.message.text
    sid = context.user_data.get("edit_setting_id")
    key = context.user_data.get("edit_setting_key")

    if sid is None:
        await update.message.reply_text("خطأ.")
        return ConversationHandler.END

    db = get_db()
    s = db.query(Setting).filter(Setting.id == sid).first()
    if s:
        s.value = val
        db.commit()
    db.close()

    context.user_data.pop("edit_setting_id", None)
    context.user_data.pop("edit_setting_key", None)

    from bot.keyboards import back_to_menu
    await update.message.reply_text(f"✅ تم تحديث {key} = {val}", reply_markup=back_to_menu())
    return ConversationHandler.END


async def setting_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data.pop("edit_setting_id", None)
    context.user_data.pop("edit_setting_key", None)
    from bot.keyboards import main_menu
    await query.edit_message_text("❌ تم الإلغاء", reply_markup=main_menu())
    return ConversationHandler.END


# ─────────────────────── HELPERS ───────────────────────

async def handle_skip(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    action = query.data
    if action == "skip_image":
        return await prod_add_image_skip(update, context)
    elif action == "skip_sizes":
        return await prod_add_sizes_skip(update, context)
    elif action == "skip_colors":
        return await prod_add_colors_skip(update, context)
    elif action == "skip_prints":
        return await prod_add_prints_skip(update, context)
    elif action == "skip_phone":
        return await cust_add_phone_skip(update, context)
    elif action == "skip_addr":
        return await cust_add_addr_skip(update, context)
    return ConversationHandler.END


async def cart_item_detail(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    parts = query.data.split("_")
    idx = int(parts[2])
    cart = context.user_data.get("cart", [])
    if 0 <= idx < len(cart):
        item = cart[idx]
        from bot.keyboards import cart_keyboard
        await query.edit_message_text(
            f"{item['name']}\nالكمية: {item['qty']}\nالسعر: {item['price']:,.0f}\nالإجمالي: {item['total']:,.0f}",
            reply_markup=cart_keyboard(cart)
        )


def get_handlers():
    add_prod_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(prod_add_start, pattern="^prod_add$")],
        states={
            PROD_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, prod_add_name)],
            PROD_CATEGORY: [CallbackQueryHandler(prod_add_category, pattern="^pcat_")],
            PROD_BUY: [MessageHandler(filters.TEXT & ~filters.COMMAND, prod_add_buy)],
            PROD_SELL: [MessageHandler(filters.TEXT & ~filters.COMMAND, prod_add_sell)],
            PROD_STOCK: [MessageHandler(filters.TEXT & ~filters.COMMAND, prod_add_stock)],
            PROD_MIN: [MessageHandler(filters.TEXT & ~filters.COMMAND, prod_add_min)],
            PROD_IMAGE: [
                MessageHandler(filters.PHOTO, prod_add_image),
                CallbackQueryHandler(prod_add_image_skip, pattern="^skip_image$"),
            ],
            PROD_SIZES: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, prod_add_sizes),
                CallbackQueryHandler(prod_add_sizes_skip, pattern="^skip_sizes$"),
            ],
            PROD_COLORS: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, prod_add_colors),
                CallbackQueryHandler(prod_add_colors_skip, pattern="^skip_colors$"),
            ],
            PROD_PRINTS: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, prod_add_prints),
                CallbackQueryHandler(prod_add_prints_skip, pattern="^skip_prints$"),
            ],
            PROD_NOTES: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, prod_add_notes),
                CallbackQueryHandler(prod_add_notes_skip, pattern="^skip_notes$"),
            ],
        },
        fallbacks=[CallbackQueryHandler(cancel, pattern="^cancel$")],
        allow_reentry=True,
        per_message=False,
    )

    add_cust_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(cust_add_start, pattern="^cust_add$")],
        states={
            CUST_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, cust_add_name)],
            CUST_PHONE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, cust_add_phone),
                CallbackQueryHandler(cust_add_phone_skip, pattern="^skip_phone$"),
            ],
            CUST_ADDR: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, cust_add_addr),
                CallbackQueryHandler(cust_add_addr_skip, pattern="^skip_addr$"),
            ],
        },
        fallbacks=[CallbackQueryHandler(cancel, pattern="^cancel$")],
        allow_reentry=True,
        per_message=False,
    )

    edit_setting_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(setting_edit, pattern="^set_")],
        states={
            EDIT_VALUE: [MessageHandler(filters.TEXT & ~filters.COMMAND, setting_save)],
        },
        fallbacks=[CallbackQueryHandler(setting_cancel, pattern="^menu$")],
        allow_reentry=True,
        per_message=False,
    )

    return [
        CommandHandler("start", start),
        CallbackQueryHandler(menu, pattern="^menu$"),
        CallbackQueryHandler(noop, pattern="^noop$"),

        # POS
        CallbackQueryHandler(pos_categories, pattern="^pos_cats$"),
        CallbackQueryHandler(pos_products, pattern="^cat_"),
        CallbackQueryHandler(pos_products, pattern="^prods_"),
        CallbackQueryHandler(pos_product_select, pattern="^prod_"),
        CallbackQueryHandler(pos_qty_change, pattern="^qty_"),
        CallbackQueryHandler(pos_add_to_cart, pattern="^add_"),
        CallbackQueryHandler(pos_view_cart, pattern="^view_cart$"),
        CallbackQueryHandler(pos_remove_item, pattern="^rm_"),
        CallbackQueryHandler(pos_checkout, pattern="^checkout$"),
        CallbackQueryHandler(pos_confirm_invoice, pattern="^confirm_inv$"),
        CallbackQueryHandler(pos_cancel_invoice, pattern="^cancel_inv$"),
        CallbackQueryHandler(cart_item_detail, pattern="^cart_item_"),

        # Products
        CallbackQueryHandler(products_list, pattern="^prods_"),
        CallbackQueryHandler(product_view, pattern="^pview_"),
        CallbackQueryHandler(product_delete, pattern="^pdel_"),
        add_prod_conv,

        # Invoices
        CallbackQueryHandler(invoices_list, pattern="^invs_"),
        CallbackQueryHandler(invoice_detail, pattern="^inv_"),

        # Customers
        CallbackQueryHandler(customers_list, pattern="^custs_"),
        CallbackQueryHandler(customer_detail, pattern="^cust_"),
        add_cust_conv,

        # Reports
        CallbackQueryHandler(reports_menu, pattern="^reports$"),
        CallbackQueryHandler(report_today, pattern="^rep_today$"),
        CallbackQueryHandler(report_month, pattern="^rep_month$"),
        CallbackQueryHandler(report_low_stock, pattern="^rep_low$"),

        # Settings
        CallbackQueryHandler(settings_menu, pattern="^settings$"),
        edit_setting_conv,

        # Skip buttons for forms
        CallbackQueryHandler(handle_skip, pattern="^skip_"),
    ]
