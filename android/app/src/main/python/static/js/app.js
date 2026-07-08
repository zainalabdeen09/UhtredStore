const state = {
  token: localStorage.getItem('token'),
  currentPage: 'dashboard',
  cart: [],
  products: [],
  customers: [],
  invoices: [],
  categories: [],
  settings: {}
};

const API_BASE = '';

function getHeaders() {
  return { 'Content-Type': 'application/json' };
}

async function apiGet(endpoint) {
  const res = await fetch(API_BASE + '/api' + endpoint, { headers: getHeaders() });
  if (!res.ok) { const e = await res.json().catch(() => ({ error: res.statusText })); throw new Error(e.error || 'Request failed'); }
  return res.json();
}

async function apiPost(endpoint, data) {
  const res = await fetch(API_BASE + '/api' + endpoint, { method: 'POST', headers: getHeaders(), body: JSON.stringify(data) });
  if (!res.ok) { const e = await res.json().catch(() => ({ error: res.statusText })); throw new Error(e.error || 'Request failed'); }
  return res.json();
}

async function apiPut(endpoint, data) {
  const res = await fetch(API_BASE + '/api' + endpoint, { method: 'PUT', headers: getHeaders(), body: JSON.stringify(data) });
  if (!res.ok) { const e = await res.json().catch(() => ({ error: res.statusText })); throw new Error(e.error || 'Request failed'); }
  return res.json();
}

async function apiDelete(endpoint) {
  const res = await fetch(API_BASE + '/api' + endpoint, { method: 'DELETE', headers: getHeaders() });
  if (!res.ok) { const e = await res.json().catch(() => ({ error: res.statusText })); throw new Error(e.error || 'Request failed'); }
  return res.json();
}

function formatCurrency(amount) {
  return Number(amount).toLocaleString('ar-IQ') + ' د.ع';
}

function formatDate(iso) {
  if (!iso) return '';
  const d = new Date(iso);
  return d.toLocaleDateString('ar-IQ', { year: 'numeric', month: 'short', day: 'numeric' });
}

function escapeHtml(str) {
  if (!str) return '';
  const div = document.createElement('div');
  div.textContent = str;
  return div.innerHTML;
}

function showToast(msg, type) {
  type = type || 'info';
  const icons = { success: 'fa-check-circle', error: 'fa-times-circle', warning: 'fa-exclamation-triangle', info: 'fa-info-circle' };
  const container = document.getElementById('toastContainer');
  const el = document.createElement('div');
  el.className = 'toast toast-' + type;
  el.innerHTML = '<i class="fas ' + (icons[type] || icons.info) + '"></i> ' + escapeHtml(msg);
  container.appendChild(el);
  setTimeout(() => { el.classList.add('toast-removing'); setTimeout(() => el.remove(), 300); }, 3000);
}

function showModal(html, title) {
  document.getElementById('modalTitle').textContent = title || '';
  document.getElementById('modalBody').innerHTML = html;
  document.getElementById('modalOverlay').style.display = 'flex';
}

function closeModal() {
  document.getElementById('modalOverlay').style.display = 'none';
}

async function handleLogin() {
  const username = document.getElementById('loginUsername').value.trim();
  const password = document.getElementById('loginPassword').value.trim();
  const errEl = document.getElementById('loginError');
  errEl.textContent = '';
  if (!username || !password) { errEl.textContent = 'الرجاء إدخال اسم المستخدم وكلمة المرور'; return; }
  try {
    const res = await apiPost('/auth/login', { username, password });
    if (res.success) {
      localStorage.setItem('token', '1');
      state.token = '1';
      document.getElementById('loginOverlay').style.display = 'none';
      document.getElementById('app').style.display = 'flex';
      initNav();
      navigate('dashboard');
    } else {
      errEl.textContent = 'اسم المستخدم أو كلمة المرور غير صحيحة';
    }
  } catch (e) {
    errEl.textContent = e.message || 'خطأ في الاتصال بالخادم';
  }
}

document.addEventListener('keydown', function(e) {
  if (e.key === 'Enter' && document.getElementById('loginOverlay').style.display !== 'none') {
    const pw = document.getElementById('loginPassword');
    if (document.activeElement === pw || document.activeElement === document.getElementById('loginUsername')) {
      handleLogin();
    }
  }
});

function logout() {
  localStorage.removeItem('token');
  state.token = null;
  state.cart = [];
  document.getElementById('app').style.display = 'none';
  document.getElementById('loginOverlay').style.display = 'flex';
  document.getElementById('loginUsername').value = '';
  document.getElementById('loginPassword').value = '';
}

const navItems = [
  { id: 'dashboard', label: 'الرئيسية', icon: 'fa-chart-pie' },
  { id: 'pos', label: 'نقطة البيع', icon: 'fa-cash-register' },
  { id: 'products', label: 'المنتجات', icon: 'fa-box' },
  { id: 'inventory', label: 'المخزون', icon: 'fa-warehouse' },
  { id: 'stockadd', label: 'إضافة مخزون', icon: 'fa-plus-circle' },
  { id: 'invoices', label: 'الفواتير', icon: 'fa-file-invoice' },
  { id: 'customers', label: 'العملاء', icon: 'fa-users' },
  { id: 'reports', label: 'التقارير', icon: 'fa-chart-bar' },
  { id: 'settings', label: 'الإعدادات', icon: 'fa-cog' }
];

function initNav() {
  let sidebarHtml = '';
  let bottomHtml = '';
  navItems.forEach(function(item) {
    const active = item.id === state.currentPage ? 'active' : '';
    sidebarHtml += '<div class="nav-item ' + active + '" onclick="navigate(\'' + item.id + '\')"><i class="fas ' + item.icon + '"></i><span>' + item.label + '</span></div>';
    bottomHtml += '<div class="nav-item ' + active + '" onclick="navigate(\'' + item.id + '\')"><i class="fas ' + item.icon + '"></i><span>' + item.label + '</span></div>';
  });
  document.getElementById('sidebarNav').innerHTML = sidebarHtml;
  document.getElementById('bottomNav').innerHTML = bottomHtml;
}

function updateNav(page) {
  state.currentPage = page;
  document.querySelectorAll('.nav-item').forEach(function(el) {
    el.classList.toggle('active', el.getAttribute('onclick') === "navigate('" + page + "')");
  });
}

function navigate(page) {
  state.currentPage = page;
  updateNav(page);
  const loaders = {
    dashboard: loadDashboard,
    pos: loadPOS,
    products: loadProducts,
    inventory: loadInventory,
    stockadd: loadStockAdd,
    invoices: loadInvoices,
    customers: loadCustomers,
    reports: loadReports,
    settings: loadSettings
  };
  const fn = loaders[page];
  if (fn) fn();
}

