<?php require_once 'includes/config.php'; $pageTitle = 'Loans'; require_once 'includes/header.php'; ?>

<div class="toolbar">
  <input type="text" id="loanSearch" class="toolbar-search" placeholder="Search by book or member...">
  <select id="statusFilter" class="toolbar-filter">
    <option value="all">All Active</option>
    <option value="active">Active</option>
    <option value="overdue">Overdue</option>
    <option value="returned">Returned</option>
  </select>
  <button class="btn btn-primary" onclick="showModal('checkoutModal')">+ New Checkout</button>
</div>

<div class="card">
  <table>
    <thead><tr>
      <th>Loan ID</th><th>Book</th><th>Member</th><th>Checkout Date</th><th>Due Date</th><th>Return Date</th><th>Status</th><th>Actions</th>
    </tr></thead>
    <tbody id="loansTableBody"></tbody>
  </table>
</div>

<div class="modal-overlay" id="checkoutModal">
  <div class="modal">
    <div class="modal-header">
      <h2>New Checkout</h2>
      <button class="modal-close" onclick="hideModal('checkoutModal')">&times;</button>
    </div>
    <div class="modal-body">
      <p id="checkoutNotice" style="background:#fef3c7;color:#92400e;padding:10px;border-radius:6px;font-size:13px;"></p>
      <div class="form-group">
        <label for="memberInput">Member (informational only)</label>
        <input type="text" id="memberInput" placeholder="Member name (not submitted)" readonly disabled>
      </div>
      <div class="form-group">
        <label for="bookInput">Book ID, Title, or ISBN</label>
        <input type="text" id="bookInput" placeholder="Enter book ID or search term">
      </div>
    </div>
    <div class="modal-footer">
      <button class="btn btn-secondary" onclick="hideModal('checkoutModal')">Cancel</button>
      <button class="btn btn-primary" onclick="saveCheckout()">Checkout</button>
    </div>
  </div>
</div>

<script src="js/loans.js"></script>

<?php require_once 'includes/footer.php'; ?>
