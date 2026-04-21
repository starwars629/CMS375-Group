(function () {
    let currentUser = null;

    async function loadProfile() {
        const result = await apiRequest('/users/me', 'GET');
        if (!result.ok) {
            showNotification(result.error || 'Failed to load profile', 'error');
            return;
        }
        currentUser = result.data;
        setUser(currentUser);

        document.getElementById('profileName').value = currentUser.name || '';
        document.getElementById('profileEmail').value = currentUser.email || '';
        document.getElementById('profileRole').value = currentUser.role || '';

        const s = currentUser.stats || {};
        document.getElementById('statBorrowed').textContent = s.currently_borrowed || 0;
        document.getElementById('statOverdue').textContent = s.overdue_books || 0;
        document.getElementById('statReservations').textContent = s.pending_reservations || 0;
        document.getElementById('statFine').textContent = '$' + Number(currentUser.fine_balance || 0).toFixed(2);
    }

    async function loadMyLoans() {
        const tbody = document.getElementById('profileLoansBody');
        if (!tbody || !currentUser) return;

        const result = await apiRequest('/users/' + currentUser.user_id + '/loans', 'GET');
        if (!result.ok) {
            tbody.innerHTML = '<tr><td colspan="4" style="color:#dc2626;text-align:center;padding:24px;">' +
                escapeHtml(result.error || 'Failed to load loans') + '</td></tr>';
            return;
        }
        const loans = result.data.loans || [];
        if (loans.length === 0) {
            tbody.innerHTML = '<tr><td colspan="4" style="text-align:center;padding:24px;color:#6b7280;">No loans</td></tr>';
            return;
        }
        let html = '';
        for (let i = 0; i < loans.length; i++) {
            const l = loans[i];
            html += '<tr>' +
                '<td>' + escapeHtml(l.title) + '</td>' +
                '<td>' + formatDate(l.checkout_date) + '</td>' +
                '<td>' + formatDate(l.due_date) + '</td>' +
                '<td>' + escapeHtml(l.status || (l.days_overdue > 0 ? 'overdue' : 'active')) + '</td>' +
                '</tr>';
        }
        tbody.innerHTML = html;
    }

    async function loadMyFines() {
        const tbody = document.getElementById('profileFinesBody');
        if (!tbody || !currentUser) return;

        const result = await apiRequest('/fines/user/' + currentUser.user_id, 'GET');
        if (!result.ok) {
            tbody.innerHTML = '<tr><td colspan="4" style="color:#dc2626;text-align:center;padding:24px;">' +
                escapeHtml(result.error || 'Failed to load fines') + '</td></tr>';
            return;
        }
        const fines = result.data.fines || [];
        if (fines.length === 0) {
            tbody.innerHTML = '<tr><td colspan="4" style="text-align:center;padding:24px;color:#6b7280;">No fines</td></tr>';
            return;
        }
        let html = '';
        for (let i = 0; i < fines.length; i++) {
            const f = fines[i];
            html += '<tr>' +
                '<td>' + escapeHtml(f.book_title || '—') + '</td>' +
                '<td>$' + Number(f.amount).toFixed(2) + '</td>' +
                '<td>' + escapeHtml(f.paid_status) + '</td>' +
                '<td>' + formatDate(f.issued_at) + '</td>' +
                '</tr>';
        }
        tbody.innerHTML = html;
    }

    window.saveProfile = async function () {
        if (!currentUser) return;
        const payload = {
            name: document.getElementById('profileName').value.trim(),
            email: document.getElementById('profileEmail').value.trim()
        };
        const result = await apiRequest('/users/' + currentUser.user_id, 'PUT', payload);
        if (result.ok) {
            showNotification('Profile updated', 'success');
            if (result.data.user) setUser(result.data.user);
        } else {
            showNotification(result.error || 'Update failed', 'error');
        }
    };

    window.changePassword = async function () {
        const cur = document.getElementById('currentPw').value;
        const neu = document.getElementById('newPw').value;
        const conf = document.getElementById('confirmPw').value;
        if (!cur || !neu || !conf) {
            showNotification('Fill in all password fields', 'error');
            return;
        }
        if (neu !== conf) {
            showNotification('New passwords do not match', 'error');
            return;
        }
        const result = await apiRequest('/auth/change-password', 'POST', {
            current_password: cur,
            new_password: neu
        });
        if (result.ok) {
            showNotification('Password changed', 'success');
            document.getElementById('passwordForm').reset();
        } else {
            showNotification(result.error || 'Password change failed', 'error');
        }
    };

    document.addEventListener('DOMContentLoaded', async function () {
        requireAuth();
        await loadProfile();
        await Promise.all([loadMyLoans(), loadMyFines()]);
    });
})();