function showLoading() {
  document.getElementById('content').innerHTML = '<div class="loading-state"><i class="fas fa-spinner"></i><p style="margin-top:10px;color:var(--text-muted)">جاري التحميل...</p></div>';
}

function showError(msg) {
  document.getElementById('content').innerHTML = '<div class="error-state"><i class="fas fa-exclamation-circle"></i><p>' + escapeHtml(msg) + '</p></div>';
}

function renderContent(html) {
  document.getElementById('content').innerHTML = html;
}

/* ===== DASHBOARD ===== */
async function loadDashboard() {
  showLoading();
  try {
    const [stats, invoices] = await Promise.all([
      apiGet('/stats/dashboard'),
      apiGet('/invoices?search=')
    ]);
    const recent = invoices.slice(0, 20);
    renderContent(renderDashboard(stats, recent));
  } catch (e) {
    showError(e.message);
  }
}

function renderDashboard(stats, invoices) {
  return '<div class="page-header"><h1><i class="fas fa-chart-pie"></i> لوحة التحكم</h1></div>' +
    '<div class="stats-grid">' +
    statCard('fa-money-bill-wave', 'مبيعات اليوم', formatCurrency(stats.today_sales), 'success') +
    statCard('fa-shopping-cart', 'طلبات اليوم', stats.today_orders, 'accent') +
    statCard('fa-box', 'إجمالي المنتجات', stats.total_products, 'accent') +
    statCard('fa-exclamation-triangle', 'مخزون منخفض', stats.low_stock, 'danger') +
    statCard('fa-users', 'إجمالي العملاء', stats.total_customers, 'accent') +
    statCard('fa-chart-line', 'مبيعات الشهر', formatCurrency(stats.month_sales), 'success') +
    '</div>' +
    '<div class="card"><div class="card-title"><i class="fas fa-file-invoice"></i> آخر الفواتير</div>' +
    (invoices.length === 0 ? '<div class="empty-table-msg">لا توجد فواتير بعد</div>' :
    '<div class="table-wrap"><table><thead><tr><th>رقم الفاتورة</th><th>الزبون</th><th>الإجمالي</th><th>التاريخ</th></tr></thead><tbody>' +
    invoices.map(function(inv) {
      return '<tr><td>' + escapeHtml(inv.invoice_number) + '</td><td>' + escapeHtml(inv.customer_name || '-') + '</td><td>' + formatCurrency(inv.grand_total) + '</td><td>' + formatDate(inv.created_at) + '</td></tr>';
    }).join('') +
    '</tbody></table></div>') + '</div>';
}

function statCard(icon, label, value, color) {
  return '<div class="stat-card ' + color + '"><div class="stat-icon"><i class="fas ' + icon + '"></i></div><div class="stat-label">' + label + '</div><div class="stat-value">' + value + '</div></div>';
}

/* ===== POS ===== */
async function loadPOS() {
  showLoading();
  try {
    const [products, categories] = await Promise.all([
      apiGet('/products?search='),
      apiGet('/categories')
    ]);
    state.products = products;
    state.categories = categories;
    renderContent(renderPOS(products, categories));
    setupPOSEvents();
    updateCartUI();
  } catch (e) {
    showError(e.message);
  }
}

function renderPOS(products, categories) {
  var catOptions = '<option value="">جميع التصنيفات</option>';
  categories.forEach(function(c) {
    catOptions += '<option value="' + c.id + '">' + escapeHtml(c.name) + '</option>';
  });
  var productCards = products.map(function(p) {
    var stockClass = p.current_stock <= 0 ? 'out' : (p.current_stock < p.min_stock ? 'low' : '');
    var disabled = p.current_stock <= 0 ? 'disabled' : '';
    return '<div class="product-card ' + disabled + '" data-id="' + p.id + '">' +
      '<div class="p-category">' + escapeHtml(p.category_name || '') + '</div>' +
      '<div class="p-name">' + escapeHtml(p.name) + '</div>' +
      '<div class="p-price">' + formatCurrency(p.sell_price) + '</div>' +
      '<div class="p-stock ' + stockClass + '">المخزون: ' + p.current_stock + '</div>' +
      '<button class="add-btn" onclick="addToCart(' + p.id + ')"><i class="fas fa-plus"></i> إضافة</button>' +
      '</div>';
  }).join('');

  return '<div class="pos-layout">' +
    '<div class="pos-products">' +
    '<div class="product-search">' +
    '<input type="text" id="posSearch" placeholder="بحث عن منتج..." oninput="filterPOS()">' +
    '<select id="posCategory" onchange="filterPOS()">' + catOptions + '</select>' +
    '</div>' +
    '<div class="product-grid" id="posGrid">' +
    (products.length === 0 ? '<div class="empty-state" style="grid-column:1/-1"><i class="fas fa-box-open"></i><p>لا توجد منتجات</p></div>' : productCards) +
    '</div>' +
    '</div>' +
    '<div class="pos-cart" id="posCartPanel">' +
    '<h3><i class="fas fa-shopping-cart"></i> سلة المشتريات <span class="cart-count" id="cartCount">0</span></h3>' +
    '<div class="cart-customer">' +
    '<input type="text" id="custName" placeholder="اسم الزبون">' +
    '<input type="text" id="custPhone" placeholder="رقم الهاتف">' +
    '<input type="text" id="custAddress" placeholder="العنوان">' +
    '</div>' +
    '<div class="cart-items" id="cartItems"><div class="empty-table-msg">أضف منتجات إلى السلة</div></div>' +
    '<div class="cart-total" id="cartTotal"><div class="total-row"><span>المجموع</span><span id="cartSubtotal">0 د.ع</span></div><div class="total-row grand"><span>الإجمالي</span><span id="cartGrandTotal">0 د.ع</span></div></div>' +
    '<div class="cart-actions">' +
    '<button class="btn btn-success" onclick="saveInvoice(false)"><i class="fas fa-save"></i> حفظ</button>' +
    '<button class="btn btn-primary" onclick="saveInvoice(true)"><i class="fas fa-print"></i> حفظ وطباعة</button>' +
    '<button class="btn btn-outline" onclick="clearCart()"><i class="fas fa-trash"></i> تفريغ</button>' +
    '</div>' +
    '</div>' +
    '</div>';
}

function setupPOSEvents() {
  document.getElementById('posSearch').addEventListener('input', filterPOS);
  document.getElementById('posCategory').addEventListener('change', filterPOS);
}

