const API_BASE = 'http://localhost:5000/api';

function getToken() {
    return sessionStorage.getItem('token');
}

function setToken(token) {
    sessionStorage.setItem('token', token);
    localStorage.setItem('token', token);
}

function clearToken() {
    sessionStorage.removeItem('token');
    localStorage.removeItem('token');
    sessionStorage.removeItem('user');
    localStorage.removeItem('user');
}

function getUser() {
    const raw = sessionStorage.getItem('user') || localStorage.getItem('user');
    if (!raw) return null;
    try { return JSON.parse(raw); } catch (e) { return null; }
}

function setUser(user) {
    const json = JSON.stringify(user);
    sessionStorage.setItem('user', json);
    localStorage.setItem('user', json);
}

function hasRole() {
    const u = getUser();
    if (!u) return false;
    for (let i = 0; i < arguments.length; i++) {
        if (u.role === arguments[i]) return true;
    }
    return false;
}

function isStaff() { return hasRole('librarian', 'admin'); }
function isAdmin() { return hasRole('admin'); }

function isLoggedIn() {
    return !!sessionStorage.getItem('token') || !!localStorage.getItem('token');
}

function logout() {
    clearToken();
    window.location.href = 'index.php';
}

function requireAuth() {
    if (!isLoggedIn()) {
        window.location.href = 'index.php';
    } else if (!sessionStorage.getItem('token') && localStorage.getItem('token')) {
        sessionStorage.setItem('token', localStorage.getItem('token'));
    }
}

async function apiRequest(endpoint, method = 'GET', body = null) {
    const url = API_BASE + endpoint;

    const headers = {
        'Content-Type': 'application/json'
    };

    const token = getToken() || localStorage.getItem('token');
    if (token) {
        headers['Authorization'] = 'Bearer ' + token;
    }

    const options = {
        method: method,
        headers: headers
    };

    if (body && method !== 'GET') {
        options.body = JSON.stringify(body);
    }

    try {
        const response = await fetch(url, options);
        const data = await response.json().catch(() => ({}));

        if (response.status === 401) {
            if (!window.location.pathname.endsWith('index.php') &&
                !window.location.pathname.endsWith('register.php')) {
                logout();
            }
            return { ok: false, success: false, status: 401, error: data.error || 'Unauthorized', data: data };
        }

        if (!response.ok) {
            return { ok: false, success: false, status: response.status, error: data.error || 'Request failed', data: data };
        }

        return { ok: true, success: true, status: response.status, data: data };
    } catch (error) {
        return { ok: false, success: false, status: 0, error: error.message || 'Network error' };
    }
}

function toggleSidebar() {
    var sidebar = document.querySelector('.sidebar');
    var overlay = document.getElementById('sidebarOverlay');
    if (sidebar) {
        sidebar.classList.toggle('active');
    }
    if (overlay) {
        overlay.classList.toggle('active');
    }
}

function showModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.style.display = 'flex';
    }
}

function hideModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.style.display = 'none';
    }
}

function showNotification(message, type = 'success') {
    const colors = {
        success: '#10b981',
        error: '#ef4444',
        warning: '#f59e0b'
    };

    const notification = document.createElement('div');
    notification.style.cssText =
        'position:fixed;top:20px;right:20px;padding:14px 24px;border-radius:8px;color:#fff;' +
        'font-size:14px;font-weight:500;z-index:10000;box-shadow:0 4px 12px rgba(0,0,0,0.15);' +
        'transition:opacity 0.3s ease,transform 0.3s ease;transform:translateX(0);opacity:1;' +
        'max-width:400px;word-wrap:break-word;' +
        'background-color:' + (colors[type] || colors.success) + ';';

    notification.textContent = message;
    document.body.appendChild(notification);

    setTimeout(function () {
        notification.style.opacity = '0';
        notification.style.transform = 'translateX(40px)';
        setTimeout(function () {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 300);
    }, 3000);
}

function formatDate(dateStr) {
    if (!dateStr) return '';
    const months = [
        'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
        'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'
    ];
    const date = new Date(dateStr);
    if (isNaN(date.getTime())) return dateStr;
    const month = months[date.getMonth()];
    const day = date.getDate();
    const year = date.getFullYear();
    return month + ' ' + day + ', ' + year;
}

function escapeHtml(str) {
    if (str === null || str === undefined) return '';
    return String(str)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#39;');
}

function createBadge(text, type) {
    return '<span class="badge badge-' + type + '">' + escapeHtml(text) + '</span>';
}

function renderTable(containerId, columns, data, rowRenderer) {
    const container = document.getElementById(containerId);
    if (!container) return;

    let html = '<table>';

    html += '<thead><tr>';
    for (let i = 0; i < columns.length; i++) {
        html += '<th>' + escapeHtml(columns[i].label) + '</th>';
    }
    html += '</tr></thead>';

    html += '<tbody>';
    if (!data || data.length === 0) {
        html += '<tr><td colspan="' + columns.length + '" style="text-align:center;padding:24px;color:#6b7280;">No records found</td></tr>';
    } else {
        for (let i = 0; i < data.length; i++) {
            html += rowRenderer(data[i]);
        }
    }
    html += '</tbody>';

    html += '</table>';
    container.innerHTML = html;
}

function applyRoleGating() {
    const user = getUser();
    const role = user ? user.role : null;
    const isStaffRole = role === 'librarian' || role === 'admin';
    const isAdminRole = role === 'admin';

    document.querySelectorAll('[data-role="staff"]').forEach(function (el) {
        if (!isStaffRole) el.style.display = 'none';
    });
    document.querySelectorAll('[data-role="admin"]').forEach(function (el) {
        if (!isAdminRole) el.style.display = 'none';
    });

}

document.addEventListener('DOMContentLoaded', function () {
    var hamburger = document.querySelector('.hamburger');
    var sidebar = document.querySelector('.sidebar');

    if (hamburger && sidebar) {
        hamburger.addEventListener('click', function () {
            sidebar.classList.toggle('active');
            hamburger.classList.toggle('active');
        });
    }

    var overlays = document.querySelectorAll('.modal-overlay');

    for (var i = 0; i < overlays.length; i++) {
        overlays[i].addEventListener('click', function (e) {
            if (e.target === this) {
                this.style.display = 'none';
            }
        });
    }

    applyRoleGating();
});
