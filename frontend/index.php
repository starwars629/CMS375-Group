<?php
require_once 'includes/config.php';
$pageTitle = 'Login';
require_once 'includes/header.php';
?>

<div class="login-page">
    <div class="login-card">
        <div class="login-header">
            <h1>Library Management System</h1>
        </div>
        <form id="loginForm" onsubmit="handleLogin(event)">
            <div class="form-group">
                <label for="email">Email Address</label>
                <input type="email" id="email" placeholder="Enter your email" required>
            </div>
            <div class="form-group">
                <label for="password">Password</label>
                <input type="password" id="password" placeholder="Enter your password" required>
            </div>
            <div id="loginError" class="login-error hidden"></div>
            <button type="submit" class="btn btn-primary btn-block">Sign In</button>
        </form>
        <div class="login-footer">
            <p style="margin: 8px 0;">Don't have an account? <a href="register.php">Create one</a></p>
        </div>
    </div>
</div>

<script>
    async function handleLogin(e) {
        e.preventDefault();

        var email = document.getElementById('email').value;
        var password = document.getElementById('password').value;
        var errorDiv = document.getElementById('loginError');

        errorDiv.classList.add('hidden');
        errorDiv.textContent = '';

        var result = await apiRequest('/auth/login', 'POST', { email: email, password: password });

        if (result.ok) {
            setToken(result.data.token);
            if (result.data.user) {
                setUser(result.data.user);
            }
            window.location.href = 'dashboard.php';
        } else {
            errorDiv.textContent = result.error || 'Login failed. Please check your credentials.';
            errorDiv.classList.remove('hidden');
        }
    }

    if (isLoggedIn()) {
        window.location.href = 'dashboard.php';
    }
</script>

<?php require_once 'includes/footer.php'; ?>
