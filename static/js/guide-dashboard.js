// Guide Dashboard JavaScript for Content Management

// Load guide's own content
function loadMyContent() {
    const container = document.getElementById('myContentContainer');
    if (!container) return;

    // Show loading state
    container.innerHTML = `
        <div class="text-center py-4">
            <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Loading...</span>
            </div>
            <p class="text-muted mt-2">Loading your Jharkhand content...</p>
        </div>
    `;

    fetch('/guide/my_content')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                displayContent(data.content);
            } else {
                container.innerHTML = `
                    <div class="alert alert-danger">
                        <i class="fas fa-exclamation-triangle me-2"></i>
                        Failed to load content: ${data.message || 'Unknown error'}
                    </div>
                `;
            }
        })
        .catch(error => {
            console.error('Error loading content:', error);
            container.innerHTML = `
                <div class="alert alert-danger">
                    <i class="fas fa-exclamation-triangle me-2"></i>
                    Error loading content. Please try again.
                </div>
            `;
        });
}

// Display content in the container
function displayContent(contentList) {
    const container = document.getElementById('myContentContainer');

    if (!contentList || contentList.length === 0) {
        container.innerHTML = `
            <div class="text-center py-5">
                <i class="fas fa-images fa-4x text-muted mb-3"></i>
                <h5 class="text-muted">No Content Yet</h5>
                <p class="text-muted">Share your first Jharkhand tourism content to get started!</p>
                <button class="btn btn-primary" onclick="document.getElementById('content-tab').click()">
                    <i class="fas fa-plus me-2"></i>Add Content
                </button>
            </div>
        `;
        return;
    }

    let html = '<div class="row">';

    contentList.forEach(content => {
        const uploadDate = new Date(content.upload_date).toLocaleDateString();
        const categoryIcon = getCategoryIcon(content.upload_type);
        const categoryBadge = getCategoryBadge(content.upload_type);

        html += `
            <div class="col-lg-6 col-xl-4 mb-4">
                <div class="card h-100 shadow-sm">
                    ${content.image_path ? `
                        <div class="position-relative">
                            <img src="/static/${content.image_path}" class="card-img-top" alt="${content.title}" style="height: 200px; object-fit: cover;">
                            <div class="position-absolute top-0 end-0 m-2">
                                ${categoryBadge}
                            </div>
                        </div>
                    ` : `
                        <div class="card-img-top bg-light d-flex align-items-center justify-content-center" style="height: 200px;">
                            <i class="fas ${categoryIcon} fa-3x text-muted"></i>
                        </div>
                    `}
                    <div class="card-body d-flex flex-column">
                        <h6 class="card-title">${content.title}</h6>
                        <p class="card-text text-muted small flex-grow-1">${content.description.substring(0, 100)}${content.description.length > 100 ? '...' : ''}</p>
                        <div class="mt-auto">
                            ${content.location ? `<small class="text-muted d-block"><i class="fas fa-map-pin me-1"></i>${content.location}</small>` : ''}
                            <small class="text-muted d-block"><i class="fas fa-calendar me-1"></i>${uploadDate}</small>
                        </div>
                    </div>
                    <div class="card-footer bg-transparent">
                        <div class="d-flex gap-2">
                            <button class="btn btn-outline-primary btn-sm flex-fill" onclick="editContent(${content.id})">
                                <i class="fas fa-edit me-1"></i>Edit
                            </button>
                            <button class="btn btn-outline-danger btn-sm flex-fill" onclick="deleteContent(${content.id})">
                                <i class="fas fa-trash me-1"></i>Delete
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        `;
    });

    html += '</div>';
    container.innerHTML = html;
}

// Get icon for content category
function getCategoryIcon(type) {
    const icons = {
        'event': 'fa-calendar-alt',
        'photo': 'fa-camera',
        'location': 'fa-map-marker-alt',
        'waterfall': 'fa-water',
        'temple': 'fa-gopuram',
        'wildlife': 'fa-paw',
        'industrial': 'fa-industry'
    };
    return icons[type] || 'fa-image';
}

// Get badge for content category
function getCategoryBadge(type) {
    const badges = {
        'event': '<span class="badge bg-warning text-dark"><i class="fas fa-calendar-alt me-1"></i>Event</span>',
        'photo': '<span class="badge bg-info"><i class="fas fa-camera me-1"></i>Photo</span>',
        'location': '<span class="badge bg-success"><i class="fas fa-map-marker-alt me-1"></i>Location</span>',
        'waterfall': '<span class="badge bg-primary"><i class="fas fa-water me-1"></i>Waterfall</span>',
        'temple': '<span class="badge bg-secondary"><i class="fas fa-gopuram me-1"></i>Temple</span>',
        'wildlife': '<span class="badge bg-success"><i class="fas fa-paw me-1"></i>Wildlife</span>',
        'industrial': '<span class="badge bg-dark"><i class="fas fa-industry me-1"></i>Industrial</span>'
    };
    return badges[type] || '<span class="badge bg-secondary"><i class="fas fa-image me-1"></i>Content</span>';
}