function filterPOS() {
  var search = document.getElementById('posSearch').value.trim().toLowerCase();
  var catId = document.getElementById('posCategory').value;
  var filtered = state.products.filter(function(p) {
    if (search && !p.name.toLowerCase().includes(search)) return false;
    if (catId && p.category_id != catId) return false;
    return true;
  });
  var grid = document.getElementById('posGrid');
  if (filtered.length === 0) {
    grid.innerHTML = '<div class="empty-state" style="grid-column:1/-1"><i class="fas fa-box-open"></i><p>لا توجد منتجات مطابقة</p></div>';
    return;
  }
  grid.innerHTML = filtered.map(function(p) {
    var stockClass = p.current_stock <= 0 ? 'out' : (p.current_stock < p.min_stock ? 'low' : '');
    var disabled = p.current_stock <= 0 ? 'disabled' : '';
    return '<div class="product-card ' + disabled + '" data-id="' + p.id + '">' +
      '<div class="p-category">' + escapeHtml(p.category_name || '') + '</div>' +
      '<div class="p-name">' + escapeHtml(p.name) + '</div>' +
      '<div class="p-price">' + formatCurrency(p.sell_price) + '</div>' +
      '<div class="p-stock ' + stockClass + '">المخزون: ' + p.current_stock + '</div>' +
      '<button class="add-btn" onclick="addToCart(' + p.id + ')"><i class="fas fa-plus"></i> إضافة</button>' +
      '</div>';
  }).join('');
}

function addToCart(productId) {
  var product = state.products.find(function(p) { return p.id === productId; });
  if (!product || product.current_stock <= 0) return;
  var existing = state.cart.find(function(c) { return c.product_id === productId; });
  if (existing) {
    if (existing.quantity >= product.current_stock) {
      showToast('الكمية المتاحة غير كافية', 'warning');
      return;
    }
    existing.quantity += 1;
  } else {
    state.cart.push({
      product_id: product.id,
      product_name: product.name,
      quantity: 1,
      price: product.sell_price,
      size: '',
      color: '',
      print_location: ''
    });
  }
  updateCartUI();
  showToast('تمت إضافة ' + product.name + ' إلى السلة', 'success');
}

function removeFromCart(index) {
  state.cart.splice(index, 1);
  updateCartUI();
}

function updateCartItem(index, field, value) {
  if (state.cart[index]) {
    state.cart[index][field] = value;
  }
}

function updateCartUI() {
  var container = document.getElementById('cartItems');
  var countEl = document.getElementById('cartCount');
  var subtotalEl = document.getElementById('cartSubtotal');
  var grandEl = document.getElementById('cartGrandTotal');
  if (!container) return;
  if (state.cart.length === 0) {
    container.innerHTML = '<div class="empty-table-msg">أضف منتجات إلى السلة</div>';
    if (countEl) countEl.textContent = '0';
    if (subtotalEl) subtotalEl.textContent = formatCurrency(0);
    if (grandEl) grandEl.textContent = formatCurrency(0);
    return;
  }
  if (countEl) countEl.textContent = state.cart.length;
  var subtotal = 0;
  var rows = state.cart.map(function(item, i) {
    var total = item.quantity * item.price;
    subtotal += total;
    return '<tr>' +
      '<td>' + escapeHtml(item.product_name) + '</td>' +
      '<td><input class="qty-input" type="number" min="1" value="' + item.quantity + '" onchange="updateCartQty(' + i + ',this.value)"></td>' +
      '<td>' + formatCurrency(item.price) + '</td>' +
      '<td>' + formatCurrency(total) + '</td>' +
      '<td><button class="remove-btn" onclick="removeFromCart(' + i + ')"><i class="fas fa-times"></i></button></td>' +
      '</tr>';
  }).join('');
  container.innerHTML = '<table><thead><tr><th>المنتج</th><th>الكمية</th><th>السعر</th><th>المجموع</th><th></th></tr></thead><tbody>' + rows + '</tbody></table>';
  if (subtotalEl) subtotalEl.textContent = formatCurrency(subtotal);
  if (grandEl) grandEl.textContent = formatCurrency(subtotal);
}

function updateCartQty(index, val) {
  var qty = parseInt(val) || 1;
  if (qty < 1) qty = 1;
  var item = state.cart[index];
  if (item) {
    var product = state.products.find(function(p) { return p.id === item.product_id; });
    if (product && qty > product.current_stock) {
      showToast('الكمية المتاحة غير كافية. الحد الأقصى: ' + product.current_stock, 'warning');
      qty = product.current_stock;
    }
    item.quantity = qty;
  }
  updateCartUI();
}

function clearCart() {
  if (state.cart.length === 0) return;
  state.cart = [];
  updateCartUI();
  showToast('تم تفريغ السلة', 'info');
}

async function saveInvoice(shouldPrint) {
  if (state.cart.length === 0) { showToast('السلة فارغة', 'warning'); return; }
  var customerName = (document.getElementById('custName') && document.getElementById('custName').value.trim()) || '';
  var customerPhone = (document.getElementById('custPhone') && document.getElementById('custPhone').value.trim()) || '';
  var customerAddress = (document.getElementById('custAddress') && document.getElementById('custAddress').value.trim()) || '';
  var items = state.cart.map(function(item) {
    return {
      product_id: item.product_id,
      product_name: item.product_name,
      quantity: item.quantity,
      price: item.price,
      size: item.size || '',
      color: item.color || '',
      print_location: item.print_location || ''
    };
  });
  try {
    var result = await apiPost('/invoices', {
      customer_name: customerName,
      customer_phone: customerPhone,
      customer_address: customerAddress,
      discount: 0,
      notes: '',
      items: items
    });
    state.cart = [];
    updateCartUI();
    showToast('تم حفظ الفاتورة رقم ' + result.invoice_number, 'success');
    if (shouldPrint) {
      printInvoice(result.id);
    }
  } catch (e) {
    showToast(e.message || 'خطأ في حفظ الفاتورة', 'error');
  }
}

async function printInvoice(id) {
  try {
    var res = await fetch(API_BASE + '/api/invoices/' + id + '/print', { headers: getHeaders() });
    if (!res.ok) throw new Error('Print failed');
    var html = await res.text();
    var win = window.open('', '_blank');
    if (!win) { showToast('الرجاء السماح للنوافذ المنبثقة', 'warning'); return; }
    win.document.write(html);
    win.document.close();
    setTimeout(function() { win.print(); }, 500);
  } catch (e) {
    showToast(e.message, 'error');
  }
}

/* ===== PRODUCTS ===== */
async function loadProducts() {
  showLoading();
  try {
    var search = '';
    var [products, categories] = await Promise.all([
      apiGet('/products?search='),
      apiGet('/categories')
    ]);
    state.products = products;
    state.categories = categories;
    renderContent(renderProducts(products, categories));
  } catch (e) {
    showError(e.message);
  }
}

