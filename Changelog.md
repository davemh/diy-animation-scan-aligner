# Changelog

## [1.0.0] – 2025-09-18
**First Working Release with GUI (macOS)**

### Added
- Simple GUI for batch alignment.
- Radial buttons to select pegbar position (**Top** or **Bottom**).
- Directory selection for choosing location of scans, and destination for aligned versions (defaults to: `scans/` and `aligned/`).
- **Run Alignment** and **Cancel** buttons.
- Simple progress bar (tied to overall batch).
- macOS `.app` executable.

### Fixed
- Corrected button-text contrast issues (white-on-white fixed for Run and Cancel buttons).
- Prevented multiple instances of the app from launching during processing.
- Improved peg hole detection and page alignment when using the GUI.

### Notes
- Windows and Linux builds are not included in this release.
- Large batch previews may process very slowly; batch isn't complete until a confirmation modal appears.
- For now, the GUI does not support the preview and debug features of the command line version