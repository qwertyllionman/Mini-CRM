/**
 * Mini-CRM Single-Page Application Logic.
 * Handles client-side state, API communication, table rendering,
 * debounced search, filtering, pagination, modal flows,
 * audit history timeline, and Chart.js analytics.
 */

// Application State
const state = {
    activeTab: 'leads',
    page: 1,
    pageSize: 10,
    search: '',
    statusFilter: 'all',
    sourceFilter: 'all',
    sortBy: 'created_at',
    order: 'desc',
    currentUser: null,
    currentLead: null,
    leadsData: {
        items: [],
        total: 0,
        page: 1,
        page_size: 10,
        total_pages: 1
    },
    statusChart: null,
    sourceChart: null,
    searchTimeout: null,
    authMode: 'login'
};

// Status Configurations & Badges
const STATUS_CONFIG = {
    'New': { label: 'New (Yangi)', bg: 'bg-sky-50', text: 'text-sky-700', border: 'border-sky-200', dot: 'bg-sky-500', hex: '#0284c7' },
    'Contacted': { label: 'Contacted (Bog\'lanilgan)', bg: 'bg-amber-50', text: 'text-amber-700', border: 'border-amber-200', dot: 'bg-amber-500', hex: '#d97706' },
    'Qualified': { label: 'Qualified (Saralangan)', bg: 'bg-purple-50', text: 'text-purple-700', border: 'border-purple-200', dot: 'bg-purple-500', hex: '#7c3aed' },
    'Won': { label: 'Won (Yutib olingan)', bg: 'bg-emerald-50', text: 'text-emerald-700', border: 'border-emerald-200', dot: 'bg-emerald-500', hex: '#16a34a' },
    'Lost': { label: 'Lost (Yo\'qotilgan)', bg: 'bg-rose-50', text: 'text-rose-700', border: 'border-rose-200', dot: 'bg-rose-500', hex: '#dc2626' }
};

// -----------------------------------------------------------------------------
// API Helper
// -----------------------------------------------------------------------------
async function api(endpoint, options = {}) {
    const token = localStorage.getItem('token');
    const headers = {
        'Content-Type': 'application/json',
        ...(options.headers || {})
    };

    if (token) {
        headers['Authorization'] = `Bearer ${token}`;
    }

    try {
        const response = await fetch(endpoint, {
            ...options,
            headers
        });

        if (response.status === 204) {
            return null;
        }

        const data = await response.json();

        if (!response.ok) {
            // If unauthorized, clear token and state
            if (response.status === 401 && token) {
                localStorage.removeItem('token');
                state.currentUser = null;
                renderAuthSection();
            }
            const errorMsg = data.detail || 'Xatolik yuz berdi.';
            throw new Error(typeof errorMsg === 'string' ? errorMsg : JSON.stringify(errorMsg));
        }

        return data;
    } catch (err) {
        throw err;
    }
}

// -----------------------------------------------------------------------------
// Initialization
// -----------------------------------------------------------------------------
document.addEventListener('DOMContentLoaded', async () => {
    lucide.createIcons();
    await checkAuth();
    await loadLeads();
    await updateStatusCounts();
});

// -----------------------------------------------------------------------------
// Authentication
// -----------------------------------------------------------------------------
async function checkAuth() {
    const token = localStorage.getItem('token');
    if (!token) {
        state.currentUser = null;
        renderAuthSection();
        return;
    }

    try {
        const user = await api('/api/auth/me');
        state.currentUser = user;
    } catch (e) {
        localStorage.removeItem('token');
        state.currentUser = null;
    }
    renderAuthSection();
}

function renderAuthSection() {
    const container = document.getElementById('auth-section');
    if (!container) return;

    if (state.currentUser) {
        container.innerHTML = `
            <div class="flex items-center space-x-2">
                <div class="flex items-center space-x-2 bg-indigo-50 border border-indigo-100 rounded-xl px-3 py-1.5">
                    <div class="w-6 h-6 rounded-full bg-indigo-600 text-white flex items-center justify-center text-xs font-bold">
                        ${state.currentUser.full_name ? state.currentUser.full_name.charAt(0).toUpperCase() : 'U'}
                    </div>
                    <span class="text-xs font-bold text-slate-700 hidden sm:inline">${escapeHtml(state.currentUser.full_name)}</span>
                </div>
                <button onclick="logout()" title="Tizimdan chiqish" class="p-2 text-slate-400 hover:text-rose-600 hover:bg-rose-50 rounded-lg transition">
                    <i data-lucide="log-out" class="w-4 h-4"></i>
                </button>
            </div>
        `;
    } else {
        container.innerHTML = `
            <button onclick="openAuthModal('login')" class="text-xs font-bold text-indigo-600 hover:text-indigo-700 bg-indigo-50 hover:bg-indigo-100 px-3.5 py-2 rounded-xl transition border border-indigo-100">
                Kirish / Ro'yxatdan o'tish
            </button>
        `;
    }
    lucide.createIcons();
}

