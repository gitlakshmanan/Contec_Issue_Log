// AJAX logic for loading CR list and handling delete actions
(function(){
    // Helper: get cookie value (CSRF)
    function getCookie(name) {
        const value = `; ${document.cookie}`;
        const parts = value.split(`; ${name}=`);
        if (parts.length === 2) return parts.pop().split(';').shift();
        return null;
    }

    const csrftoken = getCookie('csrftoken');

    // Configure jQuery AJAX with CSRF
    if (window.jQuery) {
        $.ajaxSetup({
            headers: {
                'X-CSRFToken': csrftoken || ''
            }
        });
    }

    function loadCRData() {
        $.ajax({
            url: '/cr/api/cr-data/',
            method: 'GET',
            success: function(data) {
                const tbody = $('#crTable tbody');
                tbody.empty();

                data.forEach(function(cr) {
                    const row = `
                        <tr>
                            <td>${cr.cr_number || ''}</td>
                            <td>${cr.effecting_app || ''}</td>
                            <td>${cr.cr_raised_by || ''}</td>
                            <td>${cr.cr_raised_on ? new Date(cr.cr_raised_on).toLocaleDateString() : ''}</td>
                            <td>
                                <span class="badge ${cr.status === 'approved' ? 'bg-success' : (cr.status === 'submitted' ? 'bg-warning text-dark' : 'bg-secondary')} text-capitalize">
                                    ${cr.status || ''}
                                </span>
                            </td>
                            <td class="d-none d-md-table-cell">${cr.cr_approved_by || ''}</td>
                            <td class="d-none d-md-table-cell">${cr.process_manager || ''}</td>
                            <td>
                                <a href="/cr/${cr.id}/" class="btn btn-sm btn-info">
                                    <i class="fas fa-eye"></i>
                                </a>
                                <a href="/cr/${cr.id}/edit/" class="btn btn-sm btn-warning">
                                    <i class="fas fa-edit"></i>
                                </a>
                                <button class="btn btn-sm btn-danger delete-cr" data-cr-id="${cr.id}">
                                    <i class="fas fa-trash"></i>
                                </button>
                            </td>
                        </tr>
                    `;
                    tbody.append(row);
                });
            },
            error: function() {
                if (typeof showToast === 'function') {
                    showToast('Error loading change requests', 'danger');
                } else {
                    console.error('Error loading change requests');
                }
            }
        });
    }

    // Initial load
    $(document).ready(function() {
        loadCRData();

        // Delete CR handler (delegated)
        $(document).on('click', '.delete-cr', function() {
            const crId = $(this).data('cr-id');
            if (!crId) return;
            if (!confirm('Are you sure you want to delete this change request?')) return;

            $.ajax({
                url: `/cr/api/cr/${crId}/delete/`,
                method: 'DELETE',
                headers: { 'X-CSRFToken': csrftoken || '' },
                success: function() {
                    if (typeof showToast === 'function') showToast('Change request deleted successfully', 'success');
                    loadCRData();
                },
                error: function() {
                    if (typeof showToast === 'function') showToast('Error deleting change request', 'danger');
                }
            });
        });
    });

})();
