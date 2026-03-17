# HEICShift

## Overview
Universal image batch converter with PyQt6 GUI. Scans directories recursively and converts HEIC, AVIF, WebP, JPEG XL, Camera RAW, TIFF, BMP, JPEG 2000, QOI, and ICO/CUR files to JPEG, PNG, WebP, or TIFF with full metadata preservation.

## Tech Stack
- **Language**: Python 3.10+
- **GUI**: PyQt6 (Fusion style, Catppuccin Mocha theme)
- **HEIC/AVIF Decoding**: pillow-heif (registers as Pillow plugin)
- **JPEG XL**: pillow-jxl-plugin (optional, registers as Pillow plugin)
- **Camera RAW**: rawpy wrapping libraw (optional)
- **QOI**: qoi package (optional)
- **Image Processing**: Pillow (handles WebP, TIFF, BMP, JP2, ICO natively)
- **Parallelism**: ThreadPoolExecutor (configurable 1-32 workers)

## Key File
- `heicshift.py` — Single-file application

## Build / Run
```bash
python heicshift.py
# Required deps auto-install: Pillow, pillow-heif, PyQt6
# Optional deps auto-install: rawpy, pillow-jxl-plugin, qoi
```

## Supported Input Formats
| Format | Extensions | Decoder | Required |
|---|---|---|---|
| HEIC/HEIF | .heic .heif .hif | pillow-heif | Yes |
| AVIF | .avif | pillow-heif | Yes |
| WebP | .webp | Pillow | Yes |
| TIFF | .tif .tiff | Pillow | Yes |
| BMP | .bmp | Pillow | Yes |
| JPEG 2000 | .jp2 .j2k .jpx | Pillow | Yes |
| ICO/CUR | .ico .cur | Pillow | Yes |
| JPEG XL | .jxl | pillow-jxl-plugin | Optional |
| Camera RAW | .cr2 .cr3 .nef .arw .dng .orf .rw2 .raf | rawpy | Optional |
| QOI | .qoi | qoi | Optional |

## Features
- Auto-detect format: JPEG for photos, PNG for transparent images
- **In-place mode**: converts next to the original file and deletes source on success
- EXIF, ICC color profile, and XMP metadata preservation
- Parallel conversion with configurable worker count
- Preserves folder structure in output (optional)
- Name collision handling
- JPEG 4:4:4 chroma subsampling for maximum color fidelity
- Scan breakdown by format family
- Startup log shows which optional formats are available
- Settings persistence via QSettings
- Embedded log panel, stats dashboard
- Cancel support mid-conversion

## Architecture
- `_bootstrap()` auto-installs required + optional deps
- `get_supported_extensions()` dynamically builds extension set based on available deps
- `_open_image()` routes to correct decoder: rawpy for RAW, qoi for QOI, Pillow+plugins for everything else
- `convert_file()` is thread-safe; `in_place=True` saves to source dir and deletes original
- `ScanWorker(QThread)` scans in background
- `ConvertWorker(QThread)` manages ThreadPoolExecutor for parallel conversion
- GUI updates via pyqtSignal

## Version
- v2.0.0 — Universal converter: add AVIF, WebP, JPEG XL, Camera RAW, TIFF, BMP, JP2, QOI, ICO support
- v1.1.0 — Add in-place conversion mode (convert next to source, delete HEIC)
- v1.0.0 — Initial release

## Gotchas
- iPhone HEIC files use Display P3 ICC profiles — passed through to output for correct color
- JPEG cannot store transparency — auto mode falls back to PNG when alpha detected
- pillow-heif on Windows uses bundled libheif; no system install needed
- RAW files: metadata (EXIF) not preserved — rawpy does a full demosaic, no EXIF passthrough
- QOI files: no metadata to preserve (format doesn't support it)
- Optional deps fail gracefully — those formats are excluded from scanning, logged on startup
