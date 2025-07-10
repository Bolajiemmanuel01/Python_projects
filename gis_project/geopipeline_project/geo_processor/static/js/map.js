import { map, drawnItems, aoiLayerGroup, imageryLayerGroup } from './map_init.js';
import { renderAOIs, refreshAOIs, submitAOI } from './aoi.js';
import { renderImagery, displayImageOnMap,  } from './sentinel.js';
import { getCSRFToken, openModal } from './ui.js';


// Ensure that the Save button runs
document.getElementById('confirmAoiName').addEventListener('click', submitAOI);

// Load AOI into dropdown and Map
fetch('/api/aois/')
.then(res => res.json())
// create the select element
.then(data => {
    const select = document.getElementById('aoiSelect');

    // Extract data from th json, the iterate over it. Create the option element and store the properties we need there
    data.features.forEach(feature => {
    const option = document.createElement('option');
    option.value = feature.id;
    option.textContent = feature.properties.name;
    select.appendChild(option);
    });

    // Render the data
    renderAOIs(data);
});

// load all sentinel imagery by default
fetch('/api/sentinel-imagery-geo/')
.then(res => res.json())
.then(data => renderImagery(data));

// Make the filter logic effective
document.getElementById('aoiSelect').addEventListener('change', (e) => {
    const selectedId = e.target.value;

    aoiLayerGroup.clearLayers();
    imageryLayerGroup.clearLayers();

    // If there's no selection
    if (!selectedId) {
        // Load all AOI Layer
        fetch('/api/aois/')
        .then(res => res.json())
        .then(data => renderAOIs(data));
        // Load all Sentinel Imagery
        fetch('/api/sentinel-imagery-geo/')
        .then(res => res.json())
        .then(data => renderImagery(data));
    } else {
        // Let's call the AOIs by the selected ID
        fetch(`/api/aois/${selectedId}/`)
        .then(res => res.json())
        .then(feature => {
            renderAOIs({"type": "FeatureCollection", "features": [feature]}, true);
        });
        // Let's call the Sentinel Imagery by the selected ID
        fetch(`/api/sentinel-imagery-geo/?aoi_id=${selectedId}`)
        .then(res => res.json())
        .then(data => renderImagery(data));
    }
});


// This Handles AOI creation and workflow
let drawnGeometry = null;

// Attaching the drawing on the Map 
map.on(L.Draw.Event.CREATED, (e) => {
    drawnItems.clearLayers(); // clears existing drawing
    const layer = e.layer;
    drawnItems.addLayer(layer);
    drawnGeometry = layer.toGeoJSON().geometry;
    openModal(); //Open modal for name input
});

// hold the currently displayed raster
let sentinelRasterLayer = null;
let sentinelRasterOverlayControlAdded = false;
let name = null

