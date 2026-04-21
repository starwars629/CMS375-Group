<?php require_once 'includes/config.php'; $pageTitle = 'Fines'; require_once 'includes/header.php'; ?>

<div class="stats-grid" style="grid-template-columns: repeat(3, 1fr);">
  <div class="stat-card">
    <div class="stat-value" id="totalFinesAmount">$0.00</div>
    <div class="stat-label">Total Fines</div>
  </div>
  <div class="stat-card">
    <div class="stat-value" id="paidFinesAmount" style="color: #059669;">$0.00</div>
    <div class="stat-label">Paid</div>
  </div>
  <div class="stat-card">
    <div class="stat-value" id="unpaidFinesAmount" style="color: #dc2626;">$0.00</div>
    <div class="stat-label">Unpaid</div>
  </div>
</div>

<div class="toolbar">
  <input type="text" id="fineSearch" class="toolbar-search" placeholder="Search fines...">
  <select id="statusFilter" class="toolbar-filter">
    <option value="">All</option>
    <option value="paid">Paid</option>
    <option value="unpaid">Unpaid</option>
  </select>
  <button class="btn btn-secondary" data-role="staff" onclick="showUsersWithFines()">Users With Fines</button>
</div>

<div class="modal-overlay" id="usersWithFinesModal">
  <div class="modal" style="max-width:700px;">
    <div class="modal-header">
      <h3>Users With Outstanding Fines</h3>
      <button class="modal-close" onclick="hideModal('usersWithFinesModal')">&times;</button>
    </div>
    <div class="modal-body" id="usersWithFinesBody"></div>
    <div class="modal-footer">
      <button class="btn btn-secondary" onclick="hideModal('usersWithFinesModal')">Close</button>
    </div>
  </div>
</div>

<div class="card">
  <table>
    <thead><tr>
      <th>Fine ID</th><th>Member</th><th>Book</th><th>Amount</th><th>Reason</th><th>Status</th><th>Date Issued</th><th>Actions</th>
    </tr></thead>
    <tbody id="finesTableBody"></tbody>
  </table>
</div>

<script src="js/fines.js"></script>

<?php require_once 'includes/footer.php'; ?>