function openAuthModal(mode = 'login') {
    state.authMode = mode;
    switchAuthTab(mode);
    document.getElementById('auth-modal').classList.remove('hidden');
    document.getElementById('auth-error-msg').classList.add('hidden');
}

function closeAuthModal() {
    document.getElementById('auth-modal').classList.add('hidden');
    document.getElementById('auth-form').reset();
}

function switchAuthTab(mode) {
    state.authMode = mode;
    const loginTab = document.getElementById('auth-tab-login');
    const regTab = document.getElementById('auth-tab-register');
    const fullnameGroup = document.getElementById('auth-fullname-group');
    const submitBtn = document.getElementById('auth-submit-btn');

    if (mode === 'login') {
        loginTab.className = "flex-1 py-3 text-center border-b-2 border-indigo-600 text-indigo-600 font-bold";
        regTab.className = "flex-1 py-3 text-center border-b-2 border-transparent text-slate-400 hover:text-slate-700 font-semibold";
        fullnameGroup.classList.add('hidden');
        submitBtn.textContent = 'Kirish';
    } else {
        regTab.className = "flex-1 py-3 text-center border-b-2 border-indigo-600 text-indigo-600 font-bold";
        loginTab.className = "flex-1 py-3 text-center border-b-2 border-transparent text-slate-400 hover:text-slate-700 font-semibold";
        fullnameGroup.classList.remove('hidden');
        submitBtn.textContent = "Ro'yxatdan o'tish";
    }
}

async function handleAuthSubmit(event) {
    event.preventDefault();
    const email = document.getElementById('auth-email').value.trim();
    const password = document.getElementById('auth-password').value;
    const fullName = document.getElementById('auth-fullname').value.trim();
    const errorEl = document.getElementById('auth-error-msg');
    errorEl.classList.add('hidden');

    try {
        let res;
        if (state.authMode === 'login') {
            res = await api('/api/auth/login', {
                method: 'POST',
                body: JSON.stringify({ email, password })
            });
            showToast('Muvaffaqiyatli tizimga kirdingiz!', 'success');
        } else {
            if (!fullName) {
                errorEl.textContent = "Iltimos, to'liq ismingizni kiriting.";
                errorEl.classList.remove('hidden');
                return;
            }
            res = await api('/api/auth/register', {
                method: 'POST',
                body: JSON.stringify({ email, password, full_name: fullName })
            });
            showToast("Ro'yxatdan o'tish muvaffaqiyatli yakunlandi!", 'success');
        }

        localStorage.setItem('token', res.access_token);
        state.currentUser = res.user;
        renderAuthSection();
        closeAuthModal();
        await loadLeads();
    } catch (err) {
        errorEl.textContent = err.message;
        errorEl.classList.remove('hidden');
    }
}

function logout() {
    localStorage.removeItem('token');
    state.currentUser = null;
    renderAuthSection();
    showToast('Tizimdan chiqdingiz.', 'info');
    loadLeads();
}

// -----------------------------------------------------------------------------
// Navigation Tabs
// -----------------------------------------------------------------------------
function switchTab(tab) {
    state.activeTab = tab;
    const leadsTabBtn = document.getElementById('nav-leads-btn');
    const dashTabBtn = document.getElementById('nav-dashboard-btn');
    const leadsSec = document.getElementById('tab-leads');
    const dashSec = document.getElementById('tab-dashboard');

    if (tab === 'leads') {
        leadsTabBtn.className = "nav-tab px-4 py-2 rounded-lg text-sm font-semibold transition flex items-center space-x-2 bg-white text-indigo-600 shadow-xs";
        dashTabBtn.className = "nav-tab px-4 py-2 rounded-lg text-sm font-semibold transition flex items-center space-x-2 text-slate-600 hover:text-slate-900";
        leadsSec.classList.remove('hidden');
        dashSec.classList.add('hidden');
        loadLeads();
    } else {
        dashTabBtn.className = "nav-tab px-4 py-2 rounded-lg text-sm font-semibold transition flex items-center space-x-2 bg-white text-indigo-600 shadow-xs";
        leadsTabBtn.className = "nav-tab px-4 py-2 rounded-lg text-sm font-semibold transition flex items-center space-x-2 text-slate-600 hover:text-slate-900";
        leadsSec.classList.add('hidden');
        dashSec.classList.remove('hidden');
        loadDashboardStats();
    }
    lucide.createIcons();
}

