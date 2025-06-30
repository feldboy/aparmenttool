async function apiCall(url, options = {}) {
    // ...existing code...
    const response = await fetch(url, options);
    if (response.status === 401) {
        console.error('API Error: Unauthorized (401). Please check your authentication.');
        // Optionally, trigger a logout or redirect to login page here
        // window.location.href = '/login';
        throw new Error('Unauthorized');
    }
    if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
    }
    return response.json();
}

async function loadFacebookStatus() {
    try {
        // ...existing code...
        await apiCall('/api/facebook/status');
        // ...existing code...
    } catch (error) {
        if (error.message === 'Unauthorized') {
            alert('Your session has expired. Please log in again.');
            // Optionally, redirect to login
            // window.location.href = '/login';
        } else {
            console.error('API Error:', error);
        }
    }
}