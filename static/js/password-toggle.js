const eyeIcon = `
    <svg viewBox="0 0 24 24" fill="none" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
        <path d="M2 12s3.5-7 10-7 10 7 10 7-3.5 7-10 7-10-7-10-7"></path>
        <circle cx="12" cy="12" r="3"></circle>
    </svg>
`;

const eyeOffIcon = `
    <svg viewBox="0 0 24 24" fill="none" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
        <path d="M3 3l18 18"></path>
        <path d="M10.6 10.6A2 2 0 0 0 13.4 13.4"></path>
        <path d="M9.9 4.2A10.6 10.6 0 0 1 12 4c6.5 0 10 8 10 8a18.5 18.5 0 0 1-3 4.4"></path>
        <path d="M6.6 6.6C3.6 8.6 2 12 2 12s3.5 8 10 8a10.8 10.8 0 0 0 4.2-.8"></path>
    </svg>
`;

function updatePasswordToggle(button, input) {
    const isVisible = input.type === 'text';
    button.innerHTML = isVisible ? eyeOffIcon : eyeIcon;
    button.setAttribute('aria-label', isVisible ? 'Hide password' : 'Show password');
    button.setAttribute('title', isVisible ? 'Hide password' : 'Show password');
}

function setupPasswordToggle(button) {
    const targetId = button.dataset.passwordToggle;
    const input = targetId
        ? document.getElementById(targetId)
        : button.closest('.password-field')?.querySelector('input');

    if (!input || input.dataset.passwordToggleReady) return;

    input.dataset.passwordToggleReady = 'true';
    updatePasswordToggle(button, input);
}

document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('[data-password-toggle]').forEach(setupPasswordToggle);
});

document.addEventListener('click', (event) => {
    const button = event.target.closest('[data-password-toggle]');
    if (!button) return;

    const input = document.getElementById(button.dataset.passwordToggle);
    if (!input) return;

    input.type = input.type === 'password' ? 'text' : 'password';
    updatePasswordToggle(button, input);
    input.focus();
});
