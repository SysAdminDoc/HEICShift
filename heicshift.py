"""
HEICShift v1.1.0 - High-performance HEIC batch converter
Scans directories recursively and converts .HEIC/.HEIF files to JPEG or PNG.
Auto-detects optimal format: PNG for images with transparency, JPEG for photos.
Preserves EXIF metadata, ICC color profiles, and XMP data.
"""

import sys, os, subprocess, importlib

APP_VERSION = "1.1.0"

def _bootstrap():
    """Auto-install dependencies before imports."""
    required = {
        "PIL": "Pillow",
        "pillow_heif": "pillow-heif",
        "PyQt6": "PyQt6",
    }
    for module, package in required.items():
        try:
            importlib.import_module(module)
        except ImportError:
            for cmd_extra in [[], ["--user"], ["--break-system-packages"]]:
                try:
                    subprocess.check_call(
                        [sys.executable, "-m", "pip", "install", package, "-q"] + cmd_extra,
                        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                    )
                    break
                except subprocess.CalledProcessError:
                    continue

_bootstrap()

import time
import json
import traceback
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field

from PIL import Image, ImageCms
from pillow_heif import register_heif_opener

register_heif_opener()

from PyQt6.QtCore import (
    Qt, QThread, pyqtSignal, QTimer, QSettings, QSize,
)
from PyQt6.QtGui import (
    QFont, QColor, QPalette, QIcon, QPixmap, QPainter, QAction,
)
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QFileDialog, QComboBox, QSpinBox, QSlider,
    QProgressBar, QPlainTextEdit, QCheckBox, QGroupBox, QGridLayout,
    QFrame, QSplitter, QStatusBar, QMessageBox, QLineEdit, QStyle,
    QSizePolicy, QSystemTrayIcon,
)

# ── Catppuccin Mocha Palette ──────────────────────────────────────────────────
CAT = {
    "base":      "#1e1e2e", "mantle":   "#181825", "crust":    "#11111b",
    "surface0":  "#313244", "surface1": "#45475a", "surface2": "#585b70",
    "overlay0":  "#6c7086", "overlay1": "#7f849c",
    "text":      "#cdd6f4", "subtext0": "#a6adc8", "subtext1": "#bac2de",
    "lavender":  "#b4befe", "blue":     "#89b4fa", "sapphire": "#74c7ec",
    "sky":       "#89dceb", "teal":     "#94e2d5", "green":    "#a6e3a1",
    "yellow":    "#f9e2af", "peach":    "#fab387", "maroon":   "#eba0ac",
    "red":       "#f38ba8", "mauve":    "#cba6f7", "pink":     "#f5c2e7",
    "flamingo":  "#f2cdcd", "rosewater":"#f5e0dc",
}

