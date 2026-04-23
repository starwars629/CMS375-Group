(function () {
    let currentFilter = '';
    let allFines = [];
    let searchTimer = null;

    async function loadFines() {
        const tbody = document.getElementById('finesTableBody');
        if (!tbody) return;
        tbody.innerHTML = '<tr><td colspan="8" style="text-align:center;padding:24px;color:#6b7280;">Loading...</td></tr>';

        const user = getUser();
        if (!user) {
            tbody.innerHTML = '<tr><td colspan="8" style="text-align:center;color:#dc2626;">Not authenticated</td></tr>';
            return;
        }

        let result;
        if (isStaff() && (currentFilter === '' || currentFilter === 'unpaid')) {
            result = await apiRequest('/fines/outstanding', 'GET');
            if (result.ok) {
                allFines = (result.data.fines || []).map(function (f) {
                    return Object.assign({}, f, { paid_status: 'unpaid' });
                });
                updateStats({
                    total: result.data.total_outstanding || 0,
                    unpaid: result.data.total_outstanding || 0,
                    paid: 0
                });
            }
        } else {
            const qs = currentFilter ? '?status=' + encodeURIComponent(currentFilter) : '';
            result = await apiRequest('/fines/user/' + user.user_id + qs, 'GET');
            if (result.ok) {
                allFines = result.data.fines || [];
                const paid = Number(result.data.total_fines_paid) || 0;
                const unpaid = Number(result.data.fine_balance) || 0;
                updateStats({ total: paid + unpaid, paid: paid, unpaid: unpaid });
            }
        }

        if (!result.ok) {
            tbody.innerHTML = '<tr><td colspan="8" style="text-align:center;padding:24px;color:#dc2626;">' +
                escapeHtml(result.error || 'Failed to load fines') + '</td></tr>';
            return;
        }

        renderFines(allFines);
    }

    function updateStats(s) {
        const totalEl = document.getElementById('totalFinesAmount');
        const paidEl = document.getElementById('paidFinesAmount');
        const unpaidEl = document.getElementById('unpaidFinesAmount');
        if (totalEl) totalEl.textContent = '$' + Number(s.total).toFixed(2);
        if (paidEl) paidEl.textContent = '$' + Number(s.paid).toFixed(2);
        if (unpaidEl) unpaidEl.textContent = '$' + Number(s.unpaid).toFixed(2);
    }

    function renderFines(fines) {
        const tbody = document.getElementById('finesTableBody');
        if (!tbody) return;

        const q = ((document.getElementById('fineSearch') || {}).value || '').trim().toLowerCase();
        if (q) {
            fines = fines.filter(function (f) {
                return (f.book_title || '').toLowerCase().indexOf(q) !== -1 ||
                    (f.borrower_name || '').toLowerCase().indexOf(q) !== -1 ||
                    (f.borrower_email || '').toLowerCase().indexOf(q) !== -1;
            });
        }

        if (fines.length === 0) {
            tbody.innerHTML = '<tr><td colspan="8" style="text-align:center;padding:24px;color:#6b7280;">No fines found</td></tr>';
            return;
        }

        const user = getUser();

        let html = '';
        for (let i = 0; i < fines.length; i++) {
            const f = fines[i];
            const isUnpaid = f.paid_status === 'unpaid';
            const badgeType = isUnpaid ? 'danger' : 'success';

            let actions = '';
            if (isUnpaid) {
                actions += '<button class="btn btn-sm btn-primary" onclick="payFine(' + f.fine_id + ')">Pay</button>';
                if (isStaff()) {
                    actions += ' <button class="btn btn-sm btn-secondary" onclick="waiveFine(' + f.fine_id + ')">Waive</button>';
                }
            }

            const memberLabel = f.borrower_name || (user ? user.name : '—');

            html += '<tr>' +
                '<td>' + f.fine_id + '</td>' +
                '<td>' + escapeHtml(memberLabel) + '</td>' +
                '<td>' + escapeHtml(f.book_title || '—') + '</td>' +
                '<td>$' + Number(f.amount).toFixed(2) + '</td>' +
                '<td>Overdue return</td>' +
                '<td>' + createBadge(f.paid_status || 'unpaid', badgeType) + '</td>' +
                '<td>' + formatDate(f.issued_at) + '</td>' +
                '<td>' + actions + '</td>' +
                '</tr>';
        }
        tbody.innerHTML = html;
    }

    window.payFine = async function (fineId) {
        if (!confirm('Mark this fine as paid?')) return;
        const result = await apiRequest('/fines/' + fineId + '/pay', 'POST');
        if (result.ok) {
            showNotification('Fine paid: $' + result.data.amount_paid, 'success');
            loadFines();
        } else {
            showNotification(result.error || 'Payment failed', 'error');
        }
    };

    window.showUsersWithFines = async function () {
        const result = await apiRequest('/users/with-fines', 'GET');
        const body = document.getElementById('usersWithFinesBody');
        if (!body) return;

        if (!result.ok) {
            body.innerHTML = '<p style="color:#dc2626;">' + escapeHtml(result.error || 'Failed to load') + '</p>';
            showModal('usersWithFinesModal');
            return;
        }
        const users = result.data.users || [];
        if (users.length === 0) {
            body.innerHTML = '<p style="color:#6b7280;">No users with outstanding fines.</p>';
        } else {
            let html = '<table><thead><tr><th>ID</th><th>Name</th><th>Email</th><th>Total Owed</th></tr></thead><tbody>';
            for (let i = 0; i < users.length; i++) {
                const u = users[i];
                html += '<tr>' +
                    '<td>' + u.user_id + '</td>' +
                    '<td>' + escapeHtml(u.name) + '</td>' +
                    '<td>' + escapeHtml(u.email) + '</td>' +
                    '<td>$' + Number(u.total_owed).toFixed(2) + '</td>' +
                    '</tr>';
            }
            html += '</tbody></table>';
            body.innerHTML = html;
        }
        showModal('usersWithFinesModal');
    };

    window.waiveFine = async function (fineId) {
        if (!confirm('Waive this fine? This cannot be undone.')) return;
        const result = await apiRequest('/fines/' + fineId + '/waive', 'POST');
        if (result.ok) {
            showNotification('Fine waived: $' + result.data.amount_waived, 'success');
            loadFines();
        } else {
            showNotification(result.error || 'Waive failed', 'error');
        }
    };

    function wireControls() {
        const status = document.getElementById('statusFilter');
        if (status) {
            status.addEventListener('change', function () {
                currentFilter = status.value;
                loadFines();
            });
        }
        const search = document.getElementById('fineSearch');
        if (search) {
            search.addEventListener('input', function () {
                clearTimeout(searchTimer);
                searchTimer = setTimeout(function () {
                    renderFines(allFines);
                }, 250);
            });
        }
    }

    document.addEventListener('DOMContentLoaded', function () {
        requireAuth();
        wireControls();
        loadFines();
    });
})();
