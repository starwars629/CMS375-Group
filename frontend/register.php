<?php
require_once 'includes/config.php';
$pageTitle = 'Register';
require_once 'includes/header.php';
?>

<div class="login-page">
    <div class="login-card">
        <div class="login-header">
            <h1>Create Account</h1>
        </div>
        <form id="registerForm" onsubmit="handleRegister(event)">
            <div class="form-group">
                <label for="regName">Full Name</label>
                <input type="text" id="regName" placeholder="Enter your name" required>
            </div>
            <div class="form-group">
                <label for="regEmail">Email Address</label>
                <input type="email" id="regEmail" placeholder="you@example.com" required>
            </div>
            <div class="form-group">
                <label for="regPassword">Password</label>
                <input type="password" id="regPassword" placeholder="Min 8 chars, letter + digit" required>
            </div>
            <div class="form-group">
                <label for="regPasswordConfirm">Confirm Password</label>
                <input type="password" id="regPasswordConfirm" placeholder="Re-enter password" required>
            </div>
            <div id="registerError" class="login-error hidden"></div>
            <button type="submit" class="btn btn-primary btn-block">Create Account</button>
        </form>
        <div class="login-footer">
            <p style="margin: 8px 0;">Already have an account? <a href="index.php">Sign In</a></p>
        </div>
    </div>
</div>

<script src="js/register.js"></script>

<?php require_once 'includes/footer.php'; ?>
