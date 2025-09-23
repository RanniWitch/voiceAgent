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
        
        # Test button
        ttk.Button(button_frame, text="🧪 Test Selected Microphone", 
                  command=self.test_microphone, width=25).pack(pady=(0, 5))
        
        # Save button (prominent)
        save_button = ttk.Button(button_frame, text="💾 Save Selection", 
                                command=self.save_selection, width=25)
        save_button.pack(pady=(0, 5))
        
        # Refresh button
        ttk.Button(button_frame, text="🔄 Refresh List", 
                  command=self.populate_microphones, width=25).pack(pady=(0, 5))
        
        # Status label
        self.status_label = ttk.Label(button_frame, text="Select a microphone and test it first", 
                                     font=("Arial", 9), foreground="blue")
        self.status_label.pack(pady=(10, 0))
        
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
            # Test the microphone with more sensitive settings
            test_mic = None
            test_recognizer = sr.Recognizer()
            
            # Make it more sensitive for testing
            test_recognizer.energy_threshold = 300  # Lower = more sensitive
            test_recognizer.dynamic_energy_threshold = True
            test_recognizer.pause_threshold = 0.5
            
            messagebox.showinfo("Testing", "🎤 Speak loudly and clearly for 5 seconds!\n\nSay something like 'Hello, this is a test'")
            
            try:
                test_mic = sr.Microphone(device_index=mic_index)
                
                with test_mic as source:
                    print(f"🎤 Testing microphone {mic_index}...")
                    # Quick ambient noise adjustment
                    test_recognizer.adjust_for_ambient_noise(source, duration=0.3)
                    print(f"🎤 Energy threshold: {test_recognizer.energy_threshold}")
                    
                    # Listen for longer with more sensitive settings
                    audio = test_recognizer.listen(source, timeout=6, phrase_time_limit=5)
                    print("🎤 Audio captured, processing...")
                    
                # Try to recognize
                try:
                    text = test_recognizer.recognize_google(audio)
                    messagebox.showinfo("Test Result", f"✅ Microphone working perfectly!\n\nHeard: '{text}'\n\nClick 'Save Selection' to use this microphone.")
                    self.selected_mic_index = mic_index
                except sr.UnknownValueError:
                    messagebox.showinfo("Test Result", "✅ Microphone detected audio but couldn't understand speech.\n\nThis usually means the microphone is working but the audio wasn't clear enough.\n\nClick 'Save Selection' if you want to use this microphone anyway.")
                    self.selected_mic_index = mic_index
                except sr.RequestError as e:
                    messagebox.showerror("Network Error", f"❌ Could not connect to speech recognition service: {e}\n\nBut the microphone captured audio successfully!")
                    self.selected_mic_index = mic_index
                    
            except sr.WaitTimeoutError:
                messagebox.showwarning("No Audio", "❌ No audio detected.\n\nMake sure:\n• Microphone is not muted\n• You're speaking loudly\n• The correct microphone is selected")
            except Exception as mic_error:
                messagebox.showerror("Microphone Error", f"❌ Could not access microphone {mic_index}:\n{mic_error}\n\nThis microphone may be in use by another application or not available.")
            finally:
                # Safely close microphone if it was opened
                if test_mic is not None:
                    try:
                        if hasattr(test_mic, 'stream') and test_mic.stream is not None:
                            test_mic.stream.close()
                    except:
                        pass
                        
        except Exception as e:
            messagebox.showerror("Test Failed", f"❌ Microphone test failed: {e}\n\nTry using the simple microphone test instead:\npy simple_microphone_test.py")
            
    def save_selection(self):
        """Save the microphone selection"""
        selection = self.mic_listbox.curselection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a microphone from the list first.")
            return
            
        # Use the selected microphone even if not tested
        mic_index = selection[0]
        
        try:
            # Save to config file
            mic_names = sr.Microphone.list_microphone_names()
            config = {
                'microphone_index': mic_index,
                'microphone_name': mic_names[mic_index]
            }
            
            with open('microphone_config.json', 'w') as f:
                json.dump(config, f, indent=2)
                
            self.status_label.config(text="✅ Saved! Restart voice assistant to use new microphone.", 
                                   foreground="green")
            
            messagebox.showinfo("Saved Successfully", 
                              f"✅ Microphone selection saved!\n\n"
                              f"Selected: {config['microphone_name']}\n\n"
                              f"🔄 Restart your voice assistant to use the new microphone.\n\n"
                              f"💡 Tip: Avoid microphones with 'Stereo Mix' or 'What U Hear' to prevent voice chat interference.")
            
        except Exception as e:
            messagebox.showerror("Save Failed", f"Could not save selection: {e}")
            self.status_label.config(text="❌ Save failed", foreground="red")
            
    def run(self):
        """Start the application"""
        self.root.mainloop()

if __name__ == "__main__":
    app = MicrophoneSelector()
    app.run()