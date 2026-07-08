def build_invoice_html(invoice: dict, store: dict) -> str:
    items_rows = ""
    for i, item in enumerate(invoice.get("items", []), 1):
        items_rows += f"""
        <tr>
            <td style="text-align:center;">{i}</td>
            <td style="text-align:center;">{item['quantity']}</td>
            <td style="text-align:center;">{item['price']:,.0f}</td>
            <td>{item['product_name']}</td>
            <td style="text-align:center;">{item['total']:,.0f}</td>
            <td style="text-align:center;">{item.get('print_location', '')}</td>
            <td style="text-align:center;">{item.get('size', '')}</td>
            <td style="text-align:center;">{item.get('color', '')}</td>
        </tr>"""

    store_name = store.get('store_name', 'Uhtred Store')
    store_phone = store.get('store_phone', '')
    store_address = store.get('store_address', '')

    return f"""<!DOCTYPE html>
<html dir="rtl">
<head>
<meta charset="UTF-8">
<title>فاتورة - {invoice.get('invoice_number', '')}</title>
<style>
@page {{ size: A4; margin: 15mm; }}
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
body {{
    font-family: 'Traditional Arabic', 'Tahoma', 'Arial', sans-serif;
    direction: rtl;
    color: #000;
    padding: 20px;
}}
.invoice-box {{
    max-width: 800px;
    margin: auto;
    border: 2px solid #000;
    padding: 25px;
}}
.header {{
    text-align: center;
    border-bottom: 2px solid #000;
    padding-bottom: 12px;
    margin-bottom: 18px;
}}
.header h1 {{
    font-size: 26px;
    font-weight: bold;
    margin: 0;
}}
.header h2 {{
    font-size: 18px;
    font-weight: bold;
    margin: 8px 0 0 0;
}}
.info-table {{
    width: 100%;
    border-collapse: collapse;
    margin-bottom: 18px;
}}
.info-table td {{
    padding: 4px 6px;
    font-size: 14px;
    vertical-align: top;
}}
.info-table .label {{
    font-weight: bold;
    width: 100px;
}}
.items-table {{
    width: 100%;
    border-collapse: collapse;
    margin-bottom: 16px;
}}
.items-table th {{
    border: 1px solid #000;
    padding: 8px 4px;
    font-weight: bold;
    font-size: 13px;
    text-align: center;
    background: #fff;
    color: #000;
}}
.items-table td {{
    border: 1px solid #000;
    padding: 6px 4px;
    font-size: 13px;
    text-align: center;
}}
.items-table td:nth-child(4) {{
    text-align: right;
}}
.total-section {{
    margin-top: 10px;
    padding-top: 10px;
    border-top: 2px solid #000;
    text-align: left;
}}
.total-section .total-row {{
    font-size: 18px;
    font-weight: bold;
}}
.notes-section {{
    margin-top: 12px;
    padding: 8px;
    font-size: 13px;
}}
.footer {{
    text-align: center;
    margin-top: 20px;
    padding-top: 12px;
    border-top: 1px solid #999;
    font-size: 13px;
    color: #333;
}}
.footer .thank-you {{
    font-size: 16px;
    font-weight: bold;
    color: #000;
    margin-bottom: 6px;
}}
@media print {{
    body {{ padding: 0; }}
    .invoice-box {{ border: 2px solid #000; }}
    .no-print {{ display: none; }}
}}
</style>
</head>
<body>
<div class="invoice-box">
    <div class="header">
        <h1>{store_name}</h1>
        <h2>فاتورة مبيعات</h2>
    </div>

    <table class="info-table">
        <tr>
            <td class="label">اسم الزبون:</td>
            <td>{invoice.get('customer_name', '')}</td>
            <td class="label">التاريخ:</td>
            <td>{invoice.get('invoice_date', '')}</td>
        </tr>
        <tr>
            <td class="label">رقم الهاتف:</td>
            <td>{invoice.get('customer_phone', '')}</td>
            <td class="label">رقم الفاتورة:</td>
            <td>{invoice.get('invoice_number', '')}</td>
        </tr>
        <tr>
            <td class="label">عنوان الزبون:</td>
            <td colspan="3">{invoice.get('customer_address', '')}</td>
        </tr>
    </table>

    <table class="items-table">
        <thead>
            <tr>
                <th style="width:40px;">رقم</th>
                <th style="width:50px;">الكمية</th>
                <th style="width:60px;">السعر</th>
                <th>وصف المنتج</th>
                <th style="width:70px;">الإجمالي</th>
                <th style="width:80px;">مكان الطباعة</th>
                <th style="width:50px;">المقاس</th>
                <th style="width:60px;">اللون</th>
            </tr>
        </thead>
        <tbody>
            {items_rows}
            {_get_empty_rows(invoice.get('items', []))}
        </tbody>
    </table>

    <div class="total-section">
        <div class="total-row">الإجمالي المطلوب: {invoice.get('grand_total', 0):,.0f} د.ع</div>
    </div>

    <div class="notes-section">
        <strong>ملاحظات:</strong> {invoice.get('notes', '')}
    </div>

    <div class="footer">
        <div class="thank-you">شكراً لتسوقك من {store_name}</div>
        <div>يرجى الاحتفاظ بالفاتورة فهي وثيقة تضمن حقوق الطرفين</div>
        {f'<div style="margin-top:6px;">{store_phone} | {store_address}</div>' if store_phone or store_address else ''}
    </div>
</div>
</body>
</html>"""


def _get_empty_rows(items):
    count = len(items)
    rows = ""
    for i in range(count + 1, 13):
        rows += f"""
        <tr>
            <td style="text-align:center;">{i}</td>
            <td></td><td></td><td></td><td></td><td></td><td></td><td></td>
        </tr>"""
    return rows
