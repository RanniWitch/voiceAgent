#!/usr/bin/env python3
"""
Wake Word System Launcher
Choose between training a custom wake word or using the assistant
"""

import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import sys
import os

class WakeWordLauncher:
    def __init__(self):
        self.setup_gui()
        
    def check_custom_model(self):
        """Check if a custom wake word model exists"""
        try:
            if os.path.exists('custom_wake_word_model.pkl'):
                import pickle
                with open('custom_wake_word_model.pkl', 'rb') as f:
                    model = pickle.load(f)
                    
                if model.get('trained', False):
                    return True, model.get('word', 'Unknown')
            return False, None
        except:
            return False, None
            
    def setup_gui(self):
        """Setup the launcher GUI"""
        self.root = tk.Tk()
        self.root.title("Wake Word System Launcher")
        self.root.geometry("600x500")
        self.root.resizable(False, False)
        
        # Main frame
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, text="Wake Word Voice Assistant", 
                              font=("Arial", 18, "bold"))
        title_label.pack(pady=(0, 20))
        
        # Check for existing model
        has_model, wake_word = self.check_custom_model()
        
        if has_model:
            status_text = f"✅ Custom wake word trained: '{wake_word}'"
            status_color = "green"
        else:
            status_text = "⚠️ No custom wake word trained (will use generic wake words)"
            status_color = "orange"
            
        status_label = ttk.Label(main_frame, text=status_text, 
                               font=("Arial", 11))
        status_label.pack(pady=(0, 30))
        
        # Training section
        training_frame = ttk.LabelFrame(main_frame, text="🎓 Train Custom Wake Word", padding="20")
        training_frame.pack(fill=tk.X, pady=(0, 20))
        
        training_desc = """Create your own personalized wake word:
• Type any word or phrase you want
• Say it 3 times to train the AI
• Much more accurate than generic wake words
• Only responds to YOUR voice and pronunciation"""
        
        ttk.Label(training_frame, text=training_desc, 
                 font=("Arial", 10), justify=tk.LEFT).pack(anchor=tk.W, pady=(0, 15))
        
        ttk.Button(training_frame, text="🎤 Train Custom Wake Word", 
                  command=self.launch_trainer, width=30).pack()
        
        # Assistant section
        assistant_frame = ttk.LabelFrame(main_frame, text="🎤 Use Voice Assistant", padding="20")
        assistant_frame.pack(fill=tk.X, pady=(0, 20))
        
        if has_model:
            assistant_desc = f"""Start the always-listening voice assistant:
• Responds to your custom wake word: '{wake_word}'
• Say '{wake_word}' followed by any command
• Opens websites, answers questions, controls system
• Trained specifically for your voice"""
        else:
            assistant_desc = """Start the always-listening voice assistant:
• Uses generic wake words: 'Hey Assistant', 'Computer'
• Say wake word followed by any command
• Opens websites, answers questions, controls system
• Train a custom wake word for better accuracy"""
        
        ttk.Label(assistant_frame, text=assistant_desc, 
                 font=("Arial", 10), justify=tk.LEFT).pack(anchor=tk.W, pady=(0, 15))
        
        ttk.Button(assistant_frame, text="🚀 Start Voice Assistant", 
                  command=self.launch_assistant, width=30).pack()
        
        # Examples section
        examples_frame = ttk.LabelFrame(main_frame, text="💡 Example Commands", padding="20")
        examples_frame.pack(fill=tk.X)
        
        if has_model:
            examples_text = f"""After saying '{wake_word}':
• "What time is it?"
• "Open YouTube"
• "Tell me a joke"
• "What is 5 plus 3?"
• "Explain quantum physics"
• "Open calculator"
• "Go to Google"
• "Goodbye" (stops listening)"""
        else:
            examples_text = """After saying 'Hey Assistant' or 'Computer':
• "What time is it?"
• "Open YouTube"
• "Tell me a joke"
• "What is 5 plus 3?"
• "Explain quantum physics"
• "Open calculator"
• "Go to Google"
• "Goodbye" (stops listening)"""
        
        ttk.Label(examples_frame, text=examples_text, 
                 font=("Consolas", 9), justify=tk.LEFT).pack(anchor=tk.W)
        
    def launch_trainer(self):
        """Launch the wake word trainer"""
        try:
            subprocess.Popen(["py", "custom_wake_word_trainer.py"])
            messagebox.showinfo("Trainer Launched", 
                              "Custom Wake Word Trainer opened in a new window.\n\n"
                              "After training, restart this launcher to see your new wake word.")
        except Exception as e:
            messagebox.showerror("Launch Error", f"Could not launch trainer: {e}")
            
    def launch_assistant(self):
        """Launch the wake word assistant"""
        try:
            subprocess.Popen(["py", "wake_word_assistant.py"])
            messagebox.showinfo("Assistant Launched", 
                              "Wake Word Assistant opened in a new window.\n\n"
                              "Click 'Start Wake Word Detection' to begin always-listening mode.")
        except Exception as e:
            messagebox.showerror("Launch Error", f"Could not launch assistant: {e}")
            
    def run(self):
        """Start the launcher"""
        self.root.mainloop()

if __name__ == "__main__":
    try:
        launcher = WakeWordLauncher()
        launcher.run()
    except KeyboardInterrupt:
        print("\nLauncher stopped")
    except Exception as e:
        print(f"Error: {e}")