// -----------------------------------------------------------------------------
// Leads Listing & Filtering
// -----------------------------------------------------------------------------
async function loadLeads() {
    const tableBody = document.getElementById('leads-table-body');
    const emptyState = document.getElementById('leads-empty-state');
    const loadingState = document.getElementById('leads-loading-state');

    loadingState.classList.remove('hidden');
    emptyState.classList.add('hidden');

    const params = new URLSearchParams({
        page: state.page,
        page_size: state.pageSize,
        sort_by: state.sortBy,
        order: state.order
    });

    if (state.search.trim()) params.append('search', state.search.trim());
    if (state.statusFilter !== 'all') params.append('status', state.statusFilter);
    if (state.sourceFilter !== 'all') params.append('source', state.sourceFilter);

    try {
        const data = await api(`/api/leads?${params.toString()}`);
        state.leadsData = data;
        loadingState.classList.add('hidden');

        if (!data.items || data.items.length === 0) {
            tableBody.innerHTML = '';
            emptyState.classList.remove('hidden');
            renderPagination(0, 0, 1, 1);
            return;
        }

        renderLeadsTable(data.items);
        renderPagination(data.total, data.items.length, data.page, data.total_pages);
    } catch (err) {
        loadingState.classList.add('hidden');
        showToast('Leadlarni yuklashda xatolik: ' + err.message, 'error');
    }
}

function renderLeadsTable(leads) {
    const tbody = document.getElementById('leads-table-body');
    tbody.innerHTML = '';

    leads.forEach(lead => {
        const conf = STATUS_CONFIG[lead.status] || STATUS_CONFIG['New'];
        const createdDate = formatDate(lead.created_at);

        const tr = document.createElement('tr');
        tr.className = "hover:bg-slate-50/80 transition-colors group cursor-pointer";
        tr.onclick = (e) => {
            // Prevent drawer if clicked on dropdown or action buttons
            if (e.target.closest('select') || e.target.closest('button') || e.target.closest('a')) return;
            openDetailDrawer(lead.id);
        };

        tr.innerHTML = `
            <td class="py-4 px-6 font-semibold text-slate-900">
                <div class="flex items-center space-x-3">
                    <div class="w-8 h-8 rounded-full bg-slate-100 text-slate-600 font-bold flex items-center justify-center text-xs border border-slate-200">
                        ${lead.name.charAt(0).toUpperCase()}
                    </div>
                    <div>
                        <div class="font-bold text-slate-800 hover:text-indigo-600 transition">${escapeHtml(lead.name)}</div>
                        ${lead.note ? `<div class="text-[11px] text-slate-400 font-normal truncate max-w-xs">${escapeHtml(lead.note)}</div>` : ''}
                    </div>
                </div>
            </td>
            <td class="py-4 px-6">
                <div class="space-y-1">
                    ${lead.phone ? `
                        <a href="tel:${lead.phone}" class="inline-flex items-center space-x-1.5 text-xs text-slate-700 hover:text-indigo-600 font-medium">
                            <i data-lucide="phone" class="w-3.5 h-3.5 text-emerald-500"></i>
                            <span>${escapeHtml(lead.phone)}</span>
                        </a><br>
                    ` : ''}
                    ${lead.email ? `
                        <a href="mailto:${lead.email}" class="inline-flex items-center space-x-1.5 text-xs text-slate-500 hover:text-indigo-600">
                            <i data-lucide="mail" class="w-3.5 h-3.5 text-sky-500"></i>
                            <span>${escapeHtml(lead.email)}</span>
                        </a>
                    ` : ''}
                    ${!lead.phone && !lead.email ? '<span class="text-xs text-slate-400 italic">Mavjud emas</span>' : ''}
                </div>
            </td>
            <td class="py-4 px-6">
                <span class="inline-flex items-center px-2.5 py-1 rounded-md text-xs font-medium bg-slate-100 text-slate-700 border border-slate-200">
                    ${escapeHtml(lead.source)}
                </span>
            </td>
            <td class="py-4 px-6">
                <!-- Inline Status Selector -->
                <div class="relative inline-block" onclick="event.stopPropagation()">
                    <select 
                        onchange="quickChangeStatus(${lead.id}, this.value)" 
                        class="appearance-none pr-7 pl-2.5 py-1 rounded-full text-xs font-semibold border ${conf.bg} ${conf.text} ${conf.border} focus:outline-none focus:ring-2 focus:ring-indigo-500/20 cursor-pointer transition"
                    >
                        <option value="New" ${lead.status === 'New' ? 'selected' : ''}>New</option>
                        <option value="Contacted" ${lead.status === 'Contacted' ? 'selected' : ''}>Contacted</option>
                        <option value="Qualified" ${lead.status === 'Qualified' ? 'selected' : ''}>Qualified</option>
                        <option value="Won" ${lead.status === 'Won' ? 'selected' : ''}>Won</option>
                        <option value="Lost" ${lead.status === 'Lost' ? 'selected' : ''}>Lost</option>
                    </select>
                    <i data-lucide="chevron-down" class="w-3.5 h-3.5 absolute right-2 top-1/2 -translate-y-1/2 ${conf.text} pointer-events-none"></i>
                </div>
            </td>
            <td class="py-4 px-6 text-xs text-slate-500 font-medium">
                ${createdDate}
            </td>
            <td class="py-4 px-6 text-right space-x-1" onclick="event.stopPropagation()">
                <button onclick="openDetailDrawer(${lead.id})" title="Ko'rish" class="p-1.5 text-slate-400 hover:text-indigo-600 hover:bg-indigo-50 rounded-lg transition">
                    <i data-lucide="eye" class="w-4 h-4"></i>
                </button>
                <button onclick="openEditLeadModal(${lead.id})" title="Tahrirlash" class="p-1.5 text-slate-400 hover:text-indigo-600 hover:bg-indigo-50 rounded-lg transition">
                    <i data-lucide="edit-3" class="w-4 h-4"></i>
                </button>
                <button onclick="confirmDeleteLead(${lead.id})" title="O'chirish" class="p-1.5 text-slate-400 hover:text-rose-600 hover:bg-rose-50 rounded-lg transition">
                    <i data-lucide="trash-2" class="w-4 h-4"></i>
                </button>
            </td>
        `;

        tbody.appendChild(tr);
    });

    lucide.createIcons();
}

