"""CLI for static map featured-image rendering."""

from __future__ import annotations

import argparse
import json

from .renderer import Marker, PRESETS, TileSource, render_map, save_image


def parse_latlon(value: str) -> tuple[float, float]:
    parts = [part.strip() for part in value.split(",")]
    if len(parts) != 2:
        raise argparse.ArgumentTypeError("expected LAT,LON")
    lat, lon = float(parts[0]), float(parts[1])
    if not -90 <= lat <= 90 or not -180 <= lon <= 180:
        raise argparse.ArgumentTypeError("latitude/longitude out of range")
    return lat, lon


def parse_marker(value: str) -> Marker:
    parts = [part.strip() for part in value.split(",", 2)]
    if len(parts) < 2:
        raise argparse.ArgumentTypeError("expected LAT,LON[,LABEL]")
    lat, lon = float(parts[0]), float(parts[1])
    if not -90 <= lat <= 90 or not -180 <= lon <= 180:
        raise argparse.ArgumentTypeError("marker latitude/longitude out of range")
    label = parts[2] if len(parts) == 3 else ""
    return Marker(lat, lon, label)


def route_from_geojson(path: str) -> list[tuple[float, float]]:
    with open(path, encoding="utf-8") as handle:
        data = json.load(handle)
    geometry = data.get("geometry") if data.get("type") == "Feature" else data
    if not isinstance(geometry, dict) or geometry.get("type") != "LineString":
        raise ValueError("route GeoJSON must be a LineString or a Feature containing one")
    coords = geometry.get("coordinates")
    if not isinstance(coords, list):
        raise ValueError("route GeoJSON has no coordinates")
    return [(float(lat), float(lon)) for lon, lat, *_ in coords]


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Render a static map image for an app, article, or social card")
    parser.add_argument("--center", required=True, type=parse_latlon, help="LAT,LON")
    parser.add_argument("--zoom", type=int, default=13)
    parser.add_argument("--preset", choices=sorted(PRESETS), default="og")
    parser.add_argument("--width", type=int)
    parser.add_argument("--height", type=int)
    parser.add_argument("--marker", action="append", default=[], type=parse_marker, help="LAT,LON[,LABEL]; repeatable")
    parser.add_argument("--route-geojson")
    parser.add_argument("--output", required=True)
    parser.add_argument("--tile-url", default=TileSource.template)
    parser.add_argument("--attribution", default=TileSource.attribution)
    parser.add_argument("--user-agent", default=TileSource.user_agent)
    parser.add_argument("--cache-dir")
    args = parser.parse_args(argv)

    width, height = PRESETS[args.preset]
    width = args.width or width
    height = args.height or height
    route = route_from_geojson(args.route_geojson) if args.route_geojson else []
    source = TileSource(args.tile_url, args.attribution, args.user_agent)
    image = render_map(
        center=args.center,
        zoom=args.zoom,
        width=width,
        height=height,
        markers=args.marker,
        route=route,
        source=source,
        cache_dir=args.cache_dir,
    )
    print(save_image(image, args.output))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
