# HEICShift

Universal image batch converter with a modern GUI. Scans directories recursively and converts HEIC, AVIF, WebP, JPEG XL, Camera RAW, TIFF, BMP, JPEG 2000, QOI, and ICO files to JPEG, PNG, WebP, or TIFF with full metadata preservation.

![Python 3.10+](https://img.shields.io/badge/Python-3.10+-3776AB?logo=python&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-blue)

## Why HEICShift?

Most image converters get the details wrong — they strip metadata, mangle colors by dropping ICC profiles, or use lossy 4:2:0 chroma subsampling by default. HEICShift is built on research into what existing tools do poorly:

| Problem | Other Tools | HEICShift |
|---|---|---|
| **Color accuracy** | ImageMagick strips ICC profiles with `-strip`, causing Display P3 → sRGB color shift | Passes ICC profiles through to output — colors stay accurate |
| **Chroma subsampling** | Most default to 4:2:0 (halves color resolution) | Uses 4:4:4 — full color fidelity |
| **Format selection** | Force you to pick JPEG or PNG for everything | Auto-detects: JPEG for photos, PNG only when transparency exists |
| **Metadata** | Online converters and many CLI tools strip EXIF/GPS/timestamps | Preserves EXIF, ICC, and XMP data by default |
| **Performance** | Single-threaded or limited concurrency | Parallel conversion with configurable worker count (up to 32) |
| **Format coverage** | Most only handle HEIC or one format at a time | 10+ input format families from a single tool |

## Supported Input Formats

| Format | Extensions | Decoder | Install |
|---|---|---|---|
| HEIC/HEIF | `.heic` `.heif` `.hif` | pillow-heif | Auto |
| AVIF | `.avif` | pillow-heif | Auto |
| WebP | `.webp` | Pillow | Auto |
| TIFF | `.tif` `.tiff` | Pillow | Auto |
| BMP | `.bmp` | Pillow | Auto |
| JPEG 2000 | `.jp2` `.j2k` `.jpx` | Pillow | Auto |
| ICO/CUR | `.ico` `.cur` | Pillow | Auto |
| JPEG XL | `.jxl` | pillow-jxl-plugin | Auto (optional) |
| Camera RAW | `.cr2` `.cr3` `.nef` `.arw` `.dng` `.orf` `.rw2` `.raf` | rawpy/libraw | Auto (optional) |
| QOI | `.qoi` | qoi | Auto (optional) |

**Output formats:** JPEG, PNG, WebP, TIFF

Optional decoders are installed automatically on first launch. If installation fails (e.g. no compiler for rawpy), those formats are skipped gracefully and the app logs which are unavailable.

## Features

- **Auto format detection** — JPEG for photos, PNG when alpha channel is present
- **10+ input formats** — HEIC, AVIF, WebP, JXL, RAW, TIFF, BMP, JP2, QOI, ICO
- **CLI mode** — headless conversion via `--input` flag for scripting and automation
- **In-place conversion** — convert next to the original and delete the source file
- **Atomic writes** — in-place mode uses temp file + atomic rename for crash-safe conversion
- **Output validation** — verifies file exists, size > 0, and passes integrity check before accepting
- **Disk space pre-check** — blocks conversion if estimated output exceeds available space, warns at 80%
- **Strip metadata** — option to remove all EXIF/ICC/XMP from output files
- **Auto-open output folder** — automatically opens the output folder when conversion finishes
- **File count in title bar** — shows file count after scan, progress during conversion, summary when done
- **Resize upscaling guard** — warns when image is already smaller than the resize target
- **Conversion presets** — Web Optimized, Archive Quality, Mobile Friendly, Print/TIFF one-click presets
- **Smart option visibility** — format-specific controls auto-show/hide based on output format
- **Dark title bar** — native dark title bar on Windows 10/11 matching Catppuccin theme
- **Conversion speed stats** — elapsed time + files/sec displayed in status bar during conversion
- **Log context menu** — right-click for Copy Selection, Copy All, Open File Location
- **Source/output overlap guard** — prevents output directory from overwriting source files
- **Drag & drop** — drop a folder onto the window to set the source directory
- **Format filter** — per-family checkboxes to include or exclude input formats from scanning
- **Skip existing** — resume interrupted batches by skipping files where output already exists
- **EXIF auto-rotate** — applies orientation from EXIF metadata before saving (prevents double-rotation)
- **Image resize** — Max Dimension (px) or Scale (%) with LANCZOS resampling
- **Filename prefix/suffix** — prepend or append text to output filenames
- **Progressive JPEG** — optional progressive encoding for web-optimized output
- **Lossless WebP** — optional lossless mode when WebP is selected as output
- **JPEG chroma subsampling** — toggle between 4:4:4 (default, max fidelity) and 4:2:0 (smaller files)
- **sRGB color conversion** — convert embedded ICC profiles (Display P3, Adobe RGB, etc.) to sRGB
- **TIFF compression** — None, LZW, or Deflate when TIFF output is selected
- **PNG compression level** — adjustable 1–9 for PNG output (default 6)
- **Recent directories** — dropdown of last 10 source directories for quick re-access
- **Metadata preservation** — EXIF, ICC color profiles, XMP
- **Parallel conversion** — 1–32 workers via ThreadPoolExecutor
- **Recursive scanning** — processes entire directory trees
- **Folder structure preservation** — mirrors source layout in output (optional)
- **Quality control** — adjustable slider (50–100) for JPEG/WebP
- **Scan breakdown** — shows count per format family after scanning
- **Live stats** — files found, total size, converted, skipped, failed, space saved
- **Progress ETA** — shows current filename and estimated time remaining
- **Completion notification** — system tray balloon + notification sound when batch finishes
- **Embedded log** — per-file results with timing and size delta, export to file or clear
- **Cancel support** — stop mid-conversion without corrupting output
- **Settings persistence** — remembers all settings including format filter state across sessions
- **Catppuccin Mocha dark theme** — including dark scrollbars and dark title bar
- **Cross-platform** — native file manager integration on Windows, macOS, and Linux

## Installation

```bash
git clone https://github.com/SysAdminDoc/HEICShift.git
cd HEICShift
python heicshift.py
```

All dependencies install automatically on first launch. No manual setup.

## Usage

1. **Browse** or **drag & drop** a directory containing image files
2. **Filter** which input formats to include (optional — all enabled by default)
3. **Scan** to discover all supported files (recursive by default)
4. **Adjust settings** — format, quality, workers, metadata toggle
5. **Convert All** — output goes to `source/converted/` by default

Toggle **"Convert in place"** to save output next to each source file and delete the original.

Enable **"Skip files that already have output"** to resume interrupted batches without re-converting.

The log panel shows per-file results with size before/after and conversion time. Logs can be exported to a text file.

## CLI Usage

Run HEICShift from the command line for scripted or headless operation. If `--input` is provided, the GUI is skipped entirely.

```bash
# Convert a directory to JPEG at quality 85
python heicshift.py --input ./photos --format jpeg --quality 85

# Convert to WebP with 4 workers, output to specific folder
python heicshift.py -i ./photos -o ./output -f webp -w 4

# Dry run — list files that would be converted
python heicshift.py --input ./photos --dry-run

# In-place conversion (saves next to originals, deletes source)
python heicshift.py --input ./photos --in-place

# Strip metadata and resize
python heicshift.py --input ./photos --strip-metadata --resize max_dim:1920

# Print version
python heicshift.py --version
```

**CLI flags:**

| Flag | Description |
|---|---|
| `-i`, `--input` | Source directory (enables CLI mode) |
| `-o`, `--output` | Output directory (default: `<input>/converted`) |
| `-f`, `--format` | Output format: `auto`, `jpeg`, `png`, `webp`, `tiff` |
| `-q`, `--quality` | JPEG/WebP quality 50–100 (default: 92) |
| `-w`, `--workers` | Parallel worker count (default: min(cpu_count, 8)) |
| `--in-place` | Convert next to originals, delete source |
| `--recursive` | Scan subdirectories (default) |
| `--no-recursive` | Only scan top-level directory |
| `--dry-run` | List files and exit without converting |
| `--strip-metadata` | Remove all EXIF/ICC/XMP from output |
| `--resize` | Resize by max dimension, e.g. `max_dim:1920` |
| `--version` | Print version and exit |

**Exit codes:** 0 = all OK, 1 = partial failure, 2 = total failure or bad input.

## How It Works

```
Source Directory          HEICShift                    Output
 photos/                                                converted/
  ├─ IMG_001.heic   ──→  pillow-heif decoder    ──→    ├─ IMG_001.jpg
  ├─ IMG_002.avif   ──→  Pillow processing      ──→    ├─ IMG_002.jpg
  ├─ shot.webp      ──→  EXIF/ICC passthrough   ──→    ├─ shot.jpg
  ├─ photo.cr2      ──→  rawpy demosaic         ──→    ├─ photo.jpg
  └─ render.qoi     ──→  qoi decoder            ──→    └─ render.jpg
```

## Tech Stack

- **[pillow-heif](https://github.com/bigcat88/pillow_heif)** — HEIC/HEIF/AVIF decoding
- **[pillow-jxl-plugin](https://github.com/niclas-niclas/pillow-jxl-plugin)** — JPEG XL decoding (optional)
- **[rawpy](https://github.com/letmaik/rawpy)** — Camera RAW demosaicing via libraw (optional)
- **[qoi](https://github.com/kodonnell/qoi)** — QOI format decoding (optional)
- **[Pillow](https://python-pillow.org/)** — image processing, WebP/TIFF/BMP/JP2/ICO decoding, output encoding
- **[PyQt6](https://www.riverbankcomputing.com/software/pyqt/)** — GUI framework

## Known Limitations

- **HDR gain maps** in HEIC files are lost during conversion (no JPEG/PNG equivalent). Keep originals for HDR workflows.
- **Apple Live Photo** motion data and depth maps cannot be preserved in any static format.
- **Camera RAW metadata** — rawpy performs a full demosaic; EXIF is not carried through. Use ExifTool as a post-pass if needed.
- **QOI** has no metadata support by design — nothing to preserve.
- **HEIC odd dimensions** may produce artifacts in some downstream decoders (libheif/codec limitation).

## License

MIT
