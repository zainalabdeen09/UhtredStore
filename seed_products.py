import sys, json
sys.path.insert(0, '.')
from database import init_db, SessionLocal
from models import Category, Product, StockMovement

init_db()
db = SessionLocal()

cats = {
    'teeterbo': 'خامة تتيربو قالب هاف',
    'cotton_half': 'تيشيرت قطني قالب هاف',
    'cotton_first': 'تيشيرت قطني درجة اولى قالب عادي',
    'cotton_lycra': 'تيشيرت درجة ثانية قطني + ليگرا',
    'gym_set': 'سيتات جم',
    'pajama': 'بجامه',
    'polo': 'تيشيرت بولو',
    'makhoot': 'تيشيرت مكحوت',
    'gym_tshirt': 'تيشيرتات GYM',
}

cat_ids = {}
for key, name in cats.items():
    c = db.query(Category).filter(Category.name == name).first()
    if not c:
        c = Category(name=name)
        db.add(c)
        db.flush()
    cat_ids[key] = c.id

sizes_all = ['S', 'M', 'L', 'XL']
colors_bw = ['أسود', 'أبيض']
colors_black = ['أسود']
colors_black_gray = ['أسود', 'رصاصي']

products = []

# 1. خامة تتيربو قالب هاف
cat = cat_ids['teeterbo']
for name_s, price, prints in [
    ('سادة بدون طباعة', 20000, ['بدون']),
    ('طباعة جهة واحدة (حجم متوسط او كبير)', 25000, ['أمامي', 'خلفي']),
    ('طباعة جهتين (وسط+كبير)', 27000, ['أمامي', 'خلفي', 'كم']),
    ('طباعة جهتين (كبير)', 30000, ['أمامي', 'خلفي', 'كم']),
]:
    products.append({'name': f'تتيربو هاف - {name_s}', 'cat': cat, 'price': price, 'stock': 50, 'colors': colors_bw, 'sizes': sizes_all, 'prints': prints})

# 2. تيشيرت قطني قالب هاف
cat = cat_ids['cotton_half']
for name_s, price, prints in [
    ('سادة بدون طباعة', 20000, ['بدون']),
    ('طباعة جهة واحدة (حجم متوسط او كبير)', 23000, ['أمامي', 'خلفي']),
    ('طباعة جهتين (وسط+كبير)', 25000, ['أمامي', 'خلفي', 'كم']),
    ('طباعة جهتين (كبير)', 28000, ['أمامي', 'خلفي', 'كم']),
]:
    products.append({'name': f'تيشيرت قطني هاف - {name_s}', 'cat': cat, 'price': price, 'stock': 50, 'colors': colors_bw, 'sizes': sizes_all, 'prints': prints})

# 3. تيشيرت قطني درجة اولى قالب عادي
cat = cat_ids['cotton_first']
for name_s, price, prints in [
    ('سادة بدون طباعة', 19000, ['بدون']),
    ('طباعة جهة واحدة (حجم متوسط او كبير)', 22000, ['أمامي', 'خلفي']),
    ('طباعة جهتين (وسط+كبير)', 24000, ['أمامي', 'خلفي', 'كم']),
    ('طباعة جهتين (كبير)', 26000, ['أمامي', 'خلفي', 'كم']),
]:
    products.append({'name': f'تيشيرت قطني درجة اولى - {name_s}', 'cat': cat, 'price': price, 'stock': 50, 'colors': colors_bw, 'sizes': sizes_all, 'prints': prints})

# 4. تيشيرت درجة ثانية قطني + ليگرا
cat = cat_ids['cotton_lycra']
for name_s, price, prints in [
    ('سادة بدون طباعة', 15000, ['بدون']),
    ('طباعة جهة واحدة (حجم متوسط او كبير)', 18000, ['أمامي', 'خلفي']),
    ('طباعة جهتين (وسط+كبير)', 20000, ['أمامي', 'خلفي', 'كم']),
    ('طباعة جهتين (كبير)', 22000, ['أمامي', 'خلفي', 'كم']),
]:
    products.append({'name': f'تيشيرت درجة ثانية - {name_s}', 'cat': cat, 'price': price, 'stock': 50, 'colors': colors_black, 'sizes': sizes_all, 'prints': prints})

