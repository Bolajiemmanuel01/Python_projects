// Map initializtion tool

// Create Map
export const map = L.map('map').setView([9.0820, 8.6753], 6); // Nigeria center

// Let's define our Layers

// Street map - Default Base layer
const streetMap = L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
maxZoom: 18,
attribution: '© OpenStreetMap'
});

// Satelite map - From ESRI
const satelliteMap = L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', {
maxZoom: 18,
attribution: 'Tiles © Esri'
});

// Add default base layer
streetMap.addTo(map);

// Base layers object
const baseMaps = {
"Street Map": streetMap,
"Satellite View": satelliteMap
};

// Define AOI Layer
export const aoiLayerGroup = L.layerGroup().addTo(map);
// Define Imagery Layer
export const imageryLayerGroup = L.layerGroup().addTo(map);
// Raster Layer
export const sentinelRasterGroup = L.layerGroup().addTo(map);


// Add Map Overlay
const overlayMaps = {
"AOIs": aoiLayerGroup,
"Sentinel Imagery": imageryLayerGroup,
"Sentinel Raster Image": sentinelRasterGroup
};

// Add Layer Control
L.control.layers(baseMaps, overlayMaps, { collapsed: false }).addTo(map);


// Add Leaflet draw integrations
export const drawnItems = new L.FeatureGroup().addTo(map);

// Add Leaflet drawing control
const drawControl = new L.Control.Draw({
draw: {
    polyline: false,
    marker: false,
    circle: false,
    circlemarker: false,
    rectangle: {
    shapeOptions: {
        color: "#28a745",
        weight: 2,
        fillOpacity: 0.4
    }
    },
    polygon: {
    allowIntersection: false,
    showArea: true,
    shapeOptions: {
        color: "#007bff",
        weight: 2,
        fillOpacity: 0.4
    }
    }
},
edit: {
    featureGroup: drawnItems,
    edit: true,
    remove: true
}
});

// Attach it to the map
map.addControl(drawControl);