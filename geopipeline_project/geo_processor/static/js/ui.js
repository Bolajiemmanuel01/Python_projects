// Utility functions

export function getCSRFToken() {
    const name = 'csrftoken';
    const cookieValue = document.cookie
        .split('; ')
        .find(row => row.startsWith(name + '='))
        ?.split('=')[1];
    return cookieValue || '';
}


// Create function to open modal
export function openModal() {
    const modalElement = document.getElementById('aoiNameModal');
    let modal = bootstrap.Modal.getInstance(modalElement);

    if (!modal) {
        modal = new bootstrap.Modal(modalElement); // initialize if not already
    }

    modal.show();
}


// Create function to close modal
export function closeModal() {
    // Get the modal element on the page
    const modalElement = document.getElementById('aoiNameModal');
    const modal = bootstrap.Modal.getInstance(modalElement);
    modal.hide();
    document.getElementById('aoiNameInput').value = '';
    document.getElementById('aoiDescriptionInput').value = '';
}


// POPUP Function
export function createAoiPopupContent(aoi) {
    return `
        <div>
        <strong>${aoi.properties.name}</strong><br/>
        ${aoi.properties.description || ''}<br/><br/>
        <button class="btn btn-sm btn-success download-sent-img-btn" data-id="${aoi.id}">Download Sentinel Image</button>
        <button class="btn btn-sm btn-warning edit-aoi-btn" data-id="${aoi.id}">Edit</button>
        <button class="btn btn-sm btn-warning edit-geo-aoi-btn" data-id="${aoi.id}">Edit Geometry</button>
        <button class="btn btn-sm btn-danger delete-aoi-btn" data-id="${aoi.id}">Delete</button>

        <hr>
        <div><b>Download History(Last three downloads):</b></div>
        <div id="popup-download-list-${aoi.id}"><i>Loading...</i></div>
        </div>
    `;
}