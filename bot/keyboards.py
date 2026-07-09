from telegram import InlineKeyboardButton, InlineKeyboardMarkup


def main_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🛒 نقطة البيع", callback_data="pos_cats")],
        [InlineKeyboardButton("📦 المنتجات", callback_data="prods_0"),
         InlineKeyboardButton("📋 الفواتير", callback_data="invs_0")],
        [InlineKeyboardButton("👤 العملاء", callback_data="custs_0"),
         InlineKeyboardButton("📊 التقارير", callback_data="reports")],
        [InlineKeyboardButton("⚙️ الإعدادات", callback_data="settings")],
    ])


def back_to_menu():
    return InlineKeyboardMarkup([[InlineKeyboardButton("🔙 القائمة الرئيسية", callback_data="menu")]])


def categories_keyboard(cats):
    kb = []
    row = []
    for i, c in enumerate(cats):
        row.append(InlineKeyboardButton(c.name, callback_data=f"cat_{c.id}"))
        if len(row) == 2 or i == len(cats) - 1:
            kb.append(row)
            row = []
    kb.append([InlineKeyboardButton("🔙 رجوع", callback_data="menu")])
    return InlineKeyboardMarkup(kb)


def products_keyboard(products, page, total_pages):
    kb = []
    for p in products:
        kb.append([InlineKeyboardButton(f"{p.name}  |  {p.sell_price:,.0f} د.ع", callback_data=f"prod_{p.id}")])
    nav = []
    if page > 0:
        nav.append(InlineKeyboardButton("⬅️ السابق", callback_data=f"prods_{page-1}"))
    if page < total_pages - 1:
        nav.append(InlineKeyboardButton("التالي ➡️", callback_data=f"prods_{page+1}"))
    if nav:
        kb.append(nav)
    kb.append([InlineKeyboardButton("🔙 رجوع", callback_data="menu")])
    return InlineKeyboardMarkup(kb)


def product_detail_keyboard(pid):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("➕ إضافة للسلة", callback_data=f"cart_{pid}")],
        [InlineKeyboardButton("🔙 رجوع", callback_data="pos_cats")],
        [InlineKeyboardButton("🔙 القائمة الرئيسية", callback_data="menu")],
    ])


def cart_keyboard(cart):
    kb = []
    for i, item in enumerate(cart):
        kb.append([
            InlineKeyboardButton(f"{item['name']} ×{item['qty']} - {item['total']:,.0f}", callback_data=f"cart_item_{i}"),
            InlineKeyboardButton("❌", callback_data=f"rm_{i}"),
        ])
    kb.append([InlineKeyboardButton("➕ إضافة منتج", callback_data="pos_cats")])
    kb.append([InlineKeyboardButton("✅ إنهاء الفاتورة", callback_data="checkout")])
    kb.append([InlineKeyboardButton("🔙 القائمة الرئيسية", callback_data="menu")])
    return InlineKeyboardMarkup(kb)


def qty_keyboard(pid):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("➖", callback_data=f"qty_dn_{pid}"),
         InlineKeyboardButton("➕", callback_data=f"qty_up_{pid}")],
        [InlineKeyboardButton("✅ تأكيد", callback_data=f"add_{pid}")],
        [InlineKeyboardButton("🔙 رجوع", callback_data="pos_cats")],
    ])


def confirm_invoice_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("✅ تأكيد وحفظ", callback_data="confirm_inv")],
        [InlineKeyboardButton("🔙 تعديل الفاتورة", callback_data="view_cart")],
        [InlineKeyboardButton("❌ إلغاء", callback_data="cancel_inv")],
    ])


def products_list_keyboard(products, page, total_pages):
    kb = []
    for p in products:
        kb.append([InlineKeyboardButton(f"{p.name} (مخزون: {p.current_stock})", callback_data=f"pview_{p.id}")])
    nav = []
    if page > 0:
        nav.append(InlineKeyboardButton("⬅️", callback_data=f"prods_{page-1}"))
    nav.append(InlineKeyboardButton(f"{page+1}/{total_pages}", callback_data="noop"))
    if page < total_pages - 1:
        nav.append(InlineKeyboardButton("➡️", callback_data=f"prods_{page+1}"))
    if nav:
        kb.append(nav)
    kb.append([InlineKeyboardButton("➕ إضافة منتج", callback_data="prod_add")])
    kb.append([InlineKeyboardButton("🔙 القائمة الرئيسية", callback_data="menu")])
    return InlineKeyboardMarkup(kb)


