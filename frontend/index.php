<?php
require_once 'includes/config.php';
$pageTitle = 'Login';
require_once 'includes/header.php';
?>

<div class="login-page">
    <div class="login-card">
        <div class="login-header">
            <h1>LibraryMS</h1>
            <p>Library Management System</p>
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
            <a href="#" onclick="demoLogin(event)">Demo Login (Skip Authentication)</a>
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

        if (result.success) {
            setToken(result.data.token);
            window.location.href = 'dashboard.php';
        } else {
            errorDiv.textContent = result.error || 'Login failed. Please check your credentials.';
            errorDiv.classList.remove('hidden');
        }
    }

    function demoLogin(e) {
        e.preventDefault();
        setToken('demo-token-123');
        window.location.href = 'dashboard.php';
    }

    if (isLoggedIn()) {
        window.location.href = 'dashboard.php';
    }
</script>

<?php require_once 'includes/footer.php'; ?>