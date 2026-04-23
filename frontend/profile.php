<?php require_once 'includes/config.php'; $pageTitle = 'My Profile'; require_once 'includes/header.php'; ?>

<div class="stats-grid" style="grid-template-columns: repeat(4, 1fr); margin-bottom:24px;">
  <div class="stat-card">
    <div class="stat-value" id="statBorrowed">--</div>
    <div class="stat-label">Currently Borrowed</div>
  </div>
  <div class="stat-card">
    <div class="stat-value" id="statOverdue" style="color:#dc2626;">--</div>
    <div class="stat-label">Overdue</div>
  </div>
  <div class="stat-card">
    <div class="stat-value" id="statReservations">--</div>
    <div class="stat-label">Pending Reservations</div>
  </div>
  <div class="stat-card">
    <div class="stat-value" id="statFine" style="color:#dc2626;">--</div>
    <div class="stat-label">Fine Balance</div>
  </div>
</div>

<div class="dashboard-grid" style="display:grid;grid-template-columns:1fr 1fr;gap:24px;">
  <div class="card">
    <div class="card-header"><h2>Profile Details</h2></div>
    <div style="padding:16px;">
      <form id="profileForm">
        <div class="form-group">
          <label for="profileName">Full Name</label>
          <input type="text" id="profileName" required>
        </div>
        <div class="form-group">
          <label for="profileEmail">Email</label>
          <input type="email" id="profileEmail" required>
        </div>
        <div class="form-group">
          <label>Role</label>
          <input type="text" id="profileRole" disabled>
        </div>
        <button type="button" class="btn btn-primary" onclick="saveProfile()">Update Profile</button>
      </form>
    </div>
  </div>

  <div class="card">
    <div class="card-header"><h2>Change Password</h2></div>
    <div style="padding:16px;">
      <form id="passwordForm">
        <div class="form-group">
          <label for="currentPw">Current Password</label>
          <input type="password" id="currentPw" required>
        </div>
        <div class="form-group">
          <label for="newPw">New Password</label>
          <input type="password" id="newPw" placeholder="Min 8 chars, letter + digit" required>
        </div>
        <div class="form-group">
          <label for="confirmPw">Confirm New Password</label>
          <input type="password" id="confirmPw" required>
        </div>
        <button type="button" class="btn btn-primary" onclick="changePassword()">Change Password</button>
      </form>
    </div>
  </div>
</div>

<div class="card" style="margin-top:24px;">
  <div class="card-header"><h2>My Loans</h2></div>
  <table>
    <thead><tr><th>Book</th><th>Checkout</th><th>Due</th><th>Status</th></tr></thead>
    <tbody id="profileLoansBody"><tr><td colspan="4" style="text-align:center;padding:24px;color:#6b7280;">Loading...</td></tr></tbody>
  </table>
</div>

<div class="card" style="margin-top:24px;">
  <div class="card-header"><h2>My Fines</h2></div>
  <table>
    <thead><tr><th>Book</th><th>Amount</th><th>Status</th><th>Issued</th></tr></thead>
    <tbody id="profileFinesBody"><tr><td colspan="4" style="text-align:center;padding:24px;color:#6b7280;">Loading...</td></tr></tbody>
  </table>
</div>

<script src="js/profile.js"></script>

<?php require_once 'includes/footer.php'; ?>
