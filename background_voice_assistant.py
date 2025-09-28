#!/usr/bin/env python3
"""
Background Voice Assistant
Runs silently in background, shows beautiful visualizer only when wake word is detected
"""

import tkinter as tk
from tkinter import ttk
import numpy as np
import threading
import time
import math
import speech_recognition as sr
import queue
import json
import os
import sys
from wake_word_assistant import WakeWordAssistant

class BackgroundVoiceAssistant:
    def __init__(self):
        self.audio_queue = queue.Queue()
        self.is_running = True
        self.visualizer_window = None
        
        # Voice assistant
        self.assistant = None
        self.setup_assistant()
        
        # Screen recorder
        self.screen_recorder = None
        self.setup_screen_recorder()
        
        # App launcher
        self.app_launcher = None
        self.setup_app_launcher()
        
        # Create system tray icon (simple approach)
        self.create_tray_icon()
        
        # Start background listening
        self.start_background_listening()
        
    def setup_assistant(self):
        """Setup the voice assistant"""
        try:
            self.assistant = WakeWordAssistant()
            if self.assistant.use_custom_model:
                self.wake_word = self.assistant.custom_wake_word_model['word']
            else:
                self.wake_word = "hey assistant"
            print(f"🎤 Background assistant ready. Wake word: '{self.wake_word}'")
        except Exception as e:
            print(f"Error setting up assistant: {e}")
            self.wake_word = "hey assistant"
    
    def setup_screen_recorder(self):
        """Setup the screen recorder"""
        try:
            from screen_recorder import VoiceControlledRecorder
            self.screen_recorder = VoiceControlledRecorder()
            print("📹 Screen recorder ready - continuous recording started")
        except Exception as e:
            print(f"⚠️ Screen recorder not available: {e}")
            self.screen_recorder = None
    
    def setup_app_launcher(self):
        """Setup the application launcher"""
        try:
            from app_launcher import ApplicationLauncher
            self.app_launcher = ApplicationLauncher()
            print("🚀 App launcher ready - scanned installed applications")
        except Exception as e:
            print(f"⚠️ App launcher not available: {e}")
            self.app_launcher = None
    
    def create_tray_icon(self):
        """Create a simple tray icon window"""
        self.tray_root = tk.Tk()
        self.tray_root.title("Voice Assistant")
        self.tray_root.geometry("300x150")
        self.tray_root.configure(bg='#2C2C2C')
        
        # Position in bottom right corner
        self.tray_root.geometry("+{}+{}".format(
            self.tray_root.winfo_screenwidth() - 320,
            self.tray_root.winfo_screenheight() - 200
        ))
        
        # Make it stay on top but not steal focus
        self.tray_root.attributes('-topmost', True)
        self.tray_root.attributes('-alpha', 0.9)
        
        # Content
        tk.Label(
            self.tray_root,
            text="🎤 Voice Assistant",
            font=("Arial", 14, "bold"),
            fg="#FFFFFF",
            bg="#2C2C2C"
        ).pack(pady=10)
        
        self.status_label = tk.Label(
            self.tray_root,
            text=f"Listening for '{self.wake_word}'...",
            font=("Arial", 10),
            fg="#CCCCCC",
            bg="#2C2C2C"
        )
        self.status_label.pack(pady=5)
        
        # Minimize button
        tk.Button(
            self.tray_root,
            text="Hide",
            command=self.hide_tray,
            bg="#444444",
            fg="#FFFFFF",
            relief="flat"
        ).pack(pady=10)
        
        # Handle window close
        self.tray_root.protocol("WM_DELETE_WINDOW", self.close_app)
        
        # Start minimized
        self.tray_root.withdraw()
    
    def hide_tray(self):
        """Hide the tray window"""
        self.tray_root.withdraw()
    
    def show_tray(self):
        """Show the tray window"""
        self.tray_root.deiconify()
        self.tray_root.lift()
    
    def start_background_listening(self):
        """Start listening in background"""
        def listen_thread():
            recognizer = sr.Recognizer()
            
            # Use saved microphone if available
            mic_index = None
            try:
                with open('microphone_config.json', 'r') as f:
                    config = json.load(f)
                    mic_index = config.get('microphone_index')
                    print(f"Using saved microphone: {mic_index}")
            except FileNotFoundError:
                print("No saved microphone config, using default")
            
            if mic_index is not None:
                microphone = sr.Microphone(device_index=mic_index)
            else:
                microphone = sr.Microphone()
            
            # Configure for wake word detection
            recognizer.energy_threshold = 4000
            recognizer.dynamic_energy_threshold = True
            recognizer.pause_threshold = 0.8
            
            with microphone as source:
                print("🎤 Calibrating microphone...")
                recognizer.adjust_for_ambient_noise(source, duration=1)
                print(f"Energy threshold: {recognizer.energy_threshold}")
            
            print("🎧 Background listening started...")
            
            while self.is_running:
                try:
                    with microphone as source:
                        # Listen for wake word
                        audio = recognizer.listen(source, timeout=1, phrase_time_limit=4)
                        
                        # Process in background thread
                        threading.Thread(
                            target=self.process_wake_word,
                            args=(audio, recognizer),
                            daemon=True
                        ).start()
                        
                except sr.WaitTimeoutError:
                    pass  # Normal timeout, continue listening
                except Exception as e:
                    print(f"Background listening error: {e}")
                    time.sleep(1)
        
        threading.Thread(target=listen_thread, daemon=True).start()
    
    def handle_wake_word_detected(self, text, wake_word):
        """Handle wake word detection on main thread"""
        # Update tray status
        self.status_label.config(text=f"Wake word detected! Opening visualizer...")
        
        # Show visualizer
        self.show_visualizer(text, wake_word)
    
    def process_wake_word(self, audio, recognizer):
        """Process audio for wake word detection"""
        if not self.assistant:
            return
            
        try:
            # Convert audio to text
            text = recognizer.recognize_google(audio)
            
            # Convert audio data for wake word detection
            audio_data = np.frombuffer(audio.get_raw_data(), dtype=np.int16).astype(np.float32)
            
            # Check for wake word
            detected, wake_word = self.assistant.detect_wake_word(text, audio_data)
            
            if detected:
                print(f"🎯 Wake word detected: '{wake_word}' - Opening visualizer...")
                
                # Schedule GUI updates on main thread
                self.tray_root.after(0, self.handle_wake_word_detected, text, wake_word)
                
        except sr.UnknownValueError:
            pass  # Couldn't understand audio - normal
        except sr.RequestError as e:
            print(f"Speech recognition error: {e}")
        except Exception as e:
            print(f"Wake word processing error: {e}")
    
    def show_visualizer(self, initial_text, wake_word):
        """Show the beautiful visualizer window"""
        try:
            if self.visualizer_window and self.visualizer_window.winfo_exists():
                # Visualizer already open, just bring to front
                self.visualizer_window.lift()
                return
        except:
            # Window reference is stale, create new one
            self.visualizer_window = None
        
        # Create visualizer window
        self.visualizer_window = tk.Toplevel()
        self.visualizer_window.title("Voice Assistant - Active")
        self.visualizer_window.geometry("800x600")
        self.visualizer_window.configure(bg='#000000')
        self.visualizer_window.attributes('-topmost', True)
        
        # Center the window
        self.center_window(self.visualizer_window)
        
        # Create visualizer content
        self.setup_visualizer_ui()
        
        # Start visualizer animation
        self.start_visualizer_animation()
        
        # Process the initial command
        command = self.assistant.extract_command_after_wake_word(initial_text, wake_word)
        if command and command.strip():
            self.process_command(command)
        else:
            try:
                self.visualizer_status.config(text="I'm listening. What can I help you with?")
            except:
                pass
            # Listen for follow-up command
            threading.Thread(target=self.listen_for_command, daemon=True).start()
    
    def center_window(self, window):
        """Center window on screen"""
        window.update_idletasks()
        x = (window.winfo_screenwidth() // 2) - (800 // 2)
        y = (window.winfo_screenheight() // 2) - (600 // 2)
        window.geometry(f"800x600+{x}+{y}")
    
    def setup_visualizer_ui(self):
        """Setup the visualizer UI"""
        # Main canvas for visualization
        self.visualizer_canvas = tk.Canvas(
            self.visualizer_window,
            width=800,
            height=400,
            bg="#000000",
            highlightthickness=0
        )
        self.visualizer_canvas.pack(pady=50)
        
        # Status label
        self.visualizer_status = tk.Label(
            self.visualizer_window,
            text="Processing your request...",
            font=("Arial", 16),
            fg="#FFFFFF",
            bg="#000000"
        )
        self.visualizer_status.pack(pady=10)
        
        # Close button (more prominent)
        close_button = tk.Button(
            self.visualizer_window,
            text="✕ Close & Return to Background",
            command=self._immediate_close,
            font=("Arial", 12, "bold"),
            bg="#FF4444",
            fg="#FFFFFF",
            activebackground="#FF6666",
            relief="flat",
            padx=30,
            pady=12
        )
        close_button.pack(pady=20)
        
        # Auto-close info
        tk.Label(
            self.visualizer_window,
            text="(Will auto-close after response)",
            font=("Arial", 9),
            fg="#888888",
            bg="#000000"
        ).pack()
        
        # Handle window close
        self.visualizer_window.protocol("WM_DELETE_WINDOW", self._immediate_close)
        
        # Add keyboard shortcuts
        self.visualizer_window.bind('<Escape>', lambda e: self._immediate_close())
        self.visualizer_window.bind('<Control-w>', lambda e: self._immediate_close())
        
        # Make sure window can receive focus for keyboard events
        self.visualizer_window.focus_set()
        
        # Animation variables
        self.wave_amplitude = 0.5
        self.wave_phase = 0.0
        self.wave_color = "#00FF00"  # Green for active
        self.animation_active = True
    
    def start_visualizer_animation(self):
        """Start the visualizer animation"""
        self.animate_visualizer()
    
    def animate_visualizer(self):
        """Animate the visualizer using Tkinter's after method"""
        if not self.animation_active or not self.visualizer_window:
            return
            
        try:
            if self.visualizer_window.winfo_exists():
                self.wave_phase += 0.15
                self.draw_visualizer_waveform()
                # Schedule next frame
                self.visualizer_window.after(16, self.animate_visualizer)  # ~60 FPS
        except:
            self.animation_active = False
    
    def draw_visualizer_waveform(self):
        """Draw the animated waveform"""
        if not self.visualizer_canvas.winfo_exists():
            return
            
        self.visualizer_canvas.delete("all")
        
        width = 800
        height = 400
        center_y = height // 2
        
        # Draw multiple wave layers
        layers = [
            {"amplitude_mult": 1.0, "frequency_mult": 1.0, "width": 4},
            {"amplitude_mult": 0.7, "frequency_mult": 1.5, "width": 3},
            {"amplitude_mult": 0.4, "frequency_mult": 2.0, "width": 2},
        ]
        
        for layer in layers:
            points = []
            
            for x in range(0, width, 3):
                # Complex wave pattern
                y1 = math.sin((x * 0.02 + self.wave_phase) * layer["frequency_mult"]) * 60
                y2 = math.sin((x * 0.01 + self.wave_phase * 1.3) * layer["frequency_mult"]) * 40
                y3 = math.sin((x * 0.025 + self.wave_phase * 0.8) * layer["frequency_mult"]) * 25
                
                y = (y1 + y2 + y3) * self.wave_amplitude * layer["amplitude_mult"]
                points.extend([x, center_y + y])
            
            if len(points) >= 4:
                self.visualizer_canvas.create_line(
                    points,
                    fill=self.wave_color,
                    width=layer["width"],
                    smooth=True,
                    capstyle=tk.ROUND
                )
        
        # Pulsing center circle
        pulse_size = 8 + 15 * self.wave_amplitude * math.sin(self.wave_phase * 2)
        self.visualizer_canvas.create_oval(
            width//2 - pulse_size, center_y - pulse_size,
            width//2 + pulse_size, center_y + pulse_size,
            fill=self.wave_color,
            outline=""
        )
    
    def listen_for_command(self):
        """Listen for command after wake word"""
        try:
            recognizer = sr.Recognizer()
            
            # Use same microphone setup
            mic_index = None
            try:
                with open('microphone_config.json', 'r') as f:
                    config = json.load(f)
                    mic_index = config.get('microphone_index')
            except FileNotFoundError:
                pass
            
            if mic_index is not None:
                microphone = sr.Microphone(device_index=mic_index)
            else:
                microphone = sr.Microphone()
            
            recognizer.energy_threshold = 300
            recognizer.pause_threshold = 1.0
            
            with microphone as source:
                recognizer.adjust_for_ambient_noise(source, duration=0.2)
            
            # Change color to indicate listening for command
            self.wave_color = "#FFFF00"  # Yellow for listening
            
            with microphone as source:
                audio = recognizer.listen(source, timeout=5, phrase_time_limit=8)
            
            command_text = recognizer.recognize_google(audio)
            print(f"Command: '{command_text}'")
            
            if command_text.strip():
                self.process_command(command_text)
            else:
                self.show_response("I didn't catch that. Please try again.")
                
        except sr.WaitTimeoutError:
            self.show_response("I'm still here. Say my wake word if you need me.")
            # Schedule close on main thread
            try:
                self.tray_root.after(3000, self._immediate_close)
            except:
                threading.Timer(3.0, self._immediate_close).start()
        except sr.UnknownValueError:
            self.show_response("I didn't understand that. Please try again.")
            # Schedule close on main thread
            try:
                self.tray_root.after(3000, self._immediate_close)
            except:
                threading.Timer(3.0, self._immediate_close).start()
        except Exception as e:
            print(f"Command listening error: {e}")
            self.show_response("Sorry, there was an error.")
            # Schedule close on main thread
            try:
                self.tray_root.after(2000, self._immediate_close)
            except:
                threading.Timer(2.0, self._immediate_close).start()
    
    def process_command(self, command):
        """Process the voice command"""
        self.wave_color = "#FFD700"  # Gold for processing
        
        try:
            if self.visualizer_status and self.visualizer_status.winfo_exists():
                self.visualizer_status.config(text=f"Processing: '{command}'")
        except:
            pass
        
        try:
            # Check if it's a screen recording command first
            if self.screen_recorder:
                recording_response = self.screen_recorder.process_recording_command(command)
                if recording_response:
                    self.show_response(recording_response)
                    return
            
            # Check if it's an app launch command
            if self.app_launcher and command.lower().startswith('open '):
                app_name = command[5:].strip()  # Remove "open " prefix
                if app_name:
                    launch_response = self.app_launcher.launch_app(app_name)
                    self.show_response(launch_response)
                    return
            
            # Process as regular command
            response = self.assistant.classify_and_execute_command(command)
            self.show_response(response)
        except Exception as e:
            print(f"Command processing error: {e}")
            self.show_response("Sorry, I couldn't process that command.")
    
    def show_response(self, response):
        """Show the response"""
        self.wave_color = "#FF69B4"  # Pink for response
        response_text = response[:80] + "..." if len(response) > 80 else response
        
        try:
            if self.visualizer_status and self.visualizer_status.winfo_exists():
                self.visualizer_status.config(text=response_text)
        except:
            pass
        
        print(f"Response: {response}")
        
        # Auto-close after response - schedule on main thread
        response_length = len(response)
        if response_length < 30:
            delay = 1500  # 1.5 seconds for short responses
        elif response_length < 60:
            delay = 2000  # 2 seconds for medium responses  
        else:
            delay = 2500  # 2.5 seconds for long responses
        
        # Always schedule close on the main thread
        def schedule_close():
            try:
                if self.tray_root and self.tray_root.winfo_exists():
                    self.tray_root.after(delay, self._immediate_close)
            except:
                # Last resort: force close after delay
                threading.Timer(delay/1000.0, self._immediate_close).start()
        
        # Run the scheduling on main thread
        try:
            self.tray_root.after(0, schedule_close)
        except:
            # Fallback
            threading.Timer(delay/1000.0, self._immediate_close).start()
    
    def _safe_close_visualizer(self):
        """Safely close visualizer with error handling"""
        try:
            self._close_visualizer_safe()
        except:
            # If safe close fails, force close
            self._force_close_visualizer()
    
    def _force_close_visualizer(self):
        """Force close visualizer even if threading issues occur"""
        print("🔄 Force closing visualizer...")
        self.animation_active = False
        
        try:
            if self.visualizer_window:
                print("📱 Destroying visualizer window...")
                # Withdraw window first, then destroy
                self.visualizer_window.withdraw()
                self.visualizer_window.destroy()
                print("✅ Visualizer window destroyed")
        except Exception as e:
            print(f"⚠️ Error destroying visualizer: {e}")
        
        self.visualizer_window = None
        
        # Update tray status safely
        try:
            if hasattr(self, 'status_label') and self.status_label:
                self.status_label.config(text=f"Listening for '{self.wake_word}'...")
                print("📱 Tray status updated")
        except Exception as e:
            print(f"⚠️ Error updating tray: {e}")
        
        print("🎧 Back to background listening...")
    
    def _immediate_close(self):
        """Immediately close visualizer without delays"""
        print("⚡ Immediate close requested")
        self.animation_active = False
        
        if self.visualizer_window:
            try:
                # Stop any pending after() calls
                self.visualizer_window.after_cancel('all')
            except:
                pass
            
            try:
                # Hide window immediately
                self.visualizer_window.withdraw()
                # Then destroy it
                self.visualizer_window.destroy()
                print("✅ Window immediately closed")
            except Exception as e:
                print(f"⚠️ Error in immediate close: {e}")
        
        self.visualizer_window = None
        
        # Update tray
        try:
            if hasattr(self, 'status_label') and self.status_label:
                self.status_label.config(text=f"Listening for '{self.wake_word}'...")
        except:
            pass
        
        print("🎧 Returned to background listening")
    
    def close_visualizer(self):
        """Close the visualizer window"""
        # Schedule on main thread
        if self.visualizer_window:
            try:
                self.visualizer_window.after(0, self._close_visualizer_safe)
            except:
                self._close_visualizer_safe()
        else:
            self._close_visualizer_safe()
    
    def _close_visualizer_safe(self):
        """Safely close visualizer on main thread"""
        print("🔄 Safe closing visualizer...")
        self.animation_active = False
        
        try:
            if self.visualizer_window and self.visualizer_window.winfo_exists():
                print("📱 Window exists, destroying...")
                # Withdraw window first, then destroy
                self.visualizer_window.withdraw()
                self.visualizer_window.destroy()
                print("✅ Visualizer window destroyed safely")
        except Exception as e:
            print(f"⚠️ Error in safe close: {e}")
        
        self.visualizer_window = None
        
        # Update tray status
        try:
            if hasattr(self, 'status_label') and self.status_label:
                self.status_label.config(text=f"Listening for '{self.wake_word}'...")
                print("📱 Tray status updated")
        except Exception as e:
            print(f"⚠️ Error updating tray in safe close: {e}")
        
        print("🎧 Back to background listening...")
    
    def close_app(self):
        """Close the entire application"""
        self.is_running = False
        self.animation_active = False
        
        if self.visualizer_window and self.visualizer_window.winfo_exists():
            self.visualizer_window.destroy()
        
        self.tray_root.quit()
        self.tray_root.destroy()
        
        print("👋 Voice assistant closed")
    
    def run(self):
        """Start the application"""
        print("🎤 Background Voice Assistant Starting...")
        print(f"Listening for wake word: '{self.wake_word}'")
        print("The visualizer will appear when you say your wake word!")
        print("Right-click the system tray to access settings.")
        
        # Show tray briefly then hide
        self.show_tray()
        self.tray_root.after(3000, self.hide_tray)  # Auto-hide after 3 seconds
        
        self.tray_root.mainloop()

if __name__ == "__main__":
    app = BackgroundVoiceAssistant()
    app.run()