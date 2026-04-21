(function () {
    let currentFilter = '';
    let allReservations = [];
    let searchTimer = null;

    async function loadReservations() {
        const tbody = document.getElementById('reservationsTableBody');
        if (!tbody) return;
        tbody.innerHTML = '<tr><td colspan="6" style="text-align:center;padding:24px;color:#6b7280;">Loading...</td></tr>';

        const user = getUser();
        if (!user) {
            tbody.innerHTML = '<tr><td colspan="6" style="text-align:center;color:#dc2626;">Not authenticated</td></tr>';
            return;
        }

        const qs = currentFilter ? '?status=' + encodeURIComponent(currentFilter) : '';
        const result = await apiRequest('/reservations/user/' + user.user_id + qs, 'GET');

        if (!result.ok) {
            tbody.innerHTML = '<tr><td colspan="6" style="text-align:center;padding:24px;color:#dc2626;">' +
                escapeHtml(result.error || 'Failed to load reservations') + '</td></tr>';
            return;
        }

        allReservations = result.data.reservations || [];
        renderReservations(allReservations);
    }

    function renderReservations(rs) {
        const tbody = document.getElementById('reservationsTableBody');
        if (!tbody) return;

        const q = ((document.getElementById('reservationSearch') || {}).value || '').trim().toLowerCase();
        if (q) {
            rs = rs.filter(function (r) {
                return (r.title || '').toLowerCase().indexOf(q) !== -1 ||
                    (r.author || '').toLowerCase().indexOf(q) !== -1;
            });
        }

        if (rs.length === 0) {
            tbody.innerHTML = '<tr><td colspan="6" style="text-align:center;padding:24px;color:#6b7280;">No reservations found</td></tr>';
            return;
        }

        const user = getUser();
        const memberName = user ? user.name : '—';

        let html = '';
        for (let i = 0; i < rs.length; i++) {
            const r = rs[i];
            const badgeType = r.status === 'pending' ? 'warning' : (r.status === 'fulfilled' ? 'success' : 'secondary');

            let actions = '';
            if (r.status === 'pending') {
                actions = '<button class="btn btn-sm btn-danger" onclick="cancelReservation(' + r.reservation_id + ')">Cancel</button>';
            }

            html += '<tr>' +
                '<td>' + r.reservation_id + '</td>' +
                '<td>' + escapeHtml(r.title || '') + '</td>' +
                '<td>' + escapeHtml(memberName) + '</td>' +
                '<td>' + formatDate(r.reservation_date) + '</td>' +
                '<td>' + createBadge(r.status, badgeType) + '</td>' +
                '<td>' + actions + '</td>' +
                '</tr>';
        }
        tbody.innerHTML = html;
    }

    window.cancelReservation = async function (resId) {
        if (!confirm('Cancel this reservation?')) return;
        const result = await apiRequest('/reservations/' + resId + '/cancel', 'PUT');
        if (result.ok) {
            showNotification('Reservation cancelled', 'success');
            loadReservations();
        } else {
            showNotification(result.error || 'Cancel failed', 'error');
        }
    };

    window.saveReservation = async function () {
        const bookInput = document.getElementById('resBookInput').value.trim();
        if (!bookInput) {
            showNotification('Please enter a book ID or title', 'error');
            return;
        }

        let bookId = parseInt(bookInput, 10);
        if (isNaN(bookId)) {
            const search = await apiRequest('/books?query=' + encodeURIComponent(bookInput) + '&limit=5', 'GET');
            if (!search.ok || !search.data.books || search.data.books.length === 0) {
                showNotification('Book not found', 'error');
                return;
            }
            if (search.data.books.length > 1) {
                const titles = search.data.books.map(function (b) { return b.book_id + ': ' + b.title; }).join('\n');
                showNotification('Multiple matches. Enter book ID:\n' + titles, 'warning');
                return;
            }
            bookId = search.data.books[0].book_id;
        }

        const result = await apiRequest('/reservations', 'POST', { book_id: bookId });
        if (result.ok) {
            hideModal('reservationModal');
            document.getElementById('reservationForm').reset();
            showNotification('Reservation created', 'success');
            loadReservations();
        } else {
            showNotification(result.error || 'Failed to create reservation', 'error');
        }
    };

    window.viewBookQueue = async function () {
        const input = document.getElementById('queueBookInput').value.trim();
        if (!input) {
            showNotification('Enter a book ID', 'error');
            return;
        }
        let bookId = parseInt(input, 10);
        if (isNaN(bookId)) {
            const search = await apiRequest('/books?query=' + encodeURIComponent(input) + '&limit=1', 'GET');
            if (!search.ok || !search.data.books || search.data.books.length === 0) {
                showNotification('Book not found', 'error');
                return;
            }
            bookId = search.data.books[0].book_id;
        }

        const result = await apiRequest('/reservations/book/' + bookId, 'GET');
        if (!result.ok) {
            showNotification(result.error || 'Failed to load queue', 'error');
            return;
        }

        const body = document.getElementById('queueBody');
        if (!body) return;
        const d = result.data;
        let html = '<p><strong>Book:</strong> ' + escapeHtml(d.title) + ' by ' + escapeHtml(d.author) + '</p>' +
            '<p><strong>Available copies:</strong> ' + d.available_copies + '</p>' +
            '<p><strong>Queue length:</strong> ' + d.queue_length + '</p>';

        if (d.queue && d.queue.length > 0) {
            html += '<table><thead><tr><th>#</th><th>Reserved</th><th>Name</th><th>Email</th><th>Role</th></tr></thead><tbody>';
            for (let i = 0; i < d.queue.length; i++) {
                const q = d.queue[i];
                html += '<tr>' +
                    '<td>' + (i + 1) + '</td>' +
                    '<td>' + formatDate(q.reservation_date) + '</td>' +
                    '<td>' + escapeHtml(q.borrower_name) + '</td>' +
                    '<td>' + escapeHtml(q.borrower_email) + '</td>' +
                    '<td>' + escapeHtml(q.role) + '</td>' +
                    '</tr>';
            }
            html += '</tbody></table>';
        }

        body.innerHTML = html;
        showModal('queueModal');
    };

    function wireControls() {
        const status = document.getElementById('statusFilter');
        if (status) {
            status.addEventListener('change', function () {
                currentFilter = status.value;
                loadReservations();
            });
        }
        const search = document.getElementById('reservationSearch');
        if (search) {
            search.addEventListener('input', function () {
                clearTimeout(searchTimer);
                searchTimer = setTimeout(function () {
                    renderReservations(allReservations);
                }, 250);
            });
        }
    }

    document.addEventListener('DOMContentLoaded', function () {
        requireAuth();
        wireControls();
        loadReservations();
    });
})();
