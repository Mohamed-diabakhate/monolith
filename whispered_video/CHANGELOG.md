# Changelog

## [2024-01-01] - Output Format Updates

### Changed

- **Transcript Output**: Changed from `.txt` to `.md` extension

  - Now generates properly formatted markdown files
  - Includes metadata header with language, duration, and timestamp
  - Uses markdown syntax for better readability
  - Segments are separated by double line breaks for better formatting

- **Summary Output**: Changed from `.txt` to `.json` extension
  - Now generates structured JSON data instead of plain text
  - Machine-readable format for programmatic access
  - Includes all metadata, performance metrics, and cost analysis
  - Segments with timestamps and word-level data when available

### Technical Changes

- Updated `utils.py`:

  - Added `json` import
  - Modified `create_output_paths()` to use `.md` and `.json` extensions

- Updated `transcriber.py`:

  - Modified `_write_transcript()` to use markdown formatting
  - Completely rewrote `_write_summary()` to output JSON structure
  - Added `CLOUD_RUN_PRICING` import
  - Removed old helper functions `_write_performance_summary()` and `_write_cost_analysis()`

- Updated `main.py`:

  - Added summary file path to output messages
  - Now shows both transcript and summary file paths

- Updated `README.md`:
  - Updated output format documentation
  - Added examples of both markdown and JSON formats
  - Updated feature list to highlight new formats

### Benefits

- **Markdown Transcripts**: Better readability, proper formatting, easy to include in documentation
- **JSON Summaries**: Machine-readable, structured data, easy to parse and process programmatically
- **Backward Compatibility**: Existing functionality remains the same, only output format changed

### Files Affected

- `app/utils.py`
- `app/transcriber.py`
- `app/main.py`
- `app/README.md`
- `app/test_output_formats.py` (new test file)
