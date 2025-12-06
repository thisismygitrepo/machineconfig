# Changelog

All notable changes to Machineconfig are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

### Added
- MkDocs documentation with Material theme
- Comprehensive CLI reference
- API documentation with mkdocstrings

---

## [8.28] - 2025-12-03

### Added
- GNU Nano to development utilities
- WSL port management with normalized firewall rules
- WSL home linking and port opening functionality in CLI
- SSH port change functionality and installation checks for Linux/WSL
- Windows firewall port opening for WSL
- Cowsay and lolcat integration

### Changed
- Refactored SSH key management for Windows
- Enhanced WSL home directory inference with user-specific prioritization

### Fixed
- Language support definitions and file extensions in Helix installer
- WSL timeout issues
- ANSI code stripping in Zellij session names
- Installation pattern check for space-separated architecture strings

---

## [8.27] - 2025-12-01

### Added
- ImageMagick installer configuration
- 7zip dependency for yazi

### Changed
- Updated PowerShell commands to use `irm` instead of `iex`

---

## [8.26] - 2025-12-01

### Added
- Help option for all DevOps subcommands
- Pure Python agents command functions
- Helper functions for session management, file downloading, PDF processing, and system specs analysis
- Help option for AI Agents and layouts management subcommands
- New commands for cloud, devops, and utils modules

### Changed
- Implemented lazy loading for CLI entry points (faster startup)
- Refactored CLI entry point structure
- Updated standalone_mode handling in command functions

---

## [8.25] - 2025-12-01

### Added
- VirusTotal integration for scanning installed applications
- Installation checks module with reporting
- Script listing functionality with `list_available_scripts`
- SSH command module with install, add key, identity, and debug functions
- Lint and type check automation task

### Changed
- Replaced `search` method with `glob` for file matching
- Refactored PathExtended usage to standard Path imports
- Removed unnecessary `--scope user` flag from winget install

### Fixed
- File size calculations now use `stat()` for accuracy
- SSH diagnostics for Windows refactored
- Exception handling for `Set-ExecutionPolicy` in OpenSSH installation

---

## [8.24] - 2025-11-29

### Changed
- Various stability improvements and bug fixes

---

## [8.23] - 2025-11-28

### Changed
- Package management improvements

---

## [8.22] - 2025-11-27

### Changed
- Session management enhancements

---

## [8.21] - 2025-11-26

### Changed
- Configuration improvements

---

## [8.20] - 2025-11-26

### Changed
- Cross-platform compatibility updates

---

## [8.19] - 2025-11-26

### Changed
- Minor improvements

---

## [8.18] - 2025-11-26

### Changed
- Bug fixes and stability improvements

---

## [8.17] - 2025-11-24

### Changed
- Documentation updates

---

## Supported Platforms

- Linux (Debian, Ubuntu, Arch, Fedora)
- macOS
- Windows (with WSL support)

---

## Contributing

See the [contributing guide](contributing/index.md) for how to propose changes to this changelog.
