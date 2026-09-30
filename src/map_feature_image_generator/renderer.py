"""Static slippy-map image rendering with configurable tile sources."""

from __future__ import annotations

import io
import math
import os
import urllib.parse
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Iterable

from PIL import Image, ImageDraw, ImageFont

TILE_SIZE = 256
MAX_LAT = 85.05112878
PRESETS = {
    "og": (1200, 630),
    "16:9": (1280, 720),
    "4:3": (1200, 900),
    "square": (1080, 1080),
    "portrait": (1080, 1350),
}


@dataclass(frozen=True)
class TileSource:
    template: str = "https://tile.openstreetmap.org/{z}/{x}/{y}.png"
    attribution: str = "© OpenStreetMap contributors"
    user_agent: str = "map-feature-image-generator/0.1 (+https://github.com/myidealwrld/map-feature-image-generator)"


@dataclass(frozen=True)
class Marker:
    lat: float
    lon: float
    label: str = ""


def clamp_lat(lat: float) -> float:
    return max(-MAX_LAT, min(MAX_LAT, float(lat)))


def latlon_to_global_pixel(lat: float, lon: float, zoom: int) -> tuple[float, float]:
    lat = clamp_lat(lat)
    lon = float(lon)
    scale = TILE_SIZE * (2 ** int(zoom))
    x = (lon + 180.0) / 360.0 * scale
    sin_lat = math.sin(math.radians(lat))
    y = (0.5 - math.log((1 + sin_lat) / (1 - sin_lat)) / (4 * math.pi)) * scale
    return x, y


def _tile_cache_path(cache_dir: str | os.PathLike[str], source: TileSource, z: int, x: int, y: int) -> Path:
    host = urllib.parse.urlparse(source.template).hostname or "tiles"
    return Path(cache_dir) / host / str(z) / str(x) / f"{y}.png"


def fetch_tile(z: int, x: int, y: int, source: TileSource, cache_dir: str | None = None) -> Image.Image:
    tiles_across = 2 ** z
    x = x % tiles_across
    if y < 0 or y >= tiles_across:
        return Image.new("RGB", (TILE_SIZE, TILE_SIZE), "white")

    cache_path = _tile_cache_path(cache_dir, source, z, x, y) if cache_dir else None
    if cache_path and cache_path.exists():
        return Image.open(cache_path).convert("RGB")

    url = source.template.format(z=z, x=x, y=y)
    request = urllib.request.Request(url, headers={"User-Agent": source.user_agent, "Accept": "image/*"})
    with urllib.request.urlopen(request, timeout=30) as response:
        data = response.read()
    tile = Image.open(io.BytesIO(data)).convert("RGB")
    if tile.size != (TILE_SIZE, TILE_SIZE):
        tile = tile.resize((TILE_SIZE, TILE_SIZE))
    if cache_path:
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        tile.save(cache_path, "PNG")
    return tile


def _point_on_canvas(lat: float, lon: float, zoom: int, center_x: float, left: float, top: float) -> tuple[float, float]:
    x, y = latlon_to_global_pixel(lat, lon, zoom)
    scale = TILE_SIZE * (2 ** zoom)
    while x - center_x > scale / 2:
        x -= scale
    while center_x - x > scale / 2:
        x += scale
    return x - left, y - top


def render_map(
    *,
    center: tuple[float, float],
    zoom: int,
    width: int,
    height: int,
    markers: Iterable[Marker] = (),
    route: Iterable[tuple[float, float]] = (),
    source: TileSource | None = None,
    cache_dir: str | None = None,
    tile_loader: Callable[[int, int, int, TileSource, str | None], Image.Image] = fetch_tile,
    marker_color: str = "#d1495b",
    route_color: str = "#274c77",
) -> Image.Image:
    if width <= 0 or height <= 0:
        raise ValueError("width and height must be positive")
    if zoom < 0 or zoom > 22:
        raise ValueError("zoom must be between 0 and 22")

    source = source or TileSource()
    center_x, center_y = latlon_to_global_pixel(center[0], center[1], zoom)
    left = center_x - width / 2
    top = center_y - height / 2
    right = left + width
    bottom = top + height

    min_tile_x = math.floor(left / TILE_SIZE)
    max_tile_x = math.floor((right - 1) / TILE_SIZE)
    min_tile_y = math.floor(top / TILE_SIZE)
    max_tile_y = math.floor((bottom - 1) / TILE_SIZE)

    canvas = Image.new("RGB", (width, height), "white")
    for tile_y in range(min_tile_y, max_tile_y + 1):
        for tile_x in range(min_tile_x, max_tile_x + 1):
            tile = tile_loader(zoom, tile_x, tile_y, source, cache_dir).convert("RGB")
            paste_x = round(tile_x * TILE_SIZE - left)
            paste_y = round(tile_y * TILE_SIZE - top)
            canvas.paste(tile, (paste_x, paste_y))

    draw = ImageDraw.Draw(canvas)
    route_points = [_point_on_canvas(lat, lon, zoom, center_x, left, top) for lat, lon in route]
    if len(route_points) >= 2:
        draw.line(route_points, fill=route_color, width=max(3, round(min(width, height) / 180)), joint="curve")

    radius = max(7, round(min(width, height) / 55))
    font = ImageFont.load_default()
    for marker in markers:
        x, y = _point_on_canvas(marker.lat, marker.lon, zoom, center_x, left, top)
        draw.ellipse(
            (x - radius, y - radius, x + radius, y + radius),
            fill=marker_color,
            outline="white",
            width=max(2, radius // 4),
        )
        if marker.label:
            bbox = draw.textbbox((0, 0), marker.label, font=font)
            text_w = bbox[2] - bbox[0]
            text_h = bbox[3] - bbox[1]
            pad = 4
            tx = min(max(4, x + radius + 5), width - text_w - pad * 2 - 4)
            ty = min(max(4, y - text_h / 2 - pad), height - text_h - pad * 2 - 4)
            draw.rounded_rectangle(
                (tx, ty, tx + text_w + pad * 2, ty + text_h + pad * 2),
                radius=4,
                fill="white",
                outline="#777777",
            )
            draw.text((tx + pad, ty + pad), marker.label, fill="#111111", font=font)

    attribution = source.attribution.strip()
    if attribution:
        bbox = draw.textbbox((0, 0), attribution, font=font)
        text_w = bbox[2] - bbox[0]
        text_h = bbox[3] - bbox[1]
        x = max(4, width - text_w - 10)
        y = max(4, height - text_h - 8)
        draw.rectangle((x - 3, y - 2, width, height), fill="white")
        draw.text((x, y), attribution, fill="#333333", font=font)

    return canvas


def save_image(image: Image.Image, output: str) -> str:
    path = Path(output)
    path.parent.mkdir(parents=True, exist_ok=True)
    suffix = path.suffix.lower()
    if suffix in {".jpg", ".jpeg"}:
        image.save(path, "JPEG", quality=92, optimize=True)
    elif suffix == ".webp":
        image.save(path, "WEBP", quality=92, method=4)
    else:
        if not suffix:
            path = path.with_suffix(".png")
        image.save(path, "PNG", optimize=True)
    return str(path)
