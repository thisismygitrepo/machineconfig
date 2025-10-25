# Design Document: Full macOS Support for machineconfig

## Overview

This design document outlines the architecture and implementation approach for adding comprehensive macOS support to the machineconfig package. The goal is to achieve feature parity with the existing Linux and Windows implementations while leveraging macOS-specific package managers and system characteristics.

The current macOS implementation is minimal, with basic Homebrew support and limited application installation. This design expands the functionality to match the comprehensive setup capabilities available on Linux and Windows platforms.

## Architecture

### Platform Detection Enhancement

The existing platform detection system in `installer_types.py` already correctly identifies macOS as "macos" when `platform.system()` returns "Darwin". This foundation will be extended to support macOS-specific installation workflows.

### Package Manager Integration

**Primary Package Manager: Homebrew**
- Homebrew will serve as the primary package manager for both CLI tools and GUI applications
- Homebrew Cask will handle GUI application installations
- Automatic Homebrew installation if not present on the system

**Secondary Package Managers:**
- Mac App Store CLI (mas) for App Store applications
- Direct downloads for applications not available through package managers
- Language-specific package managers (npm, pip, cargo, etc.)

### Directory Structure Expansion

The current macOS setup structure will be expanded to match the Linux implementation:

```
src/machineconfig/setup_mac/
├── __init__.py (enhanced)
├── apps.sh (comprehensive rewrite)
├── apps_gui.sh (new)
├── uv.sh (enhanced)
├── ssh/
│   └── openssh_setup.sh (new)
└── others/
    ├── system_preferences.sh (new)
    └── development_tools.sh (new)
```

## Components and Interfaces

### Enhanced Setup Scripts

**apps.sh (Core CLI Applications)**
- Essential system tools (git, curl, wget equivalents)
- Development tools (make, rust, node.js, python tools)
- Terminal enhancements (fortune, figlet, cowsay, lolcat, chafa)
- Network tools (sshfs via macFUSE, nfs utilities)
- Database clients (sqlite3, postgresql-client, redis-cli)

**apps_gui.sh (GUI Applications)**
- Browsers (Brave, Chrome, Firefox)
- Development IDEs (Visual Studio Code, Cursor)
- Productivity tools (Obsidian, Bitwarden)
- Media tools (OBS Studio, VLC)
- System utilities (7-Zip equivalent: The Unarchiver)

**system_preferences.sh (macOS System Configuration)**
- Dock preferences and organization
- Finder settings and view options
- Security and privacy settings
- Keyboard and trackpad configurations
- Energy saver and display settings

### Package Group Mapping

Each package group from the existing system will be mapped to macOS equivalents:

**ESSENTIAL_SYSTEM Group:**
- git → git (Homebrew)
- nano → nano (Homebrew)
- curl → curl (built-in, updated via Homebrew)
- nvm → nvm (script installation)
- nodejs → node (via nvm or Homebrew)

**TerminalEyeCandy Group:**
- fortune → fortune (Homebrew)
- figlet → figlet (Homebrew)
- cowsay → cowsay (Homebrew)
- lolcat → lolcat (Homebrew)
- chafa → chafa (Homebrew)

**DEV_SYSTEM Group:**
- graphviz → graphviz (Homebrew)
- make → make (Xcode Command Line Tools or Homebrew)
- rust → rustup (script installation)
- sqlite3 → sqlite (built-in, updated via Homebrew)
- postgresql-client → postgresql (Homebrew)
- redis-tools → redis (Homebrew)

### Installation Strategy

**Dependency Resolution:**
1. Check for Xcode Command Line Tools installation
2. Install Homebrew if not present
3. Update Homebrew and formulae
4. Install packages with error handling and fallbacks
5. Configure installed applications

**Error Handling:**
- Graceful failure handling for individual package installations
- Alternative installation methods for failed packages
- Comprehensive logging of installation attempts and results
- User-friendly error messages with suggested solutions

## Data Models

### macOS-Specific Installer Data

The existing `InstallerData` TypedDict structure supports macOS through the `fileNamePattern` field. The installer data will be expanded to include:

