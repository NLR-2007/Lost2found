document.addEventListener('DOMContentLoaded', () => {
    if (!window.api.requireAuth()) return;

    const form = document.getElementById('report-lost-form');
    const msgBox = document.getElementById('form-message');

    function showMessage(msg, isError = true) {
        msgBox.textContent = msg;
        msgBox.className = `message-box ${isError ? 'error' : 'success'}`;
    }

    if (form) {
        form.addEventListener('submit', async (e) => {
            e.preventDefault();

            const mobile = document.getElementById('mobile').value;
            if (mobile.length !== 10 || isNaN(mobile)) {
                showMessage('Mobile number must be exactly 10 digits.');
                return;
            }

            const formData = new FormData(form);
            const submitBtn = form.querySelector('button[type="submit"]');
            submitBtn.disabled = true;
            submitBtn.textContent = 'Submitting...';

            const response = await window.api.apiFetch('/lost', {
                method: 'POST',
                body: formData // Let the browser set Content-Type to multipart/form-data
            });

            if (response.ok) {
                showMessage('Lost item reported successfully!', false);
                form.reset();
            } else {
                showMessage(response.data.message || 'Failed to report item.');
            }

            submitBtn.disabled = false;
            submitBtn.textContent = 'Submit Report';

            // Auto hide success after 3 seconds
            if (response.ok) {
                setTimeout(() => {
                    msgBox.style.display = 'none';
                    window.location.href = 'user-dashboard.html';
                }, 2000);
            }
        });
    }
});
