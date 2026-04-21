(function () {
    let currentFilter = 'all';
    let allLoans = [];
    let searchTimer = null;

    async function loadLoans() {
        const tbody = document.getElementById('loansTableBody');
        if (!tbody) return;
        tbody.innerHTML = '<tr><td colspan="8" style="text-align:center;padding:24px;color:#6b7280;">Loading...</td></tr>';

        const user = getUser();
        let result;

        if (isStaff()) {
            if (currentFilter === 'overdue') {
                result = await apiRequest('/loans/overdue', 'GET');
            } else {
                result = await apiRequest('/loans/active', 'GET');
            }
        } else if (user) {
            const qs = currentFilter !== 'all' ? '?status=' + encodeURIComponent(currentFilter) : '';
            result = await apiRequest('/users/' + user.user_id + '/loans' + qs, 'GET');
        } else {
            tbody.innerHTML = '<tr><td colspan="8" style="text-align:center;color:#dc2626;">Not authenticated</td></tr>';
            return;
        }

        if (!result.ok) {
            tbody.innerHTML = '<tr><td colspan="8" style="text-align:center;padding:24px;color:#dc2626;">' +
                escapeHtml(result.error || 'Failed to load loans') + '</td></tr>';
            return;
        }

        allLoans = result.data.loans || [];

        let filtered = allLoans;
        if (isStaff() && currentFilter === 'returned') {
            filtered = [];
        } else if (isStaff() && currentFilter === 'active') {
            filtered = allLoans.filter(function (l) {
                return !l.days_overdue || l.days_overdue <= 0;
            });
        }

        renderLoans(filtered);
    }

    function renderLoans(loans) {
        const tbody = document.getElementById('loansTableBody');
        if (!tbody) return;

        const searchTerm = (document.getElementById('loanSearch') || {}).value || '';
        const q = searchTerm.trim().toLowerCase();
        if (q) {
            loans = loans.filter(function (l) {
                return (l.title || '').toLowerCase().indexOf(q) !== -1 ||
                    (l.borrower_name || l.name || '').toLowerCase().indexOf(q) !== -1 ||
                    (l.ISBN || '').toLowerCase().indexOf(q) !== -1;
            });
        }

        if (loans.length === 0) {
            tbody.innerHTML = '<tr><td colspan="8" style="text-align:center;padding:24px;color:#6b7280;">No loans found</td></tr>';
            return;
        }

        let html = '';
        for (let i = 0; i < loans.length; i++) {
            const l = loans[i];
            const daysOverdue = l.days_overdue || 0;
            const isOverdue = daysOverdue > 0;
            const statusText = l.status ? l.status : (isOverdue ? 'overdue' : 'active');
            const badgeType = isOverdue ? 'danger' : (statusText === 'returned' ? 'secondary' : 'success');

            let actions = '';
            if (statusText !== 'returned') {
                actions += '<button class="btn btn-sm btn-primary" onclick="returnLoan(' + l.loan_id + ')">Return</button>';
                if (!isOverdue) {
                    actions += ' <button class="btn btn-sm btn-secondary" onclick="renewLoan(' + l.loan_id + ')">Renew</button>';
                }
            }

            html += '<tr>' +
                '<td>' + l.loan_id + '</td>' +
                '<td>' + escapeHtml(l.title || '') + '</td>' +
                '<td>' + escapeHtml(l.borrower_name || l.name || '—') + '</td>' +
                '<td>' + formatDate(l.checkout_date) + '</td>' +
                '<td>' + formatDate(l.due_date) + (isOverdue ? ' <span style="color:#dc2626;">(+' + daysOverdue + 'd)</span>' : '') + '</td>' +
                '<td>' + formatDate(l.return_date) + '</td>' +
                '<td>' + createBadge(statusText, badgeType) + '</td>' +
                '<td>' + actions + '</td>' +
                '</tr>';
        }
        tbody.innerHTML = html;
    }

    window.returnLoan = async function (loanId) {
        if (!confirm('Return this loan?')) return;
        const result = await apiRequest('/loans/' + loanId + '/return', 'POST');
        if (result.ok) {
            let msg = 'Book returned';
            if (result.data.fine) {
                msg += ' — fine of $' + result.data.fine.amount + ' added (' + result.data.fine.days_overdue + ' days overdue)';
            }
            showNotification(msg, result.data.fine ? 'warning' : 'success');
            loadLoans();
        } else {
            showNotification(result.error || 'Return failed', 'error');
        }
    };

    window.renewLoan = async function (loanId) {
        const result = await apiRequest('/loans/' + loanId + '/renew', 'POST');
        if (result.ok) {
            showNotification('Renewed. New due date: ' + result.data.new_due_date, 'success');
            loadLoans();
        } else {
            showNotification(result.error || 'Renewal failed', 'error');
        }
    };

    window.saveCheckout = async function () {
        const bookInput = document.getElementById('bookInput').value.trim();
        if (!bookInput) {
            showNotification('Please enter a book ID, title, or ISBN', 'error');
            return;
        }

        let bookId = parseInt(bookInput, 10);

        if (isNaN(bookId)) {
            const search = await apiRequest('/books?query=' + encodeURIComponent(bookInput) + '&limit=5', 'GET');
            if (!search.ok || !search.data.books || search.data.books.length === 0) {
                showNotification('Book not found matching "' + bookInput + '"', 'error');
                return;
            }
            if (search.data.books.length > 1) {
                const titles = search.data.books.map(function (b) { return b.book_id + ': ' + b.title; }).join('\n');
                showNotification('Multiple matches. Enter book ID:\n' + titles, 'warning');
                return;
            }
            bookId = search.data.books[0].book_id;
        }

        const result = await apiRequest('/loans/checkout', 'POST', { book_id: bookId });
        if (result.ok) {
            hideModal('checkoutModal');
            document.getElementById('memberInput').value = '';
            document.getElementById('bookInput').value = '';
            showNotification('Checked out. Due ' + result.data.due_date, 'success');
            loadLoans();
        } else {
            showNotification(result.error || 'Checkout failed', 'error');
        }
    };

    function wireControls() {
        const status = document.getElementById('statusFilter');
        if (status) {
            status.addEventListener('change', function () {
                currentFilter = status.value;
                loadLoans();
            });
        }

        const search = document.getElementById('loanSearch');
        if (search) {
            search.addEventListener('input', function () {
                clearTimeout(searchTimer);
                searchTimer = setTimeout(function () {
                    renderLoans(allLoans);
                }, 250);
            });
        }

        const notice = document.getElementById('checkoutNotice');
        if (notice) {
            const u = getUser();
            notice.textContent = 'Note: checkout is recorded under your account (' +
                (u ? u.name : 'current user') + '). Backend does not support staff checkout on behalf of members.';
        }
    }

    document.addEventListener('DOMContentLoaded', function () {
        requireAuth();
        wireControls();
        loadLoans();
    });
})();
