# Map Feature Image Generator

Generate static map images for app cards, featured images, articles, or social previews from slippy-map tiles, markers, and optional routes.

## Features

- PNG, JPEG, and WebP output
- OpenGraph, 16:9, 4:3, square, and portrait presets
- Custom width/height
- Center + zoom controls
- Repeatable labeled markers
- GeoJSON LineString route overlays
- Configurable tile URL, attribution, and User-Agent
- Optional on-disk tile cache
- OpenStreetMap tiles by default
- No API key required for the default tile source

## Installation

Python 3.10+:

```sh
git clone https://github.com/myidealwrld/map-feature-image-generator.git
cd map-feature-image-generator
python3 -m pip install .
```

## Quick start

```sh
map-feature-image \
  --center 13.91,-60.98 \
  --zoom 12 \
  --preset og \
  --marker '13.91,-60.98,Example' \
  --output featured-map.png
```

Add a route:

```sh
map-feature-image \
  --center 13.91,-60.98 \
  --zoom 12 \
  --preset 16:9 \
  --route-geojson examples/route.geojson \
  --marker '13.91,-60.98,Start' \
  --output route.webp
```

## Presets

- `og`: 1200×630
- `16:9`: 1280×720
- `4:3`: 1200×900
- `square`: 1080×1080
- `portrait`: 1080×1350

Use `--width` and `--height` to override a preset.

## Tile providers

The default source is the OpenStreetMap standard tile server and attribution is rendered into the image automatically. Keep usage modest, retain attribution, identify your client with a real User-Agent, and follow the provider's tile usage policy. For production/high-volume rendering, use a tile provider that explicitly supports your volume and set:

```sh
--tile-url 'https://your-provider/{z}/{x}/{y}.png'
--attribution 'Your attribution'
--user-agent 'your-app/1.0'
```

Use `--cache-dir .tile-cache` to avoid repeatedly downloading the same tiles.

## Python API

```python
from map_feature_image_generator import Marker, render_map, save_image

image = render_map(
    center=(13.91, -60.98),
    zoom=12,
    width=1200,
    height=630,
    markers=[Marker(13.91, -60.98, "Example")],
)
save_image(image, "map.png")
```

## Development

```sh
python3 -m pip install -e .
python3 -m unittest discover -s tests -v
```

The test suite renders images with synthetic in-memory tiles, so CI does not depend on a live map provider.

## Security

Do not hard-code private coordinates, API keys, or provider secrets in examples. If your tile provider uses a secret token, inject it through your own runtime configuration and keep it out of Git history.

## License

Apache-2.0. See `LICENSE`.
