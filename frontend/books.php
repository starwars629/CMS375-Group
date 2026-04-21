<?php require_once 'includes/config.php'; $pageTitle = 'Books'; require_once 'includes/header.php'; ?>

<div class="toolbar">
  <input type="text" id="bookSearch" class="toolbar-search" placeholder="Search by title, author, or ISBN...">
  <select id="categoryFilter" class="toolbar-filter">
    <option value="">All Genres</option>
    <option value="Fiction">Fiction</option>
    <option value="Dystopian">Dystopian</option>
    <option value="Fantasy">Fantasy</option>
    <option value="Science Fiction">Science Fiction</option>
    <option value="Romance">Romance</option>
    <option value="Technology">Technology</option>
    <option value="Non-Fiction">Non-Fiction</option>
    <option value="Biography">Biography</option>
    <option value="History">History</option>
  </select>
  <button class="btn btn-primary" data-role="staff" onclick="showModal('bookModal')">+ Add Book</button>
</div>

<div class="card">
  <table>
    <thead><tr>
      <th>ISBN</th><th>Title</th><th>Author</th><th>Genre</th><th>Location</th><th>Status</th><th>Actions</th>
    </tr></thead>
    <tbody id="booksTableBody"></tbody>
  </table>
  <div class="pagination" style="display:flex;justify-content:space-between;align-items:center;padding:12px;">
    <button class="page-btn" id="prevPage">&laquo; Prev</button>
    <span id="pageInfo" style="color:#6b7280;"></span>
    <button class="page-btn" id="nextPage">Next &raquo;</button>
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
        <div class="form-group">
          <label for="bookIsbn">ISBN</label>
          <input type="text" id="bookIsbn" placeholder="9780000000000" required>
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
          <label for="bookCategory">Genre</label>
          <select id="bookCategory" required>
            <option value="">Select genre</option>
            <option>Fiction</option>
            <option>Dystopian</option>
            <option>Fantasy</option>
            <option>Science Fiction</option>
            <option>Romance</option>
            <option>Technology</option>
            <option>Non-Fiction</option>
            <option>Biography</option>
            <option>History</option>
          </select>
        </div>
        <div class="form-group">
          <label for="bookYear">Published Year</label>
          <input type="number" id="bookYear" placeholder="2024" min="1000" max="2100" required>
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

<div class="modal-overlay" id="bookDetailModal">
  <div class="modal">
    <div class="modal-header">
      <h3>Book Details</h3>
      <button class="modal-close" onclick="hideModal('bookDetailModal')">&times;</button>
    </div>
    <div class="modal-body" id="bookDetailBody"></div>
    <div class="modal-footer">
      <button class="btn btn-secondary" onclick="hideModal('bookDetailModal')">Close</button>
    </div>
  </div>
</div>

<script src="js/books.js"></script>

<?php require_once 'includes/footer.php'; ?>
