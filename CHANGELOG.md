# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

### Added

- `.gitignore` for Python, IDE, and project-specific files
- `.env.example` template for environment variable configuration
- `CONTRIBUTING.md` with contribution guidelines
- `LICENSE` (MIT)
- `CHANGELOG.md` for tracking project changes
- `docs/` directory with setup, architecture, development, and API documentation
- `tests/` directory with initial test structure and unit tests
- GitHub Actions CI workflow for linting and testing
- GitHub issue templates (bug report, feature request)
- GitHub pull request template
- Proper logging throughout the codebase (replacing print statements)
- Docstrings for all classes and functions
- Input validation for PDF file uploads

### Fixed

- `api.py`: Changed `return HTTPException(...)` to `raise HTTPException(...)` in upload endpoint
- `rag.py`: Fixed mutable default argument `chat_history: List[dict] = []` → `chat_history: Optional[List[dict]] = None`
- `rag.py`: Removed unused `Optional` import (now used after fix)

### Changed

- Pinned dependency versions in `requirements.txt` for reproducible builds
- Added `langchain-text-splitters` as an explicit dependency
- Improved README with comprehensive documentation sections
- Reorganized project documentation into `docs/` directory