STYLESHEET = f"""
QMainWindow, QWidget {{
    background-color: {CAT['base']};
    color: {CAT['text']};
    font-family: 'Segoe UI', 'Inter', sans-serif;
    font-size: 13px;
}}
QGroupBox {{
    background-color: {CAT['mantle']};
    border: 1px solid {CAT['surface1']};
    border-radius: 8px;
    margin-top: 14px;
    padding: 16px 12px 12px 12px;
    font-weight: 600;
    font-size: 13px;
    color: {CAT['lavender']};
}}
QGroupBox::title {{
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 2px 10px;
    background-color: {CAT['mantle']};
    border-radius: 4px;
}}
QPushButton {{
    background-color: {CAT['surface0']};
    color: {CAT['text']};
    border: 1px solid {CAT['surface1']};
    border-radius: 6px;
    padding: 7px 18px;
    font-weight: 500;
    min-height: 20px;
}}
QPushButton:hover {{
    background-color: {CAT['surface1']};
    border-color: {CAT['lavender']};
}}
QPushButton:pressed {{
    background-color: {CAT['surface2']};
}}
QPushButton:disabled {{
    background-color: {CAT['crust']};
    color: {CAT['overlay0']};
    border-color: {CAT['surface0']};
}}
QPushButton#primaryBtn {{
    background-color: {CAT['blue']};
    color: {CAT['crust']};
    border: none;
    font-weight: 700;
    font-size: 14px;
    padding: 10px 28px;
}}
QPushButton#primaryBtn:hover {{
    background-color: {CAT['lavender']};
}}
QPushButton#primaryBtn:disabled {{
    background-color: {CAT['surface1']};
    color: {CAT['overlay0']};
}}
QPushButton#stopBtn {{
    background-color: {CAT['red']};
    color: {CAT['crust']};
    border: none;
    font-weight: 700;
}}
QPushButton#stopBtn:hover {{
    background-color: {CAT['maroon']};
}}
QLineEdit {{
    background-color: {CAT['surface0']};
    color: {CAT['text']};
    border: 1px solid {CAT['surface1']};
    border-radius: 6px;
    padding: 6px 10px;
    selection-background-color: {CAT['blue']};
}}
QLineEdit:focus {{
    border-color: {CAT['lavender']};
}}
QComboBox {{
    background-color: {CAT['surface0']};
    color: {CAT['text']};
    border: 1px solid {CAT['surface1']};
    border-radius: 6px;
    padding: 6px 10px;
    min-width: 120px;
}}
QComboBox:hover {{
    border-color: {CAT['lavender']};
}}
QComboBox::drop-down {{
    border: none;
    width: 24px;
}}
QComboBox QAbstractItemView {{
    background-color: {CAT['surface0']};
    color: {CAT['text']};
    border: 1px solid {CAT['surface1']};
    selection-background-color: {CAT['surface1']};
    selection-color: {CAT['lavender']};
}}
QSpinBox {{
    background-color: {CAT['surface0']};
    color: {CAT['text']};
    border: 1px solid {CAT['surface1']};
    border-radius: 6px;
    padding: 4px 8px;
}}
QSlider::groove:horizontal {{
    background: {CAT['surface0']};
    height: 6px;
    border-radius: 3px;
}}
QSlider::handle:horizontal {{
    background: {CAT['lavender']};
    width: 16px;
    height: 16px;
    margin: -5px 0;
    border-radius: 8px;
}}
QSlider::sub-page:horizontal {{
    background: {CAT['blue']};
    border-radius: 3px;
}}
QProgressBar {{
    background-color: {CAT['surface0']};
    border: 1px solid {CAT['surface1']};
    border-radius: 6px;
    text-align: center;
    color: {CAT['text']};
    font-weight: 600;
    min-height: 22px;
}}
QProgressBar::chunk {{
    background-color: {CAT['green']};
    border-radius: 5px;
}}
QPlainTextEdit {{
    background-color: {CAT['crust']};
    color: {CAT['subtext0']};
    border: 1px solid {CAT['surface0']};
    border-radius: 6px;
    padding: 8px;
    font-family: 'Cascadia Code', 'Consolas', monospace;
    font-size: 12px;
    selection-background-color: {CAT['surface1']};
}}
QCheckBox {{
    spacing: 8px;
    color: {CAT['text']};
}}
QCheckBox::indicator {{
    width: 18px;
    height: 18px;
    border-radius: 4px;
    border: 2px solid {CAT['surface2']};
    background-color: {CAT['surface0']};
}}
QCheckBox::indicator:checked {{
    background-color: {CAT['blue']};
    border-color: {CAT['blue']};
}}
QLabel#dimLabel {{
    color: {CAT['overlay1']};
    font-size: 12px;
}}
QLabel#statValue {{
    color: {CAT['green']};
    font-size: 22px;
    font-weight: 700;
}}
QLabel#statLabel {{
    color: {CAT['overlay1']};
    font-size: 11px;
}}
QStatusBar {{
    background-color: {CAT['mantle']};
    color: {CAT['subtext0']};
    border-top: 1px solid {CAT['surface0']};
    font-size: 12px;
}}
QFrame#separator {{
    background-color: {CAT['surface1']};
    max-height: 1px;
}}
"""


# ── Data ──────────────────────────────────────────────────────────────────────

