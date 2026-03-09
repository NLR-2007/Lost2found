document.addEventListener('DOMContentLoaded', async () => {
    if (!window.api.requireAuth()) return;

    const user = window.api.getUser();
    if (user) {
        document.getElementById('user-name-display').textContent = user.name;
    }

    const logoutBtn = document.getElementById('logout-btn');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', (e) => {
            e.preventDefault();
            window.api.logout();
        });
    }

    // Toggle logic for filtering All / Lost / Found
    const filterBtns = document.querySelectorAll('.filter-btn');
    let currentFilter = 'all'; // 'all', 'lost', 'found'

    filterBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            filterBtns.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            currentFilter = btn.dataset.filter;
            renderTable();
        });
    });

    let allItems = [];

    async function loadUserItems() {
        const response = await window.api.apiFetch('/my-items');
        if (response.ok) {
            allItems = [...response.data.lost, ...response.data.found];
            // Sort by created_at descending
            allItems.sort((a, b) => new Date(b.created_at) - new Date(a.created_at));
            renderTable();
        } else {
            console.error("Failed to load user items", response.data.message);
        }
    }

    function renderTable() {
        const tbody = document.getElementById('user-items-tbody');
        if (!tbody) return;

        tbody.innerHTML = '';

        const filtered = allItems.filter(item => {
            if (currentFilter === 'all') return true;
            return item.type === currentFilter;
        });

        if (filtered.length === 0) {
            tbody.innerHTML = `<tr><td colspan="10" class="text-center text-muted py-4">No items found matching this filter.</td></tr>`;
            return;
        }

        filtered.forEach(item => {
            const tr = document.createElement('tr');

            const photoCell = item.image
                ? `<img src="${UPLOAD_URL}/${item.image}" alt="${item.item_name}" class="item-thumb" onerror="this.onerror=null; this.parentElement.innerHTML='<div class=\\'no-image\\'>Not Found</div>';">`
                : `<div class="no-image">No Img</div>`;

            const typeBadgeClass = item.type === 'lost' ? 'badge-lost' : 'badge-found';
            const statusBadgeClass = `badge-${item.status}`;
            const statusCapitalized = item.status.charAt(0).toUpperCase() + item.status.slice(1);

            const recoveredDisplay = item.recovered_at
                ? window.api.formatDateTime(item.recovered_at)
                : '-';

            tr.innerHTML = `
                <td>${photoCell}</td>
                <td style="font-weight: 600;">${item.item_name}</td>
                <td><span class="badge ${typeBadgeClass}">${item.type.toUpperCase()}</span></td>
                <td>${item.location}</td>
                <td>${window.api.formatDate(item.created_at)}</td>
                <td>${window.api.formatDayOfWeek(item.created_at)}</td>
                <td>${window.api.formatTime(item.created_at)}</td>
                <td><span class="badge ${statusBadgeClass}"><span class="status-dot ${item.status}"></span> ${statusCapitalized}</span></td>
                <td>${recoveredDisplay}</td>
                <td>
                    <button class="btn btn-danger btn-delete-item" data-id="${item.id}" data-type="${item.type}" style="padding: 0.3rem 0.8rem; font-size: 0.85rem;">
                        Delete
                    </button>
                </td>
            `;
            tbody.appendChild(tr);
        });

        attachDeleteListeners();
    }

    function attachDeleteListeners() {
        document.querySelectorAll('.btn-delete-item').forEach(btn => {
            btn.addEventListener('click', async (e) => {
                const itemId = e.target.dataset.id;
                const itemType = e.target.dataset.type;

                if (!confirm("Are you sure you want to delete this item? This action cannot be undone.")) return;

                const response = await window.api.apiFetch(`/delete-item?item_id=${itemId}&type=${itemType}`, {
                    method: 'DELETE'
                });

                if (response.ok) {
                    alert('Item deleted successfully');
                    loadUserItems(); // Reload
                } else {
                    alert(response.data.message || 'Failed to delete item');
                }
            });
        });
    }

    // Initialize
    loadUserItems();
});