# 5. سيتات جم
cat = cat_ids['gym_set']
gym_sets = [
    ('سيت جم رياضي (شورت + تيشيرت ردان)', [
        ('سادة', 30000), ('طباعة جهة واحدة', 35000), ('طباعة جهتين', 37000),
    ], colors_black),
    ('سيت جم (قالب باندا + شورت مبطن)', [
        ('سادة', 27000), ('طباعة جهة واحدة', 32000), ('طباعة جهتين', 35000),
    ], ['أسود', 'أبيض']),
    ('سيت جم وتر بروف الكامل', [
        ('سادة', 22000), ('طباعة جهة واحدة', 25000), ('طباعة جهتين', 35000),
    ], colors_black),
    ('سيت جم فلتر + شورت وتر بروف', [
        ('سادة', 20000), ('طباعة جهة واحدة', 25000), ('طباعة جهتين (كبير او وسط)', 27000),
    ], colors_black),
    ('سيت جم (تيشيرت جم شارك + شورت)', [
        ('كامل', 40000),
    ], colors_black),
]
for base_name, variants, colors in gym_sets:
    for vname, price in variants:
        prints = ['بدون'] if vname == 'سادة' or vname == 'كامل' else ['أمامي', 'خلفي']
        if 'جهتين' in vname:
            prints = ['أمامي', 'خلفي', 'كم']
        products.append({'name': f'{base_name} - {vname}', 'cat': cat, 'price': price, 'stock': 30, 'colors': colors, 'sizes': ['M', 'L', 'XL'], 'prints': prints})

# 6. بجامه
cat = cat_ids['pajama']
pajama_items = [
    ('بجامه جوغر كلاسك (شريط مطاطي)', [
        ('سادة', 23000), ('طباعة جهة واحدة', 25000), ('طباعة جهتين (كبير او وسط)', 27000),
        ('طباعة جهتين (كبير)', 30000), ('طباعة ثلاث جهات', 33000),
    ]),
    ('بجامه جوغر بريميوم (حلقة)', [
        ('سادة', 23000), ('طباعة جهة واحدة', 25000), ('طباعة جهتين (كبير او وسط)', 27000),
        ('طباعة جهتين (كبير)', 30000), ('طباعة ثلاث جهات', 33000),
    ]),
    ('سيت بجامه + تيشيرت تتيربو', [
        ('سادة', 38000), ('طباعة جهة واحدة', 40000), ('طباعة جهتين (كبير او وسط)', 45000),
        ('طباعة جهتين (كبير)', 50000),
    ]),
]
for base_name, variants in pajama_items:
    for vname, price in variants:
        prints = ['بدون'] if vname == 'سادة' else ['أمامي', 'خلفي']
        if 'جهتين' in vname or 'ثلاث' in vname:
            prints = ['أمامي', 'خلفي', 'كم']
        products.append({'name': f'{base_name} - {vname}', 'cat': cat, 'price': price, 'stock': 30, 'colors': colors_bw, 'sizes': ['M', 'L', 'XL'], 'prints': prints})

# 7. تيشيرت بولو
cat = cat_ids['polo']
for base_name, variants, colors in [
    ('تيشيرت بولو أسود', [('سادة', 18000), ('طباعة جهة واحدة', 22000), ('طباعة جهتين', 25000)], colors_black),
    ('تيشيرت بولو أبيض', [('سادة', 18000), ('طباعة جهة واحدة', 22000), ('طباعة جهتين', 25000)], ['أبيض']),
]:
    for vname, price in variants:
        prints = ['بدون'] if vname == 'سادة' else (['أمامي', 'خلفي', 'كم'] if 'جهتين' in vname else ['أمامي', 'خلفي'])
        products.append({'name': f'{base_name} - {vname}', 'cat': cat, 'price': price, 'stock': 30, 'colors': colors, 'sizes': sizes_all, 'prints': prints, 'notes': 'القياسات الخاصة + 1000 دينار على السعر'})

