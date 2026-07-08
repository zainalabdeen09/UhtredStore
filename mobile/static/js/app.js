const state = {
  loggedIn: localStorage.getItem('uhtred_logged_in') === '1',
  currentPage: 'dashboard',
  cart: [],
  products: [],
  customers: [],
  invoices: [],
  categories: [],
  settings: {}
};
const API_BASE = '';
function h() { return { 'Content-Type': 'application/json' }; }

if (state.loggedIn) { document.getElementById('login-overlay').style.display = 'none'; }

async function doLogin() {
  const u = document.getElementById('login-username').value.trim();
  const p = document.getElementById('login-password').value.trim();
  const errEl = document.getElementById('login-error');
  const btn = document.getElementById('login-btn');
  if (!u || !p) { errEl.textContent = 'أدخل اسم المستخدم وكلمة المرور'; return; }
  btn.disabled = true; errEl.textContent = '';
  try {
    const r = await fetch('/api/auth/login', { method: 'POST', headers: h(), body: JSON.stringify({ username: u, password: p }) });
    const d = await r.json();
    if (d.success) {
      localStorage.setItem('uhtred_logged_in', '1');
      state.loggedIn = true;
      document.getElementById('login-overlay').style.display = 'none';
      renderPage('dashboard');
    } else {
      errEl.textContent = 'اسم المستخدم أو كلمة المرور خطأ';
    }
  } catch (e) {
    errEl.textContent = 'خطأ في الاتصال: ' + e.message;
  }
  btn.disabled = false;
}
async function g(e) { const r = await fetch(API_BASE + '/api' + e, { headers: h() }); if (!r.ok) { const d = await r.json().catch(() => ({ error: r.statusText })); throw new Error(d.error || 'Request failed'); } return r.json(); }
async function p(e, d) { const r = await fetch(API_BASE + '/api' + e, { method: 'POST', headers: h(), body: JSON.stringify(d) }); if (!r.ok) { const ed = await r.json().catch(() => ({ error: r.statusText })); throw new Error(ed.error || 'Request failed'); } return r.json(); }
async function put(e, d) { const r = await fetch(API_BASE + '/api' + e, { method: 'PUT', headers: h(), body: JSON.stringify(d) }); if (!r.ok) { const ed = await r.json().catch(() => ({ error: r.statusText })); throw new Error(ed.error || 'Request failed'); } return r.json(); }
async function del(e) { const r = await fetch(API_BASE + '/api' + e, { method: 'DELETE', headers: h() }); if (!r.ok) { const ed = await r.json().catch(() => ({ error: r.statusText })); throw new Error(ed.error || 'Request failed'); } return r.json(); }
function fc(a) { return Number(a).toLocaleString('ar-IQ') + ' د.ع'; }
function fd(iso) { if (!iso) return ''; const d = new Date(iso); return d.toLocaleDateString('ar-IQ', { year: 'numeric', month: 'short', day: 'numeric' }); }
function fn(iso) { if (!iso) return ''; const d = new Date(iso); return d.toLocaleDateString('ar-IQ', { year: 'numeric', month: 'short', day: 'numeric' }) + ' ' + d.toLocaleTimeString('ar-IQ', { hour: '2-digit', minute: '2-digit' }); }

function toast(msg, type = 'info') {
  const c = document.getElementById('toast-container');
  const t = document.createElement('div'); t.className = 'toast ' + type; t.textContent = msg;
  c.appendChild(t); setTimeout(() => { t.remove(); }, 3000);
}

function toggleSidebar() {
  document.getElementById('sidebar').classList.toggle('open');
  document.getElementById('sidebar-overlay').classList.toggle('active');
}

function closeSidebar() {
  if (window.innerWidth <= 768) {
    document.getElementById('sidebar').classList.remove('open');
    document.getElementById('sidebar-overlay').classList.remove('active');
  }
}

function navigateTo(page, push = true) {
  state.currentPage = page;
  document.getElementById('page-title').textContent = document.querySelector(`.sidebar-item[data-page="${page}"]`)?.textContent.trim() || page;
  document.querySelectorAll('.sidebar-item').forEach(el => el.classList.remove('active'));
  const active = document.querySelector(`.sidebar-item[data-page="${page}"]`);
  if (active) active.classList.add('active');
  closeSidebar();
  renderPage(page);
  if (push) history.pushState({ page }, '', '/#' + page);
}

window.addEventListener('popstate', function(e) {
  if (e.state && e.state.page) { navigateTo(e.state.page, false); }
});

function logout() {
  localStorage.removeItem('uhtred_logged_in');
  state.loggedIn = false;
  closeSidebar();
  document.getElementById('login-overlay').style.display = 'flex';
  document.getElementById('login-username').value = '';
  document.getElementById('login-password').value = '';
  document.getElementById('login-error').textContent = '';
}

