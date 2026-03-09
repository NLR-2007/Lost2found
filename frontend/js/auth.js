document.addEventListener('DOMContentLoaded', () => {
    // If a token exists and we're on login/register/admin-login, redirect appropriately
    if (api.getToken()) {
        const user = api.getUser();
        const currentPath = window.location.pathname;

        if (currentPath.includes('login.html') || currentPath.includes('register.html')) {
            if (user && user.role === 'admin') {
                window.location.href = 'admin-dashboard.html';
            } else {
                window.location.href = 'user-dashboard.html';
            }
        } else if (currentPath.includes('admin-login.html')) {
            // Only redirect if they are actually an admin
            if (user && user.role === 'admin') {
                window.location.href = 'admin-dashboard.html';
            } else {
                // If they have a user token but try to hit admin-login, let them stay and log in as admin
                // or optionally redirect them back to user dashboard. We'll let them stay.
                console.log("User session active, but on admin login. No redirect.");
            }
        }
    }

    const loginForm = document.getElementById('login-form');
    const registerForm = document.getElementById('register-form');
    const adminLoginForm = document.getElementById('admin-login-form');
    const msgBox = document.getElementById('auth-message');

    function showMessage(msg, isError = true) {
        msgBox.textContent = msg;
        msgBox.className = `message-box ${isError ? 'error' : 'success'}`;
    }

    if (loginForm) {
        loginForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const email = document.getElementById('email').value;
            const password = document.getElementById('password').value;
            const captchaInput = document.getElementById('captcha-answer').value;

            if (!validateCaptcha(captchaInput)) {
                showMessage("Incorrect CAPTCHA answer. Try again.");
                generateCaptcha();
                document.getElementById('captcha-answer').value = '';
                return;
            }

            const response = await api.apiFetch('/login', {
                method: 'POST',
                body: JSON.stringify({ email, password })
            });

            if (response.ok) {
                localStorage.setItem('token', response.data.token);
                localStorage.setItem('user', JSON.stringify(response.data.user));
                window.location.href = 'user-dashboard.html';
            } else {
                showMessage(response.data.message || "Login failed");
                generateCaptcha();
                document.getElementById('captcha-answer').value = '';
            }
        });
    }

    if (registerForm) {
        registerForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const name = document.getElementById('name').value;
            const email = document.getElementById('email').value;
            const password = document.getElementById('password').value;
            const captchaInput = document.getElementById('captcha-answer').value;

            if (!validateCaptcha(captchaInput)) {
                showMessage("Incorrect CAPTCHA answer. Try again.");
                generateCaptcha();
                document.getElementById('captcha-answer').value = '';
                return;
            }

            const response = await api.apiFetch('/register', {
                method: 'POST',
                body: JSON.stringify({ name, email, password })
            });

            if (response.ok) {
                showMessage("Registration successful! Redirecting to login...", false);
                setTimeout(() => {
                    window.location.href = 'login.html';
                }, 1500);
            } else {
                showMessage(response.data.message || "Registration failed");
                generateCaptcha();
                document.getElementById('captcha-answer').value = '';
            }
        });
    }

    if (adminLoginForm) {
        let otpSent = false;

        adminLoginForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const email = document.getElementById('email').value;
            let password = ""; // Password won't be sent until OTP request passes initially, wait, we need password for OTP?
            // "NO DEFAULT OTP WHEN USER AFTER USER ENTER PASSWORD IF IT IS CORRECT AUTOMATICALLY THE OTP SHOULD BE SENT"
            // The logic should be: We send email+password to `/request-otp`. Wait.. /request-otp doesn't check password currently in python backend.
            // Let's modify JS to just send it, and we will update backend to verify password!
            password = document.getElementById('password').value;

            if (!otpSent) {
                // Step 1: Request OTP
                const response = await api.apiFetch('/request-otp', {
                    method: 'POST',
                    body: JSON.stringify({ email, password })
                });

                if (response.ok) {
                    otpSent = true;
                    document.getElementById('otp-group').style.display = 'block';
                    document.getElementById('email').readOnly = true;
                    // Keep password editable in case they need to correct it later or if server was picky
                    document.getElementById('admin-submit-btn').textContent = 'Verify OTP & Login';
                    showMessage("OTP Sent to Telegram Check your bot!", false);
                } else {
                    showMessage(response.data.message || "Failed to initiate login");
                }
            } else {
                // Step 2: Verify OTP
                const otp = document.getElementById('otp').value;
                const response = await api.apiFetch('/admin-login', {
                    method: 'POST',
                    body: JSON.stringify({ email, password, otp })
                });

                if (response.ok) {
                    localStorage.setItem('token', response.data.token);
                    localStorage.setItem('user', JSON.stringify(response.data.user));
                    window.location.href = 'admin-dashboard.html';
                } else {
                    // If login fails (wrong OTP), don't reset otpSent so they can try again
                    showMessage(response.data.message || "Login failed");
                }
            }
        });
    }
});