function renderPagination(total, countOnPage, page, totalPages) {
    const rangeText = document.getElementById('pagination-range-text');
    const container = document.getElementById('pagination-buttons');

    const start = total === 0 ? 0 : (page - 1) * state.pageSize + 1;
    const end = total === 0 ? 0 : start + countOnPage - 1;
    rangeText.textContent = `Ko'rsatilmoqda: ${start}-${end} dan ${total} ta`;

    container.innerHTML = '';

    // Previous Button
    const prevBtn = document.createElement('button');
    prevBtn.disabled = page <= 1;
    prevBtn.className = `p-1.5 rounded-lg border border-slate-200 ${page <= 1 ? 'opacity-40 cursor-not-allowed text-slate-300' : 'hover:bg-slate-50 text-slate-600'} transition`;
    prevBtn.innerHTML = '<i data-lucide="chevron-left" class="w-4 h-4"></i>';
    prevBtn.onclick = () => {
        if (state.page > 1) {
            state.page--;
            loadLeads();
        }
    };
    container.appendChild(prevBtn);

    // Page Buttons
    let startPage = Math.max(1, page - 2);
    let endPage = Math.min(totalPages, startPage + 4);
    if (endPage - startPage < 4) {
        startPage = Math.max(1, endPage - 4);
    }

    for (let p = startPage; p <= endPage; p++) {
        const btn = document.createElement('button');
        const isActive = p === page;
        btn.className = `w-7 h-7 rounded-lg text-xs font-bold transition ${
            isActive ? 'bg-indigo-600 text-white shadow-xs' : 'text-slate-600 hover:bg-slate-100'
        }`;
        btn.textContent = p;
        btn.onclick = () => {
            state.page = p;
            loadLeads();
        };
        container.appendChild(btn);
    }

    // Next Button
    const nextBtn = document.createElement('button');
    nextBtn.disabled = page >= totalPages;
    nextBtn.className = `p-1.5 rounded-lg border border-slate-200 ${page >= totalPages ? 'opacity-40 cursor-not-allowed text-slate-300' : 'hover:bg-slate-50 text-slate-600'} transition`;
    nextBtn.innerHTML = '<i data-lucide="chevron-right" class="w-4 h-4"></i>';
    nextBtn.onclick = () => {
        if (state.page < totalPages) {
            state.page++;
            loadLeads();
        }
    };
    container.appendChild(nextBtn);

    lucide.createIcons();
}