function renderPage(page) {
  const c = document.getElementById('page-content');
  switch (page) {
    case 'dashboard': renderDashboard(c); break;
    case 'pos': renderPOS(c); break;
    case 'inventory': renderInventory(c); break;
    case 'products': renderProducts(c); break;
    case 'customers': renderCustomers(c); break;
    case 'invoices': renderInvoices(c); break;
    case 'reports': renderReports(c); break;
    case 'stock': renderStock(c); break;
    case 'settings': renderSettings(c); break;
    default: c.innerHTML = '<div class="loading">الصفحة غير موجودة</div>';
  }
}

/* ============ DASHBOARD ============ */
async function renderDashboard(c) {
  c.innerHTML = '<div class="loading">جاري التحميل...</div>';
  try {
    const data = await g('/stats');
    c.innerHTML = `
      <div class="stats-grid">
        <div class="stat-card"><div class="label">مبيعات اليوم</div><div class="value" style="color:var(--success)">${fc(data.today_sales || 0)}</div></div>
        <div class="stat-card"><div class="label">مبيعات الشهر</div><div class="value" style="color:var(--primary)">${fc(data.month_sales || 0)}</div></div>
        <div class="stat-card"><div class="label">المنتجات</div><div class="value">${data.total_products || 0}</div></div>
        <div class="stat-card"><div class="label">الزبائن</div><div class="value">${data.total_customers || 0}</div></div>
        <div class="stat-card"><div class="label">الفواتير</div><div class="value">${data.total_invoices || 0}</div></div>
        <div class="stat-card"><div class="label">منتجات منخفضة</div><div class="value" style="color:${(data.low_stock || 0) > 0 ? 'var(--danger)' : 'var(--text)'}">${data.low_stock || 0}</div></div>
      </div>
      <div class="card"><div class="card-title">آخر الفواتير</div><div id="recent-invoices"></div></div>`;
    if (data.recent_invoices) {
      const ri = document.getElementById('recent-invoices');
      if (data.recent_invoices.length === 0) { ri.innerHTML = '<div style="color:var(--text2);padding:12px;text-align:center">لا توجد فواتير</div>'; }
      else {
        let html = '<div class="table-wrap"><table>';
        data.recent_invoices.forEach(inv => {
          html += `<tr onclick="showInvoiceDetail(${inv.id})"><td>${inv.invoice_number}</td><td>${inv.customer_name || 'نقدي'}</td><td>${fc(inv.grand_total)}</td><td style="color:var(--text2);font-size:11px">${fd(inv.created_at)}</td></tr>`;
        });
        html += '</table></div>';
        ri.innerHTML = html;
      }
    }
  } catch (e) { c.innerHTML = `<div class="card" style="text-align:center;color:var(--danger);padding:40px">خطأ: ${e.message}</div>`; }
}

/* ============ POS ============ */
async function renderPOS(c) {
  c.innerHTML = '<div class="loading">جاري التحميل...</div>';
  try {
    const [products, categories] = await Promise.all([g('/products'), g('/categories')]);
    state.products = products; state.categories = categories;
    c.innerHTML = `
      <div class="pos-container">
        <div class="pos-products">
          <div class="pos-search"><input type="text" id="pos-search" placeholder="بحث عن منتج..." oninput="filterPOSProducts()"></div>
          <div class="pos-categories" id="pos-categories"></div>
          <div class="pos-grid" id="pos-grid"></div>
        </div>
        <div class="pos-cart" id="pos-cart">
          <div class="pos-cart-header">السلة (${state.cart.length})</div>
          <div class="pos-cart-items" id="cart-items"></div>
          <div class="pos-cart-footer" id="cart-footer"></div>
        </div>
      </div>`;
    renderPOSSidebar(categories);
    renderPOSProducts(products);
    renderCart();
  } catch (e) { c.innerHTML = `<div class="card" style="text-align:center;color:var(--danger);padding:40px">خطأ: ${e.message}</div>`; }
}

function renderPOSSidebar(categories) {
  const c = document.getElementById('pos-categories');
  let html = '<button class="pos-cat-btn active" onclick="filterPOSCategory(this,\'\')">الكل</button>';
  categories.forEach(cat => { html += `<button class="pos-cat-btn" onclick="filterPOSCategory(this,'${cat.id}')">${cat.name}</button>`; });
  c.innerHTML = html;
}

function renderPOSProducts(products) {
  const grid = document.getElementById('pos-grid');
  if (!grid) return;
  if (products.length === 0) { grid.innerHTML = '<div style="color:var(--text2);text-align:center;padding:40px;grid-column:1/-1">لا توجد منتجات</div>'; return; }
  let html = '';
  products.forEach(p => {
    const lowStock = p.current_stock <= (p.min_stock || 5);
    html += `<div class="pos-item" onclick="addToCart(${p.id})"><div class="pos-item-name">${p.name}</div><div class="pos-item-price">${fc(p.sell_price)}</div><div class="pos-item-stock" style="color:${lowStock?'var(--danger)':'var(--text2)'}">مخزون: ${p.current_stock}</div></div>`;
  });
  grid.innerHTML = html;
}

function filterPOSProducts() {
  const q = document.getElementById('pos-search').value.toLowerCase();
  const filtered = state.products.filter(p => p.name.toLowerCase().includes(q));
  renderPOSProducts(filtered);
}

