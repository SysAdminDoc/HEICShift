# HEICShift

## Overview
Universal image batch converter with PyQt6 GUI. Scans directories recursively and converts JPEG, PNG, HEIC, AVIF, WebP, JPEG XL, Camera RAW, TIFF, BMP, JPEG 2000, QOI, and ICO/CUR files to JPEG, PNG, WebP, AVIF, TIFF, or JPEG XL with full metadata preservation.

## Tech Stack
- **Language**: Python 3.10+
- **GUI**: PyQt6 (Fusion style, Catppuccin Mocha theme)
- **CLI**: argparse (headless mode via `--input` flag)
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
# GUI mode
python heicshift.py

# CLI mode
python heicshift.py --input ./photos --format jpeg --quality 85
python heicshift.py --input ./photos --dry-run
python heicshift.py --version

# Required deps auto-install: Pillow, pillow-heif, PyQt6
# Optional deps auto-install: rawpy, pillow-jxl-plugin, qoi
```

## CI/CD
- `.github/workflows/build.yml` — PyInstaller builds (Windows/macOS/Linux)
- Trigger via `workflow_dispatch`, optional version input creates a GitHub release

## Supported Input Formats
| Format | Extensions | Decoder | Required |
|---|---|---|---|
| JPEG | .jpg .jpeg .jpe .jfif | Pillow | Yes |
| PNG | .png | Pillow | Yes |
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
- **JPEG/PNG as input**: convert between any supported formats (JPEG->WebP, PNG->JPEG, etc.); same-format no-op auto-skipped unless resize/sRGB/strip-metadata is active
- **AVIF output**: AVIF encoding via Pillow's native AV1 codec with quality slider
- **JPEG XL output**: JPEG XL encoding via pillow-jxl-plugin with quality slider and effort=7 (conditional on plugin)
- **CLI mode**: headless conversion via `--input` flag with full feature parity (all GUI options exposed as flags)
- **In-place mode**: converts next to the original file and deletes source on success
- **Atomic writes**: in-place mode uses temp file + `os.replace()` for crash-safe conversion
- **Output validation**: verifies output exists, has size > 0, passes `Image.verify()` before accepting
- **Disk space pre-check**: blocks conversion if output exceeds available space, warns at 80%
- **Strip metadata**: option to remove all EXIF/ICC/XMP from output (mutually exclusive with preserve)
- **Auto-open output folder**: optional auto-open on conversion completion
- **File count in title bar**: shows file count after scan, progress during conversion, summary on done
- **Resize upscaling guard**: warns when image is already smaller than resize target
- **Better error logging**: `ConvertResult.warnings` field, `[WARN]` log lines for sRGB failures, RAW metadata, resize skips
- **Stats color reset**: stat label colors reset to green on new batch start
- **Dependency version logging**: Pillow/pillow-heif/PyQt6 + optional dep versions on startup
- **CSV export**: structured conversion report with per-file status, sizes, timing, warnings
- **Drag & drop**: drop folders or individual image files onto the window
- **Format filter**: per-family checkboxes to include/exclude input formats from scanning
- **Skip existing**: resume interrupted batches by skipping files with existing output
- **EXIF auto-rotate**: applies orientation from EXIF before saving (prevents double-rotation)
- **Image resize**: Max Dimension (px) or Scale (%) with LANCZOS resampling
- **Output filename prefix/suffix**: prepend/append text to output filenames
- **Progressive JPEG**: optional progressive encoding for web-optimized JPEGs
- **Lossless WebP**: optional lossless mode for WebP output
- **Recent directories**: dropdown of last 10 source directories for quick access
- **JPEG chroma subsampling toggle**: switch between 4:4:4 (default) and 4:2:0 for smaller files
- **sRGB color space conversion**: convert embedded ICC profiles (e.g. Display P3) to sRGB
- **TIFF compression**: None / LZW / Deflate for TIFF output
- **PNG compression level**: adjustable 1–9 (default 6)
- **Conversion presets**: Web Optimized, Archive Quality, Mobile Friendly, Print/TIFF one-click presets
- **Smart option visibility**: format-specific controls auto-show/hide based on output format selection
- **Dark title bar**: native dark title bar on Windows 10/11
- **Conversion speed stats**: elapsed time + files/sec in status bar during conversion
- **Log context menu**: right-click log for Copy Selection, Copy All, Open File Location
- **Source/output overlap guard**: blocks conversion when output dir equals source dir
- **Completion sound**: platform-specific notification sound on batch finish
- **Drag & drop hover visual**: lavender border highlight on source input during drag hover
- **Output format tooltips**: descriptive tooltips on each output format option
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
- `convert_file()` is thread-safe; atomic writes via temp file + `os.replace()` for in-place mode; post-save validation via `Image.verify()`; `ConvertResult.warnings` list for non-fatal issues; supports `in_place`, `skip_existing`, `resize_mode`/`resize_value`, `prefix`/`suffix`, `lossless_webp`, `progressive_jpeg`, `chroma_subsampling`, `convert_to_srgb`, `tiff_compression`, `png_compress_level`
- `PRESETS` dict — built-in conversion presets (Web Optimized, Archive Quality, Mobile Friendly, Print/TIFF)
- `SIZE_ESTIMATE_FACTORS` / `_estimate_output_size()` — per-format disk space estimation
- `_build_parser()` — argparse CLI, `_run_cli()` — headless conversion with ThreadPoolExecutor
- `_log_dep_versions_cli()` — prints dependency versions to stdout for CLI mode
- `_update_title()` — dynamic window title with file count / conversion progress / done summary
- `_apply_dark_titlebar()` — uses DwmSetWindowAttribute for native dark title bar on Windows
- `_on_log_context_menu()` — right-click menu for log panel with copy and open file location
- `_export_csv()` — CSV report export of conversion results
- `ScanWorker(QThread)` scans in background, accepts filtered extension set
- `ConvertWorker(QThread)` manages ThreadPoolExecutor for parallel conversion, emits `current_file` signal
- GUI updates via pyqtSignal
- `_open_path()` cross-platform folder opener (os.startfile / open / xdg-open)
- `_create_app_icon()` generates window/tray icon via QPainter

## Version
- v2.8.0 — XMP metadata passthrough for AVIF/JXL output, UI scaling (QScrollArea + QSplitter, reduced minimum size 700x520, column stretch for grid layouts), removed rigid pixel constraints (setMaximumWidth/setFixedHeight/setFixedWidth), lossless WebP checkbox hidden in Auto mode, resize mode preserves user values, format index bounds check on settings restore, QSizePolicy import removed
- v2.7.0 — JPEG XL output format (pillow-jxl-plugin, conditional), CLI full parity (--tiff-compression, --png-level, --resize scale:VALUE), CLI progress counters + wall-clock time + files/sec, sorted scan results
- v2.6.0 — AVIF output format (Pillow native AV1), CSV conversion report export, drag & drop individual files, CLI parity (--skip-existing, --progressive, --chroma-420, --lossless, --srgb, --prefix, --suffix, --no-structure), wall-clock time in done summary
- v2.5.1 — JPEG/PNG input support (universal converter), same-format no-op skip guard
- v2.5.0 — CLI mode (headless conversion), disk space pre-check, strip metadata option, auto-open output folder, file count in title bar, resize upscaling guard, better error logging (warnings), stats color reset, dependency version logging
- v2.4.0 — Atomic writes for in-place mode, output file validation, dark title bar, conversion presets, smart format-dependent option visibility, log context menu, source/output overlap guard, elapsed time + speed stats
- v2.3.0 — Memory safety (try/finally in convert_file), drag & drop hover visual, completion sound, JPEG chroma subsampling toggle, sRGB color space conversion, TIFF compression, PNG compression level, output format tooltips
- v2.2.0 — Image resize, filename prefix/suffix, progressive JPEG, lossless WebP, recent directories dropdown, dark scrollbar theming
- v2.1.0 — Drag & drop, format filter, skip existing, EXIF auto-rotate, ETA progress, tray notifications, log export/clear, cross-platform open, PyInstaller CI/CD
- v2.0.0 — Universal converter: add AVIF, WebP, JPEG XL, Camera RAW, TIFF, BMP, JP2, QOI, ICO support
- v1.1.0 — Add in-place conversion mode (convert next to source, delete HEIC)
- v1.0.0 — Initial release

## Gotchas
- iPhone HEIC files use Display P3 ICC profiles — passed through to output for correct color (or converted to sRGB with the new toggle)
- JPEG cannot store transparency — auto mode falls back to PNG when alpha detected
- pillow-heif on Windows uses bundled libheif; no system install needed
- RAW files: metadata (EXIF) not preserved — rawpy does a full demosaic, no EXIF passthrough
- QOI files: no metadata to preserve (format doesn't support it)
- Optional deps fail gracefully — those formats are excluded from scanning, logged on startup
- EXIF auto-rotate uses `ImageOps.exif_transpose()` — refreshes EXIF bytes from transposed image to strip orientation tag
- Format filter state persisted as JSON in QSettings
- Atomic writes use `.heicshift.tmp` suffix — temp files cleaned on failure, absent on success
- Source/output overlap guard blocks exact same dir but warns (not blocks) for subdirs since `source/converted` is the default pattern
- AVIF output requires Pillow 11+ (native AV1 support) — auto-installed by bootstrap
- AVIF encoding quality defaults use same slider as JPEG/WebP (50-100), speed=6 (balanced)
- JPEG XL output: quality maps to pillow-jxl-plugin `quality` param (1-100), effort=7 (good compression/speed tradeoff)
- JPEG XL combo item disabled in GUI when pillow-jxl-plugin not installed; CLI exits with error code 2
- Controls above the log panel are wrapped in QScrollArea — scrollable on small screens (720p/768p)
- QSplitter between controls and log panel — user can drag the divider
- Minimum window size is 700x520 (was 780x700); QScrollArea handles overflow
- opt_grid and filter_layout have column stretch for proportional sizing on wide monitors
- No rigid pixel constraints on prefix/suffix/tiff/png controls or log buttons
