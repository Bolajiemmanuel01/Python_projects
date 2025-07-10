// Sentinel Functions

import { sentinelRasterGroup, imageryLayerGroup, map } from './map_init.js';
import { getCSRFToken } from './ui.js';
import { aoiIdToLayerMap } from './aoi.js';




export function renderImagery(geojson) {
    L.geoJSON(geojson, {
        style: { color: 'red', weight: 1, dashArray: '4' },
        onEachFeature: (feature, layer) => {
            const { timestamp, cloud_coverage } = feature.properties;
            layer.bindPopup(`<b>AOI:</b> ${feature.properties.name}<br><b>Description:</b> ${feature.properties.description || 'N/A'}`);
        }
    }).addTo(imageryLayerGroup); // Add to Layer
}

// Function to display the image on the map
export function displayImageOnMap(url, aoiId, imageType = 'true_color') {
    const layer = aoiIdToLayerMap[aoiId];
    if (!layer || !layer.getBounds) {
        alert("Could not determine bounds for AOI.");
        return;
    }

    const aoiBounds = layer.getBounds();
    sentinelRasterGroup.clearLayers();

    let raster = L.imageOverlay(url, aoiBounds, { opacity: 0.7 });

    // Opacity slider control
    const slider = document.getElementById('opacitySlider');
    if (slider) {
        slider.addEventListener('input', function () {
            const value = parseFloat(this.value);
            if (raster) raster.setOpacity(value);
        });
    }

    // Remove image button
    const removeBtn = document.getElementById('removeImageBtn');
    if (removeBtn) {
        removeBtn.addEventListener('click', function () {
            if (raster) {
                map.removeLayer(raster);
                sentinelRasterGroup.clearLayers();
                raster = null;
                const legend = document.getElementById('ndviLegend');
                if (legend) legend.style.display = 'none';
            }
        });
    }

    // ✅ NDVI LEGEND DISPLAY
    const legend = document.getElementById('ndviLegend');
    console.log("Image type received:", imageType);
    if (imageType === 'ndvi' && legend) {
        legend.style.display = 'block';
    } else if (legend) {
        legend.style.display = 'none';
    }

    sentinelRasterGroup.addLayer(raster);
    map.fitBounds(aoiBounds);
}


// Download Sentinel Image function
export function downloadImage(aoiId, startDate, endDate) {
    fetch(`/api/aois/${aoiId}/download/`, {
        method: 'POST',
        headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCSRFToken()
        },
        body: JSON.stringify({
        start_date: startDate,
        end_date: endDate
        })
    })
    .then(res => {
        if (!res.ok) {
        throw new Error('Image download failed');
        }
        return res.blob();
    })
    .then(blob => {
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `sentinel_image_aoi_${aoiId}.png`;
        document.body.appendChild(a);
        a.click();
        a.remove();
    })
    .catch(error => alert(error.message));
}

// export function displayImageOnMap(url, aoiId, imageType = 'true_color') {
//     const layer = aoiIdToLayerMap[aoiId];
//     if (!layer || !layer.getBounds) {
//         alert("Could not determine bounds for AOI.");
//         return;
//     }

//     const aoiBounds = layer.getBounds();

//     // Optional: clear old raster layers if you want only one shown at a time
//     sentinelRasterGroup.clearLayers();

//     // Create an image overlay and add to group
//     let raster = L.imageOverlay(url, aoiBounds, {
//         opacity: 0.7
//     });
//     document.getElementById('opacitySlider').addEventListener('input', function () {
//         const value = parseFloat(this.value);
//         if (raster) {
//         raster.setOpacity(value);
//         }
//     });

//     document.getElementById('removeImageBtn').addEventListener('click', function () {
//         if (raster) {
//             map.removeLayer(raster);
//             raster = null;
//             sentinelRasterGroup.clearLayers();
//             document.getElementById('ndviLegend').style.display = 'none';
//         }
//     });

//     // Show NDVI legend if type is NDVI
//     const legend = document.getElementById('ndviLegend');
//     if (imageType === 'ndvi') {
//         legend.style.display = 'block';
//     } else {
//         legend.style.display = 'none';
//     }


//     sentinelRasterGroup.addLayer(raster);

//     // Auto-zoom
//     map.fitBounds(aoiBounds);

// }
