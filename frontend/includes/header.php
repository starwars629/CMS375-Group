<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title><?php echo $pageTitle . ' - ' . SITE_NAME; ?></title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="css/style.css">
</head>
<body>
<?php if (basename($_SERVER['PHP_SELF']) !== 'index.php'): ?>
    <button class="hamburger" onclick="toggleSidebar()" id="hamburger">&#9776;</button>
    <div class="sidebar-overlay" id="sidebarOverlay" onclick="toggleSidebar()"></div>
    <nav class="sidebar">
        <div class="sidebar-logo">
            <h2>Library Management</h2>
        </div>
        <ul class="sidebar-nav">
            <li class="<?php echo basename($_SERVER['PHP_SELF']) === 'dashboard.php' ? 'active' : ''; ?>">
                <a href="dashboard.php">Dashboard</a>
            </li>
            <li class="<?php echo basename($_SERVER['PHP_SELF']) === 'books.php' ? 'active' : ''; ?>">
                <a href="books.php">Books</a>
            </li>
            <li class="<?php echo basename($_SERVER['PHP_SELF']) === 'users.php' ? 'active' : ''; ?>">
                <a href="users.php">Members</a>
            </li>
            <li class="<?php echo basename($_SERVER['PHP_SELF']) === 'loans.php' ? 'active' : ''; ?>">
                <a href="loans.php">Loans</a>
            </li>
            <li class="<?php echo basename($_SERVER['PHP_SELF']) === 'reservations.php' ? 'active' : ''; ?>">
                <a href="reservations.php">Reservations</a>
            </li>
            <li class="<?php echo basename($_SERVER['PHP_SELF']) === 'fines.php' ? 'active' : ''; ?>">
                <a href="fines.php">Fines</a>
            </li>
        </ul>
        <hr>
        <a href="#" onclick="logout()">Logout</a>
    </nav>
    <div class="main-content">
        <div class="top-bar">
            <h1><?php echo $pageTitle; ?></h1>
        </div>
<?php endif; ?>