# HEICShift

## Overview
High-performance HEIC/HEIF batch converter with PyQt6 GUI. Scans directories recursively and converts to JPEG, PNG, WebP, or TIFF with full metadata preservation.

## Tech Stack
- **Language**: Python 3.10+
- **GUI**: PyQt6 (Fusion style, Catppuccin Mocha theme)
- **HEIC Decoding**: pillow-heif (registers as Pillow plugin)
- **Image Processing**: Pillow
- **Parallelism**: ThreadPoolExecutor (configurable 1-32 workers)

## Key File
- `heicshift.py` — Single-file application, ~580 lines

## Build / Run
```bash
python heicshift.py
# Dependencies auto-install via _bootstrap(): Pillow, pillow-heif, PyQt6
```

## Features
- Auto-detect format: JPEG for photos, PNG for transparent images
- EXIF, ICC color profile, and XMP metadata preservation
- Parallel conversion with configurable worker count
- Preserves folder structure in output (optional)
- Name collision handling
- JPEG 4:4:4 chroma subsampling for maximum color fidelity
- Settings persistence via QSettings
- Embedded log panel, stats dashboard
- Cancel support mid-conversion

## Architecture
- `_bootstrap()` auto-installs deps
- `scan_directory()` finds HEIC/HEIF files via glob
- `convert_file()` is thread-safe, handles single file conversion
- `ScanWorker(QThread)` scans in background
- `ConvertWorker(QThread)` manages ThreadPoolExecutor for parallel conversion
- GUI updates via pyqtSignal

## Version
- v1.0.0 — Initial release

## Gotchas
- iPhone HEIC files use Display P3 ICC profiles — passed through to output for correct color
- JPEG cannot store transparency — auto mode falls back to PNG when alpha detected
- pillow-heif on Windows uses bundled libheif; no system install needed