function filterPOSCategory(btn, catId) {
  document.querySelectorAll('.pos-cat-btn').forEach(b => b.classList.remove('active'));
  btn.classList.add('active');
  const filtered = catId ? state.products.filter(p => String(p.category_id) === catId) : state.products;
  renderPOSProducts(filtered);
}

function addToCart(productId) {
  const p = state.products.find(x => x.id === productId);
  if (!p) return;
  if (p.current_stock <= 0) { toast('المنتج غير متوفر', 'error'); return; }
  const existing = state.cart.find(x => x.id === productId);
  if (existing) {
    if (existing.qty >= p.current_stock) { toast('الكمية المطلوبة أكثر من المتوفر', 'error'); return; }
    existing.qty++;
  } else { state.cart.push({ id: p.id, name: p.name, price: p.sell_price, qty: 1, stock: p.current_stock }); }
  renderCart();
}

function updateCartQty(productId, delta) {
  const item = state.cart.find(x => x.id === productId);
  if (!item) return;
  const p = state.products.find(x => x.id === productId);
  item.qty += delta;
  if (item.qty <= 0) { state.cart = state.cart.filter(x => x.id !== productId); }
  else if (p && item.qty > p.current_stock) { item.qty = p.current_stock; toast('الكمية القصوى: ' + p.current_stock, 'error'); }
  renderCart();
}

function removeFromCart(productId) { state.cart = state.cart.filter(x => x.id !== productId); renderCart(); }

function renderCart() {
  const items = document.getElementById('cart-items');
  const footer = document.getElementById('cart-footer');
  const header = document.querySelector('.pos-cart-header');
  if (!items) return;
  if (header) header.textContent = 'السلة (' + state.cart.length + ')';
  if (state.cart.length === 0) {
    items.innerHTML = '<div style="color:var(--text2);text-align:center;padding:20px">السلة فارغة</div>';
    if (footer) footer.innerHTML = `<div style="color:var(--text2);text-align:center">أضف منتجات من القائمة</div>`;
    return;
  }
  let html = '';
  let subtotal = 0;
  state.cart.forEach(item => {
    const total = item.price * item.qty;
    subtotal += total;
    html += `<div class="cart-item"><div class="cart-item-name">${item.name}</div><div class="cart-item-qty"><button onclick="updateCartQty(${item.id},-1)">−</button><span>${item.qty}</span><button onclick="updateCartQty(${item.id},1)">+</button></div><div class="cart-item-price">${fc(total)}</div><button class="cart-item-remove" onclick="removeFromCart(${item.id})">✕</button></div>`;
  });
  items.innerHTML = html;
  if (footer) {
    footer.innerHTML = `
      <div class="cart-total-row"><span>المجموع</span><span>${fc(subtotal)}</span></div>
      <div class="cart-total-row"><span>الخصم</span><span><input type="number" id="pos-discount" value="0" min="0" style="width:70px;padding:4px;background:var(--bg);border:1px solid var(--bg3);border-radius:4px;color:var(--text);text-align:center" onchange="updateCartTotal()"></span></div>
      <div class="cart-grand-total" id="cart-grand-total">${fc(subtotal)}</div>
      <button class="checkout-btn" onclick="checkout()">إتمام البيع</button>`;
  }
}

function updateCartTotal() {
  const subtotal = state.cart.reduce((s, i) => s + i.price * i.qty, 0);
  const discount = parseFloat(document.getElementById('pos-discount')?.value || 0);
  const total = Math.max(0, subtotal - discount);
  const gt = document.getElementById('cart-grand-total');
  if (gt) gt.textContent = fc(total);
}

async function checkout() {
  const customerName = prompt('اسم الزبون (اختياري):');
  const customerPhone = prompt('رقم الهاتف (اختياري):');
  const customerAddress = prompt('العنوان (اختياري):');
  const discount = parseFloat(document.getElementById('pos-discount')?.value || 0);
  try {
    const result = await p('/invoices', {
      items: state.cart.map(i => ({ product_id: i.id, product_name: i.name, quantity: i.qty, price: i.price })),
      customer_name: customerName || '', customer_phone: customerPhone || '', customer_address: customerAddress || '',
      discount: discount
    });
    toast('تم إتمام البيع - ' + result.invoice_number, 'success');
    state.cart = [];
    renderCart();
    // Refresh products
    const products = await g('/products');
    state.products = products;
    renderPOSProducts(products);
    if (result.invoice_id) showInvoiceDetail(result.invoice_id);
  } catch (e) { toast('خطأ: ' + e.message, 'error'); }
}

/* ============ INVENTORY ============ */
async function renderInventory(c) {
  c.innerHTML = '<div class="loading">جاري التحميل...</div>';
  try {
    const products = await g('/products');
    c.innerHTML = `
      <div class="search-bar"><input type="text" placeholder="بحث..." oninput="filterInvTable(this.value)" id="inv-search"></div>
      <div class="table-wrap"><table><thead><tr><th>المنتج</th><th>المخزون</th><th>الحد الأدنى</th><th>سعر البيع</th></tr></thead><tbody id="inv-body"></tbody></table></div>`;
    state.products = products;
    renderInvTable(products);
  } catch (e) { c.innerHTML = `<div style="color:var(--danger);padding:20px">خطأ: ${e.message}</div>`; }
}

