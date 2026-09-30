import json
import os
import tempfile
import unittest

from PIL import Image

from map_feature_image_generator.cli import parse_marker, route_from_geojson
from map_feature_image_generator.renderer import Marker, TileSource, latlon_to_global_pixel, render_map, save_image


def fake_tile(_z, x, y, _source, _cache):
    value = (abs(x * 31 + y * 17) % 180) + 50
    return Image.new("RGB", (256, 256), (value, 220, 205))


class RendererTests(unittest.TestCase):
    def test_world_center(self):
        x, y = latlon_to_global_pixel(0, 0, 0)
        self.assertAlmostEqual(x, 128)
        self.assertAlmostEqual(y, 128)

    def test_renders_expected_dimensions_with_markers_and_route(self):
        image = render_map(
            center=(13.91, -60.98),
            zoom=12,
            width=640,
            height=360,
            markers=[Marker(13.91, -60.98, "Example")],
            route=[(13.90, -60.99), (13.92, -60.97)],
            source=TileSource(attribution="Example tiles"),
            tile_loader=fake_tile,
        )
        self.assertEqual(image.size, (640, 360))
        with tempfile.TemporaryDirectory() as tmp:
            path = save_image(image, os.path.join(tmp, "map.png"))
            self.assertTrue(os.path.exists(path))
            with Image.open(path) as saved:
                self.assertEqual(saved.size, (640, 360))

    def test_marker_and_geojson_parsing(self):
        marker = parse_marker("13.91,-60.98,Example")
        self.assertEqual(marker.label, "Example")
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "route.geojson")
            with open(path, "w", encoding="utf-8") as handle:
                json.dump(
                    {"type": "LineString", "coordinates": [[-60.99, 13.90], [-60.97, 13.92]]},
                    handle,
                )
            self.assertEqual(route_from_geojson(path)[0], (13.90, -60.99))


if __name__ == "__main__":
    unittest.main()
