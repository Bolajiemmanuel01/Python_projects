// AOI Functions
import { map, aoiLayerGroup } from './map_init.js';
import { getCSRFToken, createAoiPopupContent, closeModal } from './ui.js';
import { drawnGeometry } from './map.js';


let aoiLayer;


export const aoiIdToLayerMap = {};
// Create the configuration function
export function renderAOIs(geojson, zoom = false) {
    aoiLayerGroup.clearLayers(); // Optional: ensure no duplicates
    aoiLayer = L.geoJSON(geojson, {
        style: { color: 'blue', weight: 2 },
        onEachFeature: (feature, layer) => {
        const id = feature.id;
        if (id) {
            aoiIdToLayerMap[id] = layer;  // ✅ Track each layer by AOI ID
        }
        layer.bindPopup(createAoiPopupContent(feature));
        }
    });
    aoiLayerGroup.addLayer(aoiLayer);


    // Optional: zoom to AOI if needed
    if (zoom && geojson.features.length === 1) {
        map.fitBounds(aoiLayer.getBounds());
    }
}



// Refresh Function
export function refreshAOIs() {
    fetch('/api/aois/')
    .then(res => res.json())
    .then(data => {
        renderAOIs(data); // Existing render function
        const select = document.getElementById('aoiSelect')
        select.innerHTML = '<option value="">-- All AOIs --</option>';
        data.features.forEach(feature => {
        const option = document.createElement('option');
        option.value = feature.id;
        option.textContent = feature.properties.name;
        select.appendChild(option);
        });
    });
}



    
// Submit Function for New AOI
export function submitAOI() {
    const name = document.getElementById('aoiNameInput').value.trim();
    const description = document.getElementById('aoiDescriptionInput').value.trim();
    const properties = { name: name, description: description };

    // Checks and Alerts when the AOI name is't there 
    if (!name || !drawnGeometry) {
        alert("AOI name and Geometry are required.");
        return;
    }

    // Post the information to the Database
    fetch('/api/aois/', {
        method: 'POST',
        headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCSRFToken()
        },
        body: JSON.stringify({geometry: drawnGeometry, properties})
    })
    .then(res => {
        if (!res.ok) throw new Error("Failed to save AOI."); // Check if it saved
        return res.json();
    })
    .then(() => {
        alert("AOI saved.");
        closeModal();
        refreshAOIs(); // reload and render
    })
    .catch(err => {
        console.error(err);
        alert("Error saving AOI."); // Catch Error
    });
}

export {aoiLayer};