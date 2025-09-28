#!/usr/bin/env python3
"""
Application Launcher System
Scans all installed applications and provides voice-controlled launching
"""

import os
import winreg
import subprocess
import json
import time
from pathlib import Path
import re
from difflib import SequenceMatcher

class ApplicationLauncher:
    def __init__(self):
        self.apps = {}
        self.app_cache_file = "app_cache.json"
        self.load_or_scan_apps()
    
    def load_or_scan_apps(self):
        """Load apps from cache or scan if cache is old/missing"""
        if self.should_rescan_apps():
            print("🔍 Scanning installed applications...")
            self.scan_installed_apps()
            self.save_app_cache()
        else:
            print("📂 Loading applications from cache...")
            self.load_app_cache()
        
        print(f"✅ Found {len(self.apps)} applications")
    
    def should_rescan_apps(self):
        """Check if we should rescan apps (cache is old or missing)"""
        if not os.path.exists(self.app_cache_file):
            return True
        
        # Rescan if cache is older than 24 hours
        cache_age = time.time() - os.path.getmtime(self.app_cache_file)
        return cache_age > 24 * 60 * 60  # 24 hours in seconds
    
    def scan_installed_apps(self):
        """Scan for all installed applications"""
        self.apps = {}
        
        # Scan multiple sources
        self.scan_start_menu()
        self.scan_registry_uninstall()
        self.scan_common_paths()
        self.scan_uwp_apps()
        
        # Remove duplicates and clean up
        self.clean_app_list()
    
    def scan_start_menu(self):
        """Scan Start Menu shortcuts"""
        start_menu_paths = [
            os.path.expandvars(r"%APPDATA%\Microsoft\Windows\Start Menu\Programs"),
            os.path.expandvars(r"%PROGRAMDATA%\Microsoft\Windows\Start Menu\Programs"),
        ]
        
        for start_path in start_menu_paths:
            if os.path.exists(start_path):
                self._scan_directory_for_shortcuts(start_path)
    
    def _scan_directory_for_shortcuts(self, directory):
        """Recursively scan directory for .lnk files"""
        try:
            for root, dirs, files in os.walk(directory):
                for file in files:
                    if file.endswith('.lnk'):
                        shortcut_path = os.path.join(root, file)
                        app_name = os.path.splitext(file)[0]
                        
                        # Skip common non-app shortcuts
                        if self._is_valid_app_name(app_name):
                            self.apps[app_name.lower()] = {
                                'name': app_name,
                                'path': shortcut_path,
                                'type': 'shortcut'
                            }
        except Exception as e:
            print(f"Error scanning {directory}: {e}")
    
    def scan_registry_uninstall(self):
        """Scan Windows Registry for installed programs"""
        registry_paths = [
            r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall",
            r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall"
        ]
        
        for reg_path in registry_paths:
            try:
                with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, reg_path) as key:
                    i = 0
                    while True:
                        try:
                            subkey_name = winreg.EnumKey(key, i)
                            with winreg.OpenKey(key, subkey_name) as subkey:
                                try:
                                    display_name = winreg.QueryValueEx(subkey, "DisplayName")[0]
                                    install_location = None
                                    
                                    try:
                                        install_location = winreg.QueryValueEx(subkey, "InstallLocation")[0]
                                    except FileNotFoundError:
                                        pass
                                    
                                    if self._is_valid_app_name(display_name):
                                        self.apps[display_name.lower()] = {
                                            'name': display_name,
                                            'path': install_location,
                                            'type': 'registry'
                                        }
                                except FileNotFoundError:
                                    pass
                            i += 1
                        except OSError:
                            break
            except Exception as e:
                print(f"Error scanning registry {reg_path}: {e}")
    
    def scan_common_paths(self):
        """Scan common installation directories"""
        common_paths = [
            r"C:\Program Files",
            r"C:\Program Files (x86)",
            os.path.expandvars(r"%LOCALAPPDATA%\Programs"),
        ]
        
        for base_path in common_paths:
            if os.path.exists(base_path):
                try:
                    for item in os.listdir(base_path):
                        item_path = os.path.join(base_path, item)
                        if os.path.isdir(item_path) and self._is_valid_app_name(item):
                            # Look for executable files
                            exe_files = self._find_executables(item_path)
                            if exe_files:
                                self.apps[item.lower()] = {
                                    'name': item,
                                    'path': exe_files[0],  # Use first found executable
                                    'type': 'directory'
                                }
                except Exception as e:
                    print(f"Error scanning {base_path}: {e}")
    
    def scan_uwp_apps(self):
        """Scan for UWP/Microsoft Store apps"""
        try:
            # Use PowerShell to get UWP apps
            ps_command = "Get-AppxPackage | Where-Object {$_.Name -notlike '*Microsoft*' -and $_.Name -notlike '*Windows*'} | Select-Object Name, PackageFullName"
            result = subprocess.run(
                ["powershell", "-Command", ps_command],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                for line in lines[3:]:  # Skip header lines
                    if line.strip():
                        parts = line.strip().split()
                        if len(parts) >= 2:
                            app_name = parts[0]
                            if self._is_valid_app_name(app_name):
                                self.apps[app_name.lower()] = {
                                    'name': app_name,
                                    'path': f"shell:AppsFolder\\{parts[1]}!App",
                                    'type': 'uwp'
                                }
        except Exception as e:
            print(f"Error scanning UWP apps: {e}")
    
    def _find_executables(self, directory, max_depth=2):
        """Find executable files in directory"""
        executables = []
        try:
            for root, dirs, files in os.walk(directory):
                # Limit search depth
                level = root.replace(directory, '').count(os.sep)
                if level >= max_depth:
                    dirs[:] = []  # Don't go deeper
                
                for file in files:
                    if file.endswith('.exe') and not file.lower().startswith('unins'):
                        exe_path = os.path.join(root, file)
                        executables.append(exe_path)
                        
                        # Stop after finding a few executables
                        if len(executables) >= 3:
                            return executables
        except Exception:
            pass
        
        return executables
    
    def _is_valid_app_name(self, name):
        """Check if this looks like a valid application name"""
        if not name or len(name) < 2:
            return False
        
        # Skip common non-app entries
        skip_patterns = [
            'uninstall', 'readme', 'license', 'help', 'documentation',
            'update', 'setup', 'install', 'config', 'settings',
            'microsoft visual c++', 'microsoft .net', 'directx',
            'windows', 'system', 'driver', 'runtime'
        ]
        
        name_lower = name.lower()
        return not any(pattern in name_lower for pattern in skip_patterns)
    
    def clean_app_list(self):
        """Remove duplicates and clean up app list"""
        # Remove apps with very similar names (keep the shorter one)
        apps_to_remove = []
        app_names = list(self.apps.keys())
        
        for i, name1 in enumerate(app_names):
            for name2 in app_names[i+1:]:
                similarity = SequenceMatcher(None, name1, name2).ratio()
                if similarity > 0.8:  # Very similar names
                    # Keep the shorter, simpler name
                    if len(name1) > len(name2):
                        apps_to_remove.append(name1)
                    else:
                        apps_to_remove.append(name2)
        
        for app_name in apps_to_remove:
            if app_name in self.apps:
                del self.apps[app_name]
    
    def save_app_cache(self):
        """Save app list to cache file"""
        try:
            with open(self.app_cache_file, 'w') as f:
                json.dump(self.apps, f, indent=2)
        except Exception as e:
            print(f"Error saving app cache: {e}")
    
    def load_app_cache(self):
        """Load app list from cache file"""
        try:
            with open(self.app_cache_file, 'r') as f:
                self.apps = json.load(f)
        except Exception as e:
            print(f"Error loading app cache: {e}")
            self.scan_installed_apps()
    
    def find_app(self, app_name):
        """Find application by name (fuzzy matching)"""
        app_name_lower = app_name.lower().strip()
        
        # Exact match first
        if app_name_lower in self.apps:
            return self.apps[app_name_lower]
        
        # Partial match
        for name, app_info in self.apps.items():
            if app_name_lower in name or name in app_name_lower:
                return app_info
        
        # Fuzzy match
        best_match = None
        best_score = 0
        
        for name, app_info in self.apps.items():
            score = SequenceMatcher(None, app_name_lower, name).ratio()
            if score > best_score and score > 0.6:  # Minimum similarity threshold
                best_score = score
                best_match = app_info
        
        return best_match
    
    def launch_app(self, app_name):
        """Launch application by name"""
        app_info = self.find_app(app_name)
        
        if not app_info:
            return f"Application '{app_name}' not found"
        
        try:
            app_path = app_info['path']
            app_type = app_info['type']
            
            if app_type == 'uwp':
                # Launch UWP app
                subprocess.Popen(['explorer', app_path])
            elif app_path and os.path.exists(app_path):
                if app_path.endswith('.lnk'):
                    # Launch shortcut
                    os.startfile(app_path)
                elif app_path.endswith('.exe'):
                    # Launch executable
                    subprocess.Popen([app_path])
                else:
                    # Try to open directory or file
                    os.startfile(app_path)
            else:
                # Try to launch by name using Windows search
                subprocess.Popen(['explorer', f'shell:AppsFolder\\{app_info["name"]}'])
            
            return f"Launching {app_info['name']}"
            
        except Exception as e:
            return f"Failed to launch {app_info['name']}: {e}"
    
    def list_apps(self, filter_text=None):
        """List available applications"""
        if filter_text:
            filter_lower = filter_text.lower()
            filtered_apps = {name: info for name, info in self.apps.items() 
                           if filter_lower in name or filter_lower in info['name'].lower()}
            return filtered_apps
        
        return self.apps
    
    def get_app_suggestions(self, partial_name, limit=5):
        """Get app suggestions for partial name"""
        partial_lower = partial_name.lower()
        suggestions = []
        
        # Find apps that start with or contain the partial name
        for name, app_info in self.apps.items():
            if partial_lower in name or partial_lower in app_info['name'].lower():
                score = SequenceMatcher(None, partial_lower, name).ratio()
                suggestions.append((app_info['name'], score))
        
        # Sort by score and return top suggestions
        suggestions.sort(key=lambda x: x[1], reverse=True)
        return [name for name, score in suggestions[:limit]]

# Test the app launcher
if __name__ == "__main__":
    print("🚀 Application Launcher Test")
    print("="*50)
    
    launcher = ApplicationLauncher()
    
    print(f"\nFound {len(launcher.apps)} applications")
    
    # Show some examples
    print("\nSample applications found:")
    count = 0
    for name, info in launcher.apps.items():
        if count < 10:
            print(f"  • {info['name']} ({info['type']})")
            count += 1
        else:
            break
    
    # Test app finding
    test_apps = ["chrome", "notepad", "calculator", "discord", "steam"]
    
    print(f"\nTesting app search:")
    for app in test_apps:
        result = launcher.find_app(app)
        if result:
            print(f"  ✅ '{app}' → {result['name']}")
        else:
            print(f"  ❌ '{app}' → Not found")
    
    print(f"\nTest complete!")