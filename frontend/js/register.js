function validatePassword(pw) {
    if (pw.length < 8) return 'Password must be at least 8 characters';
    if (!/[A-Z]/.test(pw)) return 'Password must contain an uppercase letter';
    if (!/[a-z]/.test(pw)) return 'Password must contain a lowercase letter';
    if (!/[0-9]/.test(pw)) return 'Password must contain a digit';
    return null;
}

async function handleRegister(e) {
    e.preventDefault();

    const name = document.getElementById('regName').value.trim();
    const email = document.getElementById('regEmail').value.trim();
    const password = document.getElementById('regPassword').value;
    const confirm = document.getElementById('regPasswordConfirm').value;
    const errorDiv = document.getElementById('registerError');

    errorDiv.classList.add('hidden');
    errorDiv.textContent = '';

    if (password !== confirm) {
        errorDiv.textContent = 'Passwords do not match';
        errorDiv.classList.remove('hidden');
        return;
    }

    const pwError = validatePassword(password);
    if (pwError) {
        errorDiv.textContent = pwError;
        errorDiv.classList.remove('hidden');
        return;
    }

    const reg = await apiRequest('/auth/register', 'POST', { name: name, email: email, password: password });
    if (!reg.ok) {
        errorDiv.textContent = reg.error || 'Registration failed';
        errorDiv.classList.remove('hidden');
        return;
    }

    const login = await apiRequest('/auth/login', 'POST', { email: email, password: password });
    if (login.ok) {
        setToken(login.data.token);
        if (login.data.user) setUser(login.data.user);
        window.location.href = 'dashboard.php';
    } else {
        window.location.href = 'index.php';
    }
}