def product_view_keyboard(pid):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("✏️ تعديل", callback_data=f"pedit_{pid}"),
         InlineKeyboardButton("🗑️ حذف", callback_data=f"pdel_{pid}")],
        [InlineKeyboardButton("🔙 رجوع", callback_data="prods_0")],
        [InlineKeyboardButton("🔙 القائمة الرئيسية", callback_data="menu")],
    ])


def invoices_keyboard(invoices, page, total_pages):
    kb = []
    for inv in invoices:
        kb.append([InlineKeyboardButton(
            f"#{inv.invoice_number} - {inv.customer_name} - {inv.grand_total:,.0f} د.ع",
            callback_data=f"inv_{inv.id}"
        )])
    nav = []
    if page > 0:
        nav.append(InlineKeyboardButton("⬅️", callback_data=f"invs_{page-1}"))
    nav.append(InlineKeyboardButton(f"{page+1}/{total_pages}", callback_data="noop"))
    if page < total_pages - 1:
        nav.append(InlineKeyboardButton("➡️", callback_data=f"invs_{page+1}"))
    if nav:
        kb.append(nav)
    kb.append([InlineKeyboardButton("🔙 القائمة الرئيسية", callback_data="menu")])
    return InlineKeyboardMarkup(kb)


def invoice_detail_keyboard(iid):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔙 رجوع", callback_data="invs_0")],
        [InlineKeyboardButton("🔙 القائمة الرئيسية", callback_data="menu")],
    ])


def customers_keyboard(customers, page, total_pages):
    kb = []
    for c in customers:
        kb.append([InlineKeyboardButton(f"{c.name}  |  {c.phone}", callback_data=f"cust_{c.id}")])
    nav = []
    if page > 0:
        nav.append(InlineKeyboardButton("⬅️", callback_data=f"custs_{page-1}"))
    nav.append(InlineKeyboardButton(f"{page+1}/{total_pages}", callback_data="noop"))
    if page < total_pages - 1:
        nav.append(InlineKeyboardButton("➡️", callback_data=f"custs_{page+1}"))
    if nav:
        kb.append(nav)
    kb.append([InlineKeyboardButton("➕ إضافة عميل", callback_data="cust_add")])
    kb.append([InlineKeyboardButton("🔙 القائمة الرئيسية", callback_data="menu")])
    return InlineKeyboardMarkup(kb)


def customer_detail_keyboard(cid):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔙 رجوع", callback_data="custs_0")],
        [InlineKeyboardButton("🔙 القائمة الرئيسية", callback_data="menu")],
    ])


def reports_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📅 مبيعات اليوم", callback_data="rep_today")],
        [InlineKeyboardButton("📆 مبيعات هذا الشهر", callback_data="rep_month")],
        [InlineKeyboardButton("⚠️ المنتجات منخفضة المخزون", callback_data="rep_low")],
        [InlineKeyboardButton("🔙 القائمة الرئيسية", callback_data="menu")],
    ])


def settings_keyboard(settings):
    kb = []
    for s in settings:
        label = s.key.replace("_", " ").title()
        kb.append([InlineKeyboardButton(f"{label}: {s.value}", callback_data=f"set_{s.id}")])
    kb.append([InlineKeyboardButton("🔙 القائمة الرئيسية", callback_data="menu")])
    return InlineKeyboardMarkup(kb)


def add_prod_cancel():
    return InlineKeyboardMarkup([[InlineKeyboardButton("❌ إلغاء", callback_data="cancel")]])


def skip_btn(action):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("⏭️ تخطي", callback_data=action)],
        [InlineKeyboardButton("❌ إلغاء", callback_data="cancel")],
    ])
