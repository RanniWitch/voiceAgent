#!/usr/bin/env python3
"""
Windows Startup Setup for Voice Assistant
Automatically configures the voice assistant to start with Windows
"""

import os
import shutil
import tkinter as tk
from tkinter import ttk, messagebox
import winreg
import sys

class WindowsStartupSetup:
    def __init__(self):
        self.current_dir = os.getcwd()
        self.startup_folder = os.path.join(os.environ['APPDATA'], 'Microsoft', 'Windows', 'Start Menu', 'Programs', 'Startup')
        self.batch_file = os.path.join(self.current_dir, 'auto_start_voice_assistant.bat')
        self.setup_gui()
        
    def setup_gui(self):
        """Setup the startup configuration GUI"""
        self.root = tk.Tk()
        self.root.title("Voice Assistant Startup Setup")
        self.root.geometry("600x500")
        self.root.resizable(False, False)
        
        # Main frame
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, text="Voice Assistant Auto-Startup Setup", 
                              font=("Arial", 16, "bold"))
        title_label.pack(pady=(0, 20))
        
        # Description
        desc_text = """This will configure your voice assistant to start automatically when Windows boots.
After setup, just say "hey black" anytime to activate your assistant!"""
        
        ttk.Label(main_frame, text=desc_text, font=("Arial", 11), 
                 justify=tk.CENTER, wraplength=500).pack(pady=(0, 20))
        
        # Current status
        status_frame = ttk.LabelFrame(main_frame, text="Current Status", padding="15")
        status_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Check current status
        is_configured = self.check_startup_status()
        
        if is_configured:
            status_text = "✅ Voice assistant is configured to start with Windows"
            status_color = "green"
        else:
            status_text = "❌ Voice assistant is NOT configured for auto-start"
            status_color = "red"
            
        ttk.Label(status_frame, text=status_text, font=("Arial", 11)).pack()
        
        # Setup options
        options_frame = ttk.LabelFrame(main_frame, text="Setup Options", padding="15")
        options_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Method 1: Startup Folder
        method1_frame = ttk.Frame(options_frame)
        method1_frame.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Label(method1_frame, text="Method 1: Windows Startup Folder (Recommended)", 
                 font=("Arial", 12, "bold")).pack(anchor=tk.W)
        ttk.Label(method1_frame, text="• Easiest to setup and remove\n• Starts when you log in\n• Can be disabled from Task Manager", 
                 font=("Arial", 10)).pack(anchor=tk.W, pady=(5, 10))
        
        ttk.Button(method1_frame, text="🚀 Enable Auto-Start (Startup Folder)", 
                  command=self.setup_startup_folder, width=35).pack(anchor=tk.W)
        
        # Method 2: Registry
        method2_frame = ttk.Frame(options_frame)
        method2_frame.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Label(method2_frame, text="Method 2: Windows Registry", 
                 font=("Arial", 12, "bold")).pack(anchor=tk.W)
        ttk.Label(method2_frame, text="• More persistent\n• Starts for all users\n• Requires admin privileges", 
                 font=("Arial", 10)).pack(anchor=tk.W, pady=(5, 10))
        
        ttk.Button(method2_frame, text="🔧 Enable Auto-Start (Registry)", 
                  command=self.setup_registry, width=35).pack(anchor=tk.W)
        
        # Remove options
        remove_frame = ttk.LabelFrame(main_frame, text="Remove Auto-Start", padding="15")
        remove_frame.pack(fill=tk.X, pady=(0, 20))
        
        ttk.Label(remove_frame, text="Remove voice assistant from Windows startup:", 
                 font=("Arial", 11)).pack(anchor=tk.W, pady=(0, 10))
        
        button_frame = ttk.Frame(remove_frame)
        button_frame.pack(anchor=tk.W)
        
        ttk.Button(button_frame, text="🗑️ Remove from Startup", 
                  command=self.remove_startup).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(button_frame, text="📋 Show Startup Folder", 
                  command=self.open_startup_folder).pack(side=tk.LEFT)
        
        # Instructions
        instructions_frame = ttk.LabelFrame(main_frame, text="After Setup", padding="15")
        instructions_frame.pack(fill=tk.X)
        
        instructions_text = """After enabling auto-start:
1. Restart your computer (or log out and back in)
2. The voice assistant will start automatically and minimize to tray
3. Just say "hey black" followed by any command
4. Say "hey black, show window" to see the interface
5. Say "hey black, stop listening" to quit the assistant"""
        
        ttk.Label(instructions_frame, text=instructions_text, 
                 font=("Arial", 10), justify=tk.LEFT).pack(anchor=tk.W)
        
    def check_startup_status(self):
        """Check if voice assistant is configured for startup"""
        # Check startup folder
        startup_link = os.path.join(self.startup_folder, 'Voice Assistant.bat')
        if os.path.exists(startup_link):
            return True
            
        # Check registry
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, 
                               r"Software\Microsoft\Windows\CurrentVersion\Run")
            try:
                winreg.QueryValueEx(key, "VoiceAssistant")
                winreg.CloseKey(key)
                return True
            except FileNotFoundError:
                winreg.CloseKey(key)
                return False
        except:
            return False
            
    def setup_startup_folder(self):
        """Setup auto-start using Windows startup folder"""
        try:
            # Update the batch file with correct path
            batch_content = f'''@echo off
REM Auto-start Voice Assistant on Windows Boot
echo Starting Voice Assistant...

REM Change to the voice assistant directory
cd /d "{self.current_dir}"

REM Activate virtual environment and start assistant
call venv\\Scripts\\activate.bat

REM Start the voice assistant (auto-start version)
py wake_word_assistant_auto.py

REM Keep window open if there's an error
if errorlevel 1 pause
'''
            
            with open(self.batch_file, 'w') as f:
                f.write(batch_content)
            
            # Copy to startup folder
            startup_link = os.path.join(self.startup_folder, 'Voice Assistant.bat')
            shutil.copy2(self.batch_file, startup_link)
            
            messagebox.showinfo("Success!", 
                              f"Voice assistant configured for auto-start!\n\n"
                              f"Location: {startup_link}\n\n"
                              f"The assistant will start automatically when you log in to Windows.\n"
                              f"Restart your computer to test it!")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to setup auto-start: {e}")
            
    def setup_registry(self):
        """Setup auto-start using Windows registry"""
        try:
            # Create the command to run
            command = f'cmd /c "cd /d "{self.current_dir}" && call venv\\Scripts\\activate.bat && py wake_word_assistant_auto.py"'
            
            # Add to registry
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, 
                               r"Software\Microsoft\Windows\CurrentVersion\Run", 
                               0, winreg.KEY_SET_VALUE)
            
            winreg.SetValueEx(key, "VoiceAssistant", 0, winreg.REG_SZ, command)
            winreg.CloseKey(key)
            
            messagebox.showinfo("Success!", 
                              "Voice assistant added to Windows registry for auto-start!\n\n"
                              "The assistant will start automatically when Windows boots.\n"
                              "Restart your computer to test it!")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to setup registry auto-start: {e}\n\n"
                                        "You may need to run this as administrator.")
            
    def remove_startup(self):
        """Remove voice assistant from startup"""
        removed = False
        
        try:
            # Remove from startup folder
            startup_link = os.path.join(self.startup_folder, 'Voice Assistant.bat')
            if os.path.exists(startup_link):
                os.remove(startup_link)
                removed = True
                
            # Remove from registry
            try:
                key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, 
                                   r"Software\Microsoft\Windows\CurrentVersion\Run", 
                                   0, winreg.KEY_SET_VALUE)
                winreg.DeleteValue(key, "VoiceAssistant")
                winreg.CloseKey(key)
                removed = True
            except FileNotFoundError:
                pass  # Not in registry
                
            if removed:
                messagebox.showinfo("Success!", "Voice assistant removed from Windows startup.")
            else:
                messagebox.showinfo("Info", "Voice assistant was not configured for auto-start.")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to remove auto-start: {e}")
            
    def open_startup_folder(self):
        """Open the Windows startup folder"""
        try:
            os.startfile(self.startup_folder)
        except Exception as e:
            messagebox.showerror("Error", f"Could not open startup folder: {e}")
            
    def run(self):
        """Start the setup GUI"""
        self.root.mainloop()

if __name__ == "__main__":
    try:
        setup = WindowsStartupSetup()
        setup.run()
    except Exception as e:
        print(f"Error: {e}")
        input("Press Enter to exit...")