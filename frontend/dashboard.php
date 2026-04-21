<?php require_once 'includes/config.php'; $pageTitle = 'Dashboard'; require_once 'includes/header.php'; ?>

<style>
  .stats-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 24px;
    margin-bottom: 24px;
  }
  .stat-card {
    background: #fff;
    border-radius: 8px;
    padding: 20px;
    display: flex;
    align-items: center;
    gap: 16px;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  }
  .stat-icon {
    width: 48px;
    height: 48px;
    border-radius: 8px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 24px;
  }
  .stat-value {
    font-size: 24px;
    font-weight: 700;
    color: #1f2937;
  }
  .stat-label {
    font-size: 14px;
    color: #6b7280;
  }
  .dashboard-grid {
    display: grid;
    grid-template-columns: 2fr 1fr;
    gap: 24px;
  }
  @media (max-width: 992px) {
    .stats-grid {
      grid-template-columns: repeat(2, 1fr);
    }
  }
  @media (max-width: 768px) {
    .dashboard-grid {
      grid-template-columns: 1fr;
    }
  }
  @media (max-width: 576px) {
    .stats-grid {
      grid-template-columns: 1fr;
    }
  }
</style>

<div class="stats-grid">
  <div class="stat-card">
    <div class="stat-value" id="totalBooks">--</div>
    <div class="stat-label">Total Books</div>
  </div>
  <div class="stat-card">
    <div class="stat-value" id="activeLoans">--</div>
    <div class="stat-label">Active Loans</div>
  </div>
  <div class="stat-card">
    <div class="stat-value" id="pendingReservations">--</div>
    <div class="stat-label">Pending Reservations</div>
  </div>
  <div class="stat-card">
    <div class="stat-value" id="outstandingFines">--</div>
    <div class="stat-label">Outstanding Fines</div>
  </div>
</div>

<div id="adminStatsGrid" class="stats-grid" data-role="admin" style="display:none;">
  <div class="stat-card">
    <div class="stat-value" id="statTotalUsers">--</div>
    <div class="stat-label">Total Users</div>
  </div>
  <div class="stat-card">
    <div class="stat-value" id="statStudents">--</div>
    <div class="stat-label">Students</div>
  </div>
  <div class="stat-card">
    <div class="stat-value" id="statFaculty">--</div>
    <div class="stat-label">Faculty</div>
  </div>
  <div class="stat-card">
    <div class="stat-value" id="statStaff">--</div>
    <div class="stat-label">Staff (Librarian + Admin)</div>
  </div>
</div>

<div class="dashboard-grid">
  <div class="card">
    <div class="card-header">
      <h2>Recent Activity</h2>
    </div>
    <table>
      <thead>
        <tr>
          <th>Date</th>
          <th>Action</th>
          <th>Book</th>
          <th>User</th>
        </tr>
      </thead>
      <tbody id="recentActivityBody">
        <tr>
          <td colspan="4" style="text-align: center; padding: 24px; color: #6b7280;">Loading...</td>
        </tr>
      </tbody>
    </table>
  </div>

  <div class="card">
    <div class="card-header">
      <h2>Quick Actions</h2>
    </div>
    <div style="display: flex; flex-direction: column; gap: 12px;">
      <a href="books.php" class="btn btn-primary" data-role="staff">Add New Book</a>
      <a href="users.php" class="btn btn-primary" data-role="staff">Register Member</a>
      <a href="loans.php" class="btn btn-primary">Process Checkout</a>
      <a href="loans.php" class="btn btn-primary">Process Return</a>
      <a href="profile.php" class="btn btn-secondary">My Profile</a>
    </div>
  </div>
</div>

<script src="js/dashboard.js"></script>

<?php require_once 'includes/footer.php'; ?>
