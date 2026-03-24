<?php require_once 'includes/config.php'; $pageTitle = 'Loans'; require_once 'includes/header.php'; ?>

<div class="toolbar">
  <input type="text" id="loanSearch" class="search-input" placeholder="Search by book or member...">
  <select id="statusFilter">
    <option value="all">All</option>
    <option value="active">Active</option>
    <option value="returned">Returned</option>
    <option value="overdue">Overdue</option>
  </select>
  <button class="btn btn-primary" onclick="showModal('checkoutModal')">+ New Checkout</button>
</div>

<div class="card">
  <div id="loansTable"></div>
</div>

<div class="modal-overlay" id="checkoutModal">
  <div class="modal">
    <div class="modal-header">
      <h2>New Checkout</h2>
      <button class="modal-close" onclick="hideModal('checkoutModal')">&times;</button>
    </div>
    <div class="modal-body">
      <div class="form-group">
        <label for="memberInput">Member Name / ID</label>
        <input type="text" id="memberInput" placeholder="Enter member name or ID">
      </div>
      <div class="form-group">
        <label for="bookInput">Book Title / ISBN</label>
        <input type="text" id="bookInput" placeholder="Enter book title or ISBN">
      </div>
      <div class="form-group">
        <label for="dueDateInput">Due Date</label>
        <input type="date" id="dueDateInput">
      </div>
    </div>
    <div class="modal-footer">
      <button class="btn btn-secondary" onclick="hideModal('checkoutModal')">Cancel</button>
      <button class="btn btn-primary" onclick="saveCheckout()">Checkout</button>
    </div>
  </div>
</div>

<script>
  requireAuth();

  (function () {
    var due = new Date();
    due.setDate(due.getDate() + 14);
    var yyyy = due.getFullYear();
    var mm = String(due.getMonth() + 1).padStart(2, '0');
    var dd = String(due.getDate()).padStart(2, '0');
    document.getElementById('dueDateInput').value = yyyy + '-' + mm + '-' + dd;
  })();

  renderTable('loansTable',
    [{ label: 'Loan ID' }, { label: 'Book Title' }, { label: 'Member' }, { label: 'Checkout Date' }, { label: 'Due Date' }, { label: 'Return Date' }, { label: 'Status' }, { label: 'Actions' }],
    [], function () { return ''; }
  );

  function saveCheckout() {
    hideModal('checkoutModal');
    showNotification('Book checked out successfully');
  }
</script>

<?php require_once 'includes/footer.php'; ?>