// -----------------------------------------------------------------------------
// Filters & Search Handling
// -----------------------------------------------------------------------------
function handleSearchDebounce() {
    clearTimeout(state.searchTimeout);
    state.searchTimeout = setTimeout(() => {
        state.search = document.getElementById('search-input').value;
        state.page = 1;
        loadLeads();
    }, 350);
}

function handleFilterChange() {
    state.sourceFilter = document.getElementById('source-filter').value;
    state.page = 1;
    loadLeads();
}

function handleSortChange() {
    const val = document.getElementById('sort-filter').value;
    const [field, ord] = val.split(':');
    state.sortBy = field;
    state.order = ord;
    loadLeads();
}

function handlePageSizeChange() {
    state.pageSize = parseInt(document.getElementById('page-size-select').value, 10);
    state.page = 1;
    loadLeads();
}

function setStatusFilter(status) {
    state.statusFilter = status;
    state.page = 1;

    // Update active button styles
    document.querySelectorAll('.status-filter-btn').forEach(btn => {
        const btnStatus = btn.getAttribute('data-status');
        if (btnStatus === status) {
            btn.className = "status-filter-btn px-3.5 py-1.5 rounded-lg text-xs font-semibold border transition flex items-center space-x-1.5 bg-indigo-600 text-white border-indigo-600 shadow-xs";
        } else {
            btn.className = "status-filter-btn px-3.5 py-1.5 rounded-lg text-xs font-semibold border transition flex items-center space-x-1.5 bg-white text-slate-600 border-slate-200 hover:border-slate-300";
        }
    });

    loadLeads();
}

function resetFilters() {
    document.getElementById('search-input').value = '';
    document.getElementById('source-filter').value = 'all';
    document.getElementById('sort-filter').value = 'created_at:desc';
    state.search = '';
    state.sourceFilter = 'all';
    state.sortBy = 'created_at';
    state.order = 'desc';
    setStatusFilter('all');
}

async function updateStatusCounts() {
    try {
        const stats = await api('/api/dashboard/stats');
        document.getElementById('badge-count-all').textContent = stats.total_leads;
        document.getElementById('badge-count-new').textContent = stats.new_leads;
        document.getElementById('badge-count-contacted').textContent = stats.contacted_leads;
        document.getElementById('badge-count-qualified').textContent = stats.qualified_leads;
        document.getElementById('badge-count-won').textContent = stats.won_leads;
        document.getElementById('badge-count-lost').textContent = stats.lost_leads;
    } catch (e) {
        console.error('Failed to update status counts', e);
    }
}

// -----------------------------------------------------------------------------
// Lead Create / Edit Modals
// -----------------------------------------------------------------------------
function openCreateLeadModal() {
    document.getElementById('lead-modal-title').textContent = "Yangi Lead qo'shish";
    document.getElementById('lead-modal-id').value = '';
    document.getElementById('lead-form').reset();
    document.getElementById('lead-status').value = 'New';
    document.getElementById('lead-status').disabled = false;
    document.getElementById('lead-modal').classList.remove('hidden');
}

async function openEditLeadModal(id) {
    try {
        const lead = await api(`/api/leads/${id}`);
        document.getElementById('lead-modal-title').textContent = "Leadni tahrirlash";
        document.getElementById('lead-modal-id').value = lead.id;
        document.getElementById('lead-name').value = lead.name;
        document.getElementById('lead-phone').value = lead.phone || '';
        document.getElementById('lead-email').value = lead.email || '';
        document.getElementById('lead-source').value = lead.source || 'Website';
        document.getElementById('lead-status').value = lead.status;
        document.getElementById('lead-note').value = lead.note || '';

        document.getElementById('lead-modal').classList.remove('hidden');
    } catch (err) {
        showToast('Leadni yuklashda xatolik: ' + err.message, 'error');
    }
}

function closeLeadModal() {
    document.getElementById('lead-modal').classList.add('hidden');
}

