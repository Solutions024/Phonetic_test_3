/**
 * Session Manager - Core utility for managing user authentication state,
 * handling session timeouts, and ensuring server connectivity.
 */
console.log('[SESSION_MANAGER] Script loaded');

// Configuration: Connectivity check frequency (500 seconds currently)
const SESSION_CHECK_INTERVAL = 500000;
let sessionCheckInterval = null;

/**
 * initSessionManager: The entry point function that runs on page load.
 * It determines if the user is authorized to view the current page.
 */
function initSessionManager() {
    console.log('[SESSION_MANAGER] Initializing session manager');

    // Attempt to retrieve the persistent user identity from localStorage
    const userId = localStorage.getItem('userId');

    // Check if the user is currently on a 'guest' page (login)
    const isLoginPage = window.location.pathname.includes('login.html') || window.location.pathname === '/';

    console.log('[SESSION_MANAGER] Current page:', window.location.pathname, 'Is login page:', isLoginPage, 'User ID:', userId);

    // RULE 1: If on login page but already have a session, clear it.
    // This allows a clean "re-login" if the user navigates back to /login.
    if (isLoginPage && userId) {
        console.log('[SESSION_MANAGER] User is on login page but already logged in. Clearing session for fresh start.');
        clearSession(false);
    }

    // RULE 2: If on a protected page (e.g., index.html) and not logged in, force redirect to login.
    if (!isLoginPage && !userId) {
        console.log('[SESSION_MANAGER] User not logged in. Redirecting to login page.');
        window.location.href = 'login.html';
        return;
    }

    // Start background activity if the user is authenticated and on an active app page.
    if (userId && !isLoginPage) {
        console.log('[SESSION_MANAGER] User logged in. Starting background tasks.');
        // startServerMonitoring(); // Connectivity monitoring (currently disabled in code)
    }
}

/**
 * clearSession: Removes all authentication data and optionally redirects.
 * @param {boolean} showMessage - Whether to show an alert modal before redirecting.
 */
function clearSession(showMessage = true) {
    console.log('[SESSION_MANAGER] Clearing session');

    // Record the logout event timestamp locally for audit/UI purposes
    const logoutTime = new Date().toISOString();
    localStorage.setItem('lastLogoutTime', logoutTime);
    console.log('[SESSION_MANAGER] Logout time recorded:', logoutTime);

    // Explicitly delete all sensitive session keys
    localStorage.removeItem('userId');
    localStorage.removeItem('username');
    localStorage.removeItem('userRole');
    localStorage.removeItem('sessionId');
    localStorage.removeItem('loginTime');

    // If session expired (automatic logout), inform the user via the error-handler popup.
    if (showMessage) {
        showError('INVALID_CREDENTIALS', `Session expired. You have been logged out.`, true);
        setTimeout(() => {
            window.location.href = 'login.html';
        }, 2000);
    }
}

/**
 * startServerMonitoring: Periodically pings the server to ensure the session is still valid.
 */
function startServerMonitoring() {
    console.log('[SESSION_MANAGER] Starting server monitoring');

    sessionCheckInterval = setInterval(async () => {
        try {
            // Send a lightweight GET request to a protected endpoint
            const response = await fetch('/batch-uploads', {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json'
                }
            });

            // If the server returns 401, the token/session is dead on the backend.
            if (!response.ok && response.status === 401) {
                console.log('[SESSION_MANAGER] Server returned 401 Unauthorized. Logging out.');
                stopServerMonitoring();
                clearSession(true);
            }
        } catch (error) {
            // Catch network failures (e.g., backend server went down)
            console.warn('[SESSION_MANAGER] Server connectivity check failed:', error.message);
            showError('SERVER_NOT_CONNECTED', 'Connection to server lost. You have been logged out.', true);
            stopServerMonitoring();
            clearSession(false);
            setTimeout(() => {
                window.location.href = 'login.html';
            }, 2000);
        }
    }, SESSION_CHECK_INTERVAL);
}

/**
 * stopServerMonitoring: Clears the background timer to save resources.
 */
function stopServerMonitoring() {
    if (sessionCheckInterval) {
        clearInterval(sessionCheckInterval);
        sessionCheckInterval = null;
        console.log('[SESSION_MANAGER] Stopped server monitoring');
    }
}

/**
 * getSessionInfo: Utility to package current session state into a single object.
 */
function getSessionInfo() {
    return {
        userId: localStorage.getItem('userId'),
        username: localStorage.getItem('username'),
        userRole: localStorage.getItem('userRole'),
        loginTime: localStorage.getItem('loginTime'),
        lastLogoutTime: localStorage.getItem('lastLogoutTime')
    };
}

/**
 * logSessionActivity: Internal tracer for auditing user actions within the session.
 */
function logSessionActivity(activityType, details = {}) {
    const activity = {
        type: activityType,
        timestamp: new Date().toISOString(),
        userId: localStorage.getItem('userId'),
        username: localStorage.getItem('username'),
        ...details
    };
    console.log('[SESSION_MANAGER] Activity:', activity);

    // Keep a history of activities in sessionStorage (lives until tab is closed)
    const activities = JSON.parse(sessionStorage.getItem('sessionActivities') || '[]');
    activities.push(activity);
    sessionStorage.setItem('sessionActivities', JSON.stringify(activities));
}

/**
 * Event Listener: Trace when the user leaves the page.
 */
window.addEventListener('beforeunload', () => {
    console.log('[SESSION_MANAGER] Page is being unloaded');
    logSessionActivity('PAGE_UNLOAD');
    stopServerMonitoring();
});

/**
 * Event Listener: Cross-tab logout support. 
 * If the user logs out in Tab A, Tab B will detect the storage change and redirect too.
 */
window.addEventListener('storage', (event) => {
    // If 'userId' key was just cleared (became null)
    if (event.key === 'userId' && event.newValue === null) {
        console.log('[SESSION_MANAGER] Logout detected from another tab');
        logSessionActivity('LOGOUT_OTHER_TAB');
        stopServerMonitoring();
        window.location.href = 'login.html';
    }
});

/**
 * Execution: Kick off initialization once the script is loaded.
 */
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initSessionManager);
} else {
    // DOM is already ready (e.g., script loaded late or dynamically)
    initSessionManager();
}