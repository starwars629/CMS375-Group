<?php require_once 'includes/config.php'; $pageTitle = 'Members'; require_once 'includes/header.php'; ?>

<div class="toolbar">
    <input type="text" id="searchInput" class="search-input" placeholder="Search members...">
    <select id="roleFilter">
        <option value="all">All Roles</option>
        <option value="Admin">Admin</option>
        <option value="Librarian">Librarian</option>
        <option value="Member">Member</option>
    </select>
    <button class="btn btn-primary" onclick="showModal('userModal'); document.getElementById('modalTitle').textContent = 'Add Member'; document.getElementById('userForm').reset(); document.getElementById('editUserId').value = ''; document.getElementById('passwordGroup').style.display = 'block';">&#43; Add Member</button>
</div>

<div class="card">
    <div id="usersTable"></div>
</div>

<div class="modal-overlay" id="userModal">
    <div class="modal">
        <div class="modal-header">
            <h3 id="modalTitle">Add Member</h3>
            <button class="modal-close" onclick="hideModal('userModal')">&times;</button>
        </div>
        <div class="modal-body">
            <form id="userForm">
                <input type="hidden" id="editUserId" value="">
                <div class="form-group">
                    <label for="firstName">First Name</label>
                    <input type="text" id="firstName" placeholder="Enter first name" required>
                </div>
                <div class="form-group">
                    <label for="lastName">Last Name</label>
                    <input type="text" id="lastName" placeholder="Enter last name" required>
                </div>
                <div class="form-group">
                    <label for="userEmail">Email</label>
                    <input type="email" id="userEmail" placeholder="Enter email address" required>
                </div>
                <div class="form-group">
                    <label for="userPhone">Phone</label>
                    <input type="tel" id="userPhone" placeholder="Enter phone number">
                </div>
                <div class="form-group">
                    <label for="userRole">Role</label>
                    <select id="userRole">
                        <option value="Member">Member</option>
                        <option value="Librarian">Librarian</option>
                        <option value="Admin">Admin</option>
                    </select>
                </div>
                <div class="form-group" id="passwordGroup">
                    <label for="userPassword">Password</label>
                    <input type="password" id="userPassword" placeholder="Enter password">
                </div>
            </form>
        </div>
        <div class="modal-footer">
            <button class="btn btn-secondary" onclick="hideModal('userModal')">Cancel</button>
            <button class="btn btn-primary" onclick="saveUser()">Save Member</button>
        </div>
    </div>
</div>

<script>
    requireAuth();

    renderTable('usersTable',
        [{ label: 'ID' }, { label: 'Name' }, { label: 'Email' }, { label: 'Role' }, { label: 'Status' }, { label: 'Join Date' }, { label: 'Actions' }],
        [], function () { return ''; }
    );

    function saveUser() {
        hideModal('userModal');
        showNotification('Member saved successfully', 'success');
    }
</script>

<?php require_once 'includes/footer.php'; ?>