@dataclass
class ConvertResult:
    src: Path
    dst: Path | None = None
    success: bool = False
    error: str = ""
    size_before: int = 0
    size_after: int = 0
    elapsed: float = 0.0
    src_deleted: bool = False

@dataclass
class ScanResult:
    files: list[Path] = field(default_factory=list)
    total_size: int = 0
    elapsed: float = 0.0


# ── Conversion Engine ─────────────────────────────────────────────────────────

HEIC_EXTENSIONS = {".heic", ".heif", ".hif"}

def scan_directory(root: Path, recursive: bool = True) -> ScanResult:
    """Find all HEIC/HEIF files in directory."""
    t0 = time.perf_counter()
    result = ScanResult()
    pattern = "**/*" if recursive else "*"
    for p in root.glob(pattern):
        if p.is_file() and p.suffix.lower() in HEIC_EXTENSIONS:
            result.files.append(p)
            result.total_size += p.stat().st_size
    result.elapsed = time.perf_counter() - t0
    return result


def has_transparency(img: Image.Image) -> bool:
    """Check if image has actual transparency data."""
    if img.mode in ("RGBA", "LA", "PA"):
        alpha = img.getchannel("A")
        extrema = alpha.getextrema()
        return extrema[0] < 255  # has non-opaque pixels
    return False


def convert_file(
    src: Path,
    output_dir: Path,
    fmt: str = "auto",
    jpeg_quality: int = 92,
    preserve_metadata: bool = True,
    preserve_structure: bool = False,
    base_dir: Path | None = None,
    in_place: bool = False,
) -> ConvertResult:
    """Convert a single HEIC file. Thread-safe."""
    t0 = time.perf_counter()
    result = ConvertResult(src=src, size_before=src.stat().st_size)

    try:
        img = Image.open(str(src))

        # Determine output format
        if fmt == "auto":
            out_fmt = "PNG" if has_transparency(img) else "JPEG"
        elif fmt == "jpeg":
            out_fmt = "JPEG"
        elif fmt == "png":
            out_fmt = "PNG"
        elif fmt == "webp":
            out_fmt = "WEBP"
        elif fmt == "tiff":
            out_fmt = "TIFF"
        else:
            out_fmt = "JPEG"

        ext_map = {"JPEG": ".jpg", "PNG": ".png", "WEBP": ".webp", "TIFF": ".tiff"}
        ext = ext_map.get(out_fmt, ".jpg")

        # Build output path — in-place writes next to the source file
        if in_place:
            dest_dir = src.parent
        elif preserve_structure and base_dir:
            rel = src.parent.relative_to(base_dir)
            dest_dir = output_dir / rel
        else:
            dest_dir = output_dir

        dest_dir.mkdir(parents=True, exist_ok=True)
        out_path = dest_dir / (src.stem + ext)

        # Handle name collisions
        counter = 1
        while out_path.exists():
            out_path = dest_dir / f"{src.stem}_{counter}{ext}"
            counter += 1

        # Gather metadata
        save_kwargs = {}
        if preserve_metadata:
            exif = img.info.get("exif")
            icc = img.info.get("icc_profile")
            xmp = img.info.get("xmp")
            if exif:
                save_kwargs["exif"] = exif
            if icc:
                save_kwargs["icc_profile"] = icc
            if xmp and out_fmt in ("JPEG", "WEBP", "TIFF"):
                save_kwargs["xmp"] = xmp

        # Format-specific options
        if out_fmt == "JPEG":
            if img.mode in ("RGBA", "LA", "PA", "P"):
                img = img.convert("RGB")
            save_kwargs["quality"] = jpeg_quality
            save_kwargs["subsampling"] = 0  # 4:4:4 chroma
            save_kwargs["optimize"] = True
        elif out_fmt == "PNG":
            save_kwargs["optimize"] = True
        elif out_fmt == "WEBP":
            save_kwargs["quality"] = jpeg_quality
            save_kwargs["method"] = 4

        img.save(str(out_path), out_fmt, **save_kwargs)
        img.close()

        result.dst = out_path
        result.size_after = out_path.stat().st_size
        result.success = True

        # In-place mode: delete the original HEIC after successful conversion
        if in_place and result.success:
            src.unlink()
            result.src_deleted = True

    except Exception as e:
        result.error = str(e)

    result.elapsed = time.perf_counter() - t0
    return result


