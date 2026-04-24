(function () {
    let searchTimer = null;

    async function loadUsers() {
        const tbody = document.getElementById('usersTableBody');
        if (!tbody) return;

        if (!isStaff()) {
            tbody.innerHTML = '<tr><td colspan="8" style="text-align:center;padding:24px;color:#6b7280;">Staff access required.</td></tr>';
            return;
        }

        tbody.innerHTML = '<tr><td colspan="8" style="text-align:center;padding:24px;color:#6b7280;">Loading...</td></tr>';

        const search = (document.getElementById('searchInput') || {}).value || '';
        const roleFilter = (document.getElementById('roleFilter') || {}).value || '';

        const params = new URLSearchParams();
        if (search) params.set('search', search);
        if (roleFilter && roleFilter !== 'all') params.set('role', roleFilter);
        params.set('limit', 50);

        const result = await apiRequest('/users?' + params.toString(), 'GET');
        if (!result.ok) {
            tbody.innerHTML = '<tr><td colspan="8" style="text-align:center;padding:24px;color:#dc2626;">' +
                escapeHtml(result.error || 'Failed to load users') + '</td></tr>';
            return;
        }

        const users = result.data.users || [];
        if (users.length === 0) {
            tbody.innerHTML = '<tr><td colspan="8" style="text-align:center;padding:24px;color:#6b7280;">No users found</td></tr>';
            return;
        }

        let html = '';
        for (let i = 0; i < users.length; i++) {
            const u = users[i];
            const fineStr = u.fine_balance ? '$' + Number(u.fine_balance).toFixed(2) : '$0.00';
            const activeLoans = u.active_loans || 0;

            let actions = '<button class="btn btn-sm btn-secondary" onclick="viewActivity(' + u.user_id + ')">Activity</button>';
            if (isAdmin()) {
                actions += ' <button class="btn btn-sm btn-primary" onclick="openRoleChange(' + u.user_id + ', \'' + escapeJs(u.name) + '\', \'' + escapeJs(u.role) + '\')">Role</button>';
                actions += ' <button class="btn btn-sm btn-danger" onclick="deleteUser(' + u.user_id + ', \'' + escapeJs(u.name) + '\')">Delete</button>';
            }

            html += '<tr>' +
                '<td>' + u.user_id + '</td>' +
                '<td>' + escapeHtml(u.name) + '</td>' +
                '<td>' + escapeHtml(u.email) + '</td>' +
                '<td>' + createBadge(u.role, roleColor(u.role)) + '</td>' +
                '<td>' + activeLoans + '</td>' +
                '<td>' + fineStr + '</td>' +
                '<td>' + formatDate(u.created_at) + '</td>' +
                '<td>' + actions + '</td>' +
                '</tr>';
        }
        tbody.innerHTML = html;
    }

    function escapeJs(s) {
        if (!s) return '';
        return String(s).replace(/\\/g, '\\\\').replace(/'/g, "\\'").replace(/"/g, '\\"');
    }

    function roleColor(r) {
        if (r === 'admin') return 'danger';
        if (r === 'librarian') return 'info';
        if (r === 'faculty') return 'warning';
        return 'secondary';
    }

    window.viewActivity = async function (userId) {
        const result = await apiRequest('/users/' + userId + '/activity', 'GET');
        if (!result.ok) {
            showNotification(result.error || 'Failed to load activity', 'error');
            return;
        }
        const d = result.data;
        const body = document.getElementById('activityBody');
        if (!body) return;

        let html = '<h4>' + escapeHtml(d.user.name) + ' — ' + escapeHtml(d.user.email) + '</h4>';

        html += '<h5 style="margin-top:16px;">Recent Loans</h5>';
        if (d.recent_loans && d.recent_loans.length) {
            html += '<table><thead><tr><th>Book</th><th>Checkout</th><th>Due</th><th>Returned</th><th>Status</th></tr></thead><tbody>';
            for (let i = 0; i < d.recent_loans.length; i++) {
                const l = d.recent_loans[i];
                html += '<tr><td>' + escapeHtml(l.book_title) + '</td>' +
                    '<td>' + formatDate(l.checkout_date) + '</td>' +
                    '<td>' + formatDate(l.due_date) + '</td>' +
                    '<td>' + formatDate(l.return_date) + '</td>' +
                    '<td>' + escapeHtml(l.status) + '</td></tr>';
            }
            html += '</tbody></table>';
        } else {
            html += '<p style="color:#6b7280;">No loans</p>';
        }

        html += '<h5 style="margin-top:16px;">Recent Fines</h5>';
        if (d.recent_fines && d.recent_fines.length) {
            html += '<table><thead><tr><th>Book</th><th>Amount</th><th>Status</th><th>Issued</th></tr></thead><tbody>';
            for (let i = 0; i < d.recent_fines.length; i++) {
                const f = d.recent_fines[i];
                html += '<tr><td>' + escapeHtml(f.book_title) + '</td>' +
                    '<td>$' + Number(f.amount).toFixed(2) + '</td>' +
                    '<td>' + escapeHtml(f.paid_status) + '</td>' +
                    '<td>' + formatDate(f.issued_at) + '</td></tr>';
            }
            html += '</tbody></table>';
        } else {
            html += '<p style="color:#6b7280;">No fines</p>';
        }

        html += '<h5 style="margin-top:16px;">Active Reservations</h5>';
        if (d.active_reservations && d.active_reservations.length) {
            html += '<table><thead><tr><th>Book</th><th>Reserved</th><th>Status</th></tr></thead><tbody>';
            for (let i = 0; i < d.active_reservations.length; i++) {
                const r = d.active_reservations[i];
                html += '<tr><td>' + escapeHtml(r.book_title) + '</td>' +
                    '<td>' + formatDate(r.reservation_date) + '</td>' +
                    '<td>' + escapeHtml(r.status) + '</td></tr>';
            }
            html += '</tbody></table>';
        } else {
            html += '<p style="color:#6b7280;">No active reservations</p>';
        }

        body.innerHTML = html;
        showModal('activityModal');
    };

    window.openRoleChange = function (userId, name, currentRole) {
        document.getElementById('roleChangeUserId').value = userId;
        document.getElementById('roleChangeName').textContent = name;
        document.getElementById('roleChangeSelect').value = currentRole;
        showModal('roleChangeModal');
    };

    window.saveRoleChange = async function () {
        const userId = document.getElementById('roleChangeUserId').value;
        const newRole = document.getElementById('roleChangeSelect').value;
        const result = await apiRequest('/users/' + userId + '/role', 'PUT', { role: newRole });
        if (result.ok) {
            hideModal('roleChangeModal');
            showNotification('Role updated: ' + result.data.old_role + ' → ' + result.data.new_role, 'success');
            loadUsers();
        } else {
            showNotification(result.error || 'Failed to update role', 'error');
        }
    };

    window.deleteUser = async function (userId, name) {
        if (!confirm('Delete user "' + name + '"? This cannot be undone.')) return;
        const result = await apiRequest('/users/' + userId, 'DELETE');
        if (result.ok) {
            showNotification('User deleted', 'success');
            loadUsers();
        } else {
            showNotification(result.error || 'Delete failed', 'error');
        }
    };

    window.saveUser = async function () {
        const firstName = document.getElementById('firstName').value.trim();
        const lastName = document.getElementById('lastName').value.trim();
        const email = document.getElementById('userEmail').value.trim();
        const password = document.getElementById('userPassword').value;

        if (!firstName || !lastName || !email || !password) {
            showNotification('Name, email, and password required', 'error');
            return;
        }

        const payload = {
            name: firstName + ' ' + lastName,
            email: email,
            password: password
        };

        const result = await apiRequest('/auth/register', 'POST', payload);
        if (result.ok) {
            hideModal('userModal');
            document.getElementById('userForm').reset();
            showNotification('Member created (role: student by default — use Role action to elevate)', 'success');
            loadUsers();
        } else {
            showNotification(result.error || 'Failed to create user', 'error');
        }
    };

    function wireControls() {
        const search = document.getElementById('searchInput');
        if (search) {
            search.addEventListener('input', function () {
                clearTimeout(searchTimer);
                searchTimer = setTimeout(loadUsers, 300);
            });
        }
        const role = document.getElementById('roleFilter');
        if (role) role.addEventListener('change', loadUsers);
    }

    document.addEventListener('DOMContentLoaded', function () {
        requireAuth();
        wireControls();
        loadUsers();
    });
})();
