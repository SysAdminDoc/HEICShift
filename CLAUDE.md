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

## CI/CD
- `.github/workflows/build.yml` — PyInstaller builds (Windows/macOS/Linux)
- Trigger via `workflow_dispatch`, optional version input creates a GitHub release

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
- **Drag & drop**: drop a folder onto the window to set source directory
- **Format filter**: per-family checkboxes to include/exclude input formats from scanning
- **Skip existing**: resume interrupted batches by skipping files with existing output
- **EXIF auto-rotate**: applies orientation from EXIF before saving (prevents double-rotation)
- **Image resize**: Max Dimension (px) or Scale (%) with LANCZOS resampling
- **Output filename prefix/suffix**: prepend/append text to output filenames
- **Progressive JPEG**: optional progressive encoding for web-optimized JPEGs
- **Lossless WebP**: optional lossless mode for WebP output
- **Recent directories**: dropdown of last 10 source directories for quick access
- EXIF, ICC color profile, and XMP metadata preservation
- Parallel conversion with configurable worker count
- Preserves folder structure in output (optional)
- Name collision handling
- JPEG 4:4:4 chroma subsampling for maximum color fidelity
- Scan breakdown by format family
- Progress bar shows current filename + ETA
- System tray notification on batch completion
- Export log to file / Clear log buttons
- Startup log shows which optional formats are available
- Settings persistence via QSettings (including format filter state)
- Embedded log panel, stats dashboard (with skipped count)
- Cancel support mid-conversion
- Cross-platform file manager open (Windows/macOS/Linux)
- Dark-themed scrollbars matching Catppuccin Mocha
- App icon generated programmatically

## Architecture
- `_bootstrap()` auto-installs required + optional deps
- `FORMAT_FAMILIES` dict maps family name → (extension set, availability flag)
- `get_supported_extensions()` dynamically builds extension set based on available deps
- `_open_image()` routes to correct decoder: rawpy for RAW, qoi for QOI, Pillow+plugins for everything else
- `convert_file()` is thread-safe; supports `in_place`, `skip_existing`, `resize_mode`/`resize_value`, `prefix`/`suffix`, `lossless_webp`, `progressive_jpeg`
- `ScanWorker(QThread)` scans in background, accepts filtered extension set
- `ConvertWorker(QThread)` manages ThreadPoolExecutor for parallel conversion, emits `current_file` signal
- GUI updates via pyqtSignal
- `_open_path()` cross-platform folder opener (os.startfile / open / xdg-open)
- `_create_app_icon()` generates window/tray icon via QPainter

## Version
- v2.2.0 — Image resize, filename prefix/suffix, progressive JPEG, lossless WebP, recent directories dropdown, dark scrollbar theming
- v2.1.0 — Drag & drop, format filter, skip existing, EXIF auto-rotate, ETA progress, tray notifications, log export/clear, cross-platform open, PyInstaller CI/CD
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
- EXIF auto-rotate uses `ImageOps.exif_transpose()` — refreshes EXIF bytes from transposed image to strip orientation tag
- Format filter state persisted as JSON in QSettings
