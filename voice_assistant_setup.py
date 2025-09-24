#!/usr/bin/env python3
"""
Voice Assistant Setup & Launcher
First-run setup for downloadable voice assistant package
"""

import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import os
import json
import sys

class VoiceAssistantSetup:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Voice Assistant Setup")
        self.root.geometry("600x500")
        self.root.resizable(False, False)
        
        # Center the window
        self.center_window()
        
        # Check if this is first run
        self.is_first_run = not os.path.exists('custom_wake_word_model.pkl')
        
        self.setup_ui()
        
    def center_window(self):
        """Center the window on screen"""
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (600 // 2)
        y = (self.root.winfo_screenheight() // 2) - (500 // 2)
        self.root.geometry(f"600x500+{x}+{y}")
        
    def setup_ui(self):
        """Setup the main UI"""
        # Main container
        main_frame = ttk.Frame(self.root, padding="30")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, text="🎤 Voice Assistant Setup", 
                               font=("Arial", 18, "bold"))
        title_label.pack(pady=(0, 20))
        
        if self.is_first_run:
            self.setup_first_run_ui(main_frame)
        else:
            self.setup_main_menu_ui(main_frame)
            
    def setup_first_run_ui(self, parent):
        """Setup UI for first-time users"""
        # Welcome message
        welcome_text = """Welcome to your Personal Voice Assistant!
        
This assistant can:
• Answer questions and have conversations
• Open websites and applications
• Control your computer with voice commands
• Search the web and get real-time information

Let's get you set up in 2 easy steps:"""
        
        welcome_label = ttk.Label(parent, text=welcome_text, 
                                 font=("Arial", 11), justify=tk.LEFT)
        welcome_label.pack(pady=(0, 30))
        
        # Step 1: Train Wake Word
        step1_frame = ttk.LabelFrame(parent, text="Step 1: Create Your Wake Word", padding="20")
        step1_frame.pack(fill=tk.X, pady=(0, 20))
        
        step1_text = """Train a custom wake word (like "Hey Assistant" or "Computer Sarah"):
• More accurate than generic wake words
• Responds only to your voice
• Takes just 30 seconds to train"""
        
        ttk.Label(step1_frame, text=step1_text, font=("Arial", 10), 
                 justify=tk.LEFT).pack(anchor=tk.W, pady=(0, 15))
        
        ttk.Button(step1_frame, text="🎓 Train My Wake Word", 
                  command=self.train_wake_word, width=25).pack()
        
        # Step 2: Auto-start Setup
        step2_frame = ttk.LabelFrame(parent, text="Step 2: Enable Auto-Start (Optional)", padding="20")
        step2_frame.pack(fill=tk.X, pady=(0, 20))
        
        step2_text = """Make your assistant start automatically when Windows boots:
• Always ready to help
• Runs quietly in the background
• Can be disabled anytime"""
        
        ttk.Label(step2_frame, text=step2_text, font=("Arial", 10), 
                 justify=tk.LEFT).pack(anchor=tk.W, pady=(0, 15))
        
        ttk.Button(step2_frame, text="⚙️ Setup Auto-Start", 
                  command=self.setup_auto_start, width=25).pack()
        
        # Skip setup button
        skip_frame = ttk.Frame(parent)
        skip_frame.pack(fill=tk.X, pady=(20, 0))
        
        ttk.Button(skip_frame, text="Skip Setup - Start Assistant Now", 
                  command=self.start_assistant).pack()
        
    def setup_main_menu_ui(self, parent):
        """Setup UI for returning users"""
        # Status
        status_text = self.get_current_status()
        status_label = ttk.Label(parent, text=status_text, font=("Arial", 11), 
                                justify=tk.LEFT)
        status_label.pack(pady=(0, 30))
        
        # Main actions
        actions_frame = ttk.LabelFrame(parent, text="Quick Actions", padding="20")
        actions_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Start Assistant buttons (prominent)
        ttk.Button(actions_frame, text="🚀 Start Voice Assistant", 
                  command=self.start_assistant, width=30).pack(pady=(0, 10))
        
        ttk.Button(actions_frame, text="🎨 Start Visual Assistant", 
                  command=self.start_visual_assistant, width=30).pack(pady=(0, 15))
        
        # Other actions
        button_frame = ttk.Frame(actions_frame)
        button_frame.pack(fill=tk.X)
        
        ttk.Button(button_frame, text="🎓 Train New Wake Word", 
                  command=self.train_wake_word, width=20).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(button_frame, text="⚙️ Auto-Start Settings", 
                  command=self.setup_auto_start, width=20).pack(side=tk.LEFT)
        
        # Advanced options
        advanced_frame = ttk.LabelFrame(parent, text="Advanced Options", padding="20")
        advanced_frame.pack(fill=tk.X, pady=(20, 0))
        
        advanced_button_frame = ttk.Frame(advanced_frame)
        advanced_button_frame.pack(fill=tk.X)
        
        ttk.Button(advanced_button_frame, text="🔧 Test Microphone", 
                  command=self.test_microphone, width=15).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(advanced_button_frame, text="📋 View Logs", 
                  command=self.view_logs, width=15).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(advanced_button_frame, text="❓ Help", 
                  command=self.show_help, width=15).pack(side=tk.LEFT)
        
    def get_current_status(self):
        """Get current system status"""
        status_lines = ["Current Status:"]
        
        # Check wake word
        if os.path.exists('custom_wake_word_model.pkl'):
            try:
                with open('custom_wake_word_model.pkl', 'rb') as f:
                    import pickle
                    model = pickle.load(f)
                    wake_word = model.get('word', 'Unknown')
                    status_lines.append(f"✅ Custom wake word trained: '{wake_word}'")
            except:
                status_lines.append("⚠️ Wake word model found but corrupted")
        else:
            status_lines.append("⚠️ No custom wake word trained (will use generic)")
        
        # Check auto-start
        startup_folder = os.path.expanduser("~\\AppData\\Roaming\\Microsoft\\Windows\\Start Menu\\Programs\\Startup")
        if os.path.exists(os.path.join(startup_folder, "VoiceAssistant.bat")):
            status_lines.append("✅ Auto-start enabled")
        else:
            status_lines.append("⚠️ Auto-start not configured")
            
        return "\n".join(status_lines)
        
    def train_wake_word(self):
        """Launch wake word trainer"""
        try:
            subprocess.Popen([sys.executable, "custom_wake_word_trainer.py"])
            messagebox.showinfo("Wake Word Trainer", 
                              "Opening Wake Word Trainer...\n\n"
                              "After training, restart this setup to see your new wake word.")
        except Exception as e:
            messagebox.showerror("Error", f"Could not open wake word trainer: {e}")
            
    def setup_auto_start(self):
        """Launch auto-start setup"""
        try:
            subprocess.Popen([sys.executable, "setup_windows_startup.py"])
            messagebox.showinfo("Auto-Start Setup", 
                              "Opening Auto-Start Setup...\n\n"
                              "Follow the instructions to enable automatic startup.")
        except Exception as e:
            messagebox.showerror("Error", f"Could not open auto-start setup: {e}")
            
    def start_assistant(self):
        """Start the voice assistant"""
        try:
            # Check if wake word is trained
            if not os.path.exists('custom_wake_word_model.pkl'):
                result = messagebox.askyesno("No Wake Word Trained", 
                                           "You haven't trained a custom wake word yet.\n\n"
                                           "The assistant will use generic wake words like 'hey assistant'.\n\n"
                                           "Do you want to continue anyway?")
                if not result:
                    return
            
            # Start the assistant
            subprocess.Popen([sys.executable, "wake_word_assistant.py"])
            messagebox.showinfo("Assistant Started", 
                              "Voice Assistant is starting...\n\n"
                              "Look for the assistant window or check your system tray.")
            
            # Close setup window
            self.root.destroy()
            
        except Exception as e:
            messagebox.showerror("Error", f"Could not start assistant: {e}")
    
    def start_visual_assistant(self):
        """Start the visual voice assistant"""
        try:
            # Check if wake word is trained
            if not os.path.exists('custom_wake_word_model.pkl'):
                result = messagebox.askyesno("No Wake Word Trained", 
                                           "You haven't trained a custom wake word yet.\n\n"
                                           "The visual assistant will use generic wake words like 'hey assistant'.\n\n"
                                           "Do you want to continue anyway?")
                if not result:
                    return
            
            # Start the visual assistant
            subprocess.Popen([sys.executable, "voice_visualizer.py"])
            messagebox.showinfo("Visual Assistant Started", 
                              "🎨 Visual Voice Assistant is starting...\n\n"
                              "Enjoy the beautiful Siri-like waveform visualization!\n"
                              "The assistant will show real-time audio waves as you speak.")
            
            # Close setup window
            self.root.destroy()
            
        except Exception as e:
            messagebox.showerror("Error", f"Could not start visual assistant: {e}")
            
    def test_microphone(self):
        """Test microphone functionality"""
        try:
            subprocess.Popen([sys.executable, "simple_mic_test.py"])
            messagebox.showinfo("Microphone Test", 
                              "Opening microphone test...\n\n"
                              "Follow the instructions to test your microphone.")
        except Exception as e:
            messagebox.showerror("Error", f"Could not open microphone test: {e}")
            
    def view_logs(self):
        """View system logs"""
        messagebox.showinfo("Logs", "Log viewing feature coming soon!")
        
    def show_help(self):
        """Show help information"""
        help_text = """Voice Assistant Help:

WAKE WORDS:
• Train a custom wake word for best accuracy
• Generic wake words: 'hey assistant', 'computer', 'hey computer'

COMMANDS:
• "What time is it?"
• "Open YouTube"
• "Search for Python tutorials"
• "What's the weather?"
• "Tell me a joke"

TROUBLESHOOTING:
• Make sure your microphone is working
• Train a custom wake word for better recognition
• Check that the assistant window isn't minimized

For more help, check the README.md file."""
        
        messagebox.showinfo("Help", help_text)
        
    def run(self):
        """Start the setup application"""
        self.root.mainloop()

if __name__ == "__main__":
    app = VoiceAssistantSetup()
    app.run()