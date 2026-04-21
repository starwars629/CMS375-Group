<?php require_once 'includes/config.php'; $pageTitle = 'Reservations'; require_once 'includes/header.php'; ?>

<div class="toolbar">
  <input type="text" id="reservationSearch" class="toolbar-search" placeholder="Search reservations...">
  <select id="statusFilter" class="toolbar-filter">
    <option value="">All</option>
    <option value="pending">Pending</option>
    <option value="fulfilled">Fulfilled</option>
    <option value="cancelled">Cancelled</option>
  </select>
  <button class="btn btn-secondary" data-role="staff" onclick="showModal('queueLookupModal')">View Book Queue</button>
  <button class="btn btn-primary" onclick="showModal('reservationModal')">+ New Reservation</button>
</div>

<div class="card">
  <p style="padding:12px;color:#6b7280;font-size:13px;margin:0;">
    Shows reservations for the currently logged-in user. Staff can inspect per-book queues using "View Book Queue".
  </p>
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
      <p style="background:#fef3c7;color:#92400e;padding:10px;border-radius:6px;font-size:13px;">
        Reservations are recorded for the currently logged-in user. Book must be unavailable (no free copies).
      </p>
      <form id="reservationForm">
        <div class="form-group">
          <label for="resBookInput">Book ID or Title</label>
          <input type="text" id="resBookInput" placeholder="Enter book ID or search term" required>
        </div>
      </form>
    </div>
    <div class="modal-footer">
      <button class="btn btn-secondary" onclick="hideModal('reservationModal')">Cancel</button>
      <button class="btn btn-primary" onclick="saveReservation()">Save Reservation</button>
    </div>
  </div>
</div>

<div class="modal-overlay" id="queueLookupModal">
  <div class="modal">
    <div class="modal-header">
      <h3>View Reservation Queue</h3>
      <button class="modal-close" onclick="hideModal('queueLookupModal')">&times;</button>
    </div>
    <div class="modal-body">
      <div class="form-group">
        <label for="queueBookInput">Book ID or Title</label>
        <input type="text" id="queueBookInput" placeholder="Enter book ID or search term">
      </div>
    </div>
    <div class="modal-footer">
      <button class="btn btn-secondary" onclick="hideModal('queueLookupModal')">Cancel</button>
      <button class="btn btn-primary" onclick="hideModal('queueLookupModal'); viewBookQueue();">View Queue</button>
    </div>
  </div>
</div>

<div class="modal-overlay" id="queueModal">
  <div class="modal" style="max-width:700px;">
    <div class="modal-header">
      <h3>Reservation Queue</h3>
      <button class="modal-close" onclick="hideModal('queueModal')">&times;</button>
    </div>
    <div class="modal-body" id="queueBody"></div>
    <div class="modal-footer">
      <button class="btn btn-secondary" onclick="hideModal('queueModal')">Close</button>
    </div>
  </div>
</div>

<script src="js/reservations.js"></script>

<?php require_once 'includes/footer.php'; ?>