function renderProducts(products, categories) {
  return '<div class="page-header"><h1><i class="fas fa-box"></i> المنتجات</h1><div class="page-toolbar">' +
    '<input type="text" id="prodSearch" placeholder="بحث..." oninput="filterProducts()">' +
    '<button class="btn btn-primary" onclick="showAddProduct()"><i class="fas fa-plus"></i> إضافة منتج</button>' +
    '</div></div>' +
    '<div class="card"><div class="table-wrap">' +
    (products.length === 0 ? '<div class="empty-table-msg">لا توجد منتجات</div>' :
    '<table><thead><tr><th>#</th><th>الاسم</th><th>التصنيف</th><th>سعر الشراء</th><th>سعر البيع</th><th>المخزون</th><th>الحد الأدنى</th><th>إجراءات</th></tr></thead><tbody>' +
    products.map(function(p, i) {
      var stockClass = p.current_stock <= 0 ? 'stock-badge zero' : (p.current_stock < p.min_stock ? 'stock-badge low' : 'stock-badge normal');
      return '<tr><td>' + (i + 1) + '</td><td>' + escapeHtml(p.name) + '</td><td>' + escapeHtml(p.category_name || '-') + '</td><td>' + formatCurrency(p.buy_price) + '</td><td>' + formatCurrency(p.sell_price) + '</td><td><span class="' + stockClass + '">' + p.current_stock + '</span></td><td>' + p.min_stock + '</td><td>' +
        '<div class="table-actions"><button class="btn-edit" onclick="showEditProduct(' + p.id + ')"><i class="fas fa-edit"></i></button><button class="btn-delete" onclick="deleteProduct(' + p.id + ')"><i class="fas fa-trash"></i></button></div></td></tr>';
    }).join('') +
    '</tbody></table>') +
    '</div></div>';
}

function filterProducts() {
  var val = document.getElementById('prodSearch').value.trim().toLowerCase();
  var filtered = state.products.filter(function(p) { return !val || p.name.toLowerCase().includes(val); });
  var categories = state.categories;
  var tableBody = filtered.map(function(p, i) {
    var stockClass = p.current_stock <= 0 ? 'stock-badge zero' : (p.current_stock < p.min_stock ? 'stock-badge low' : 'stock-badge normal');
    return '<tr><td>' + (i + 1) + '</td><td>' + escapeHtml(p.name) + '</td><td>' + escapeHtml(p.category_name || '-') + '</td><td>' + formatCurrency(p.buy_price) + '</td><td>' + formatCurrency(p.sell_price) + '</td><td><span class="' + stockClass + '">' + p.current_stock + '</span></td><td>' + p.min_stock + '</td><td>' +
      '<div class="table-actions"><button class="btn-edit" onclick="showEditProduct(' + p.id + ')"><i class="fas fa-edit"></i></button><button class="btn-delete" onclick="deleteProduct(' + p.id + ')"><i class="fas fa-trash"></i></button></div></td></tr>';
  }).join('');
  var tableEl = document.querySelector('#content table tbody');
  if (tableEl) {
    tableEl.innerHTML = tableBody || '<tr><td colspan="8" class="empty-table-msg">لا توجد منتجات مطابقة</td></tr>';
  }
}

function showAddProduct() {
  var catOptions = '<option value="">-- اختر التصنيف --</option>';
  state.categories.forEach(function(c) {
    catOptions += '<option value="' + c.id + '">' + escapeHtml(c.name) + '</option>';
  });
  showModal(
    '<form onsubmit="saveProduct(event)" id="productForm">' +
    '<input type="hidden" id="prodId" value="">' +
    '<div class="form-group"><label>اسم المنتج <span class="required">*</span></label><input class="form-control" id="prodName" required></div>' +
    '<div class="form-row"><div class="form-group"><label>التصنيف</label><select class="form-control" id="prodCategory">' + catOptions + '</select></div>' +
    '<div class="form-group"><label>الحد الأدنى للمخزون</label><input class="form-control" type="number" id="prodMinStock" value="5" min="0"></div></div>' +
    '<div class="form-row"><div class="form-group"><label>سعر الشراء</label><input class="form-control" type="number" id="prodBuyPrice" value="0" min="0"></div>' +
    '<div class="form-group"><label>سعر البيع <span class="required">*</span></label><input class="form-control" type="number" id="prodSellPrice" value="0" min="0" required></div></div>' +
    '<div class="form-group"><label>المخزون الحالي</label><input class="form-control" type="number" id="prodStock" value="0" min="0"></div>' +
    '<div class="form-group"><label>المقاسات (مفصولة بفواصل)</label><input class="form-control" id="prodSizes" placeholder="مثال: S, M, L, XL"></div>' +
    '<div class="form-group"><label>الألوان (مفصولة بفواصل)</label><input class="form-control" id="prodColors" placeholder="مثال: أحمر, أزرق, أسود"></div>' +
    '<div class="form-group"><label>أماكن الطباعة (مفصولة بفواصل)</label><input class="form-control" id="prodPrintLocations" placeholder="مثال: أمامي, خلفي, كم"></div>' +
    '<div class="form-group"><label>ملاحظات</label><textarea class="form-control" id="prodNotes"></textarea></div>' +
    '<button type="submit" class="btn btn-success btn-block"><i class="fas fa-save"></i> حفظ</button>' +
    '</form>', 'إضافة منتج'
  );
}

