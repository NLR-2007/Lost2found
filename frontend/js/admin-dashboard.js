document.addEventListener('DOMContentLoaded', async () => {
    if (!window.api.requireAdmin()) return;

    const logoutBtn = document.getElementById('logout-btn');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', (e) => {
            e.preventDefault();
            window.api.logout();
        });
    }

    async function loadStats() {
        const response = await window.api.apiFetch('/admin/stats');
        if (response.ok) {
            document.getElementById('stat-users').textContent = response.data.users_count;
            document.getElementById('stat-lost').textContent = response.data.active_lost_count;
            document.getElementById('stat-found').textContent = response.data.active_found_count;
            document.getElementById('stat-recovered').textContent = response.data.recovered_count;
        }
    }

    async function loadUsers() {
        const response = await window.api.apiFetch('/admin/users');
        if (response.ok) {
            const tbody = document.getElementById('users-tbody');
            if (!tbody) return;

            tbody.innerHTML = '';

            if (response.data.length === 0) {
                tbody.innerHTML = `<tr><td colspan="7" class="text-center text-muted py-4">No regular users registered yet.</td></tr>`;
                return;
            }

            response.data.forEach(user => {
                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td style="font-weight: 600;">${user.name}</td>
                    <td><a href="mailto:${user.email}" style="color: var(--primary); text-decoration: none;">${user.email}</a></td>
                    <td>${window.api.formatDate(user.created_at)}</td>
                    <td><span class="badge badge-lost">${user.lost_count}</span></td>
                    <td><span class="badge badge-found">${user.found_count}</span></td>
                    <td><span class="badge badge-recovered">${user.recovered_count}</span></td>
                    <td>
                        <button class="btn btn-danger btn-delete-user" data-id="${user.id}" style="padding: 0.3rem 0.8rem; font-size: 0.85rem;">Delete</button>
                    </td>
                `;
                tbody.appendChild(tr);
            });

            // Attach delete listeners
            document.querySelectorAll('.btn-delete-user').forEach(btn => {
                btn.addEventListener('click', async (e) => {
                    const userId = e.target.dataset.id;
                    if (confirm("Are you sure you want to delete this user and all their reported items? This cannot be undone.")) {
                        await deleteUser(userId);
                    }
                });
            });
        }
    }

    async function deleteUser(userId) {
        const response = await window.api.apiFetch(`/admin/delete-user?user_id=${userId}`, {
            method: 'DELETE'
        });

        if (response.ok) {
            alert("User deleted successfully.");
            loadStats();
            loadUsers();
        } else {
            alert(response.data.message || "Failed to delete user.");
        }
    }

    // Initialize
    loadStats();
    loadUsers();
});
