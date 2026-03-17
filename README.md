# HEICShift

High-performance HEIC/HEIF batch converter with a modern GUI. Scans directories recursively and converts to JPEG, PNG, WebP, or TIFF with full metadata preservation.

![Python 3.10+](https://img.shields.io/badge/Python-3.10+-3776AB?logo=python&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-blue)

## Why HEICShift?

Most HEIC converters get the details wrong — they strip metadata, mangle colors by dropping ICC profiles, or use lossy 4:2:0 chroma subsampling by default. HEICShift is built on research into what existing tools do poorly:

| Problem | Other Tools | HEICShift |
|---|---|---|
| **Color accuracy** | ImageMagick strips ICC profiles with `-strip`, causing Display P3 → sRGB color shift | Passes ICC profiles through to output — colors stay accurate |
| **Chroma subsampling** | Most default to 4:2:0 (halves color resolution) | Uses 4:4:4 — full color fidelity |
| **Format selection** | Force you to pick JPEG or PNG for everything | Auto-detects: JPEG for photos, PNG only when transparency exists |
| **Metadata** | Online converters and many CLI tools strip EXIF/GPS/timestamps | Preserves EXIF, ICC, and XMP data by default |
| **Performance** | Single-threaded or limited concurrency | Parallel conversion with configurable worker count (up to 32) |
| **HDR awareness** | Silently discard HDR gain maps without warning | Converts SDR base correctly; documents HDR limitations |

## Features

- **Auto format detection** — JPEG for photos, PNG when alpha channel is present
- **5 output formats** — Auto, JPEG, PNG, WebP, TIFF
- **Metadata preservation** — EXIF, ICC color profiles, XMP
- **Parallel conversion** — 1–32 workers via ThreadPoolExecutor
- **Recursive scanning** — processes entire directory trees
- **Folder structure preservation** — mirrors source layout in output (optional)
- **Quality control** — adjustable slider (50–100) for JPEG/WebP
- **Live stats** — files found, total size, converted, failed, space saved
- **Embedded log** — per-file results with timing and size delta
- **Cancel support** — stop mid-conversion without corrupting output
- **Settings persistence** — remembers paths, format, quality, workers across sessions
- **Catppuccin Mocha dark theme**

## Installation

```bash
git clone https://github.com/SysAdminDoc/HEICShift.git
cd HEICShift
python heicshift.py
```

Dependencies (`Pillow`, `pillow-heif`, `PyQt6`) install automatically on first launch.

## Usage

1. **Browse** to a directory containing `.heic` / `.heif` files
2. **Scan** to discover all HEIC files (recursive by default)
3. **Adjust settings** — format, quality, workers, metadata toggle
4. **Convert All** — output goes to `source/converted/` by default

The log panel shows per-file results with size before/after and conversion time.

## Supported Formats

| Input | Output |
|---|---|
| `.heic`, `.heif`, `.hif` | `.jpg`, `.png`, `.webp`, `.tiff` |

## How It Works

```
Source Directory          HEICShift                    Output
 photos/                   pillow-heif decoder           converted/
  ├─ IMG_001.heic   ──→   Pillow processing      ──→    ├─ IMG_001.jpg
  ├─ IMG_002.HEIF   ──→   EXIF/ICC passthrough   ──→    ├─ IMG_002.jpg
  └─ screenshots/          ThreadPoolExecutor             └─ screenshots/
      └─ shot.heic  ──→   Alpha? → PNG, else JPEG ──→       └─ shot.png
```

## Tech Stack

- **[pillow-heif](https://github.com/bigcat88/pillow_heif)** — HEIC/HEIF decoding with full metadata support
- **[Pillow](https://python-pillow.org/)** — image processing and format output
- **[PyQt6](https://www.riverbankcomputing.com/software/pyqt/)** — GUI framework
- **ThreadPoolExecutor** — parallel file conversion

## Known Limitations

- HDR gain maps embedded in HEIC files are lost during conversion (no JPEG/PNG equivalent exists). For HDR workflows, keep originals.
- Apple Live Photo motion data and depth maps cannot be preserved in any static format.
- HEIC files with odd pixel dimensions may produce artifacts in some downstream decoders — this is a libheif/codec limitation, not a HEICShift issue.

## License

MIT