async function handleLeadFormSubmit(event) {
    event.preventDefault();
    const id = document.getElementById('lead-modal-id').value;
    const name = document.getElementById('lead-name').value.trim();
    const phone = document.getElementById('lead-phone').value.trim();
    const email = document.getElementById('lead-email').value.trim();
    const source = document.getElementById('lead-source').value;
    const status = document.getElementById('lead-status').value;
    const note = document.getElementById('lead-note').value.trim();

    if (!phone && !email) {
        showToast("Kamida bitta aloqa vositasi (telefon yoki email) kiritilishi shart!", 'error');
        return;
    }

    const payload = {
        name,
        phone: phone || null,
        email: email || null,
        source,
        status,
        note: note || null
    };

    const submitBtn = document.getElementById('lead-form-submit-btn');
    submitBtn.disabled = true;

    try {
        if (id) {
            await api(`/api/leads/${id}`, {
                method: 'PUT',
                body: JSON.stringify(payload)
            });
            showToast("Lead muvaffaqiyatli yangilandi!", 'success');
        } else {
            await api('/api/leads', {
                method: 'POST',
                body: JSON.stringify(payload)
            });
            showToast("Yangi lead muvaffaqiyatli yaratildi!", 'success');
        }

        closeLeadModal();
        await loadLeads();
        await updateStatusCounts();
        if (state.currentLead && state.currentLead.id == id) {
            openDetailDrawer(id);
        }
    } catch (err) {
        showToast(err.message, 'error');
    } finally {
        submitBtn.disabled = false;
    }
}

// -----------------------------------------------------------------------------
// Quick Status Changer & Delete
// -----------------------------------------------------------------------------
async function quickChangeStatus(leadId, newStatus) {
    try {
        await api(`/api/leads/${leadId}/status`, {
            method: 'PATCH',
            body: JSON.stringify({ status: newStatus })
        });
        showToast(`Status "${newStatus}" ga o'zgartirildi`, 'success');
        await loadLeads();
        await updateStatusCounts();
        if (state.currentLead && state.currentLead.id === leadId) {
            openDetailDrawer(leadId);
        }
    } catch (err) {
        showToast(err.message, 'error');
        loadLeads();
    }
}

async function confirmDeleteLead(leadId) {
    if (!confirm("Haqiqatan ham bu leadni o'chirmoqchimisiz? Ushbu amal qaytarilmaydi!")) {
        return;
    }

    try {
        await api(`/api/leads/${leadId}`, {
            method: 'DELETE'
        });
        showToast("Lead muvaffaqiyatli o'chirildi.", 'info');
        closeDetailDrawer();
        await loadLeads();
        await updateStatusCounts();
    } catch (err) {
        showToast(err.message, 'error');
    }
}

// -----------------------------------------------------------------------------
// Lead Detail Drawer & Audit History Timeline
// -----------------------------------------------------------------------------
async function openDetailDrawer(leadId) {
    try {
        const lead = await api(`/api/leads/${leadId}`);
        state.currentLead = lead;

        document.getElementById('drawer-lead-id').textContent = lead.id;
        document.getElementById('drawer-lead-name').textContent = lead.name;
        document.getElementById('drawer-lead-created').textContent = formatDate(lead.created_at);
        document.getElementById('drawer-lead-phone').textContent = lead.phone || 'Mavjud emas';
        document.getElementById('drawer-lead-email').textContent = lead.email || 'Mavjud emas';
        document.getElementById('drawer-lead-source').textContent = lead.source;
        document.getElementById('drawer-lead-note').textContent = lead.note || 'Izoh mavjud emas.';

        // Status Badge
        const conf = STATUS_CONFIG[lead.status] || STATUS_CONFIG['New'];
        document.getElementById('drawer-lead-status-badge').innerHTML = `
            <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-bold ${conf.bg} ${conf.text} border ${conf.border}">
                ${lead.status}
            </span>
        `;

        // Render Quick Status Buttons
        const buttonsContainer = document.getElementById('drawer-status-buttons');
        buttonsContainer.innerHTML = '';
        Object.keys(STATUS_CONFIG).forEach(st => {
            const stConf = STATUS_CONFIG[st];
            const isSelected = lead.status === st;
            const btn = document.createElement('button');
            btn.className = `py-1.5 px-2 rounded-lg text-[11px] font-bold border transition ${
                isSelected
                    ? `${stConf.bg} ${stConf.text} border-current ring-2 ring-indigo-500/20`
                    : 'bg-white text-slate-600 border-slate-200 hover:border-slate-300'
            }`;
            btn.textContent = st;
            btn.onclick = () => quickChangeStatus(lead.id, st);
            buttonsContainer.appendChild(btn);
        });

        // Load Activity History
        await loadDrawerActivities(leadId);

        document.getElementById('detail-drawer').classList.remove('hidden');
        lucide.createIcons();
    } catch (err) {
        showToast('Lead ma\'lumotlarini ochishda xatolik: ' + err.message, 'error');
    }
}