# 8. تيشيرت مكحوت
cat = cat_ids['makhoot']
makhoot_items = [
    ('تيشيرت مغسول رصاصي', [('سادة', 19000), ('طباعة جهة واحدة', 24000), ('طباعة جهتين (كبير او وسط)', 25000), ('طباعة جهتين كبير', 27000)], 'رصاصي'),
    ('تيشيرت مكحوت رصاصي', [('سادة', 19000), ('طباعة جهة واحدة', 23000), ('طباعة جهتين', 25000)], 'رصاصي'),
    ('تيشيرت مكحوت سلفر', [('سادة', 19000), ('طباعة جهة واحدة', 23000), ('طباعة جهتين (كبير)', 27000)], 'سلفر'),
    ('تيشيرت مكحوت ازرق فاتح', [('سادة', 19000), ('طباعة جهة واحدة', 24000), ('طباعة جهتين (كبير)', 27000)], 'أزرق فاتح'),
    ('تيشيرت مكحوت زيتوني فاتح', [('سادة', 19000), ('طباعة جهة واحدة', 24000), ('طباعة جهتين (كبير)', 27000)], 'زيتوني فاتح'),
    ('سيت (بجامه باكي + تيشيرت مكحوت رصاصي)', [('سادة', 37000), ('طباعة جهة واحدة (تيشيرت كبير - بجامه صغير)', 40000), ('طباعة جهة واحدة (تيشيرت كبير - بجامه كبير)', 45000)], 'أسود'),
    ('سيت مكحوت (تيشيرت + شورت)', [('سادة', 37000), ('طباعة جهة واحدة (تيشيرت كبير - شورت صغير)', 43000)], 'رصاصي'),
]
for base_name, variants, color in makhoot_items:
    for vname, price in variants:
        prints = ['بدون'] if vname == 'سادة' else (['أمامي', 'خلفي'] if 'جهة واحدة' in vname else ['أمامي', 'خلفي', 'كم'])
        products.append({'name': f'{base_name} - {vname}', 'cat': cat, 'price': price, 'stock': 30, 'colors': [color], 'sizes': sizes_all, 'prints': prints})

# 9. تيشيرتات GYM
cat = cat_ids['gym_tshirt']
gym_items = [
    ('تيشيرت جم رياضي ردان', [('سادة', 20000), ('طباعة جهة واحدة', 24000), ('طباعة جهتين (كبير او وسط)', 26000), ('طباعة جهتين (كبير)', 28000)], colors_black),
    ('تيشيرت جم رياضي (خامة فلتر)', [('سادة', 19000), ('طباعة جهة واحدة', 23000), ('طباعة جهتين (كبير او وسط)', 25000)], colors_black),
    ('تيشيرت جم رياضي كومبدشن (نص ردان)', [('سادة', 21000), ('طباعة جهة واحدة', 24000), ('طباعة جهتين (كبير او وسط)', 25000), ('طباعة جهتين (كبير)', 27000)], colors_black),
    ('تيشيرت جم شارك رياضي (نص ردان)', [('كامل', 35000)], colors_black_gray),
    ('تيشيرت كيمونه جم شارك', [('كامل', 35000)], colors_black),
]
for base_name, variants, colors in gym_items:
    for vname, price in variants:
        prints = ['بدون']
        if vname not in ('كامل', 'سادة'):
            prints = ['أمامي', 'خلفي']
            if 'جهتين' in vname:
                prints = ['أمامي', 'خلفي', 'كم']
        products.append({'name': f'{base_name} - {vname}', 'cat': cat, 'price': price, 'stock': 30, 'colors': colors, 'sizes': sizes_all, 'prints': prints})

# INSERT
total = len(products)
print(f'Total products to insert: {total}')
count = 0
for p in products:
    existing = db.query(Product).filter(Product.name == p['name']).first()
    if existing:
        print(f'  SKIP: {p["name"]}')
        continue
    prod = Product(
        name=p['name'],
        category_id=p['cat'],
        sell_price=float(p['price']),
        buy_price=float(p['price']) * 0.6,
        current_stock=p['stock'],
        min_stock=5,
        sizes=json.dumps(p['sizes']),
        colors=json.dumps(p['colors']),
        print_locations=json.dumps(p['prints']),
        notes=p.get('notes', ''),
    )
    db.add(prod)
    db.flush()
    db.add(StockMovement(
        product_id=prod.id,
        type='in',
        quantity=p['stock'],
        reference='initial',
        notes='الافتتاحية',
    ))
    count += 1

db.commit()
db.close()
print(f'\nDone! Added {count} new products.')