// Lets define what happnend once the popup is triggered: the edit and delete button
// First i'll delegate button events
// When the popup is open on the map
map.on('popupopen', function(e) {

    // Get all the element on the popup
    const popupNode = e.popup.getElement();

    // At the end of the popupopen handler
    const aoiId = e.popup._source.feature.id;
    const popupDownloadList = document.getElementById(`popup-download-list-${aoiId}`);
    if (popupDownloadList) {
        fetch(`/api/downloads/?aoi=${aoiId}`)
        .then(res => res.json())
        .then(data => {
            if (!data.length) {
            popupDownloadList.innerHTML = "<i>No download history for this AOI.</i>";
            return;
            }

            const list = document.createElement("ul");
            list.style.listStyle = "none";
            list.style.paddingLeft = "0";

            data.forEach(entry => {
            const item = document.createElement("li");
            item.style.borderBottom = "1px solid #ccc";
            item.style.marginBottom = "10px";
            const label = entry.image_type === 'ndvi' ? 'NDVI 🌿' :
                            entry.image_type === 'false_color' ? 'False Color 🛰️' : 'True Color 🎨';
            item.innerHTML = `
                <b>Type:</b> ${label}<br>
                <b>Dates:</b> ${entry.start_date} → ${entry.end_date}<br>
                <b>Downloaded:</b> ${new Date(entry.timestamp).toLocaleString()}<br>
                <button class="btn btn-sm btn-outline-primary re-download-btn"
                        data-id="${aoiId}"
                        data-start="${entry.start_date}"
                        data-end="${entry.end_date}"
                        data-type="${entry.image_type}">
                Re-download
                </button>
            `;
            list.appendChild(item);
            });

            popupDownloadList.innerHTML = "";
            popupDownloadList.appendChild(list);

            // Handle Re-download Buttons
            const popupNode = e.popup.getElement();
            popupNode.querySelectorAll('.re-download-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                const aoiId = btn.dataset.id;
                const start = btn.dataset.start;
                const end = btn.dataset.end;
                const type = btn.dataset.type;

                const spinner = L.DomUtil.create('div', 'spinner-border text-primary');
                spinner.setAttribute('role', 'status');
                document.body.appendChild(spinner);

                fetch(`/api/aois/${aoiId}/download/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCSRFToken()
                },
                body: JSON.stringify({
                    start_date: start,
                    end_date: end,
                    image_type: type
                })
                })
                .then(res => res.ok ? res.blob() : res.json().then(err => Promise.reject(err)))
                .then(blob => {
                const url = URL.createObjectURL(blob);
                displayImageOnMap(url, aoiId, type);
                })
                .catch(err => {
                console.error("Re-download failed:", err);
                alert("Error: " + (err?.error || "Re-download failed"));
                })
                .finally(() => spinner.remove());
            });
            });

        })
        .catch(err => {
            popupDownloadList.innerHTML = "<span style='color:red;'>Error loading download history.</span>";
            console.error(err);
        });
    }


    // Let's treat the edit AOI handler
    const editBtn = popupNode.querySelector('.edit-aoi-btn'); //This takes care of the edit button when queried
    // Check if the edit button isn't empty
    if (editBtn) {
        // Listens for when the edit button is clicked and tells it what to do
        editBtn.addEventListener('click', () => {
        // First get the ID that was passed from the selection of the AOI
        const aoiId = editBtn.dataset.id;
        // Fetch the Data to populate the edit popup
        fetch(`/api/aois/${aoiId}/`)
            // Then load the data
            .then(res => res.json())
            // now get the data that i need from the json feedback
            .then(data => {
            // get the aoiID, name and description to prefill the edit form
            document.getElementById('editAoiId').value = data.id;
            document.getElementById('editAoiName').value = data.properties.name;
            document.getElementById('editAoiDescription').value = data.properties.description || '';
            // Now dsplay the modal with the prefille values gotten 
            const modal = new bootstrap.Modal(document.getElementById('editAoiModal'));
            modal.show();
            });
        });
    }

    // EDIT GEOMETRY
    const editGeoBtn = popupNode.querySelector('.edit-geo-aoi-btn');
    if (editGeoBtn) {
        editGeoBtn.addEventListener('click', () => {
        const aoiId = editGeoBtn.dataset.id;

        // Get geometry from API
        fetch(`/api/aois/${aoiId}/`)
            .then(res => res.json())
            .then(data => {
            drawnItems.clearLayers();
            const geometry = L.geoJSON(data).getLayers()[0];

            drawnItems.addLayer(geometry);
            map.fitBounds(geometry.getBounds());

            // Now listen for edits and save when complete
            map.once('draw:edited', function(e) {
                const editedLayer = e.layers.getLayers()[0];
                const newGeometry = editedLayer.toGeoJSON().geometry;

                fetch(`/api/aois/${aoiId}/updategeo/`, {
                method: 'PATCH',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCSRFToken()
                },
                body: JSON.stringify({ geometry: newGeometry })
                })
                .then(res => {
                if (!res.ok) throw new Error("Failed to update geometry.");
                alert("Geometry updated.");
                refreshAOIs();
                })
                .catch(err => {
                console.error(err);
                alert("Error updating geometry.");
                });
            });

            alert("Now edit the geometry on the map and click save.");
            });
        });
    }

    // Download button
    const downSentBtn = popupNode.querySelector('.download-sent-img-btn'); //This takes care of the download button when queried
    // Check if the download button isn't empty
    if (downSentBtn) {
        // Listens for when the download button is clicked and tells it what to do
        downSentBtn.addEventListener('click', () => {
        // First get the ID that was passed from the selection of the AOI
        const aoiId = downSentBtn.dataset.id;

        const today = new Date().toISOString().split('T')[0];
        document.getElementById('SentinelAoiId').value = aoiId;
        document.getElementById('endDate').value = today;
        document.getElementById('startDate').value = today;
        const modal = new bootstrap.Modal(document.getElementById('downloadModal'));
        modal.show();

        // downloadImage(aoiId, "2024-01-01", "2024-01-10")
        })
    }
    // Now let's handle the delete AOI handler
    const deleteBtn = popupNode.querySelector('.delete-aoi-btn'); // This takes care o the delete button when queried
    // check if the delete button isn't empty
    if (deleteBtn) {
        // Listen for when the delete button is clicked and tell it what to do
        deleteBtn.addEventListener('click', () => {
        // get the id so we can query the right AOI
        const aoiId = deleteBtn.dataset.id;
        // Reconfirm the delete action
        if (confirm('Are you sure you want to delete this AOI?')) {
            // Now fetch the delete query
            fetch(`/api/aois/${aoiId}/delete/`, {
            method: "DELETE",
            headers: {
                'X-CSRFToken': getCSRFToken()
            }
            })
            .then(res => {
            if (!res.ok) throw new Error('Failed to delete AOI.'); // If the request isn't ok
            alert('AOI deleted.');
            refreshAOIs();
            })
            .catch(err => {
            console.error(err);
            alert('Error deleting AOI.');
            });
        }
        });
    }
});

// Listen for the submit button
document.getElementById('editAoiForm').addEventListener('submit', function(e) {
    e.preventDefault();
    // Get all the variables from the for and trim to remove exccess spaces 
    const aoiId = document.getElementById('editAoiId').value;
    const updatedName = document.getElementById('editAoiName').value.trim();
    const updatedDescription = document.getElementById('editAoiDescription').value.trim();

    if (!updatedName) {
        alert("AOI name is required!");
        return;
    }

    // Fetch the update function
    fetch(`/api/aois/${aoiId}/update/`, {
        method: 'PATCH',
        headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCSRFToken()
        },
        body: JSON.stringify({
        properties: {
            name: updatedName,
            description: updatedDescription
        }
        })
    })
    .then(res => {
        if (!res.ok) throw new Error('Failed to update AOI.'); // Check if the request was ok
        return res.json();
    })
    .then(() => {
        alert('AOI updated.');
        bootstrap.Modal.getInstance(document.getElementById('editAoiModal')).hide(); // Hide the for modal
        aoiLayerGroup.clearLayers();
        refreshAOIs(); //refresh the AOI 
    })
    .catch(err => {
        console.error(err);
        alert('Error updating AOI.');
    });
});

document.getElementById('downloadForm').addEventListener('submit', function (e) {
    e.preventDefault();

    const aoiId = document.getElementById('SentinelAoiId').value;
    const startDate = document.getElementById('startDate').value;
    const endDate = document.getElementById('endDate').value;
    const imageType = document.getElementById('imageType').value;

    if (!aoiId) {
        alert("No AOI selected.");
        return;
    }

    const spinner = L.DomUtil.create('div', 'spinner-border text-primary');
    spinner.setAttribute('role', 'status');
    document.body.appendChild(spinner);

    fetch(`/api/aois/${aoiId}/download/`, {
        method: 'POST',
        headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCSRFToken()
        },
        body: JSON.stringify({
        start_date: startDate,
        end_date: endDate,
        image_type: imageType
        })
    })
    .then(res => res.ok ? res.blob() : res.json().then(err => Promise.reject(err)))
    .then(blob => {
        const url = URL.createObjectURL(blob);
        displayImageOnMap(url, aoiId, imageType);  // ✅ this is the correct next step
    })
    .catch(err => {
        console.error("Download failed:", err);  // ✅ just log the actual error, not aoiId
        alert("Error: " + (err?.error || "Image download failed"));
    })
    .finally(() => spinner.remove());
});



// Let's make the query sentinel imagery button work
// This adds an event listener to the button, listening fr click of the button
document.getElementById('querySentinelBtn').addEventListener('click', () => {
    const selectedId = document.getElementById('aoiSelect').value;

    // Get the result container and clear it
    const resultsContainer = document.getElementById('queryResults');
    //Clear it
    resultsContainer.innerHTML = '';

    // Check if the aoi was selected, then prompt the user to select n aoi
    if (!selectedId) {
        resultsContainer.innerHTML = '<p style="text-align:center; color:red;"><b>Please select an AOI to query imagery.</b></p>';
        return;
    }

    // Let's call the api to fetch imagery linked to the AOI
    fetch(`/api/query-sentinel/${selectedId}/`)
    .then(res => {
        if (!res.ok) {
            throw new Error('Error Fetching Imagery data');
        }
        return res.json();
    })
    .then(data => {
        if (data.length === 0) {
            resultsContainer.innerHTML = '<p style="text-align:center;"><i>No imagery found for this AOI.</i></p>';
            return;
        }

        // Build and Display result
        // Design the list container
        const list = document.createElement('ul');
        list.style.listStyle = 'none';
        list.style.padding = '0'

        // populate the list container element
        data.features.forEach(item => {
            // Get the properties for each data
            const props = item.properties

            // Check if props isn't empty
            if (!props) return;


            // Create the list Item
            const listItem = document.createElement('li');
            listItem.style.marginBottom = '10px';
            listItem.style.borderBottom = '1px solid #ccc';
            // Populate it
            listItem.innerHTML = `
            <b>Tile ID:</b> ${item.id}<br>
            <b>Date:</b> ${props.timestamp}<br>
            <b>Cloud Coverage:</b> ${props.cloud_coverage}%<br>
            `;

            // Append to the list container
            list.appendChild(listItem);
        });

        resultsContainer.appendChild(list);
    })
    .catch(err => {
        console.error(err);
        resultsContainer.innerHTML = '<p style="text-align:center; color:red;">Failed to load imagery data.</p>';
    });
});


export {drawnGeometry};

// entry.image_type.toUpperCase()