function closeDetailDrawer() {
    document.getElementById('detail-drawer').classList.add('hidden');
    state.currentLead = null;
}

function editCurrentDrawerLead() {
    if (state.currentLead) {
        openEditLeadModal(state.currentLead.id);
    }
}

function deleteCurrentDrawerLead() {
    if (state.currentLead) {
        confirmDeleteLead(state.currentLead.id);
    }
}

async function loadDrawerActivities(leadId) {
    const container = document.getElementById('drawer-timeline-container');
    const countEl = document.getElementById('drawer-activity-count');
    container.innerHTML = '<div class="text-xs text-slate-400 py-2">Yuklanmoqda...</div>';

    try {
        const activities = await api(`/api/leads/${leadId}/activities`);
        countEl.textContent = `${activities.length} ta yozuv`;

        if (activities.length === 0) {
            container.innerHTML = '<div class="text-xs text-slate-400 py-2 italic">Hozircha o\'zgarishlar tarixi yo\'q.</div>';
            return;
        }

        container.innerHTML = '';
        activities.forEach(act => {
            const item = document.createElement('div');
            item.className = "timeline-item";

            let dotColor = '#94a3b8';
            if (act.action === 'CREATED') dotColor = '#6366f1';
            else if (act.action === 'STATUS_CHANGED') dotColor = '#f59e0b';
            else if (act.action === 'UPDATED') dotColor = '#06b6d4';

            item.innerHTML = `
                <div class="timeline-dot" style="background-color: ${dotColor};"></div>
                <div>
                    <div class="flex items-center justify-between text-xs">
                        <span class="font-bold text-slate-700">${escapeHtml(act.user_name || 'Tizim')}</span>
                        <span class="text-slate-400 font-medium">${formatDateTime(act.created_at)}</span>
                    </div>
                    <p class="text-xs text-slate-600 mt-1">${escapeHtml(act.description)}</p>
                    ${act.old_status && act.new_status ? `
                        <div class="mt-1.5 flex items-center space-x-1.5 text-[11px]">
                            <span class="px-2 py-0.5 rounded-md bg-slate-100 text-slate-600 font-semibold">${act.old_status}</span>
                            <i data-lucide="arrow-right" class="w-3 h-3 text-slate-400"></i>
                            <span class="px-2 py-0.5 rounded-md bg-indigo-50 text-indigo-700 font-semibold">${act.new_status}</span>
                        </div>
                    ` : ''}
                </div>
            `;
            container.appendChild(item);
        });
        lucide.createIcons();
    } catch (err) {
        container.innerHTML = `<div class="text-xs text-rose-500 py-2">${err.message}</div>`;
    }
}

// -----------------------------------------------------------------------------
// Analytics Dashboard
// -----------------------------------------------------------------------------
async function loadDashboardStats() {
    try {
        const stats = await api('/api/dashboard/stats');

        // Update KPI values
        document.getElementById('stat-total').textContent = stats.total_leads;
        document.getElementById('stat-new').textContent = stats.new_leads;
        document.getElementById('stat-contacted').textContent = stats.contacted_leads;
        document.getElementById('stat-qualified').textContent = stats.qualified_leads;
        document.getElementById('stat-won').textContent = stats.won_leads;
        document.getElementById('stat-lost').textContent = stats.lost_leads;
        document.getElementById('stat-conversion').textContent = `${stats.conversion_rate}% konversiya`;

        // Render Status Doughnut Chart
        renderStatusChart(stats.status_distribution);

        // Render Source Bar Chart
        renderSourceChart(stats.source_distribution);

        // Render Recent Activity Stream
        renderRecentActivities(stats.recent_activities);
    } catch (err) {
        showToast('Dashboard ma\'lumotlarini yuklashda xatolik: ' + err.message, 'error');
    }
}