function showEditProduct(id) {
  var p = state.products.find(function(pr) { return pr.id === id; });
  if (!p) return;
  var catOptions = '<option value="">-- اختر التصنيف --</option>';
  state.categories.forEach(function(c) {
    catOptions += '<option value="' + c.id + '"' + (c.id === p.category_id ? ' selected' : '') + '>' + escapeHtml(c.name) + '</option>';
  });
  showModal(
    '<form onsubmit="saveProduct(event)" id="productForm">' +
    '<input type="hidden" id="prodId" value="' + p.id + '">' +
    '<div class="form-group"><label>اسم المنتج <span class="required">*</span></label><input class="form-control" id="prodName" value="' + escapeHtml(p.name) + '" required></div>' +
    '<div class="form-row"><div class="form-group"><label>التصنيف</label><select class="form-control" id="prodCategory">' + catOptions + '</select></div>' +
    '<div class="form-group"><label>الحد الأدنى للمخزون</label><input class="form-control" type="number" id="prodMinStock" value="' + p.min_stock + '" min="0"></div></div>' +
    '<div class="form-row"><div class="form-group"><label>سعر الشراء</label><input class="form-control" type="number" id="prodBuyPrice" value="' + p.buy_price + '" min="0"></div>' +
    '<div class="form-group"><label>سعر البيع <span class="required">*</span></label><input class="form-control" type="number" id="prodSellPrice" value="' + p.sell_price + '" min="0" required></div></div>' +
    '<div class="form-group"><label>المخزون الحالي</label><input class="form-control" type="number" id="prodStock" value="' + p.current_stock + '" min="0"></div>' +
    '<div class="form-group"><label>المقاسات (مفصولة بفواصل)</label><input class="form-control" id="prodSizes" value="' + escapeHtml(p.sizes || '') + '" placeholder="مثال: S, M, L, XL"></div>' +
    '<div class="form-group"><label>الألوان (مفصولة بفواصل)</label><input class="form-control" id="prodColors" value="' + escapeHtml(p.colors || '') + '" placeholder="مثال: أحمر, أزرق, أسود"></div>' +
    '<div class="form-group"><label>أماكن الطباعة (مفصولة بفواصل)</label><input class="form-control" id="prodPrintLocations" value="' + escapeHtml(p.print_locations || '') + '" placeholder="مثال: أمامي, خلفي, كم"></div>' +
    '<div class="form-group"><label>ملاحظات</label><textarea class="form-control" id="prodNotes">' + escapeHtml(p.notes || '') + '</textarea></div>' +
    '<button type="submit" class="btn btn-success btn-block"><i class="fas fa-save"></i> حفظ</button>' +
    '</form>', 'تعديل منتج'
  );
}

async function saveProduct(e) {
  e.preventDefault();
  var id = document.getElementById('prodId').value;
  var data = {
    name: document.getElementById('prodName').value.trim(),
    category_id: document.getElementById('prodCategory').value ? parseInt(document.getElementById('prodCategory').value) : null,
    buy_price: parseFloat(document.getElementById('prodBuyPrice').value) || 0,
    sell_price: parseFloat(document.getElementById('prodSellPrice').value) || 0,
    current_stock: parseInt(document.getElementById('prodStock').value) || 0,
    min_stock: parseInt(document.getElementById('prodMinStock').value) || 5,
    sizes: document.getElementById('prodSizes').value.trim(),
    colors: document.getElementById('prodColors').value.trim(),
    print_locations: document.getElementById('prodPrintLocations').value.trim(),
    notes: document.getElementById('prodNotes').value.trim()
  };
  try {
    if (id) {
      await apiPut('/products/' + id, data);
      showToast('تم تحديث المنتج', 'success');
    } else {
      await apiPost('/products', data);
      showToast('تم إضافة المنتج', 'success');
    }
    closeModal();
    loadProducts();
  } catch (e) {
    showToast(e.message || 'حدث خطأ', 'error');
  }
}

async function deleteProduct(id) {
  if (!confirm('هل أنت متأكد من حذف هذا المنتج؟')) return;
  try {
    await apiDelete('/products/' + id);
    showToast('تم حذف المنتج', 'success');
    loadProducts();
  } catch (e) {
    showToast(e.message || 'حدث خطأ', 'error');
  }
}

/* ===== INVENTORY ===== */
async function loadInventory() {
  showLoading();
  try {
    var products = await apiGet('/products?search=');
    state.products = products;
    renderContent(renderInventory(products));
  } catch (e) {
    showError(e.message);
  }
}

function renderInventory(products) {
  return '<div class="page-header"><h1><i class="fas fa-warehouse"></i> المخزون</h1><div class="page-toolbar">' +
    '<input type="text" id="invSearch" placeholder="بحث..." oninput="filterInventory()">' +
    '<select id="invFilter" onchange="filterInventory()"><option value="all">الكل</option><option value="low">مخزون منخفض</option><option value="zero">مخزون صفري</option></select>' +
    '<button class="btn btn-outline" onclick="printInventory()"><i class="fas fa-print"></i> طباعة</button>' +
    '</div></div>' +
    '<div class="card"><div class="table-wrap">' +
    (products.length === 0 ? '<div class="empty-table-msg">لا توجد منتجات</div>' :
    '<table><thead><tr><th>#</th><th>المنتج</th><th>التصنيف</th><th>المخزون</th><th>الحد الأدنى</th><th>الحالة</th></tr></thead><tbody id="invBody">' +
    products.map(function(p, i) {
      return inventoryRow(p, i);
    }).join('') +
    '</tbody></table>') +
    '</div></div>';
}

function inventoryRow(p, i) {
  var status = '';
  var cls = '';
  if (p.current_stock <= 0) { status = 'نفذ'; cls = 'out'; }
  else if (p.current_stock < p.min_stock) { status = 'منخفض'; cls = 'low'; }
  else { status = 'متوفر'; cls = 'normal'; }
  return '<tr><td>' + (i + 1) + '</td><td>' + escapeHtml(p.name) + '</td><td>' + escapeHtml(p.category_name || '-') + '</td><td>' + p.current_stock + '</td><td>' + p.min_stock + '</td><td><span class="stock-badge ' + cls + '">' + status + '</span></td></tr>';
}

function filterInventory() {
  var search = document.getElementById('invSearch').value.trim().toLowerCase();
  var filter = document.getElementById('invFilter').value;
  var filtered = state.products.filter(function(p) {
    if (search && !p.name.toLowerCase().includes(search)) return false;
    if (filter === 'low') return p.current_stock > 0 && p.current_stock < p.min_stock;
    if (filter === 'zero') return p.current_stock <= 0;
    return true;
  });
  var body = document.getElementById('invBody');
  if (body) {
    body.innerHTML = filtered.length === 0 ? '<tr><td colspan="6" class="empty-table-msg">لا توجد نتائج</td></tr>' :
      filtered.map(function(p, i) { return inventoryRow(p, i); }).join('');
  }
}