# ── Worker Thread ─────────────────────────────────────────────────────────────

class ConvertWorker(QThread):
    progress = pyqtSignal(int, int)       # current, total
    file_done = pyqtSignal(object)        # ConvertResult
    finished_all = pyqtSignal(list)        # list[ConvertResult]
    log = pyqtSignal(str)

    def __init__(self, files, output_dir, fmt, quality, preserve_meta,
                 preserve_structure, base_dir, workers, in_place=False):
        super().__init__()
        self.files = files
        self.output_dir = Path(output_dir)
        self.fmt = fmt
        self.quality = quality
        self.preserve_meta = preserve_meta
        self.preserve_structure = preserve_structure
        self.base_dir = base_dir
        self.workers = workers
        self.in_place = in_place
        self._stop = False

    def stop(self):
        self._stop = True

    def run(self):
        results = []
        total = len(self.files)
        done = 0

        self.log.emit(f"Starting conversion of {total} files with {self.workers} workers...")

        with ThreadPoolExecutor(max_workers=self.workers) as pool:
            futures = {}
            for f in self.files:
                if self._stop:
                    break
                fut = pool.submit(
                    convert_file, f, self.output_dir, self.fmt,
                    self.quality, self.preserve_meta,
                    self.preserve_structure, self.base_dir,
                    self.in_place,
                )
                futures[fut] = f

            for fut in as_completed(futures):
                if self._stop:
                    pool.shutdown(wait=False, cancel_futures=True)
                    self.log.emit("Conversion cancelled by user.")
                    break

                result = fut.result()
                results.append(result)
                done += 1
                self.progress.emit(done, total)
                self.file_done.emit(result)

                if result.success:
                    saved = result.size_before - result.size_after
                    pct = (saved / result.size_before * 100) if result.size_before else 0
                    deleted_tag = "  [source deleted]" if result.src_deleted else ""
                    self.log.emit(
                        f"[OK] {result.src.name} -> {result.dst.name}  "
                        f"({_fmt_size(result.size_before)} -> {_fmt_size(result.size_after)}, "
                        f"{pct:+.1f}%)  [{result.elapsed:.2f}s]{deleted_tag}"
                    )
                else:
                    self.log.emit(f"[FAIL] {result.src.name}: {result.error}")

        self.finished_all.emit(results)


class ScanWorker(QThread):
    finished = pyqtSignal(object)  # ScanResult
    log = pyqtSignal(str)

    def __init__(self, directory, recursive):
        super().__init__()
        self.directory = Path(directory)
        self.recursive = recursive

    def run(self):
        self.log.emit(f"Scanning {'recursively' if self.recursive else ''}: {self.directory}")
        result = scan_directory(self.directory, self.recursive)
        self.log.emit(
            f"Found {len(result.files)} HEIC files "
            f"({_fmt_size(result.total_size)}) in {result.elapsed:.2f}s"
        )
        self.finished.emit(result)


# ── Helpers ───────────────────────────────────────────────────────────────────

def _fmt_size(b: int) -> str:
    for unit in ("B", "KB", "MB", "GB"):
        if b < 1024:
            return f"{b:.1f} {unit}"
        b /= 1024
    return f"{b:.1f} TB"


