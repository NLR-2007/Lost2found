const API_BASE_URL = 'http://localhost:5000/api';
const UPLOAD_URL = 'http://localhost:5000/uploads';

const api = {
    getToken: () => {
        return localStorage.getItem('token');
    },

    getUser: () => {
        const userStr = localStorage.getItem('user');
        return userStr ? JSON.parse(userStr) : null;
    },

    authHeaders: () => {
        const token = api.getToken();
        return {
            'Authorization': `Bearer ${token}`
        };
    },

    apiFetch: async (endpoint, options = {}) => {
        const url = `${API_BASE_URL}${endpoint}`;

        const headers = { ...options.headers };
        const token = api.getToken();
        if (token) {
            headers['Authorization'] = `Bearer ${token}`;
        }

        if (options.body && !(options.body instanceof FormData) && !headers['Content-Type']) {
            headers['Content-Type'] = 'application/json';
        }

        const config = {
            ...options,
            headers
        };

        try {
            const response = await fetch(url, config);
            const data = await response.json();

            if (response.status === 401 && endpoint !== '/login' && endpoint !== '/admin-login' && endpoint !== '/request-otp') {
                api.logout();
                return;
            }

            return {
                ok: response.ok,
                status: response.status,
                data
            };
        } catch (error) {
            console.error('API Fetch Error:', error);
            return {
                ok: false,
                status: 500,
                data: { message: 'Network error or unable to reach server' }
            };
        }
    },

    logout: () => {
        localStorage.removeItem('token');
        localStorage.removeItem('user');
        window.location.href = 'login.html';
    },

    requireAuth: () => {
        if (!api.getToken()) {
            window.location.href = 'login.html';
            return false;
        }
        return true;
    },

    requireAdmin: () => {
        if (!api.requireAuth()) return false;
        const user = api.getUser();
        if (!user || user.role !== 'admin') {
            window.location.href = 'user-dashboard.html';
            return false;
        }
        return true;
    },

    // MySQL stores IST time as a plain string e.g. "2026-03-04 18:11:00"
    // Browsers parse "YYYY-MM-DD HH:MM:SS" as UTC (wrong!) but
    // replacing dashes with slashes forces the browser to treat it as LOCAL time (IST) — correct!
    parseDate: (dateString) => {
        if (!dateString) return null;
        if (dateString instanceof Date) return dateString;

        let str = dateString.toString().trim();

        // If it's a standard MySQL/ISO string: "2026-03-04 18:11:00" or "2026-03-04T18:11:00"
        if (str.match(/^\d{4}-\d{2}-\d{2}[ T]\d{2}:\d{2}:\d{2}$/)) {
            // Replace dashes with slashes and ensure a space instead of T for local parsing
            str = str.replace(/-/g, '/').replace('T', ' ');
        }

        const date = new Date(str);
        return isNaN(date.getTime()) ? null : date;
    },

    formatDate: (dateString) => {
        const date = api.parseDate(dateString);
        if (!date) return 'N/A';
        return date.toLocaleDateString('en-IN', {
            year: 'numeric',
            month: 'short',
            day: 'numeric'
        });
    },

    formatTime: (dateString) => {
        const date = api.parseDate(dateString);
        if (!date) return 'N/A';
        return date.toLocaleTimeString('en-IN', {
            hour: '2-digit',
            minute: '2-digit',
            hour12: true
        });
    },

    formatDayOfWeek: (dateString) => {
        const date = api.parseDate(dateString);
        if (!date) return 'N/A';
        return date.toLocaleDateString('en-IN', { weekday: 'long' });
    },

    formatDateTime: (dateString) => {
        const date = api.parseDate(dateString);
        if (!date) return 'N/A';
        return date.toLocaleString('en-IN', {
            year: 'numeric',
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit',
            hour12: true
        });
    }
};

window.api = api;