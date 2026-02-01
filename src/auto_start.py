import os
import sys
import winreg
import shutil
from pathlib import Path
from config import Config

class AutoStart:
    """Manages Windows auto-start functionality"""
    
    @staticmethod
    def get_executable_path():
        """Get the path to the current executable or script"""
        if getattr(sys, 'frozen', False):
            # Running as compiled executable
            return sys.executable
        else:
            # Running as script
            return os.path.abspath(sys.argv[0])
    
    @staticmethod
    def add_to_registry():
        """Add application to Windows registry for auto-start"""
        try:
            # Open registry key
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                Config.REGISTRY_KEY,
                0,
                winreg.KEY_SET_VALUE
            )
            
            # Set value
            exe_path = AutoStart.get_executable_path()
            winreg.SetValueEx(
                key,
                Config.REGISTRY_VALUE_NAME,
                0,
                winreg.REG_SZ,
                f'"{exe_path}"'
            )
            
            winreg.CloseKey(key)
            return True
            
        except Exception as e:
            return False
    
    @staticmethod
    def remove_from_registry():
        """Remove application from Windows registry"""
        try:
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                Config.REGISTRY_KEY,
                0,
                winreg.KEY_SET_VALUE
            )
            
            winreg.DeleteValue(key, Config.REGISTRY_VALUE_NAME)
            winreg.CloseKey(key)
            return True
            
        except Exception as e:
            return False
    
    @staticmethod
    def add_to_startup_folder():
        """Add shortcut to Windows Startup folder"""
        try:
            # Get startup folder path
            startup_folder = os.path.join(
                os.getenv('APPDATA'),
                'Microsoft',
                'Windows',
                'Start Menu',
                'Programs',
                'Startup'
            )
            
            # Create shortcut using VBScript (Windows-compatible method)
            exe_path = AutoStart.get_executable_path()
            shortcut_path = os.path.join(startup_folder, f'{Config.APP_NAME}.lnk')
            
            # Create VBS script to create shortcut
            vbs_script = f'''
Set oWS = WScript.CreateObject("WScript.Shell")
sLinkFile = "{shortcut_path}"
Set oLink = oWS.CreateShortcut(sLinkFile)
oLink.TargetPath = "{exe_path}"
oLink.WorkingDirectory = "{os.path.dirname(exe_path)}"
oLink.Description = "{Config.APP_NAME}"
oLink.Save
'''
            
            # Write and execute VBS script
            vbs_path = os.path.join(Config.LOCAL_STORAGE_PATH, 'create_shortcut.vbs')
            with open(vbs_path, 'w') as f:
                f.write(vbs_script)
            
            os.system(f'cscript //nologo "{vbs_path}"')
            
            # Clean up VBS script
            try:
                os.remove(vbs_path)
            except:
                pass
            
            return True
            
        except Exception as e:
            return False
    
    @staticmethod
    def is_installed():
        """Check if auto-start is installed"""
        try:
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                Config.REGISTRY_KEY,
                0,
                winreg.KEY_READ
            )
            
            value, _ = winreg.QueryValueEx(key, Config.REGISTRY_VALUE_NAME)
            winreg.CloseKey(key)
            return True
            
        except Exception as e:
            return False
    
    @staticmethod
    def install():
        """Install auto-start using both methods"""
        registry_success = AutoStart.add_to_registry()
        startup_success = AutoStart.add_to_startup_folder()
        return registry_success or startup_success
    
    @staticmethod
    def uninstall():
        """Uninstall auto-start"""
        AutoStart.remove_from_registry()
        # Note: Removing from startup folder requires finding and deleting the .lnk file

if __name__ == '__main__':
    # Allow running this script to install/uninstall auto-start
    if len(sys.argv) > 1:
        if sys.argv[1] == 'install':
            if AutoStart.install():
                print('Auto-start installed successfully')
            else:
                print('Failed to install auto-start')
        elif sys.argv[1] == 'uninstall':
            if AutoStart.uninstall():
                print('Auto-start uninstalled successfully')
            else:
                print('Failed to uninstall auto-start')
        elif sys.argv[1] == 'check':
            if AutoStart.is_installed():
                print('Auto-start is installed')
            else:
                print('Auto-start is not installed')