function renderInvTable(products) {
  const b = document.getElementById('inv-body');
  if (!b) return;
  if (products.length === 0) { b.innerHTML = '<tr><td colspan="4" style="text-align:center;color:var(--text2)">لا توجد منتجات</td></tr>'; return; }
  let html = '';
  products.forEach(p => {
    const low = p.current_stock <= (p.min_stock || 5);
    html += `<tr style="color:${low?'var(--danger)':'inherit'}"><td>${p.name}</td><td>${p.current_stock}</td><td>${p.min_stock || 5}</td><td>${fc(p.sell_price)}</td></tr>`;
  });
  b.innerHTML = html;
}

function filterInvTable(q) {
  q = q.toLowerCase();
  const filtered = state.products.filter(p => p.name.toLowerCase().includes(q));
  renderInvTable(filtered);
}

/* ============ PRODUCTS ============ */
async function renderProducts(c) {
  c.innerHTML = '<div class="loading">جاري التحميل...</div>';
  try {
    const [products, categories] = await Promise.all([g('/products'), g('/categories')]);
    state.products = products; state.categories = categories;
    c.innerHTML = `<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px"><h3>المنتجات</h3><button class="btn btn-primary btn-sm" onclick="showProductForm()">+ إضافة</button></div>
      <div class="search-bar"><input type="text" placeholder="بحث..." oninput="filterProdTable(this.value)" id="prod-search"></div>
      <div class="table-wrap"><table><thead><tr><th>الاسم</th><th>القسم</th><th>المخزون</th><th>البيع</th><th></th></tr></thead><tbody id="prod-body"></tbody></table></div>`;
    renderProdTable(products);
  } catch (e) { c.innerHTML = `<div style="color:var(--danger);padding:20px">خطأ: ${e.message}</div>`; }
}

function renderProdTable(products) {
  const b = document.getElementById('prod-body');
  if (!b) return;
  if (products.length === 0) { b.innerHTML = '<tr><td colspan="5" style="text-align:center;color:var(--text2)">لا توجد منتجات</td></tr>'; return; }
  let html = '';
  products.forEach(p => {
    const cat = state.categories.find(c => c.id === p.category_id);
    html += `<tr><td>${p.name}</td><td style="color:var(--text2)">${cat ? cat.name : '-'}</td><td>${p.current_stock}</td><td>${fc(p.sell_price)}</td><td><button class="btn btn-sm" style="background:var(--danger)" onclick="deleteProduct(${p.id})">حذف</button></td></tr>`;
  });
  b.innerHTML = html;
}

function filterProdTable(q) {
  q = q.toLowerCase();
  const filtered = state.products.filter(p => p.name.toLowerCase().includes(q));
  renderProdTable(filtered);
}

function showProductForm(p) {
  const cats = state.categories;
  const m = document.getElementById('modal-overlay');
  if (m) m.remove();
  const ov = document.createElement('div'); ov.className = 'modal-overlay active'; ov.id = 'modal-overlay';
  ov.onclick = function(e) { if (e.target === ov) ov.remove(); };
  let catOpts = cats.map(c => `<option value="${c.id}">${c.name}</option>`).join('');
  ov.innerHTML = `<div class="modal-content"><div class="modal-header"><h3>${p ? 'تعديل منتج' : 'إضافة منتج'}</h3><button class="modal-close" onclick="this.closest('.modal-overlay').remove()">✕</button></div>
    <div class="form-group"><label>الاسم</label><input class="form-input" id="pf-name" value="${p ? p.name : ''}"></div>
    <div class="form-group"><label>القسم</label><select class="form-select" id="pf-category">${catOpts}</select></div>
    <div class="form-group"><label>سعر الشراء</label><input class="form-input" type="number" id="pf-buy" value="${p ? p.buy_price : 0}"></div>
    <div class="form-group"><label>سعر البيع</label><input class="form-input" type="number" id="pf-sell" value="${p ? p.sell_price : 0}"></div>
    <div class="form-group"><label>المخزون الحالي</label><input class="form-input" type="number" id="pf-stock" value="${p ? p.current_stock : 0}"></div>
    <div class="form-group"><label>الحد الأدنى</label><input class="form-input" type="number" id="pf-min" value="${p ? p.min_stock : 5}"></div>
    <button class="btn btn-primary" style="width:100%" onclick="saveProduct(${p ? p.id : null})">${p ? 'حفظ' : 'إضافة'}</button></div>`;
  document.body.appendChild(ov);
}

async function saveProduct(id) {
  const data = {
    name: document.getElementById('pf-name').value,
    category_id: parseInt(document.getElementById('pf-category').value) || null,
    buy_price: parseFloat(document.getElementById('pf-buy').value) || 0,
    sell_price: parseFloat(document.getElementById('pf-sell').value) || 0,
    current_stock: parseInt(document.getElementById('pf-stock').value) || 0,
    min_stock: parseInt(document.getElementById('pf-min').value) || 5
  };
  try {
    if (id) { await put('/products/' + id, data); toast('تم التحديث', 'success'); }
    else { await p('/products', data); toast('تمت الإضافة', 'success'); }
    document.getElementById('modal-overlay').remove();
    const products = await g('/products');
    state.products = products;
    renderProdTable(products);
  } catch (e) { toast('خطأ: ' + e.message, 'error'); }
}

