document.addEventListener('DOMContentLoaded', function() {
    const locationInput = document.getElementById('id_location');
    if (!locationInput) return;

    const mapContainer = document.getElementById('map-widget');
    if (!mapContainer) return;

    const map = L.map(mapContainer).setView([30.3753, 69.3451], 5);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
    }).addTo(map);

    let marker;

    // Function to place a marker and update input
    function updateMarker(lat, lng) {
        if (marker) {
            map.removeLayer(marker);
        }
        marker = L.marker([lat, lng]).addTo(map);
        locationInput.value = `${lat.toFixed(6)}, ${lng.toFixed(6)}`;
    }

    // Set initial marker if value exists
    if (locationInput.value) {
        const parts = locationInput.value.split(',');
        if (parts.length === 2) {
            const lat = parseFloat(parts[0]);
            const lng = parseFloat(parts[1]);
            if (!isNaN(lat) && !isNaN(lng)) {
                updateMarker(lat, lng);
                map.setView([lat, lng], 10);
            }
        }
    }

    map.on('click', function(e) {
        updateMarker(e.latlng.lat, e.latlng.lng);
    });
});