function printInventory() {
  var content = document.getElementById('content');
  var printWindow = window.open('', '_blank');
  if (!printWindow) { showToast('الرجاء السماح للنوافذ المنبثقة', 'warning'); return; }
  var html = '<!DOCTYPE html><html dir="rtl"><head><meta charset="UTF-8"><title>تقرير المخزون</title><style>' +
    'body{font-family:Arial,sans-serif;padding:20px;direction:rtl}table{width:100%;border-collapse:collapse;margin-top:16px}' +
    'th,td{border:1px solid #000;padding:8px;text-align:center}th{background:#eee}.title{text-align:center;font-size:22px;font-weight:bold;margin-bottom:4px}' +
    '.sub{text-align:center;color:#666;margin-bottom:20px}</style></head><body>' +
    '<div class="title">تقرير المخزون</div><div class="sub">' + new Date().toLocaleDateString('ar-IQ') + '</div>' +
    '<table><thead><tr><th>#</th><th>المنتج</th><th>التصنيف</th><th>المخزون</th><th>الحد الأدنى</th><th>الحالة</th></tr></thead><tbody>' +
    state.products.map(function(p, i) {
      var st = p.current_stock <= 0 ? 'نفذ' : (p.current_stock < p.min_stock ? 'منخفض' : 'متوفر');
      return '<tr><td>' + (i + 1) + '</td><td>' + escapeHtml(p.name) + '</td><td>' + escapeHtml(p.category_name || '-') + '</td><td>' + p.current_stock + '</td><td>' + p.min_stock + '</td><td>' + st + '</td></tr>';
    }).join('') +
    '</tbody></table></body></html>';
  printWindow.document.write(html);
  printWindow.document.close();
  setTimeout(function() { printWindow.print(); }, 500);
}

/* ===== STOCK ADD ===== */
async function loadStockAdd() {
  showLoading();
  try {
    var products = await apiGet('/products?search=');
    state.products = products;
    renderContent(renderStockAdd(products));
  } catch (e) {
    showError(e.message);
  }
}

function renderStockAdd(products) {
  return '<div class="page-header"><h1><i class="fas fa-plus-circle"></i> إضافة مخزون</h1><div class="page-toolbar">' +
    '<input type="text" id="stockSearch" placeholder="بحث..." oninput="filterStockAdd()">' +
    '</div></div>' +
    '<div class="card"><div class="table-wrap">' +
    (products.length === 0 ? '<div class="empty-table-msg">لا توجد منتجات</div>' :
    '<table><thead><tr><th>#</th><th>المنتج</th><th>المخزون الحالي</th><th>الحد الأدنى</th><th>إجراءات</th></tr></thead><tbody id="stockAddBody">' +
    products.map(function(p, i) {
      return '<tr><td>' + (i + 1) + '</td><td>' + escapeHtml(p.name) + '</td><td>' + p.current_stock + '</td><td>' + p.min_stock + '</td><td><button class="btn btn-success btn-sm" onclick="showAddStock(' + p.id + ')"><i class="fas fa-plus"></i> إضافة مخزون</button></td></tr>';
    }).join('') +
    '</tbody></table>') +
    '</div></div>';
}

function filterStockAdd() {
  var val = document.getElementById('stockSearch').value.trim().toLowerCase();
  var filtered = state.products.filter(function(p) { return !val || p.name.toLowerCase().includes(val); });
  var body = document.getElementById('stockAddBody');
  if (body) {
    body.innerHTML = filtered.length === 0 ? '<tr><td colspan="5" class="empty-table-msg">لا توجد منتجات مطابقة</td></tr>' :
      filtered.map(function(p, i) {
        return '<tr><td>' + (i + 1) + '</td><td>' + escapeHtml(p.name) + '</td><td>' + p.current_stock + '</td><td>' + p.min_stock + '</td><td><button class="btn btn-success btn-sm" onclick="showAddStock(' + p.id + ')"><i class="fas fa-plus"></i> إضافة مخزون</button></td></tr>';
      }).join('');
  }
}

function showAddStock(productId) {
  var p = state.products.find(function(pr) { return pr.id === productId; });
  if (!p) return;
  showModal(
    '<form onsubmit="saveAddStock(event, ' + productId + ')">' +
    '<div style="margin-bottom:16px"><strong>' + escapeHtml(p.name) + '</strong><br><span style="color:var(--text-muted);font-size:13px">المخزون الحالي: ' + p.current_stock + '</span></div>' +
    '<div class="form-group"><label>الكمية المضافة <span class="required">*</span></label><input class="form-control" type="number" id="stockQty" min="1" value="1" required></div>' +
    '<div class="form-group"><label>المرجع</label><input class="form-control" id="stockRef" placeholder="رقم الفاتورة أو المرجع"></div>' +
    '<div class="form-group"><label>ملاحظات</label><textarea class="form-control" id="stockNotes" placeholder="ملاحظات إضافية"></textarea></div>' +
    '<button type="submit" class="btn btn-success btn-block"><i class="fas fa-save"></i> حفظ</button>' +
    '</form>', 'إضافة مخزون - ' + p.name
  );
}

async function saveAddStock(e, productId) {
  e.preventDefault();
  var quantity = parseInt(document.getElementById('stockQty').value) || 1;
  var notes = document.getElementById('stockNotes').value.trim();
  if (quantity < 1) { showToast('الكمية يجب أن تكون 1 على الأقل', 'warning'); return; }
  try {
    await apiPost('/stock/add', { product_id: productId, quantity: quantity, notes: notes });
    showToast('تم إضافة المخزون بنجاح', 'success');
    closeModal();
    loadStockAdd();
  } catch (e) {
    showToast(e.message || 'حدث خطأ', 'error');
  }
}

/* ===== INVOICES ===== */
async function loadInvoices() {
  showLoading();
  try {
    var invoices = await apiGet('/invoices?search=');
    state.invoices = invoices;
    renderContent(renderInvoices(invoices));
  } catch (e) {
    showError(e.message);
  }
}

function renderInvoices(invoices) {
  return '<div class="page-header"><h1><i class="fas fa-file-invoice"></i> الفواتير</h1><div class="page-toolbar">' +
    '<input type="text" id="invSearch" placeholder="بحث عن فاتورة..." oninput="filterInvoices()">' +
    '</div></div>' +
    '<div class="card"><div class="table-wrap">' +
    (invoices.length === 0 ? '<div class="empty-table-msg">لا توجد فواتير</div>' :
    '<table><thead><tr><th>رقم الفاتورة</th><th>الزبون</th><th>رقم الهاتف</th><th>الإجمالي</th><th>التاريخ</th><th>إجراءات</th></tr></thead><tbody id="invListBody">' +
    invoices.map(function(inv) {
      return '<tr><td>' + escapeHtml(inv.invoice_number) + '</td><td>' + escapeHtml(inv.customer_name || '-') + '</td><td>' + escapeHtml(inv.customer_phone || '-') + '</td><td>' + formatCurrency(inv.grand_total) + '</td><td>' + formatDate(inv.created_at) + '</td><td>' +
        '<div class="table-actions"><button class="btn-print" onclick="printInvoice(' + inv.id + ')"><i class="fas fa-print"></i></button></div></td></tr>';
    }).join('') +
    '</tbody></table>') +
    '</div></div>';
}