async function deleteProduct(id) {
  if (!confirm('تأكيد حذف المنتج؟')) return;
  try { await del('/products/' + id); toast('تم الحذف', 'success'); const products = await g('/products'); state.products = products; renderProdTable(products); } catch (e) { toast('خطأ: ' + e.message, 'error'); }
}

/* ============ CUSTOMERS ============ */
async function renderCustomers(c) {
  c.innerHTML = '<div class="loading">جاري التحميل...</div>';
  try {
    const customers = await g('/customers');
    c.innerHTML = `<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px"><h3>الزبائن</h3><button class="btn btn-primary btn-sm" onclick="showCustomerForm()">+ إضافة</button></div>
      <div class="table-wrap"><table><thead><tr><th>الاسم</th><th>الهاتف</th><th>العنوان</th></tr></thead><tbody id="cust-body"></tbody></table></div>`;
    const b = document.getElementById('cust-body');
    if (customers.length === 0) { b.innerHTML = '<tr><td colspan="3" style="text-align:center;color:var(--text2)">لا يوجد زبائن</td></tr>'; }
    else {
      let html = '';
      customers.forEach(cus => { html += `<tr onclick="showCustomerForm(${cus.id})"><td>${cus.name}</td><td>${cus.phone || '-'}</td><td style="color:var(--text2)">${cus.address || '-'}</td></tr>`; });
      b.innerHTML = html;
    }
  } catch (e) { c.innerHTML = `<div style="color:var(--danger);padding:20px">خطأ: ${e.message}</div>`; }
}

function showCustomerForm(id) {
  const cus = id ? state.customers.find(x => x.id === id) : null;
  const ov = document.createElement('div'); ov.className = 'modal-overlay active'; ov.id = 'modal-overlay';
  ov.onclick = function(e) { if (e.target === ov) ov.remove(); };
  ov.innerHTML = `<div class="modal-content"><div class="modal-header"><h3>${cus ? 'تعديل زبون' : 'إضافة زبون'}</h3><button class="modal-close" onclick="this.closest('.modal-overlay').remove()">✕</button></div>
    <div class="form-group"><label>الاسم</label><input class="form-input" id="cf-name" value="${cus ? cus.name : ''}"></div>
    <div class="form-group"><label>الهاتف</label><input class="form-input" id="cf-phone" value="${cus ? cus.phone : ''}"></div>
    <div class="form-group"><label>العنوان</label><input class="form-input" id="cf-address" value="${cus ? cus.address : ''}"></div>
    <button class="btn btn-primary" style="width:100%" onclick="saveCustomer(${cus ? cus.id : null})">${cus ? 'حفظ' : 'إضافة'}</button></div>`;
  document.body.appendChild(ov);
}

async function saveCustomer(id) {
  const data = {
    name: document.getElementById('cf-name').value,
    phone: document.getElementById('cf-phone').value,
    address: document.getElementById('cf-address').value
  };
  try {
    if (id) { await put('/customers/' + id, data); toast('تم التحديث', 'success'); }
    else { await p('/customers', data); toast('تمت الإضافة', 'success'); }
    document.getElementById('modal-overlay').remove();
    const customers = await g('/customers');
    state.customers = customers;
    renderCustomers(document.getElementById('page-content'));
  } catch (e) { toast('خطأ: ' + e.message, 'error'); }
}

/* ============ INVOICES ============ */
async function renderInvoices(c) {
  c.innerHTML = '<div class="loading">جاري التحميل...</div>';
  try {
    const invoices = await g('/invoices');
    c.innerHTML = `<div class="search-bar"><input type="text" placeholder="بحث عن فاتورة..." oninput="filterInvTable2(this.value)" id="inv2-search"></div>
      <div class="table-wrap"><table><thead><tr><th>الرقم</th><th>الزبون</th><th>المجموع</th><th>التاريخ</th></tr></thead><tbody id="inv2-body"></tbody></table></div>`;
    state.invoices = invoices;
    renderInvTable2(invoices);
  } catch (e) { c.innerHTML = `<div style="color:var(--danger);padding:20px">خطأ: ${e.message}</div>`; }
}

function renderInvTable2(invoices) {
  const b = document.getElementById('inv2-body');
  if (!b) return;
  if (invoices.length === 0) { b.innerHTML = '<tr><td colspan="4" style="text-align:center;color:var(--text2)">لا توجد فواتير</td></tr>'; return; }
  let html = '';
  invoices.forEach(inv => { html += `<tr onclick="showInvoiceDetail(${inv.id})"><td>${inv.invoice_number}</td><td>${inv.customer_name || 'نقدي'}</td><td>${fc(inv.grand_total)}</td><td style="color:var(--text2);font-size:11px">${fd(inv.created_at)}</td></tr>`; });
  b.innerHTML = html;
}

