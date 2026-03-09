document.addEventListener('DOMContentLoaded', async () => {
    // Only accessible to admins
    if (!window.api.requireAdmin()) return;

    async function loadMatches() {
        const response = await window.api.apiFetch('/matches');
        if (response.ok) {
            renderMatches(response.data);
        } else {
            console.error("Failed to load matches", response.data.message);
        }
    }

    function renderMatches(matches) {
        const tbody = document.getElementById('matches-tbody');
        if (!tbody) return;

        tbody.innerHTML = '';

        if (matches.length === 0) {
            tbody.innerHTML = `<tr><td colspan="5" class="text-center text-muted py-4">No new match suggestions found.</td></tr>`;
            return;
        }

        matches.forEach(match => {
            const tr = document.createElement('tr');

            tr.innerHTML = `
                <td><span style="font-weight: 600; color: var(--danger);">#${match.lost_id}</span> ${match.lost_item_name}</td>
                <td><span style="font-weight: 600; color: var(--info);">#${match.found_id}</span> ${match.found_item_name}</td>
                <td>${match.category}</td>
                <td>${match.location}</td>
                <td>
                    <button class="btn btn-success btn-confirm-match" data-lost="${match.lost_id}" data-found="${match.found_id}" style="padding: 0.4rem 1rem; font-size: 0.9rem;">
                        Confirm Match
                    </button>
                </td>
            `;
            tbody.appendChild(tr);
        });

        attachListeners();
    }

    function attachListeners() {
        document.querySelectorAll('.btn-confirm-match').forEach(btn => {
            btn.addEventListener('click', async (e) => {
                const lostId = e.target.dataset.lost;
                const foundId = e.target.dataset.found;

                if (!confirm("Confirm this match? This will update both items to 'Matched' status.")) return;

                const response = await window.api.apiFetch('/confirm-match', {
                    method: 'POST',
                    body: JSON.stringify({ lost_id: lostId, found_id: foundId })
                });

                if (response.ok) {
                    alert('Match confirmed successfully');
                    loadMatches(); // Reload list
                } else {
                    alert(response.data.message || 'Failed to confirm match');
                }
            });
        });
    }

    // Initialize
    loadMatches();
});
