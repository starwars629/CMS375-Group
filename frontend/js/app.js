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
}

function isLoggedIn() {
    return !!sessionStorage.getItem('token');
}

function logout() {
    clearToken();
    window.location.href = 'index.php';
}

function requireAuth() {
    if (!isLoggedIn()) {
        window.location.href = 'index.php';
    }
}

async function apiRequest(endpoint, method = 'GET', body = null) {
    const url = API_BASE + endpoint;

    const headers = {
        'Content-Type': 'application/json'
    };

    const token = getToken();
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

        if (response.status === 401) {
            logout();
            return { success: false, error: 'Unauthorized' };
        }

        const data = await response.json();
        return { success: true, data: data };
    } catch (error) {
        return { success: false, error: error.message };
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
    const month = months[date.getMonth()];
    const day = date.getDate();
    const year = date.getFullYear();
    return month + ' ' + day + ', ' + year;
}

function createBadge(text, type) {
    return '<span class="badge badge-' + type + '">' + text + '</span>';
}

function renderTable(containerId, columns, data, rowRenderer) {
    const container = document.getElementById(containerId);
    if (!container) return;

    let html = '<table>';

    html += '<thead><tr>';
    for (let i = 0; i < columns.length; i++) {
        html += '<th>' + columns[i].label + '</th>';
    }
    html += '</tr></thead>';

    html += '<tbody>';
    if (data.length === 0) {
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
});