function filterInvTable2(q) {
  q = q.toLowerCase();
  const filtered = state.invoices.filter(i => i.invoice_number.toLowerCase().includes(q) || (i.customer_name || '').toLowerCase().includes(q));
  renderInvTable2(filtered);
}

async function showInvoiceDetail(id) {
  try {
    const inv = await g('/invoices/' + id);
    const ov = document.createElement('div'); ov.className = 'modal-overlay active'; ov.id = 'modal-overlay';
    ov.onclick = function(e) { if (e.target === ov) ov.remove(); };
    let itemsHtml = '';
    inv.items.forEach(item => {
      itemsHtml += `<div class="row"><span>${item.product_name} × ${item.quantity}</span><span>${fc(item.total)}</span></div>`;
    });
    ov.innerHTML = `<div class="modal-content"><div class="modal-header"><h3>فاتورة ${inv.invoice_number}</h3><button class="modal-close" onclick="this.closest('.modal-overlay').remove()">✕</button></div>
      <div class="invoice-detail">
        <div class="row"><span>التاريخ</span><span>${fn(inv.created_at)}</span></div>
        <div class="row"><span>الزبون</span><span>${inv.customer_name || 'نقدي'}</span></div>
        ${inv.customer_address ? `<div class="row"><span>العنوان</span><span>${inv.customer_address}</span></div>` : ''}
        <div style="margin:12px 0;border-top:1px solid var(--bg3)"></div>
        ${itemsHtml}
        <div style="margin:8px 0;border-top:1px solid var(--bg3)"></div>
        <div class="row"><span>المجموع</span><span>${fc(inv.total)}</span></div>
        ${inv.discount > 0 ? `<div class="row" style="color:var(--danger)"><span>الخصم</span><span>-${fc(inv.discount)}</span></div>` : ''}
        <div class="row cart-grand-total"><span>الإجمالي</span><span>${fc(inv.grand_total)}</span></div>
        <div class="invoice-actions">
          <button class="btn btn-primary btn-sm" onclick="printInvoice(${id})" style="flex:1">🖨️ طباعة</button>
          <button class="btn btn-success btn-sm" onclick="saveInvoiceFile(${id})" style="flex:1">💾 حفظ</button>
          <button class="btn btn-sm" onclick="shareInvoiceFile(${id})" style="flex:1;background:var(--warning);color:#000">📤 مشاركة</button>
        </div>
      </div></div>`;
    document.body.appendChild(ov);
  } catch (e) { toast('خطأ: ' + e.message, 'error'); }
}

async function printInvoice(id) {
  try {
    const inv = await g('/invoices/' + id);
    const printWin = window.open('', '_blank');
    let itemsHtml = '<table style="width:100%;border-collapse:collapse;margin:12px 0"><tr style="background:#f1f5f9"><th style="padding:6px;text-align:right;border:1px solid #ddd">المنتج</th><th style="padding:6px;text-align:center;border:1px solid #ddd">الكمية</th><th style="padding:6px;text-align:left;border:1px solid #ddd">السعر</th><th style="padding:6px;text-align:left;border:1px solid #ddd">المجموع</th></tr>';
    inv.items.forEach(item => {
      itemsHtml += `<tr><td style="padding:6px;border:1px solid #ddd">${item.product_name}</td><td style="padding:6px;border:1px solid #ddd;text-align:center">${item.quantity}</td><td style="padding:6px;border:1px solid #ddd;text-align:left">${fc(item.price)}</td><td style="padding:6px;border:1px solid #ddd;text-align:left">${fc(item.total)}</td></tr>`;
    });
    itemsHtml += '</table>';
    printWin.document.write(`
      <html dir="rtl"><head><meta charset="utf-8"><title>فاتورة ${inv.invoice_number}</title>
      <style>body{font-family:sans-serif;padding:20px;color:#333}h2{color:#0ea5e9}.total{font-size:18px;font-weight:bold;color:#0ea5e9}</style></head>
      <body><h2>${state.settings.store_name || 'Uhtred Store'}</h2>
      <p>فاتورة: ${inv.invoice_number}<br>تاريخ: ${fn(inv.created_at)}<br>زبون: ${inv.customer_name || 'نقدي'}</p>
      ${itemsHtml}
      <p>المجموع: ${fc(inv.total)}<br>${inv.discount > 0 ? 'الخصم: -' + fc(inv.discount) + '<br>' : ''}<span class="total">الإجمالي: ${fc(inv.grand_total)}</span></p>
      <p style="margin-top:20px;color:#999;font-size:12px">${state.settings.store_note || ''}</p>
      <script>window.print();window.close();<\/script></body></html>`);
    printWin.document.close();
  } catch (e) { toast('خطأ: ' + e.message, 'error'); }
}