function filterInvoices() {
  var val = document.getElementById('invSearch').value.trim().toLowerCase();
  var filtered = state.invoices.filter(function(inv) {
    if (!val) return true;
    return (inv.invoice_number && inv.invoice_number.toLowerCase().includes(val)) ||
           (inv.customer_name && inv.customer_name.toLowerCase().includes(val)) ||
           (inv.customer_phone && inv.customer_phone.includes(val));
  });
  var body = document.getElementById('invListBody');
  if (body) {
    body.innerHTML = filtered.length === 0 ? '<tr><td colspan="6" class="empty-table-msg">لا توجد فواتير مطابقة</td></tr>' :
      filtered.map(function(inv) {
        return '<tr><td>' + escapeHtml(inv.invoice_number) + '</td><td>' + escapeHtml(inv.customer_name || '-') + '</td><td>' + escapeHtml(inv.customer_phone || '-') + '</td><td>' + formatCurrency(inv.grand_total) + '</td><td>' + formatDate(inv.created_at) + '</td><td>' +
          '<div class="table-actions"><button class="btn-print" onclick="printInvoice(' + inv.id + ')"><i class="fas fa-print"></i></button></div></td></tr>';
      }).join('');
  }
}

/* ===== CUSTOMERS ===== */
async function loadCustomers() {
  showLoading();
  try {
    var customers = await apiGet('/customers?search=');
    state.customers = customers;
    renderContent(renderCustomers(customers));
  } catch (e) {
    showError(e.message);
  }
}

function renderCustomers(customers) {
  return '<div class="page-header"><h1><i class="fas fa-users"></i> العملاء</h1><div class="page-toolbar">' +
    '<input type="text" id="custSearch" placeholder="بحث..." oninput="filterCustomers()">' +
    '<button class="btn btn-primary" onclick="showAddCustomer()"><i class="fas fa-plus"></i> إضافة عميل</button>' +
    '</div></div>' +
    '<div class="card"><div class="table-wrap">' +
    (customers.length === 0 ? '<div class="empty-table-msg">لا يوجد عملاء</div>' :
    '<table><thead><tr><th>#</th><th>الاسم</th><th>رقم الهاتف</th><th>العنوان</th><th>إجراءات</th></tr></thead><tbody id="custBody">' +
    customers.map(function(c, i) {
      return '<tr><td>' + (i + 1) + '</td><td>' + escapeHtml(c.name) + '</td><td>' + escapeHtml(c.phone || '-') + '</td><td>' + escapeHtml(c.address || '-') + '</td><td>' +
        '<div class="table-actions"><button class="btn-edit" onclick="showEditCustomer(' + c.id + ')"><i class="fas fa-edit"></i></button><button class="btn-delete" onclick="deleteCustomer(' + c.id + ')"><i class="fas fa-trash"></i></button></div></td></tr>';
    }).join('') +
    '</tbody></table>') +
    '</div></div>';
}

function filterCustomers() {
  var val = document.getElementById('custSearch').value.trim().toLowerCase();
  var filtered = state.customers.filter(function(c) {
    return !val || c.name.toLowerCase().includes(val) || c.phone.includes(val);
  });
  var body = document.getElementById('custBody');
  if (body) {
    body.innerHTML = filtered.length === 0 ? '<tr><td colspan="5" class="empty-table-msg">لا يوجد عملاء مطابقون</td></tr>' :
      filtered.map(function(c, i) {
        return '<tr><td>' + (i + 1) + '</td><td>' + escapeHtml(c.name) + '</td><td>' + escapeHtml(c.phone || '-') + '</td><td>' + escapeHtml(c.address || '-') + '</td><td>' +
          '<div class="table-actions"><button class="btn-edit" onclick="showEditCustomer(' + c.id + ')"><i class="fas fa-edit"></i></button><button class="btn-delete" onclick="deleteCustomer(' + c.id + ')"><i class="fas fa-trash"></i></button></div></td></tr>';
      }).join('');
  }
}

function showAddCustomer() {
  showModal(
    '<form onsubmit="saveCustomer(event)">' +
    '<input type="hidden" id="custId" value="">' +
    '<div class="form-group"><label>اسم العميل <span class="required">*</span></label><input class="form-control" id="custName" required></div>' +
    '<div class="form-group"><label>رقم الهاتف</label><input class="form-control" id="custPhone" dir="ltr"></div>' +
    '<div class="form-group"><label>العنوان</label><textarea class="form-control" id="custAddress"></textarea></div>' +
    '<div class="form-group"><label>ملاحظات</label><textarea class="form-control" id="custNotes"></textarea></div>' +
    '<button type="submit" class="btn btn-success btn-block"><i class="fas fa-save"></i> حفظ</button>' +
    '</form>', 'إضافة عميل'
  );
}

function showEditCustomer(id) {
  var c = state.customers.find(function(cu) { return cu.id === id; });
  if (!c) return;
  showModal(
    '<form onsubmit="saveCustomer(event)">' +
    '<input type="hidden" id="custId" value="' + c.id + '">' +
    '<div class="form-group"><label>اسم العميل <span class="required">*</span></label><input class="form-control" id="custName" value="' + escapeHtml(c.name) + '" required></div>' +
    '<div class="form-group"><label>رقم الهاتف</label><input class="form-control" id="custPhone" value="' + escapeHtml(c.phone || '') + '" dir="ltr"></div>' +
    '<div class="form-group"><label>العنوان</label><textarea class="form-control" id="custAddress">' + escapeHtml(c.address || '') + '</textarea></div>' +
    '<div class="form-group"><label>ملاحظات</label><textarea class="form-control" id="custNotes">' + escapeHtml(c.notes || '') + '</textarea></div>' +
    '<button type="submit" class="btn btn-success btn-block"><i class="fas fa-save"></i> حفظ</button>' +
    '</form>', 'تعديل عميل'
  );
}

async function saveCustomer(e) {
  e.preventDefault();
  var id = document.getElementById('custId').value;
  var data = {
    name: document.getElementById('custName').value.trim(),
    phone: document.getElementById('custPhone').value.trim(),
    address: document.getElementById('custAddress').value.trim(),
    notes: document.getElementById('custNotes').value.trim()
  };
  if (!data.name) { showToast('اسم العميل مطلوب', 'warning'); return; }
  try {
    if (id) {
      await apiPut('/customers/' + id, data);
      showToast('تم تحديث العميل', 'success');
    } else {
      await apiPost('/customers', data);
      showToast('تم إضافة العميل', 'success');
    }
    closeModal();
    loadCustomers();
  } catch (e) {
    showToast(e.message || 'حدث خطأ', 'error');
  }
}