```python
# Example installer data for macOS
{
    "appName": "example-app",
    "doc": "Description of the application",
    "repoURL": "https://github.com/example/app",
    "fileNamePattern": {
        "amd64": {
            "macos": "brew install example-app",
            "linux": "apt install example-app",
            "windows": "winget install example-app"
        },
        "arm64": {
            "macos": "brew install example-app",
            "linux": "apt install example-app", 
            "windows": "winget install example-app"
        }
    }
}
```

### Configuration File Paths

macOS-specific configuration file locations will be mapped:

- `~/.config/` (XDG-style configs)
- `~/Library/Application Support/` (macOS-native app configs)
- `~/Library/Preferences/` (plist files)
- `~/.ssh/` (SSH configurations)
- `~/dotfiles/` (private dotfiles)

## Error Handling

### Installation Failures

**Homebrew Installation Issues:**
- Network connectivity problems
- Permission issues with `/opt/homebrew` or `/usr/local`
- Disk space limitations
- Conflicting installations

**Package Installation Failures:**
- Missing dependencies
- Architecture incompatibility (Intel vs Apple Silicon)
- Version conflicts
- Network timeouts

**Fallback Strategies:**
- Alternative package sources (direct downloads, different repositories)
- Manual installation instructions
- Skip non-essential packages with user notification
- Retry mechanisms with exponential backoff

### System-Specific Issues

**macOS Security Features:**
- Gatekeeper warnings for unsigned applications
- System Integrity Protection (SIP) restrictions
- Notarization requirements for downloaded applications
- Permission requests for system access

**File System Considerations:**
- Case sensitivity variations
- Extended attributes and resource forks
- Symbolic link creation permissions
- Spotlight indexing implications

## Testing Strategy

### Unit Testing

**Platform Detection Tests:**
- Verify correct macOS identification
- Test architecture detection (Intel vs Apple Silicon)
- Validate package manager availability checks

**Installation Logic Tests:**
- Mock Homebrew installation processes
- Test error handling scenarios
- Validate package group mappings

### Integration Testing

**End-to-End Installation Tests:**
- Full system setup on clean macOS installations
- Test on both Intel and Apple Silicon Macs
- Verify package group installations
- Test dotfile management and symbolic link creation

**Compatibility Testing:**
- macOS version compatibility (macOS 12+)
- Homebrew version compatibility
- Package version conflicts and resolutions

### Manual Testing Scenarios

**Fresh System Setup:**
- Test on newly installed macOS systems
- Verify Homebrew installation from scratch
- Test complete package group installations

**Existing System Integration:**
- Test on systems with existing Homebrew installations
- Verify conflict resolution with existing packages
- Test dotfile backup and restoration

**Error Recovery Testing:**
- Simulate network failures during installation
- Test recovery from partial installations
- Verify cleanup of failed installations

## Implementation Phases

### Phase 1: Core Infrastructure
- Enhance platform detection and macOS-specific paths
- Implement comprehensive Homebrew integration
- Create basic package installation framework

### Phase 2: Package Groups Implementation
- Implement all essential package groups for macOS
- Create macOS-specific installation scripts
- Add GUI application support via Homebrew Cask

### Phase 3: System Configuration
- Implement macOS system preferences configuration
- Add development environment setup
- Create SSH and security configuration scripts

### Phase 4: Advanced Features
- Implement Mac App Store integration
- Add backup and restoration capabilities
- Create migration tools from other platforms

### Phase 5: Testing and Optimization
- Comprehensive testing across macOS versions
- Performance optimization for large package installations
- Documentation and user guide creation

## Security Considerations

**Package Verification:**
- Verify Homebrew package signatures
- Check application notarization status
- Validate download checksums for direct downloads

**Permission Management:**
- Minimize required administrator privileges
- Use user-scoped installations where possible
- Provide clear explanations for permission requests

**Data Protection:**
- Encrypt private dotfiles before backup
- Secure handling of SSH keys and certificates
- Respect macOS privacy controls and permissions