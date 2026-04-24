(function () {
    const PAGE_SIZE = 20;
    let currentOffset = 0;
    let currentQuery = '';
    let currentGenre = '';
    let lastCount = 0;

    let searchTimer = null;

    async function loadBooks() {
        const params = new URLSearchParams();
        if (currentQuery) params.set('query', currentQuery);
        if (currentGenre) params.set('genre', currentGenre);
        params.set('limit', PAGE_SIZE);
        params.set('offset', currentOffset);

        const result = await apiRequest('/books?' + params.toString(), 'GET');

        const tbody = document.getElementById('booksTableBody');
        if (!tbody) return;

        if (!result.ok) {
            tbody.innerHTML = '<tr><td colspan="7" style="text-align:center;padding:24px;color:#dc2626;">' +
                escapeHtml(result.error || 'Failed to load books') + '</td></tr>';
            return;
        }

        const books = result.data.books || [];
        lastCount = books.length;

        if (books.length === 0) {
            tbody.innerHTML = '<tr><td colspan="7" style="text-align:center;padding:24px;color:#6b7280;">No books found</td></tr>';
            updatePaginationLabel();
            return;
        }

        let html = '';
        for (let i = 0; i < books.length; i++) {
            const b = books[i];
            const safeBookId = Number(b.book_id) || 0;
            const available = b.available_copies > 0;
            const statusBadge = available
                ? '<span class="badge badge-success">' + b.available_copies + '/' + b.total_copies + ' available</span>'
                : '<span class="badge badge-danger">Unavailable</span>';

            let actions = '<button class="btn btn-sm btn-secondary" onclick="viewBookDetails(' + safeBookId + ')">Details</button>';
            if (available) {
                actions += ' <button class="btn btn-sm btn-primary" onclick="checkoutBookFromList(' + safeBookId + ', \'' + escapeJsString(b.title) + '\')">Checkout</button>';
            } else {
                actions += ' <button class="btn btn-sm btn-secondary" onclick="reserveBookFromList(' + safeBookId + ', \'' + escapeJsString(b.title) + '\')">Reserve</button>';
            }

            html += '<tr>' +
                '<td>' + escapeHtml(b.ISBN || '') + '</td>' +
                '<td>' + escapeHtml(b.title || '') + '</td>' +
                '<td>' + escapeHtml(b.author || '') + '</td>' +
                '<td>' + escapeHtml(b.genre || '') + '</td>' +
                '<td>' + escapeHtml(b.location || '') + '</td>' +
                '<td>' + statusBadge + '</td>' +
                '<td>' + actions + '</td>' +
                '</tr>';
        }
        tbody.innerHTML = html;
        updatePaginationLabel();
    }

    function escapeJsString(str) {
        if (!str) return '';
        return String(str).replace(/\\/g, '\\\\').replace(/'/g, "\\'").replace(/"/g, '\\"');
    }

    function updatePaginationLabel() {
        const label = document.getElementById('pageInfo');
        if (label) {
            const start = lastCount === 0 ? 0 : currentOffset + 1;
            const end = currentOffset + lastCount;
            label.textContent = 'Showing ' + start + '-' + end;
        }
        const prev = document.getElementById('prevPage');
        const next = document.getElementById('nextPage');
        if (prev) prev.disabled = currentOffset === 0;
        if (next) next.disabled = lastCount < PAGE_SIZE;
    }

    window.viewBookDetails = async function (bookId) {
        const result = await apiRequest('/books/' + bookId, 'GET');
        if (!result.ok) {
            showNotification(result.error || 'Failed to load book', 'error');
            return;
        }
        const b = result.data;
        const body = document.getElementById('bookDetailBody');
        if (body) {
            body.innerHTML =
                '<p><strong>Title:</strong> ' + escapeHtml(b.title) + '</p>' +
                '<p><strong>Author:</strong> ' + escapeHtml(b.author) + '</p>' +
                '<p><strong>ISBN:</strong> ' + escapeHtml(b.ISBN) + '</p>' +
                '<p><strong>Genre:</strong> ' + escapeHtml(b.genre || '—') + '</p>' +
                '<p><strong>Subject:</strong> ' + escapeHtml(b.subject || '—') + '</p>' +
                '<p><strong>Location:</strong> ' + escapeHtml(b.location || '—') + '</p>' +
                '<p><strong>Copies:</strong> ' + b.available_copies + ' of ' + b.total_copies + ' available</p>' +
                '<p><strong>Added:</strong> ' + formatDate(b.created_at) + '</p>';
        }
        showModal('bookDetailModal');
    };

    window.checkoutBookFromList = async function (bookId, title) {
        if (!confirm('Check out "' + title + '"?')) return;
        const result = await apiRequest('/loans/checkout', 'POST', { book_id: bookId });
        if (result.ok) {
            showNotification('Checked out. Due ' + result.data.due_date, 'success');
            loadBooks();
        } else {
            showNotification(result.error || 'Checkout failed', 'error');
        }
    };

    window.reserveBookFromList = async function (bookId, title) {
        if (!confirm('Reserve "' + title + '"?')) return;
        const result = await apiRequest('/reservations', 'POST', { book_id: bookId });
        if (result.ok) {
            showNotification('Reservation created', 'success');
        } else {
            showNotification(result.error || 'Reservation failed', 'error');
        }
    };

    window.saveBook = async function () {
        const payload = {
            bookIsbn: document.getElementById('bookIsbn').value.trim(),
            bookTitle: document.getElementById('bookTitle').value.trim(),
            bookAuthor: document.getElementById('bookAuthor').value.trim(),
            bookGenre: document.getElementById('bookCategory').value,
            bookYear: parseInt(document.getElementById('bookYear').value, 10),
            bookCopies: parseInt(document.getElementById('bookCopies').value, 10)
        };

        if (!payload.bookIsbn || !payload.bookTitle || !payload.bookAuthor || !payload.bookGenre || !payload.bookYear || !payload.bookCopies) {
            showNotification('Please fill in all fields', 'error');
            return;
        }

        const result = await apiRequest('/books', 'POST', payload);
        if (result.ok) {
            hideModal('bookModal');
            showNotification('Book added successfully', 'success');
            document.getElementById('bookForm').reset();
            currentOffset = 0;
            loadBooks();
        } else {
            showNotification(result.error || 'Failed to add book', 'error');
        }
    };

    function wireControls() {
        const search = document.getElementById('bookSearch');
        if (search) {
            search.addEventListener('input', function () {
                clearTimeout(searchTimer);
                searchTimer = setTimeout(function () {
                    currentQuery = search.value.trim();
                    currentOffset = 0;
                    loadBooks();
                }, 300);
            });
        }

        const genre = document.getElementById('categoryFilter');
        if (genre) {
            genre.addEventListener('change', function () {
                currentGenre = genre.value;
                currentOffset = 0;
                loadBooks();
            });
        }

        const prev = document.getElementById('prevPage');
        if (prev) {
            prev.addEventListener('click', function () {
                if (currentOffset > 0) {
                    currentOffset = Math.max(0, currentOffset - PAGE_SIZE);
                    loadBooks();
                }
            });
        }

        const next = document.getElementById('nextPage');
        if (next) {
            next.addEventListener('click', function () {
                if (lastCount >= PAGE_SIZE) {
                    currentOffset += PAGE_SIZE;
                    loadBooks();
                }
            });
        }
    }

    document.addEventListener('DOMContentLoaded', function () {
        requireAuth();
        wireControls();
        loadBooks();
    });
})();