async function saveInvoiceFile(id) {
  try {
    const inv = await g('/invoices/' + id);
    let html = buildInvoiceHtml(inv);
    const base64 = btoa(unescape(encodeURIComponent(html)));
    if (typeof Android !== 'undefined' && Android.saveFile) {
      Android.saveFile('فاتورة_' + inv.invoice_number + '.html', base64, 'text/html');
    } else {
      const blob = new Blob([html], { type: 'text/html' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url; a.download = 'فاتورة_' + inv.invoice_number + '.html';
      a.click(); URL.revokeObjectURL(url);
      toast('تم التحميل', 'success');
    }
  } catch (e) { toast('خطأ: ' + e.message, 'error'); }
}

async function shareInvoiceFile(id) {
  try {
    const inv = await g('/invoices/' + id);
    const html = buildInvoiceHtml(inv);
    const base64 = btoa(unescape(encodeURIComponent(html)));
    if (typeof Android !== 'undefined' && Android.shareFile) {
      Android.shareFile('فاتورة_' + inv.invoice_number + '.html', base64, 'text/html');
    } else if (navigator.share) {
      const blob = new Blob([html], { type: 'text/html' });
      const file = new File([blob], 'فاتورة_' + inv.invoice_number + '.html', { type: 'text/html' });
      navigator.share({ files: [file], title: 'فاتورة ' + inv.invoice_number });
    } else {
      toast('المشاركة غير متوفرة على هذا الجهاز', 'error');
    }
  } catch (e) { toast('خطأ: ' + e.message, 'error'); }
}

function buildInvoiceHtml(inv) {
  let itemsHtml = '';
  inv.items.forEach(item => {
    itemsHtml += `<tr><td style="padding:6px;border:1px solid #ddd">${item.product_name}</td><td style="padding:6px;border:1px solid #ddd;text-align:center">${item.quantity}</td><td style="padding:6px;border:1px solid #ddd;text-align:left">${fc(item.price)}</td><td style="padding:6px;border:1px solid #ddd;text-align:left">${fc(item.total)}</td></tr>`;
  });
  return `<!DOCTYPE html><html dir="rtl"><head><meta charset="utf-8"><title>فاتورة ${inv.invoice_number}</title>
    <style>body{font-family:sans-serif;padding:20px;color:#333;max-width:400px;margin:auto}h2{color:#0ea5e9}.total{font-size:18px;font-weight:bold;color:#0ea5e9}</style></head>
    <body><h2>${state.settings.store_name || 'Uhtred Store'}</h2>
    <p>فاتورة: ${inv.invoice_number}<br>تاريخ: ${fn(inv.created_at)}<br>زبون: ${inv.customer_name || 'نقدي'}</p>
    <table style="width:100%;border-collapse:collapse;margin:12px 0">
    <tr style="background:#f1f5f9"><th style="padding:6px;text-align:right;border:1px solid #ddd">المنتج</th><th style="padding:6px;text-align:center;border:1px solid #ddd">الكمية</th><th style="padding:6px;text-align:left;border:1px solid #ddd">السعر</th><th style="padding:6px;text-align:left;border:1px solid #ddd">المجموع</th></tr>
    ${itemsHtml}</table>
    <p>المجموع: ${fc(inv.total)}<br>${inv.discount > 0 ? 'الخصم: -' + fc(inv.discount) + '<br>' : ''}<span class="total">الإجمالي: ${fc(inv.grand_total)}</span></p>
    <p style="margin-top:20px;color:#999;font-size:12px">${state.settings.store_note || ''}</p></body></html>`;
}

/* ============ REPORTS ============ */
async function renderReports(c) {
  c.innerHTML = '<div class="loading">جاري التحميل...</div>';
  try {
    const data = await g('/stats');
    c.innerHTML = `
      <div class="stats-grid">
        <div class="stat-card"><div class="label">مبيعات اليوم</div><div class="value" style="color:var(--success)">${fc(data.today_sales || 0)}</div></div>
        <div class="stat-card"><div class="label">مبيعات الأسبوع</div><div class="value" style="color:var(--primary)">${fc(data.week_sales || 0)}</div></div>
        <div class="stat-card"><div class="label">مبيعات الشهر</div><div class="value" style="color:var(--primary)">${fc(data.month_sales || 0)}</div></div>
        <div class="stat-card"><div class="label">إجمالي المبيعات</div><div class="value">${fc(data.total_sales || 0)}</div></div>
        <div class="stat-card"><div class="label">عدد الفواتير</div><div class="value">${data.total_invoices || 0}</div></div>
        <div class="stat-card"><div class="label">المنتجات المبيعة</div><div class="value">${data.total_items_sold || 0}</div></div>
      </div>`;
  } catch (e) { c.innerHTML = `<div style="color:var(--danger);padding:20px">خطأ: ${e.message}</div>`; }
}

/* ============ STOCK ============ */
function renderStock(c) {
  c.innerHTML = `
    <h3 style="margin-bottom:12px">إضافة مخزون</h3>
    <div class="form-group"><label>المنتج</label><select class="form-select" id="st-product"></select></div>
    <div class="form-group"><label>الكمية</label><input class="form-input" type="number" id="st-qty" min="1" value="1"></div>
    <div class="form-group"><label>المرجع</label><input class="form-input" id="st-ref" placeholder="رقم الفاتورة أو المورد"></div>
    <div class="form-group"><label>ملاحظات</label><textarea class="form-textarea" id="st-notes"></textarea></div>
    <button class="btn btn-primary" style="width:100%" onclick="addStock()">إضافة</button>
    <h3 style="margin:20px 0 12px">حركة المخزون</h3>
    <div id="stock-movements"></div>`;
  loadStockData();
}

async function loadStockData() {
  try {
    const [products, movements] = await Promise.all([g('/products'), g('/stock')]);
    const sel = document.getElementById('st-product');
    if (sel) {
      products.forEach(p => {
        const opt = document.createElement('option'); opt.value = p.id; opt.textContent = p.name + ' (مخزون: ' + p.current_stock + ')';
        sel.appendChild(opt);
      });
    }
    const m = document.getElementById('stock-movements');
    if (!m) return;
    if (movements.length === 0) { m.innerHTML = '<div style="color:var(--text2);text-align:center;padding:20px">لا توجد حركات</div>'; return; }
    let html = '<div class="table-wrap"><table><thead><tr><th>المنتج</th><th>النوع</th><th>الكمية</th><th>التاريخ</th></tr></thead><tbody>';
    movements.slice(0, 50).forEach(mv => {
      html += `<tr><td>${mv.product_name || '#' + mv.product_id}</td><td>${mv.type === 'in' ? 'إضافة' : 'بيع'}</td><td style="color:${mv.type === 'in' ? 'var(--success)' : 'var(--danger)'}">${mv.type === 'in' ? '+' : '-'}${mv.quantity}</td><td style="color:var(--text2);font-size:11px">${fn(mv.created_at)}</td></tr>`;
    });
    html += '</tbody></table></div>';
    m.innerHTML = html;
  } catch (e) { toast('خطأ: ' + e.message, 'error'); }
}

async function addStock() {
  const productId = parseInt(document.getElementById('st-product').value);
  const qty = parseInt(document.getElementById('st-qty').value);
  const reference = document.getElementById('st-ref').value;
  const notes = document.getElementById('st-notes').value;
  if (!productId || !qty) { toast('اختر المنتج والكمية', 'error'); return; }
  try {
    await p('/stock', { product_id: productId, quantity: qty, type: 'in', reference, notes });
    toast('تمت إضافة المخزون', 'success');
    document.getElementById('st-qty').value = '1';
    document.getElementById('st-ref').value = '';
    document.getElementById('st-notes').value = '';
    loadStockData();
    const products = await g('/products');
    state.products = products;
  } catch (e) { toast('خطأ: ' + e.message, 'error'); }
}

/* ============ SETTINGS ============ */
async function renderSettings(c) {
  c.innerHTML = '<div class="loading">جاري التحميل...</div>';
  try {
    const settings = await g('/settings');
    state.settings = {};
    settings.forEach(s => { state.settings[s.key] = s.value; });
    c.innerHTML = `
      <div class="card">
        <div class="card-title">إعدادات المتجر</div>
        <div class="form-group"><label>اسم المتجر</label><input class="form-input" id="s-name" value="${state.settings.store_name || ''}"></div>
        <div class="form-group"><label>رقم الهاتف</label><input class="form-input" id="s-phone" value="${state.settings.store_phone || ''}"></div>
        <div class="form-group"><label>العنوان</label><input class="form-input" id="s-address" value="${state.settings.store_address || ''}"></div>
        <div class="form-group"><label>ملاحظة الفاتورة</label><textarea class="form-textarea" id="s-note">${state.settings.store_note || ''}</textarea></div>
        <button class="btn btn-primary" style="width:100%" onclick="saveSettings()">حفظ الإعدادات</button>
      </div>
      <div class="card">
        <div class="card-title">عنوان الخادم</div>
        <div style="font-size:13px;color:var(--text2);margin-bottom:8px">${window.location.hostname}:${window.location.port || 5000}</div>
        <button class="btn btn-sm" style="background:var(--bg3);color:var(--text);width:100%" onclick="changeServerIP()">تغيير عنوان IP</button>
      </div>`;
  } catch (e) { c.innerHTML = `<div style="color:var(--danger);padding:20px">خطأ: ${e.message}</div>`; }
}

async function saveSettings() {
  try {
    await put('/settings', {
      store_name: document.getElementById('s-name').value,
      store_phone: document.getElementById('s-phone').value,
      store_address: document.getElementById('s-address').value,
      store_note: document.getElementById('s-note').value
    });
    toast('تم حفظ الإعدادات', 'success');
  } catch (e) { toast('خطأ: ' + e.message, 'error'); }
}

function changeServerIP() {
  const ip = prompt('أدخل عنوان IP الجديد:', window.location.hostname);
  if (ip) {
    const newUrl = 'http://' + ip + ':5000';
    localStorage.setItem('server_url', newUrl);
    window.location.href = newUrl;
  }
}

/* ============ INIT ============ */
document.addEventListener('DOMContentLoaded', () => {
  const urlParams = new URLSearchParams(window.location.search);
  if (urlParams.get('page')) {
    state.currentPage = urlParams.get('page');
  }
  navigateTo(state.currentPage);
});