function renderStatusChart(statusDist) {
    const ctx = document.getElementById('statusChart').getContext('2d');
    const labels = statusDist.map(item => item.status);
    const data = statusDist.map(item => item.count);
    const colors = labels.map(label => (STATUS_CONFIG[label] ? STATUS_CONFIG[label].hex : '#94a3b8'));

    if (state.statusChart) {
        state.statusChart.destroy();
    }

    state.statusChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels,
            datasets: [{
                data,
                backgroundColor: colors,
                borderWidth: 2,
                borderColor: '#ffffff',
                hoverOffset: 6
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        boxWidth: 12,
                        padding: 14,
                        font: { size: 12, family: "'Plus Jakarta Sans', sans-serif" }
                    }
                }
            },
            cutout: '70%'
        }
    });
}

function renderSourceChart(sourceDist) {
    const ctx = document.getElementById('sourceChart').getContext('2d');
    const labels = sourceDist.map(item => item.source);
    const data = sourceDist.map(item => item.count);

    if (state.sourceChart) {
        state.sourceChart.destroy();
    }

    state.sourceChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels,
            datasets: [{
                label: 'Leadlar soni',
                data,
                backgroundColor: '#6366f1',
                borderRadius: 8,
                barThickness: 24
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: { precision: 0, font: { family: "'Plus Jakarta Sans', sans-serif" } },
                    grid: { color: '#f1f5f9' }
                },
                x: {
                    grid: { display: false },
                    ticks: { font: { family: "'Plus Jakarta Sans', sans-serif" } }
                }
            }
        }
    });
}

function renderRecentActivities(activities) {
    const container = document.getElementById('recent-activities-list');
    container.innerHTML = '';

    if (!activities || activities.length === 0) {
        container.innerHTML = '<div class="text-xs text-slate-400 py-4 text-center italic">Hozircha hech qanday faoliyat qayd etilmagan.</div>';
        return;
    }

    activities.forEach(act => {
        const item = document.createElement('div');
        item.className = "flex items-start justify-between p-3 rounded-xl hover:bg-slate-50 border border-slate-100 transition";

        item.innerHTML = `
            <div class="flex items-center space-x-3">
                <div class="w-8 h-8 rounded-lg bg-indigo-50 text-indigo-600 flex items-center justify-center font-bold text-xs">
                    <i data-lucide="activity" class="w-4 h-4"></i>
                </div>
                <div>
                    <div class="text-xs font-bold text-slate-800">${escapeHtml(act.description)}</div>
                    <div class="text-[11px] text-slate-400">Muallif: <span class="font-semibold text-slate-600">${escapeHtml(act.user_name || 'Tizim')}</span> &bull; Lead #${act.lead_id}</div>
                </div>
            </div>
            <div class="text-[11px] text-slate-400 font-medium whitespace-nowrap ml-4">
                ${formatDateTime(act.created_at)}
            </div>
        `;
        container.appendChild(item);
    });

    lucide.createIcons();
}

// -----------------------------------------------------------------------------
// Toast Notifications
// -----------------------------------------------------------------------------
function showToast(message, type = 'info') {
    const container = document.getElementById('toast-container');
    const toast = document.createElement('div');

    let bg = 'bg-slate-900 text-white';
    let icon = 'info';
    if (type === 'success') {
        bg = 'bg-emerald-600 text-white';
        icon = 'check-circle-2';
    } else if (type === 'error') {
        bg = 'bg-rose-600 text-white';
        icon = 'alert-triangle';
    }

    toast.className = `toast flex items-center space-x-2.5 px-4 py-3 rounded-xl shadow-xl text-xs font-semibold ${bg}`;
    toast.innerHTML = `
        <i data-lucide="${icon}" class="w-4 h-4"></i>
        <span>${escapeHtml(message)}</span>
    `;

    container.appendChild(toast);
    lucide.createIcons();

    setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transform = 'translateY(10px)';
        toast.style.transition = 'all 0.3s ease';
        setTimeout(() => toast.remove(), 300);
    }, 3500);
}

// -----------------------------------------------------------------------------
// Utilities
// -----------------------------------------------------------------------------
function formatDate(dateStr) {
    if (!dateStr) return '-';
    const d = new Date(dateStr);
    return d.toLocaleDateString('uz-UZ', { year: 'numeric', month: 'short', day: 'numeric' });
}

function formatDateTime(dateStr) {
    if (!dateStr) return '-';
    const d = new Date(dateStr);
    return d.toLocaleDateString('uz-UZ', { month: 'short', day: 'numeric' }) + ' ' + d.toLocaleTimeString('uz-UZ', { hour: '2-digit', minute: '2-digit' });
}

function escapeHtml(str) {
    if (!str) return '';
    return String(str)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#039;');
}
