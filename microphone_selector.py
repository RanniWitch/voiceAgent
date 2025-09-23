#!/usr/bin/env python3
"""
Microphone Selector Tool
Help users select the correct microphone to avoid picking up voice chat audio
"""

import speech_recognition as sr
import tkinter as tk
from tkinter import ttk, messagebox
import json
import os

class MicrophoneSelector:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Microphone Selector")
        self.root.geometry("600x400")
        
        self.recognizer = sr.Recognizer()
        self.selected_mic_index = None
        
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the UI"""
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, text="🎤 Select Your Microphone", 
                               font=("Arial", 16, "bold"))
        title_label.pack(pady=(0, 20))
        
        # Instructions
        instructions = """To avoid picking up voice chat audio:
1. Select your physical microphone (not "Stereo Mix" or "What U Hear")
2. Test the microphone by speaking
3. Save your selection"""
        
        ttk.Label(main_frame, text=instructions, font=("Arial", 10), 
                 justify=tk.LEFT).pack(pady=(0, 20))
        
        # Microphone list
        list_frame = ttk.LabelFrame(main_frame, text="Available Microphones", padding="10")
        list_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        # Listbox with scrollbar
        list_container = ttk.Frame(list_frame)
        list_container.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(list_container)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.mic_listbox = tk.Listbox(list_container, yscrollcommand=scrollbar.set,
                                     font=("Arial", 10))
        self.mic_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.mic_listbox.yview)
        
        # Populate microphone list
        self.populate_microphones()
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(button_frame, text="🧪 Test Selected Microphone", 
                  command=self.test_microphone).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(button_frame, text="💾 Save Selection", 
                  command=self.save_selection).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(button_frame, text="🔄 Refresh List", 
                  command=self.populate_microphones).pack(side=tk.LEFT)
        
    def populate_microphones(self):
        """Populate the microphone list"""
        self.mic_listbox.delete(0, tk.END)
        
        try:
            mic_names = sr.Microphone.list_microphone_names()
            for index, name in enumerate(mic_names):
                # Highlight potentially problematic sources
                if any(term in name.lower() for term in ['stereo mix', 'what u hear', 'wave out', 'speakers']):
                    display_name = f"{index}: {name} ⚠️ (May pick up system audio)"
                else:
                    display_name = f"{index}: {name}"
                
                self.mic_listbox.insert(tk.END, display_name)
                
        except Exception as e:
            messagebox.showerror("Error", f"Could not list microphones: {e}")
            
    def test_microphone(self):
        """Test the selected microphone"""
        selection = self.mic_listbox.curselection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a microphone first.")
            return
            
        mic_index = selection[0]
        
        try:
            # Test the microphone
            test_mic = sr.Microphone(device_index=mic_index)
            
            messagebox.showinfo("Testing", "Speak now for 3 seconds to test the microphone...")
            
            with test_mic as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                audio = self.recognizer.listen(source, timeout=3, phrase_time_limit=3)
                
            # Try to recognize
            try:
                text = self.recognizer.recognize_google(audio)
                messagebox.showinfo("Test Result", f"✅ Microphone working!\n\nHeard: '{text}'")
                self.selected_mic_index = mic_index
            except sr.UnknownValueError:
                messagebox.showinfo("Test Result", "✅ Microphone detected audio but couldn't understand speech.\n\nThis is normal - the microphone is working.")
                self.selected_mic_index = mic_index
                
        except Exception as e:
            messagebox.showerror("Test Failed", f"❌ Microphone test failed: {e}")
            
    def save_selection(self):
        """Save the microphone selection"""
        if self.selected_mic_index is None:
            messagebox.showwarning("No Selection", "Please test a microphone first.")
            return
            
        try:
            # Save to config file
            config = {
                'microphone_index': self.selected_mic_index,
                'microphone_name': sr.Microphone.list_microphone_names()[self.selected_mic_index]
            }
            
            with open('microphone_config.json', 'w') as f:
                json.dump(config, f, indent=2)
                
            messagebox.showinfo("Saved", f"✅ Microphone selection saved!\n\nSelected: {config['microphone_name']}\n\nRestart your voice assistant to use the new microphone.")
            
        except Exception as e:
            messagebox.showerror("Save Failed", f"Could not save selection: {e}")
            
    def run(self):
        """Start the application"""
        self.root.mainloop()

if __name__ == "__main__":
    app = MicrophoneSelector()
    app.run()