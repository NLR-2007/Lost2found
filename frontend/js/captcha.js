let captchaAnswer = 0;

function generateCaptcha() {
    const num1 = Math.floor(Math.random() * 9) + 1;
    const num2 = Math.floor(Math.random() * 9) + 1;
    captchaAnswer = num1 + num2;

    const captchaElement = document.getElementById('captcha-question');
    if (captchaElement) {
        captchaElement.textContent = `${num1} + ${num2} = ?`;
    }
}

function validateCaptcha(inputVal) {
    return parseInt(inputVal) === captchaAnswer;
}

// Automatically generate on page load via DOMContentLoaded
document.addEventListener('DOMContentLoaded', () => {
    generateCaptcha();

    const refreshBtn = document.getElementById('refresh-captcha');
    if (refreshBtn) {
        refreshBtn.addEventListener('click', (e) => {
            e.preventDefault();
            generateCaptcha();
            document.getElementById('captcha-answer').value = '';
        });
    }
});