// Edit content - load data into modal
function editContent(contentId) {
    // Show loading in modal
    const modal = new bootstrap.Modal(document.getElementById('editContentModal'));
    const modalBody = document.querySelector('#editContentModal .modal-body');

    modalBody.innerHTML = `
        <div class="text-center py-4">
            <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Loading...</span>
            </div>
            <p class="text-muted mt-2">Loading content details...</p>
        </div>
    `;

    modal.show();

    // Fetch content data
    fetch(`/guide/edit_content/${contentId}`)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                populateEditModal(data.content);
            } else {
                modalBody.innerHTML = `
                    <div class="alert alert-danger">
                        <i class="fas fa-exclamation-triangle me-2"></i>
                        Failed to load content: ${data.message || 'Unknown error'}
                    </div>
                `;
            }
        })
        .catch(error => {
            console.error('Error loading content for edit:', error);
            modalBody.innerHTML = `
                <div class="alert alert-danger">
                    <i class="fas fa-exclamation-triangle me-2"></i>
                    Error loading content. Please try again.
                </div>
            `;
        });
}

// Populate edit modal with content data
function populateEditModal(content) {
    document.getElementById('editContentId').value = content.id;
    document.getElementById('editUploadType').value = content.upload_type;
    document.getElementById('editTitle').value = content.title;
    document.getElementById('editDescription').value = content.description;
    document.getElementById('editLocation').value = content.location || '';

    // Handle current image preview
    const currentImagePreview = document.getElementById('currentImagePreview');
    if (content.image_path) {
        currentImagePreview.innerHTML = `
            <p class="mb-2"><strong>Current Image:</strong></p>
            <img src="/static/${content.image_path}" class="img-thumbnail" style="max-height: 150px;" alt="Current image">
        `;
    } else {
        currentImagePreview.innerHTML = '<p class="text-muted">No image uploaded</p>';
    }

    // Clear file input
    document.getElementById('editImage').value = '';
}

// Update content via AJAX
function updateContent() {
    const form = document.getElementById('editContentForm');
    const formData = new FormData(form);
    const contentId = document.getElementById('editContentId').value;

    // Disable submit button
    const submitBtn = document.querySelector('#editContentModal .btn-primary');
    const originalText = submitBtn.innerHTML;
    submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Updating...';
    submitBtn.disabled = true;

    fetch(`/guide/edit_content/${contentId}`, {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Close modal
            const modal = bootstrap.Modal.getInstance(document.getElementById('editContentModal'));
            modal.hide();

            // Show success message
            showToast('Jharkhand content updated successfully!', 'success');

            // Reload content
            loadMyContent();
        } else {
            showToast('Failed to update content: ' + (data.message || 'Unknown error'), 'error');
        }
    })
    .catch(error => {
        console.error('Error updating content:', error);
        showToast('Error updating content. Please try again.', 'error');
    })
    .finally(() => {
        // Re-enable submit button
        submitBtn.innerHTML = originalText;
        submitBtn.disabled = false;
    });
}

// Delete content with confirmation
function deleteContent(contentId) {
    if (!confirm('Are you sure you want to delete this Jharkhand content? This action cannot be undone.')) {
        return;
    }

    // Show loading state on the delete button
    const deleteBtn = event.target.closest('button');
    const originalText = deleteBtn.innerHTML;
    deleteBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Deleting...';
    deleteBtn.disabled = true;

    fetch(`/guide/delete_content/${contentId}`, {
        method: 'DELETE'
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showToast('Jharkhand content deleted successfully!', 'success');
            // Reload content
            loadMyContent();
        } else {
            showToast('Failed to delete content: ' + (data.message || 'Unknown error'), 'error');
        }
    })
    .catch(error => {
        console.error('Error deleting content:', error);
        showToast('Error deleting content. Please try again.', 'error');
    })
    .finally(() => {
        // Re-enable delete button
        deleteBtn.innerHTML = originalText;
        deleteBtn.disabled = false;
    });
}

// Initialize when page loads
document.addEventListener('DOMContentLoaded', function() {
    // Load content when content tab is shown
    const contentTab = document.getElementById('content-tab');
    if (contentTab) {
        contentTab.addEventListener('shown.bs.tab', function() {
            loadMyContent();
        });
    }

    // If content panel is already active, load content
    const activeTab = document.querySelector('#guideTabs .nav-link.active');
    if (activeTab && activeTab.id === 'content-tab') {
        loadMyContent();
    }
});

// Export functions for global use
window.loadMyContent = loadMyContent;
window.editContent = editContent;
window.updateContent = updateContent;
window.deleteContent = deleteContent;
