/**
 * Error Handler - A global system for managing and displaying 
 * user-facing error and success notifications via modal popups.
 */

// A dictionary of user-friendly messages mapped to internal error codes
const errorMessages = {
    'SERVER_NOT_CONNECTED': 'Server connection failed. Please ensure the backend is running.',
    'INVALID_CREDENTIALS': 'Invalid username or password',
    'VALIDATION_FAILED': 'Please fill in all required fields',
    'CREATE_FAILED': 'Failed to create user',
    'UPDATE_FAILED': 'Failed to update user',
    'DELETE_FAILED': 'Failed to delete user',
    'ACCOUNT_DEACTIVATED': 'Your account has been deactivated. Please contact administrator.',
    'FILE_UPLOAD_FAILED': 'File upload failed',
    'NETWORK_ERROR': 'Network error occurred',
    'UNKNOWN_ERROR': 'An unexpected error occurred'
};

/**
 * createErrorPopupElement: Programmatically injects the HTML for the error popup into the DOM.
 * This avoids needing to manually include the popup boilerplate on every HTML page.
 */
function createErrorPopupElement() {
    // Prevent duplicate creation
    if (document.getElementById('error-popup')) {
        return;
    }

    const popup = document.createElement('div');
    popup.id = 'error-popup';
    popup.className = 'error-popup';
    // The popup structure: A background overlay with a centralized message card
    popup.innerHTML = `
        <div class="error-container">
            <div class="error-header">
                <i class="fa-solid fa-circle-exclamation"></i>
                <h3>Error</h3>
                <button class="error-close" onclick="closeError()">&times;</button>
            </div>
            <div class="error-body">
                <p id="error-message"></p>
            </div>
            <div class="error-footer">
                <button class="error-btn-close" onclick="closeError()">Close</button>
            </div>
        </div>
    `;
    document.body.appendChild(popup);
    console.log('[ERROR-HANDLER] Popup element created');
}

/**
 * showError: The primary high-level function to trigger a notification.
 * @param {string} errorKey - The code used to fetch a message from errorMessages.
 * @param {string} customMessage - An optional string to override the default message.
 * @param {boolean} isSuccess - If true, styles the popup as a success (green) instead of error (red).
 */
function showError(errorKey, customMessage, isSuccess = false) {
    // Ensure the popup element exists before trying to show it
    let popup = document.getElementById('error-popup');
    if (!popup) {
        createErrorPopupElement();
        popup = document.getElementById('error-popup');
    }

    if (!popup) {
        console.error('[ERROR-HANDLER] Failed to create popup element');
        return;
    }

    // Resolve which message string to display
    const messageEl = document.getElementById('error-message');
    const message = customMessage || errorMessages[errorKey] || errorMessages['UNKNOWN_ERROR'];

    if (messageEl) {
        messageEl.textContent = message;
    }

    // Capture header elements to update their icon and text based on status
    const headerTitle = popup.querySelector('.error-header h3');
    const headerIcon = popup.querySelector('.error-header i');

    if (isSuccess) {
        // Apply success theme (defined in CSS via .success class)
        popup.classList.add('success');
        if (headerTitle) headerTitle.textContent = 'Success';
        if (headerIcon) headerIcon.className = 'fa-solid fa-circle-check';
    } else {
        // Default to error theme (red/warning)
        popup.classList.remove('success');
        if (headerTitle) headerTitle.textContent = 'Error';
        if (headerIcon) headerIcon.className = 'fa-solid fa-circle-exclamation';
    }

    // Add the 'show' class to trigger CSS transitions and make the popup visible
    popup.classList.add('show');
}

/**
 * closeError: Hides the popup by removing the visibility class.
 */
function closeError() {
    const popup = document.getElementById('error-popup');
    if (popup) {
        popup.classList.remove('show');
    }
}

/**
 * initErrorHandler: Runs on page load to ensure the infrastructure is ready.
 */
function initErrorHandler() {
    if (!document.getElementById('error-popup')) {
        createErrorPopupElement();
    }
}

/**
 * Lifecycle execution: Detects when the DOM is ready to initialize the system.
 */
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initErrorHandler);
} else {
    // DOM already loaded (e.g., script included after body)
    initErrorHandler();
}

// NOTE: This area can be used to catch global window.onerror signals in the future.