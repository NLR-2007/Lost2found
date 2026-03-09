document.addEventListener('DOMContentLoaded', async () => {

    // Auth is NOT strictly required to view items per requirements? 
    // Wait, the prompt says: "Get all items endpoint accepts GET at /api/items and requires JWT."
    // So yes, we require auth.
    if (!window.api.requireAuth()) return;

    const user = window.api.getUser();
    const isAdmin = user && user.role === 'admin';

    async function loadItems() {
        const response = await window.api.apiFetch('/items');
        if (response.ok) {
            renderTable('lost-items-tbody', response.data.lost, 'lost');
            renderTable('found-items-tbody', response.data.found, 'found');
        } else {
            console.error("Failed to load items", response.data.message);
        }
    }

    function renderTable(tbodyId, items, type) {
        const tbody = document.getElementById(tbodyId);
        if (!tbody) return;

        tbody.innerHTML = '';

        if (items.length === 0) {
            const colSpan = isAdmin ? 9 : 8;
            tbody.innerHTML = `<tr><td colspan="${colSpan}" class="text-center text-muted py-4">No ${type} items reported yet.</td></tr>`;
            return;
        }

        items.forEach(item => {
            const tr = document.createElement('tr');

            const photoCell = item.image
                ? `<img src="${UPLOAD_URL}/${item.image}" alt="${item.item_name}" class="item-thumb" onerror="this.onerror=null; this.parentElement.innerHTML='<div class=\\'no-image\\'>Not Found</div>';">`
                : `<div class="no-image">No Img</div>`;

            const statusBadgeClass = `badge-${item.status}`;
            const statusCapitalized = item.status.charAt(0).toUpperCase() + item.status.slice(1);

            let adminControls = '';
            if (isAdmin) {
                adminControls = `
                    <td>
                        <div class="action-btns">
                            <select class="form-control status-select" data-id="${item.id}" data-type="${type}">
                                <option value="open" ${item.status === 'open' ? 'selected' : ''}>Open</option>
                                <option value="matched" ${item.status === 'matched' ? 'selected' : ''}>Matched</option>
                                <option value="recovered" ${item.status === 'recovered' ? 'selected' : ''}>Recovered</option>
                            </select>
                            <button class="btn btn-primary btn-update-status" data-id="${item.id}" data-type="${type}" style="padding: 0.2rem 0.5rem; font-size: 0.8rem;">Update</button>
                            <button class="btn btn-danger btn-delete-item" data-id="${item.id}" data-type="${type}" style="padding: 0.2rem 0.5rem; font-size: 0.8rem;">Delete</button>
                        </div>
                    </td>
                `;
            }

            tr.innerHTML = `
                <td>${photoCell}</td>
                <td style="font-weight: 600;">${item.item_name}</td>
                <td>${item.category}</td>
                <td>${item.location}</td>
                <td>${item.user_name}</td>
                <td><a href="mailto:${item.user_email}" style="color: var(--primary); text-decoration: none;">${item.user_email}</a></td>
                <td><span class="badge ${statusBadgeClass}"><span class="status-dot ${item.status}"></span> ${statusCapitalized}</span></td>
                <td>${window.api.formatDate(item.created_at)}</td>
                ${adminControls}
            `;
            tbody.appendChild(tr);
        });

        if (isAdmin) {
            attachAdminListeners(tbody);
        }
    }

    function attachAdminListeners(tbody) {
        tbody.querySelectorAll('.btn-update-status').forEach(btn => {
            btn.addEventListener('click', async (e) => {
                const id = e.target.dataset.id;
                const type = e.target.dataset.type;
                const selectElement = tbody.querySelector(`select[data-id="${id}"][data-type="${type}"]`);
                const newStatus = selectElement.value;

                const response = await window.api.apiFetch('/update-status', {
                    method: 'POST',
                    body: JSON.stringify({ item_id: id, type: type, status: newStatus })
                });

                if (response.ok) {
                    alert('Status updated successfully');
                    loadItems(); // Refresh table
                } else {
                    alert(response.data.message || 'Failed to update status');
                }
            });
        });

        tbody.querySelectorAll('.btn-delete-item').forEach(btn => {
            btn.addEventListener('click', async (e) => {
                if (!confirm("Are you sure you want to delete this item?")) return;

                const id = e.target.dataset.id;
                const type = e.target.dataset.type;

                const response = await window.api.apiFetch(`/delete-item?item_id=${id}&type=${type}`, {
                    method: 'DELETE'
                });

                if (response.ok) {
                    alert('Item deleted successfully');
                    loadItems(); // Refresh table
                } else {
                    alert(response.data.message || 'Failed to delete item');
                }
            });
        });
    }

    // Adjust table headers if admin
    if (isAdmin) {
        const lostThead = document.querySelector('#lost-items-table thead tr');
        const foundThead = document.querySelector('#found-items-table thead tr');
        if (lostThead) lostThead.innerHTML += '<th>Actions</th>';
        if (foundThead) foundThead.innerHTML += '<th>Actions</th>';

        // Hide report items for admin and fix dashboard link
        const navLost = document.getElementById('nav-report-lost');
        const navFound = document.getElementById('nav-report-found');
        const navDash = document.getElementById('nav-dashboard');
        if (navLost) navLost.style.display = 'none';
        if (navFound) navFound.style.display = 'none';
        if (navDash) navDash.href = 'admin-dashboard.html';
    }

    // Initialize
    loadItems();
});
