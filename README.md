# Map Feature Image Generator

This requested extraction is blocked. The inspected production sources render interactive maps for app and website views, but they do not contain a standalone map-to-image generator or a working map screenshot export pipeline.

## Why it exists

The intended goal was to extract a reusable map image generator from an existing working implementation. The source review found no such implementation, so this folder records the boundary rather than inventing a replacement.

## Features

- Source audit and exact blocker are documented.
- No image-generation feature is claimed.

## Source reviewed

- The app's native map component delegates to `react-native-maps`.
- The web map component embeds a map provider.
- Website map code uses Leaflet and live map tiles with project-specific listing data.
- The app share-image helper captures a different UI card, not a map feature image.

These are not sufficient evidence for a reusable image-generation tool. Building a new renderer, screenshot pipeline, or tile downloader here would invent functionality and could introduce provider/licensing or data issues.

## Status

See `BLOCKED.md`. No generator, examples, or generated images are included, and this project is not ready to publish.

## Installation and quick start

There is no executable package to install or run. Do not treat this folder as a generator until a production source implementation with image output is identified and tested.

## Configuration and expected output

No configuration or image output exists in this blocked copy.

## Architecture

The inspected source paths were interactive map views and a separate share-card capture helper. Neither is a map image exporter.

## Development and testing

No executable tests can be run for this blocked extraction. A future implementation must render at least three generic example images and verify file format and dimensions.

## Security

Do not add API keys, private coordinates, production listings, or downloaded map tiles. Any future map provider must be used under its documented terms.

## Licence

Apache-2.0. See `LICENSE`.