async function deleteCustomer(id) {
  if (!confirm('هل أنت متأكد من حذف هذا العميل؟')) return;
  try {
    await apiDelete('/customers/' + id);
    showToast('تم حذف العميل', 'success');
    loadCustomers();
  } catch (e) {
    showToast(e.message || 'حدث خطأ', 'error');
  }
}

/* ===== REPORTS ===== */
async function loadReports() {
  showLoading();
  try {
    var [stats, topProducts] = await Promise.all([
      apiGet('/stats/dashboard'),
      apiGet('/reports/top-products')
    ]);
    renderContent(renderReports(stats, topProducts));
  } catch (e) {
    showError(e.message);
  }
}

function renderReports(stats, topProducts) {
  var totalRevenue = topProducts.reduce(function(sum, p) { return sum + p.total_sales; }, 0);
  return '<div class="page-header"><h1><i class="fas fa-chart-bar"></i> التقارير</h1></div>' +
    '<div class="stats-grid">' +
    statCard('fa-money-bill-wave', 'مبيعات اليوم', formatCurrency(stats.today_sales), 'success') +
    statCard('fa-shopping-cart', 'طلبات اليوم', stats.today_orders, 'accent') +
    statCard('fa-chart-line', 'مبيعات الشهر', formatCurrency(stats.month_sales), 'success') +
    statCard('fa-trophy', 'إجمالي المنتجات', stats.total_products, 'warning') +
    '</div>' +
    '<div class="card"><div class="card-title"><i class="fas fa-star"></i> أفضل المنتجات مبيعاً</div>' +
    (topProducts.length === 0 ? '<div class="empty-table-msg">لا توجد مبيعات بعد</div>' :
    '<div class="table-wrap"><table><thead><tr><th>#</th><th>المنتج</th><th>الكمية المباعة</th><th>الإيرادات</th><th>النسبة</th></tr></thead><tbody>' +
    topProducts.map(function(p, i) {
      var pct = totalRevenue > 0 ? ((p.total_sales / totalRevenue) * 100).toFixed(1) : 0;
      return '<tr><td>' + (i + 1) + '</td><td>' + escapeHtml(p.product_name) + '</td><td>' + p.total_quantity + '</td><td>' + formatCurrency(p.total_sales) + '</td><td>' + pct + '%</td></tr>';
    }).join('') +
    '</tbody></table></div>') +
    '</div>';
}

/* ===== SETTINGS ===== */
async function loadSettings() {
  showLoading();
  try {
    var [settings, categories] = await Promise.all([
      apiGet('/settings'),
      apiGet('/categories')
    ]);
    state.settings = settings;
    state.categories = categories;
    renderContent(renderSettings(settings, categories));
  } catch (e) {
    showError(e.message);
  }
}

function renderSettings(settings, categories) {
  return '<div class="page-header"><h1><i class="fas fa-cog"></i> الإعدادات</h1></div>' +
    '<div class="card"><div class="settings-section">' +
    '<h3><i class="fas fa-store"></i> معلومات المتجر</h3>' +
    '<div class="form-row"><div class="form-group"><label>اسم المتجر</label><input class="form-control" id="setName" value="' + escapeHtml(settings.store_name || '') + '"></div>' +
    '<div class="form-group"><label>رقم الهاتف</label><input class="form-control" id="setPhone" value="' + escapeHtml(settings.store_phone || '') + '" dir="ltr"></div></div>' +
    '<div class="form-row"><div class="form-group"><label>العنوان</label><input class="form-control" id="setAddress" value="' + escapeHtml(settings.store_address || '') + '"></div>' +
    '<div class="form-group"><label>نسبة الضريبة (%)</label><input class="form-control" type="number" id="setTax" value="' + (settings.tax_rate || '0') + '" min="0" step="0.1"></div></div>' +
    '<div class="form-group"><label>ملاحظة الفاتورة</label><textarea class="form-control" id="setNote">' + escapeHtml(settings.store_note || '') + '</textarea></div>' +
    '<button class="btn btn-primary" onclick="saveSettings()"><i class="fas fa-save"></i> حفظ الإعدادات</button>' +
    '</div></div>' +
    '<div class="card"><div class="settings-section">' +
    '<h3><i class="fas fa-tags"></i> التصنيفات</h3>' +
    '<div class="categories-list" id="catList">' +
    (categories.length === 0 ? '<div class="empty-table-msg" style="padding:12px">لا توجد تصنيفات</div>' :
    categories.map(function(c) {
      return '<div class="category-item"><span class="cat-name"><i class="fas fa-folder"></i> ' + escapeHtml(c.name) + '</span><button class="cat-delete" onclick="deleteCategory(' + c.id + ')"><i class="fas fa-trash"></i></button></div>';
    }).join('')) +
    '</div>' +
    '<div class="category-add">' +
    '<input type="text" id="newCatName" placeholder="اسم التصنيف الجديد">' +
    '<button class="btn btn-success" onclick="addCategory()"><i class="fas fa-plus"></i> إضافة</button>' +
    '</div>' +
    '</div></div>';
}

async function saveSettings() {
  var data = {
    store_name: document.getElementById('setName').value.trim(),
    store_phone: document.getElementById('setPhone').value.trim(),
    store_address: document.getElementById('setAddress').value.trim(),
    tax_rate: document.getElementById('setTax').value || '0',
    store_note: document.getElementById('setNote').value.trim()
  };
  try {
    await apiPost('/settings', data);
    showToast('تم حفظ الإعدادات', 'success');
  } catch (e) {
    showToast(e.message || 'حدث خطأ', 'error');
  }
}

async function addCategory() {
  var name = document.getElementById('newCatName').value.trim();
  if (!name) { showToast('الرجاء إدخال اسم التصنيف', 'warning'); return; }
  try {
    await apiPost('/categories', { name: name });
    document.getElementById('newCatName').value = '';
    showToast('تم إضافة التصنيف', 'success');
    loadSettings();
  } catch (e) {
    showToast(e.message || 'حدث خطأ', 'error');
  }
}

async function deleteCategory(id) {
  if (!confirm('هل أنت متأكد من حذف هذا التصنيف؟')) return;
  try {
    await apiDelete('/categories/' + id);
    showToast('تم حذف التصنيف', 'success');
    loadSettings();
  } catch (e) {
    showToast(e.message || 'حدث خطأ', 'error');
  }
}

/* ===== INIT ===== */
(function init() {
  if (state.token) {
    document.getElementById('loginOverlay').style.display = 'none';
    document.getElementById('app').style.display = 'flex';
    initNav();
    navigate('dashboard');
  } else {
    document.getElementById('loginOverlay').style.display = 'flex';
    document.getElementById('app').style.display = 'none';
  }
})();
