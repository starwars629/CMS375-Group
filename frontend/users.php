<?php require_once 'includes/config.php'; $pageTitle = 'Members'; require_once 'includes/header.php'; ?>

<div class="toolbar">
    <input type="text" id="searchInput" class="search-input" placeholder="Search by name or email...">
    <select id="roleFilter">
        <option value="all">All Roles</option>
        <option value="student">Student</option>
        <option value="faculty">Faculty</option>
        <option value="librarian">Librarian</option>
        <option value="admin">Admin</option>
    </select>
    <button class="btn btn-primary" onclick="showModal('userModal'); document.getElementById('userForm').reset();">&#43; Add Member</button>
</div>

<div class="card">
    <table>
        <thead><tr>
            <th>ID</th><th>Name</th><th>Email</th><th>Role</th><th>Active Loans</th><th>Fine Balance</th><th>Joined</th><th>Actions</th>
        </tr></thead>
        <tbody id="usersTableBody"></tbody>
    </table>
</div>

<div class="modal-overlay" id="userModal">
    <div class="modal">
        <div class="modal-header">
            <h3>Add Member</h3>
            <button class="modal-close" onclick="hideModal('userModal')">&times;</button>
        </div>
        <div class="modal-body">
            <p style="background:#fef3c7;color:#92400e;padding:10px;border-radius:6px;font-size:13px;">
                New members are created with role <strong>student</strong>. Use the Role action after creation to change it (admin only).
            </p>
            <form id="userForm">
                <div class="form-group">
                    <label for="firstName">First Name</label>
                    <input type="text" id="firstName" placeholder="First name" required>
                </div>
                <div class="form-group">
                    <label for="lastName">Last Name</label>
                    <input type="text" id="lastName" placeholder="Last name" required>
                </div>
                <div class="form-group">
                    <label for="userEmail">Email</label>
                    <input type="email" id="userEmail" placeholder="email@example.com" required>
                </div>
                <div class="form-group">
                    <label for="userPassword">Password</label>
                    <input type="password" id="userPassword" placeholder="Min 8 chars, upper+lower+digit" required>
                </div>
            </form>
        </div>
        <div class="modal-footer">
            <button class="btn btn-secondary" onclick="hideModal('userModal')">Cancel</button>
            <button class="btn btn-primary" onclick="saveUser()">Create Member</button>
        </div>
    </div>
</div>

<div class="modal-overlay" id="activityModal">
    <div class="modal" style="max-width:800px;">
        <div class="modal-header">
            <h3>User Activity</h3>
            <button class="modal-close" onclick="hideModal('activityModal')">&times;</button>
        </div>
        <div class="modal-body" id="activityBody"></div>
        <div class="modal-footer">
            <button class="btn btn-secondary" onclick="hideModal('activityModal')">Close</button>
        </div>
    </div>
</div>

<div class="modal-overlay" id="roleChangeModal">
    <div class="modal">
        <div class="modal-header">
            <h3>Change Role</h3>
            <button class="modal-close" onclick="hideModal('roleChangeModal')">&times;</button>
        </div>
        <div class="modal-body">
            <input type="hidden" id="roleChangeUserId">
            <p>Change role for <strong id="roleChangeName"></strong></p>
            <div class="form-group">
                <label for="roleChangeSelect">New Role</label>
                <select id="roleChangeSelect">
                    <option value="student">Student</option>
                    <option value="faculty">Faculty</option>
                    <option value="librarian">Librarian</option>
                    <option value="admin">Admin</option>
                </select>
            </div>
        </div>
        <div class="modal-footer">
            <button class="btn btn-secondary" onclick="hideModal('roleChangeModal')">Cancel</button>
            <button class="btn btn-primary" onclick="saveRoleChange()">Update Role</button>
        </div>
    </div>
</div>

<script src="js/users.js"></script>

<?php require_once 'includes/footer.php'; ?>
