<?php require_once 'includes/config.php'; $pageTitle = 'Reservations'; require_once 'includes/header.php'; ?>

<div class="toolbar">
  <input type="text" id="reservationSearch" class="toolbar-search" placeholder="Search reservations...">
  <select id="statusFilter" class="toolbar-filter">
    <option value="">All</option>
    <option value="Pending">Pending</option>
    <option value="Fulfilled">Fulfilled</option>
    <option value="Cancelled">Cancelled</option>
  </select>
  <button class="btn btn-primary" onclick="showModal('reservationModal')">+ New Reservation</button>
</div>

<div class="card">
  <table>
    <thead><tr>
      <th>ID</th><th>Book Title</th><th>Member</th><th>Request Date</th><th>Status</th><th>Actions</th>
    </tr></thead>
    <tbody id="reservationsTableBody"></tbody>
  </table>
</div>

<div class="modal-overlay" id="reservationModal">
  <div class="modal">
    <div class="modal-header">
      <h3>New Reservation</h3>
      <button class="modal-close" onclick="hideModal('reservationModal')">&times;</button>
    </div>
    <div class="modal-body">
      <form id="reservationForm">
        <div class="form-group">
          <label for="resMemberName">Member Name</label>
          <input type="text" id="resMemberName" placeholder="Enter member name" required>
        </div>
        <div class="form-group">
          <label for="resBookTitle">Book Title</label>
          <input type="text" id="resBookTitle" placeholder="Enter book title" required>
        </div>
      </form>
    </div>
    <div class="modal-footer">
      <button class="btn btn-secondary" onclick="hideModal('reservationModal')">Cancel</button>
      <button class="btn btn-primary" onclick="saveReservation()">Save Reservation</button>
    </div>
  </div>
</div>

<script>
requireAuth();

document.getElementById('reservationsTableBody').innerHTML =
  '<tr><td colspan="6" style="text-align:center;padding:24px;color:#6b7280;">No records found</td></tr>';

function saveReservation() {
  hideModal('reservationModal');
  showNotification('Reservation created successfully', 'success');
  document.getElementById('reservationForm').reset();
}
</script>

<?php require_once 'includes/footer.php'; ?>