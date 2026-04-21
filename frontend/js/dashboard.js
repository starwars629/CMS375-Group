(function () {
    async function loadStats() {
        const promises = [
            apiRequest('/books?limit=200', 'GET'),
            apiRequest('/users/me', 'GET')
        ];

        if (isStaff()) {
            promises.push(apiRequest('/loans/active', 'GET'));
            promises.push(apiRequest('/fines/outstanding', 'GET'));
        }
        if (isAdmin()) {
            promises.push(apiRequest('/users/stats', 'GET'));
        }

        const results = await Promise.all(promises);

        const booksEl = document.getElementById('totalBooks');
        if (booksEl) {
            if (results[0].ok) {
                booksEl.textContent = results[0].data.count || 0;
            } else {
                booksEl.textContent = '—';
            }
        }

        const loansEl = document.getElementById('activeLoans');
        if (loansEl) {
            if (isStaff() && results[2] && results[2].ok) {
                loansEl.textContent = results[2].data.count || 0;
            } else if (results[1].ok && results[1].data.stats) {
                loansEl.textContent = results[1].data.stats.currently_borrowed || 0;
            } else {
                loansEl.textContent = '—';
            }
        }

        const resEl = document.getElementById('pendingReservations');
        if (resEl) {
            if (results[1].ok && results[1].data.stats) {
                resEl.textContent = results[1].data.stats.pending_reservations || 0;
            } else {
                resEl.textContent = '—';
            }
        }

        const finesEl = document.getElementById('outstandingFines');
        if (finesEl) {
            if (isStaff() && results[3] && results[3].ok) {
                finesEl.textContent = '$' + Number(results[3].data.total_outstanding || 0).toFixed(2);
            } else if (results[1].ok) {
                finesEl.textContent = '$' + Number(results[1].data.fine_balance || 0).toFixed(2);
            } else {
                finesEl.textContent = '—';
            }
        }

        if (isAdmin() && results[4] && results[4].ok) {
            const s = results[4].data;
            const adminGrid = document.getElementById('adminStatsGrid');
            if (adminGrid) {
                adminGrid.style.display = 'grid';
                document.getElementById('statTotalUsers').textContent = s.total_users || 0;
                document.getElementById('statStudents').textContent = s.students || 0;
                document.getElementById('statFaculty').textContent = s.faculty || 0;
                document.getElementById('statStaff').textContent = (s.librarians || 0) + (s.admins || 0);
            }
        }
    }

    async function loadRecentActivity() {
        const tbody = document.getElementById('recentActivityBody');
        if (!tbody) return;

        if (!isStaff()) {
            const user = getUser();
            if (!user) return;
            const result = await apiRequest('/users/' + user.user_id + '/loans', 'GET');
            if (result.ok && result.data.loans && result.data.loans.length > 0) {
                renderActivity(result.data.loans.slice(0, 10), false);
            } else {
                tbody.innerHTML = '<tr><td colspan="4" style="text-align:center;padding:24px;color:#6b7280;">No recent activity</td></tr>';
            }
            return;
        }

        const result = await apiRequest('/loans/active', 'GET');
        if (result.ok && result.data.loans && result.data.loans.length > 0) {
            renderActivity(result.data.loans.slice(0, 10), true);
        } else {
            tbody.innerHTML = '<tr><td colspan="4" style="text-align:center;padding:24px;color:#6b7280;">No recent activity</td></tr>';
        }
    }

    function renderActivity(loans, staff) {
        const tbody = document.getElementById('recentActivityBody');
        if (!tbody) return;

        let html = '';
        for (let i = 0; i < loans.length; i++) {
            const l = loans[i];
            const action = l.days_overdue > 0 ? 'Overdue Loan' : 'Active Loan';
            html += '<tr>' +
                '<td>' + formatDate(l.checkout_date) + '</td>' +
                '<td>' + escapeHtml(action) + '</td>' +
                '<td>' + escapeHtml(l.title || '') + '</td>' +
                '<td>' + escapeHtml(staff ? (l.borrower_name || '') : 'you') + '</td>' +
                '</tr>';
        }
        tbody.innerHTML = html;
    }

    document.addEventListener('DOMContentLoaded', async function () {
        requireAuth();
        await Promise.all([loadStats(), loadRecentActivity()]);
    });
})();