# ── Main Window ───────────────────────────────────────────────────────────────

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"HEICShift v{APP_VERSION}")
        self.setMinimumSize(780, 680)
        self.resize(880, 750)

        self.settings = QSettings("HEICShift", "HEICShift")
        self._scan_result: ScanResult | None = None
        self._worker: ConvertWorker | None = None
        self._results: list[ConvertResult] = []

        self._build_ui()
        self._restore_state()

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(16, 12, 16, 8)
        root.setSpacing(10)

        # ── Header ──
        hdr = QHBoxLayout()
        title = QLabel("HEICShift")
        title.setStyleSheet(f"font-size: 20px; font-weight: 800; color: {CAT['lavender']};")
        ver = QLabel(f"v{APP_VERSION}")
        ver.setStyleSheet(f"color: {CAT['overlay0']}; font-size: 12px; margin-left: 6px;")
        hdr.addWidget(title)
        hdr.addWidget(ver)
        hdr.addStretch()
        desc = QLabel("HEIC/HEIF batch converter with metadata preservation")
        desc.setObjectName("dimLabel")
        hdr.addWidget(desc)
        root.addLayout(hdr)

        # ── Source / Output ──
        io_group = QGroupBox("Directories")
        io_grid = QGridLayout(io_group)
        io_grid.setColumnStretch(1, 1)

        io_grid.addWidget(QLabel("Source:"), 0, 0)
        self.src_edit = QLineEdit()
        self.src_edit.setPlaceholderText("Select a directory containing HEIC files...")
        io_grid.addWidget(self.src_edit, 0, 1)
        self.src_btn = QPushButton("Browse")
        self.src_btn.clicked.connect(self._browse_source)
        io_grid.addWidget(self.src_btn, 0, 2)

        io_grid.addWidget(QLabel("Output:"), 1, 0)
        self.dst_edit = QLineEdit()
        self.dst_edit.setPlaceholderText("Converted files go here (default: source/converted)")
        io_grid.addWidget(self.dst_edit, 1, 1)
        self.dst_btn = QPushButton("Browse")
        self.dst_btn.clicked.connect(self._browse_output)
        io_grid.addWidget(self.dst_btn, 1, 2)

        self.recursive_chk = QCheckBox("Scan subdirectories")
        self.recursive_chk.setChecked(True)
        io_grid.addWidget(self.recursive_chk, 2, 1)

        self.structure_chk = QCheckBox("Preserve folder structure in output")
        self.structure_chk.setChecked(True)
        io_grid.addWidget(self.structure_chk, 2, 2)

        self.inplace_chk = QCheckBox("Convert in place (save next to original, delete HEIC)")
        self.inplace_chk.setChecked(False)
        self.inplace_chk.setStyleSheet(f"color: {CAT['peach']};")
        self.inplace_chk.toggled.connect(self._on_inplace_toggled)
        io_grid.addWidget(self.inplace_chk, 3, 1, 1, 2)

        root.addWidget(io_group)

        # ── Conversion Options ──
        opt_group = QGroupBox("Conversion Settings")
        opt_grid = QGridLayout(opt_group)

        opt_grid.addWidget(QLabel("Output Format:"), 0, 0)
        self.fmt_combo = QComboBox()
        self.fmt_combo.addItems([
            "Auto (JPEG for photos, PNG for transparency)",
            "JPEG", "PNG", "WebP", "TIFF"
        ])
        opt_grid.addWidget(self.fmt_combo, 0, 1, 1, 3)

        opt_grid.addWidget(QLabel("JPEG/WebP Quality:"), 1, 0)
        self.quality_slider = QSlider(Qt.Orientation.Horizontal)
        self.quality_slider.setRange(50, 100)
        self.quality_slider.setValue(92)
        self.quality_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.quality_slider.setTickInterval(5)
        opt_grid.addWidget(self.quality_slider, 1, 1, 1, 2)
        self.quality_label = QLabel("92")
        self.quality_label.setStyleSheet(f"color: {CAT['blue']}; font-weight: 700; min-width: 30px;")
        self.quality_slider.valueChanged.connect(lambda v: self.quality_label.setText(str(v)))
        opt_grid.addWidget(self.quality_label, 1, 3)

        opt_grid.addWidget(QLabel("Parallel Workers:"), 2, 0)
        self.workers_spin = QSpinBox()
        self.workers_spin.setRange(1, 32)
        cpu_count = os.cpu_count() or 4
        self.workers_spin.setValue(min(cpu_count, 8))
        opt_grid.addWidget(self.workers_spin, 2, 1)

        self.meta_chk = QCheckBox("Preserve EXIF / ICC / XMP metadata")
        self.meta_chk.setChecked(True)
        opt_grid.addWidget(self.meta_chk, 2, 2, 1, 2)

        root.addWidget(opt_group)

        # ── Actions ──
        actions = QHBoxLayout()
        self.scan_btn = QPushButton("Scan Directory")
        self.scan_btn.setObjectName("primaryBtn")
        self.scan_btn.clicked.connect(self._scan)
        actions.addWidget(self.scan_btn)

        self.convert_btn = QPushButton("Convert All")
        self.convert_btn.setObjectName("primaryBtn")
        self.convert_btn.setEnabled(False)
        self.convert_btn.clicked.connect(self._convert)
        actions.addWidget(self.convert_btn)

        self.stop_btn = QPushButton("Stop")
        self.stop_btn.setObjectName("stopBtn")
        self.stop_btn.setEnabled(False)
        self.stop_btn.clicked.connect(self._stop)
        actions.addWidget(self.stop_btn)

        actions.addStretch()

        self.open_output_btn = QPushButton("Open Output Folder")
        self.open_output_btn.setEnabled(False)
        self.open_output_btn.clicked.connect(self._open_output)
        actions.addWidget(self.open_output_btn)

        root.addLayout(actions)

        # ── Stats bar ──
        stats_frame = QFrame()
        stats_frame.setStyleSheet(
            f"background-color: {CAT['mantle']}; border-radius: 8px; padding: 6px;"
        )
        stats_layout = QHBoxLayout(stats_frame)
        stats_layout.setContentsMargins(16, 8, 16, 8)

        self.stat_files = self._make_stat("0", "Files Found")
        self.stat_size = self._make_stat("0 B", "Total Size")
        self.stat_done = self._make_stat("0", "Converted")
        self.stat_failed = self._make_stat("0", "Failed")
        self.stat_saved = self._make_stat("0 B", "Space Saved")

        for w in [self.stat_files, self.stat_size, self.stat_done, self.stat_failed, self.stat_saved]:
            stats_layout.addWidget(w)

        root.addWidget(stats_frame)

        # ── Progress ──
        self.progress_bar = QProgressBar()
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setValue(0)
        root.addWidget(self.progress_bar)

        # ── Log ──
        self.log_view = QPlainTextEdit()
        self.log_view.setReadOnly(True)
        self.log_view.setMaximumBlockCount(5000)
        root.addWidget(self.log_view, 1)

        # ── Status bar ──
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")

    def _make_stat(self, value: str, label: str) -> QWidget:
        w = QWidget()
        lay = QVBoxLayout(w)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)
        lay.setAlignment(Qt.AlignmentFlag.AlignCenter)
        val = QLabel(value)
        val.setObjectName("statValue")
        val.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl = QLabel(label)
        lbl.setObjectName("statLabel")
        lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lay.addWidget(val)
        lay.addWidget(lbl)
        w._val = val
        return w

    def _log(self, msg: str):
        self.log_view.appendPlainText(msg)

    # ── In-place toggle ──
    def _on_inplace_toggled(self, checked: bool):
        self.dst_edit.setEnabled(not checked)
        self.dst_btn.setEnabled(not checked)
        self.structure_chk.setEnabled(not checked)
        if checked:
            self.dst_edit.setPlaceholderText("(disabled — output goes next to each source file)")
        else:
            self.dst_edit.setPlaceholderText("Converted files go here (default: source/converted)")

    # ── Browse ──
    def _browse_source(self):
        d = QFileDialog.getExistingDirectory(self, "Select Source Directory",
                                             self.src_edit.text() or str(Path.home()))
        if d:
            self.src_edit.setText(d)
            if not self.dst_edit.text():
                self.dst_edit.setText(str(Path(d) / "converted"))

    def _browse_output(self):
        d = QFileDialog.getExistingDirectory(self, "Select Output Directory",
                                             self.dst_edit.text() or str(Path.home()))
        if d:
            self.dst_edit.setText(d)

    # ── Scan ──
    def _scan(self):
        src = self.src_edit.text().strip()
        if not src or not Path(src).is_dir():
            self._log("[ERROR] Please select a valid source directory.")
            return

        self.scan_btn.setEnabled(False)
        self.convert_btn.setEnabled(False)
        self.status_bar.showMessage("Scanning...")

        self._scanner = ScanWorker(src, self.recursive_chk.isChecked())
        self._scanner.log.connect(self._log)
        self._scanner.finished.connect(self._on_scan_done)
        self._scanner.start()

    def _on_scan_done(self, result: ScanResult):
        self._scan_result = result
        self.scan_btn.setEnabled(True)

        self.stat_files._val.setText(str(len(result.files)))
        self.stat_size._val.setText(_fmt_size(result.total_size))

        if result.files:
            self.convert_btn.setEnabled(True)
            self.status_bar.showMessage(
                f"Found {len(result.files)} files ({_fmt_size(result.total_size)}). Ready to convert."
            )
        else:
            self.status_bar.showMessage("No HEIC/HEIF files found.")

    # ── Convert ──
    def _convert(self):
        if not self._scan_result or not self._scan_result.files:
            return

        in_place = self.inplace_chk.isChecked()

        if in_place:
            # Output dir unused in in-place mode, but we need a valid Path
            dst = self.src_edit.text().strip()
        else:
            dst = self.dst_edit.text().strip()
            if not dst:
                src = self.src_edit.text().strip()
                dst = str(Path(src) / "converted")
                self.dst_edit.setText(dst)
            Path(dst).mkdir(parents=True, exist_ok=True)

        fmt_map = {0: "auto", 1: "jpeg", 2: "png", 3: "webp", 4: "tiff"}
        fmt = fmt_map.get(self.fmt_combo.currentIndex(), "auto")

        self._results = []
        self.progress_bar.setValue(0)
        self.progress_bar.setMaximum(len(self._scan_result.files))
        self.stat_done._val.setText("0")
        self.stat_failed._val.setText("0")
        self.stat_saved._val.setText("0 B")

        self.scan_btn.setEnabled(False)
        self.convert_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.open_output_btn.setEnabled(False)
        self.status_bar.showMessage("Converting...")

        if in_place:
            self._log(f"In-place mode: converted files saved next to originals, HEIC sources will be deleted")

        self._worker = ConvertWorker(
            files=self._scan_result.files,
            output_dir=Path(dst),
            fmt=fmt,
            quality=self.quality_slider.value(),
            preserve_meta=self.meta_chk.isChecked(),
            preserve_structure=self.structure_chk.isChecked(),
            base_dir=Path(self.src_edit.text().strip()),
            workers=self.workers_spin.value(),
            in_place=in_place,
        )
        self._worker.log.connect(self._log)
        self._worker.progress.connect(self._on_progress)
        self._worker.file_done.connect(self._on_file_done)
        self._worker.finished_all.connect(self._on_convert_done)
        self._worker.start()

    def _on_progress(self, current, total):
        self.progress_bar.setValue(current)
        self.status_bar.showMessage(f"Converting... {current}/{total}")

    def _on_file_done(self, result: ConvertResult):
        self._results.append(result)
        ok = sum(1 for r in self._results if r.success)
        fail = sum(1 for r in self._results if not r.success)
        saved = sum(r.size_before - r.size_after for r in self._results if r.success)

        self.stat_done._val.setText(str(ok))
        self.stat_failed._val.setText(str(fail))
        if fail:
            self.stat_failed._val.setStyleSheet(f"color: {CAT['red']}; font-size: 22px; font-weight: 700;")
        self.stat_saved._val.setText(_fmt_size(abs(saved)))
        if saved >= 0:
            self.stat_saved._val.setStyleSheet(f"color: {CAT['green']}; font-size: 22px; font-weight: 700;")
        else:
            self.stat_saved._val.setStyleSheet(f"color: {CAT['peach']}; font-size: 22px; font-weight: 700;")

    def _on_convert_done(self, results):
        self.scan_btn.setEnabled(True)
        self.convert_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.open_output_btn.setEnabled(True)

        ok = sum(1 for r in results if r.success)
        fail = sum(1 for r in results if not r.success)
        deleted = sum(1 for r in results if r.src_deleted)
        total_time = sum(r.elapsed for r in results)
        saved = sum(r.size_before - r.size_after for r in results if r.success)

        deleted_msg = f", {deleted} HEIC sources deleted" if deleted else ""
        summary = (
            f"Done! {ok} converted, {fail} failed{deleted_msg}. "
            f"Space {'saved' if saved >= 0 else 'added'}: {_fmt_size(abs(saved))}. "
            f"Total processing time: {total_time:.1f}s"
        )
        self._log(f"\n{'='*60}")
        self._log(summary)
        self._log(f"{'='*60}")
        self.status_bar.showMessage(summary)

        self._save_state()

    def _stop(self):
        if self._worker:
            self._worker.stop()
            self.stop_btn.setEnabled(False)
            self.status_bar.showMessage("Stopping...")

    def _open_output(self):
        dst = self.dst_edit.text().strip()
        if dst and Path(dst).exists():
            os.startfile(dst)

    # ── State persistence ──
    def _save_state(self):
        self.settings.setValue("src", self.src_edit.text())
        self.settings.setValue("dst", self.dst_edit.text())
        self.settings.setValue("fmt", self.fmt_combo.currentIndex())
        self.settings.setValue("quality", self.quality_slider.value())
        self.settings.setValue("workers", self.workers_spin.value())
        self.settings.setValue("recursive", self.recursive_chk.isChecked())
        self.settings.setValue("structure", self.structure_chk.isChecked())
        self.settings.setValue("metadata", self.meta_chk.isChecked())
        self.settings.setValue("inplace", self.inplace_chk.isChecked())
        self.settings.setValue("geometry", self.saveGeometry())

    def _restore_state(self):
        if v := self.settings.value("src"):
            self.src_edit.setText(v)
        if v := self.settings.value("dst"):
            self.dst_edit.setText(v)
        if (v := self.settings.value("fmt")) is not None:
            self.fmt_combo.setCurrentIndex(int(v))
        if (v := self.settings.value("quality")) is not None:
            self.quality_slider.setValue(int(v))
        if (v := self.settings.value("workers")) is not None:
            self.workers_spin.setValue(int(v))
        if (v := self.settings.value("recursive")) is not None:
            self.recursive_chk.setChecked(v == "true" or v is True)
        if (v := self.settings.value("structure")) is not None:
            self.structure_chk.setChecked(v == "true" or v is True)
        if (v := self.settings.value("metadata")) is not None:
            self.meta_chk.setChecked(v == "true" or v is True)
        if (v := self.settings.value("inplace")) is not None:
            self.inplace_chk.setChecked(v == "true" or v is True)
        if v := self.settings.value("geometry"):
            self.restoreGeometry(v)

    def closeEvent(self, event):
        self._save_state()
        if self._worker and self._worker.isRunning():
            self._worker.stop()
            self._worker.wait(3000)
        super().closeEvent(event)


# ── Entry Point ───────────────────────────────────────────────────────────────

def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setStyleSheet(STYLESHEET)

    # Dark palette fallback
    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window, QColor(CAT["base"]))
    palette.setColor(QPalette.ColorRole.WindowText, QColor(CAT["text"]))
    palette.setColor(QPalette.ColorRole.Base, QColor(CAT["crust"]))
    palette.setColor(QPalette.ColorRole.AlternateBase, QColor(CAT["surface0"]))
    palette.setColor(QPalette.ColorRole.Text, QColor(CAT["text"]))
    palette.setColor(QPalette.ColorRole.Button, QColor(CAT["surface0"]))
    palette.setColor(QPalette.ColorRole.ButtonText, QColor(CAT["text"]))
    palette.setColor(QPalette.ColorRole.Highlight, QColor(CAT["blue"]))
    palette.setColor(QPalette.ColorRole.HighlightedText, QColor(CAT["crust"]))
    app.setPalette(palette)

    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
