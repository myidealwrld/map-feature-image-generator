# Blocked: No Existing Map Image Exporter

The working code found in the app is an interactive `MapView` with native and web implementations. The website has Leaflet map pages backed by WordPress listing data. Neither path exports a static map image, and the app's `shareImage.js` captures non-map share cards only.

No source was found that accepts generic coordinates/bounds/markers and produces image files. The requested dimensions, presets, routes/GeoJSON support, and three image examples therefore cannot be extracted or truthfully tested. Creating a new map-image pipeline would violate the instruction not to invent functionality. Keep this project blocked until a working map export implementation is identified.