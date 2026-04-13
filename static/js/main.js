// Common JS functionality like Geolocation

let pickupMap, pickupMarker;
let dropoffMap, dropoffMarker;

function forwardGeocodeAndPin(address, map, marker, latId, lngId) {
    if (!address) return;
    const geocoder = new google.maps.Geocoder();
    geocoder.geocode({ address: address }, (results, status) => {
        if (status === "OK" && results[0]) {
            const loc = results[0].geometry.location;
            map.setCenter(loc);
            map.setZoom(15);
            marker.setPosition(loc);
            document.getElementById(latId).value = loc.lat();
            document.getElementById(lngId).value = loc.lng();
        } else {
            // Google failed (likely due to missing billing). Fallback to free OpenStreetMap API!
            fetch(`https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(address)}`)
            .then(res => res.json())
            .then(data => {
                if (data && data.length > 0) {
                    const lat = parseFloat(data[0].lat);
                    const lng = parseFloat(data[0].lon);
                    const loc = new google.maps.LatLng(lat, lng);
                    map.setCenter(loc);
                    map.setZoom(15);
                    marker.setPosition(loc);
                    document.getElementById(latId).value = lat;
                    document.getElementById(lngId).value = lng;
                }
            })
            .catch(err => console.error("Fallback Geocoding also failed", err));
        }
    });
}

function initMap() {
    // Default config (Center of India)
    const initialPos = { lat: 20.5937, lng: 78.9629 };
    
    // Setup Pickup Map
    const pickupMapElement = document.getElementById('map');
    if (pickupMapElement) {
        pickupMap = new google.maps.Map(pickupMapElement, {
            center: initialPos,
            zoom: 5,
        });
        
        pickupMarker = new google.maps.Marker({
            position: initialPos,
            map: pickupMap,
            draggable: true
        });
        
        // If dragging pickup marker
        pickupMarker.addListener('dragend', function(e) {
            const lat = e.latLng.lat();
            const lng = e.latLng.lng();
            document.getElementById('pickup_lat').value = lat;
            document.getElementById('pickup_lng').value = lng;
            reverseGeocode({lat: lat, lng: lng}, 'pickup_address');
        });

        // Setup Autocomplete for pickup_address
        const pickupInput = document.getElementById('pickup_address');
        if (pickupInput) {
            const autocomplete = new google.maps.places.Autocomplete(pickupInput);
            autocomplete.bindTo('bounds', pickupMap);
            
            autocomplete.addListener('place_changed', function() {
                const place = autocomplete.getPlace();
                if (!place.geometry || !place.geometry.location) {
                    // Fallback if they hit enter without selecting
                    forwardGeocodeAndPin(pickupInput.value, pickupMap, pickupMarker, 'pickup_lat', 'pickup_lng');
                    return;
                }
                
                pickupMap.setCenter(place.geometry.location);
                pickupMap.setZoom(15);
                pickupMarker.setPosition(place.geometry.location);
                
                document.getElementById('pickup_lat').value = place.geometry.location.lat();
                document.getElementById('pickup_lng').value = place.geometry.location.lng();
            });

            // Fallback when clicking away
            pickupInput.addEventListener('blur', function() {
                const latVal = document.getElementById('pickup_lat').value;
                // Only geocode if it hasn't just been set by autocomplete
                if (pickupInput.value && latVal == "0") {
                    forwardGeocodeAndPin(pickupInput.value, pickupMap, pickupMarker, 'pickup_lat', 'pickup_lng');
                }
            });
        }
    }

    // Setup Dropoff Map
    const dropoffMapElement = document.getElementById('dropoff_map');
    if (dropoffMapElement) {
        dropoffMap = new google.maps.Map(dropoffMapElement, {
            center: initialPos,
            zoom: 5,
        });
        
        dropoffMarker = new google.maps.Marker({
            position: initialPos,
            map: dropoffMap,
            draggable: true
        });
        
        // If dragging dropoff marker
        dropoffMarker.addListener('dragend', function(e) {
            const lat = e.latLng.lat();
            const lng = e.latLng.lng();
            document.getElementById('dropoff_lat').value = lat;
            document.getElementById('dropoff_lng').value = lng;
            reverseGeocode({lat: lat, lng: lng}, 'dropoff_address');
        });

        // Setup Autocomplete for dropoff_address
        const dropoffInput = document.getElementById('dropoff_address');
        if (dropoffInput) {
            const autocompleteDrop = new google.maps.places.Autocomplete(dropoffInput);
            autocompleteDrop.bindTo('bounds', dropoffMap);

            autocompleteDrop.addListener('place_changed', function() {
                const place = autocompleteDrop.getPlace();
                if (!place.geometry || !place.geometry.location) {
                    forwardGeocodeAndPin(dropoffInput.value, dropoffMap, dropoffMarker, 'dropoff_lat', 'dropoff_lng');
                    return;
                }

                dropoffMap.setCenter(place.geometry.location);
                dropoffMap.setZoom(15);
                dropoffMarker.setPosition(place.geometry.location);

                document.getElementById('dropoff_lat').value = place.geometry.location.lat();
                document.getElementById('dropoff_lng').value = place.geometry.location.lng();
            });

            // Fallback when clicking away
            dropoffInput.addEventListener('blur', function() {
                const latVal = document.getElementById('dropoff_lat').value;
                if (dropoffInput.value && latVal == "0") {
                    forwardGeocodeAndPin(dropoffInput.value, dropoffMap, dropoffMarker, 'dropoff_lat', 'dropoff_lng');
                }
            });
        }
    }
}
window.initMap = initMap;

function reverseGeocode(pos, inputElementId) {
    const geocoder = new google.maps.Geocoder();
    geocoder.geocode({ location: pos }, (results, status) => {
        const el = document.getElementById(inputElementId);
        if (!el) return;
        
        if (status === "OK" && results[0]) {
            el.value = results[0].formatted_address;
        } else {
            // Fallback: Use free OpenStreetMap to get the address words when Google fails
            fetch(`https://nominatim.openstreetmap.org/reverse?format=json&lat=${pos.lat}&lon=${pos.lng}`)
            .then(res => res.json())
            .then(data => {
                if (data && data.display_name) {
                    el.value = data.display_name;
                } else {
                    el.value = `Lat: ${pos.lat.toFixed(4)}, Lng: ${pos.lng.toFixed(4)}`;
                }
            })
            .catch(err => {
                console.error("OSM Reverse Geocoding failed", err);
                el.value = `Lat: ${pos.lat.toFixed(4)}, Lng: ${pos.lng.toFixed(4)}`;
            });
        }
    });
}

function getLocation(inputElementId) {
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(
            (position) => {
                const lat = position.coords.latitude;
                const lng = position.coords.longitude;
                const el = document.getElementById(inputElementId);
                const pos = {lat: lat, lng: lng};
                
                if (inputElementId === 'pickup_address') {
                    document.getElementById('pickup_lat').value = lat;
                    document.getElementById('pickup_lng').value = lng;
                    
                    if (pickupMap && pickupMarker) {
                        pickupMap.setCenter(pos);
                        pickupMap.setZoom(15);
                        pickupMarker.setPosition(pos);
                        reverseGeocode(pos, inputElementId);
                    } else if (el) {
                        el.value = `Lat: ${lat.toFixed(4)}, Lng: ${lng.toFixed(4)}`;
                    }
                }
            },
            (error) => {
                alert("Error getting location: " + error.message);
            }
        );
    } else {
        alert("Geolocation is not supported by this browser.");
    }
}
