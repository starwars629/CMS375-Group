<?php require_once 'includes/config.php'; $pageTitle = 'Books'; require_once 'includes/header.php'; ?>

<div class="toolbar">
  <input type="text" id="bookSearch" class="toolbar-search" placeholder="Search by title, author, or ISBN...">
  <select id="categoryFilter" class="toolbar-filter">
    <option value="">All Categories</option>
    <option value="Fiction">Fiction</option>
    <option value="Dystopian">Dystopian</option>
    <option value="Fantasy">Fantasy</option>
    <option value="Science Fiction">Science Fiction</option>
    <option value="Romance">Romance</option>
  </select>
  <button class="btn btn-primary" onclick="showModal('bookModal')">+ Add Book</button>
</div>

<div class="card">
  <table>
    <thead><tr>
      <th>ISBN</th><th>Title</th><th>Author</th><th>Category</th><th>Year</th><th>Status</th><th>Actions</th>
    </tr></thead>
    <tbody id="booksTableBody"></tbody>
  </table>
  <div class="pagination">
    <button class="page-btn">&laquo; Prev</button>
    <button class="page-btn active">1</button>
    <button class="page-btn">2</button>
    <button class="page-btn">3</button>
    <button class="page-btn">Next &raquo;</button>
  </div>
</div>

<div class="modal-overlay" id="bookModal">
  <div class="modal">
    <div class="modal-header">
      <h3 id="bookModalTitle">Add New Book</h3>
      <button class="modal-close" onclick="hideModal('bookModal')">&times;</button>
    </div>
    <div class="modal-body">
      <form id="bookForm">
        <input type="hidden" id="bookId">
        <div class="form-group">
          <label for="bookIsbn">ISBN</label>
          <input type="text" id="bookIsbn" placeholder="978-0-000-00000-0" required>
        </div>
        <div class="form-group">
          <label for="bookTitle">Title</label>
          <input type="text" id="bookTitle" placeholder="Book title" required>
        </div>
        <div class="form-group">
          <label for="bookAuthor">Author</label>
          <input type="text" id="bookAuthor" placeholder="Author name" required>
        </div>
        <div class="form-group">
          <label for="bookCategory">Category</label>
          <select id="bookCategory" required>
            <option value="">Select category</option>
            <option>Fiction</option>
            <option>Dystopian</option>
            <option>Fantasy</option>
            <option>Science Fiction</option>
            <option>Romance</option>
          </select>
        </div>
        <div class="form-group">
          <label for="bookYear">Published Year</label>
          <input type="number" id="bookYear" placeholder="2024" required>
        </div>
        <div class="form-group">
          <label for="bookCopies">Number of Copies</label>
          <input type="number" id="bookCopies" placeholder="1" min="1" required>
        </div>
      </form>
    </div>
    <div class="modal-footer">
      <button class="btn btn-secondary" onclick="hideModal('bookModal')">Cancel</button>
      <button class="btn btn-primary" onclick="saveBook()">Save Book</button>
    </div>
  </div>
</div>

<script>
requireAuth();

document.getElementById('booksTableBody').innerHTML =
  '<tr><td colspan="7" style="text-align:center;padding:24px;color:#6b7280;">No records found</td></tr>';

function saveBook() {
  hideModal('bookModal');
  showNotification('Book saved successfully', 'success');
  document.getElementById('bookModalTitle').textContent = 'Add New Book';
  document.getElementById('bookForm').reset();
}
</script>

<?php require_once 'includes/footer.php'; ?>