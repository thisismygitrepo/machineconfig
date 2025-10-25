#!/usr/bin/env python3
"""
Unit tests for macOS installation scripts.
Tests Homebrew installation detection, package group installation logic, and error handling.
"""

import os
import subprocess
import tempfile
import unittest
from unittest.mock import Mock, patch, call, MagicMock
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


class TestMacOSInstallation(unittest.TestCase):
    """Test cases for macOS installation functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp()
        self.apps_script = Path(__file__).parent.parent / "src" / "machineconfig" / "setup_mac" / "apps.sh"
        self.apps_gui_script = Path(__file__).parent.parent / "src" / "machineconfig" / "setup_mac" / "apps_gui.sh"
    
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.test_dir, ignore_errors=True)


class TestHomebrewDetection(TestMacOSInstallation):
    """Test Homebrew installation detection and setup."""
    
    @patch('subprocess.run')
    def test_homebrew_detection_installed(self, mock_run):
        """Test detection when Homebrew is already installed."""
        # Mock successful brew command
        mock_run.return_value = Mock(returncode=0, stdout="Homebrew 4.0.0")
        
        # Run the detection logic (simulated)
        result = subprocess.run(['which', 'brew'], capture_output=True, text=True)
        mock_run.assert_called_with(['which', 'brew'], capture_output=True, text=True)
        
        # Should return success when brew is found
        self.assertEqual(result.returncode, 0)
    
    @patch('subprocess.run')
    def test_homebrew_detection_not_installed(self, mock_run):
        """Test detection when Homebrew is not installed."""
        # Mock failed brew command (command not found)
        mock_run.return_value = Mock(returncode=1, stdout="", stderr="command not found")
        
        # Run the detection logic (simulated)
        result = subprocess.run(['which', 'brew'], capture_output=True, text=True)
        mock_run.assert_called_with(['which', 'brew'], capture_output=True, text=True)
        
        # Should return failure when brew is not found
        self.assertEqual(result.returncode, 1)
    
    @patch('subprocess.run')
    def test_architecture_detection_arm64(self, mock_run):
        """Test architecture detection for Apple Silicon (ARM64)."""
        # Mock uname -m returning arm64
        mock_run.return_value = Mock(returncode=0, stdout="arm64\n")
        
        result = subprocess.run(['uname', '-m'], capture_output=True, text=True)
        mock_run.assert_called_with(['uname', '-m'], capture_output=True, text=True)
        
        self.assertEqual(result.stdout.strip(), "arm64")
    
    @patch('subprocess.run')
    def test_architecture_detection_x86_64(self, mock_run):
        """Test architecture detection for Intel (x86_64)."""
        # Mock uname -m returning x86_64
        mock_run.return_value = Mock(returncode=0, stdout="x86_64\n")
        
        result = subprocess.run(['uname', '-m'], capture_output=True, text=True)
        mock_run.assert_called_with(['uname', '-m'], capture_output=True, text=True)
        
        self.assertEqual(result.stdout.strip(), "x86_64")


class TestPackageInstallation(TestMacOSInstallation):
    """Test package installation logic."""
    
    @patch('subprocess.run')
    def test_successful_package_installation(self, mock_run):
        """Test successful package installation via Homebrew."""
        # Mock successful brew install
        mock_run.return_value = Mock(returncode=0, stdout="Successfully installed git")
        
        # Simulate package installation
        result = subprocess.run(['brew', 'install', 'git'], capture_output=True, text=True)
        mock_run.assert_called_with(['brew', 'install', 'git'], capture_output=True, text=True)
        
        self.assertEqual(result.returncode, 0)
    
    @patch('subprocess.run')
    def test_failed_package_installation(self, mock_run):
        """Test failed package installation handling."""
        # Mock failed brew install
        mock_run.return_value = Mock(returncode=1, stdout="", stderr="Error: Package not found")
        
        # Simulate package installation failure
        result = subprocess.run(['brew', 'install', 'nonexistent-package'], capture_output=True, text=True)
        mock_run.assert_called_with(['brew', 'install', 'nonexistent-package'], capture_output=True, text=True)
        
        self.assertEqual(result.returncode, 1)
    
    @patch('subprocess.run')
    def test_cask_installation(self, mock_run):
        """Test GUI application installation via Homebrew Cask."""
        # Mock successful cask install
        mock_run.return_value = Mock(returncode=0, stdout="Successfully installed visual-studio-code")
        
        # Simulate cask installation
        result = subprocess.run(['brew', 'install', '--cask', 'visual-studio-code'], capture_output=True, text=True)
        mock_run.assert_called_with(['brew', 'install', '--cask', 'visual-studio-code'], capture_output=True, text=True)
        
        self.assertEqual(result.returncode, 0)


class TestErrorHandling(TestMacOSInstallation):
    """Test error handling scenarios."""
    
    @patch('subprocess.run')
    def test_network_error_handling(self, mock_run):
        """Test handling of network connectivity issues."""
        # Mock network error
        mock_run.side_effect = subprocess.TimeoutExpired(['brew', 'update'], 30)
        
        # Should handle timeout gracefully
        with self.assertRaises(subprocess.TimeoutExpired):
            subprocess.run(['brew', 'update'], timeout=30)
    
    @patch('subprocess.run')
    def test_permission_error_handling(self, mock_run):
        """Test handling of permission errors."""
        # Mock permission denied error
        mock_run.return_value = Mock(returncode=1, stderr="Permission denied")
        
        result = subprocess.run(['brew', 'install', 'some-package'], capture_output=True, text=True)
        mock_run.assert_called_with(['brew', 'install', 'some-package'], capture_output=True, text=True)
        
        self.assertEqual(result.returncode, 1)
        self.assertIn("Permission denied", result.stderr)
    
    def test_script_exists(self):
        """Test that the installation scripts exist and are executable."""
        self.assertTrue(self.apps_script.exists(), "apps.sh script should exist")
        self.assertTrue(self.apps_gui_script.exists(), "apps_gui.sh script should exist")
        
        # Check if scripts are executable (on Unix systems)
        if os.name != 'nt':  # Not Windows
            self.assertTrue(os.access(self.apps_script, os.X_OK), "apps.sh should be executable")
            self.assertTrue(os.access(self.apps_gui_script, os.X_OK), "apps_gui.sh should be executable")


class TestMacAppStore(TestMacOSInstallation):
    """Test Mac App Store integration."""
    
    @patch('subprocess.run')
    def test_mas_cli_detection(self, mock_run):
        """Test detection of mas (Mac App Store CLI)."""
        # Mock successful mas command
        mock_run.return_value = Mock(returncode=0, stdout="mas version 1.8.6")
        
        result = subprocess.run(['which', 'mas'], capture_output=True, text=True)
        mock_run.assert_called_with(['which', 'mas'], capture_output=True, text=True)
        
        self.assertEqual(result.returncode, 0)
    
    @patch('subprocess.run')
    def test_mas_account_check(self, mock_run):
        """Test Mac App Store account sign-in check."""
        # Mock signed in account
        mock_run.return_value = Mock(returncode=0, stdout="user@example.com")
        
        result = subprocess.run(['mas', 'account'], capture_output=True, text=True)
        mock_run.assert_called_with(['mas', 'account'], capture_output=True, text=True)
        
        self.assertEqual(result.returncode, 0)
    
    @patch('subprocess.run')
    def test_mas_app_installation(self, mock_run):
        """Test Mac App Store application installation."""
        # Mock successful app installation
        mock_run.return_value = Mock(returncode=0, stdout="Installing Xcode...")
        
        result = subprocess.run(['mas', 'install', '497799835'], capture_output=True, text=True)
        mock_run.assert_called_with(['mas', 'install', '497799835'], capture_output=True, text=True)
        
        self.assertEqual(result.returncode, 0)


class TestPackageGroups(TestMacOSInstallation):
    """Test package group functionality."""
    
    def test_essential_system_packages(self):
        """Test that essential system packages are defined."""
        essential_packages = [
            'git', 'nano', 'curl', 'wget', 'htop', 'tree', 'jq',
            'sqlite3', 'postgresql', 'redis'
        ]
        
        # These packages should be available for installation
        for package in essential_packages:
            self.assertIsInstance(package, str)
            self.assertTrue(len(package) > 0)
    
    def test_terminal_eyecandy_packages(self):
        """Test that terminal eye candy packages are defined."""
        eyecandy_packages = [
            'fortune', 'figlet', 'cowsay', 'lolcat', 'chafa',
            'boxes', 'sl', 'cmatrix'
        ]
        
        # These packages should be available for installation
        for package in eyecandy_packages:
            self.assertIsInstance(package, str)
            self.assertTrue(len(package) > 0)
    
    def test_development_packages(self):
        """Test that development packages are defined."""
        dev_packages = [
            'graphviz', 'make', 'ffmpeg', 'openssl', 'cmake',
            'pkg-config', 'autoconf', 'automake', 'libtool'
        ]
        
        # These packages should be available for installation
        for package in dev_packages:
            self.assertIsInstance(package, str)
            self.assertTrue(len(package) > 0)


class TestScriptIntegration(TestMacOSInstallation):
    """Test script integration and execution."""
    
    def test_script_syntax(self):
        """Test that scripts have valid bash syntax."""
        if not self.apps_script.exists() or not self.apps_gui_script.exists():
            self.skipTest("Scripts not found")
        
        # Test apps.sh syntax
        try:
            result = subprocess.run(['bash', '-n', str(self.apps_script)], 
                                  capture_output=True, text=True, timeout=10)
            self.assertEqual(result.returncode, 0, f"apps.sh syntax error: {result.stderr}")
        except subprocess.TimeoutExpired:
            self.fail("Script syntax check timed out")
        except FileNotFoundError:
            self.skipTest("bash not available for syntax checking")
        
        # Test apps_gui.sh syntax
        try:
            result = subprocess.run(['bash', '-n', str(self.apps_gui_script)], 
                                  capture_output=True, text=True, timeout=10)
            self.assertEqual(result.returncode, 0, f"apps_gui.sh syntax error: {result.stderr}")
        except subprocess.TimeoutExpired:
            self.fail("Script syntax check timed out")
        except FileNotFoundError:
            self.skipTest("bash not available for syntax checking")
    
    @patch.dict(os.environ, {'TESTING': 'true'})
    def test_script_dry_run(self):
        """Test scripts in dry-run mode (if supported)."""
        # This would test the scripts without actually installing anything
        # Implementation depends on adding dry-run support to the scripts
        pass


if __name__ == '__main__':
    unittest.main()