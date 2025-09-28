#!/usr/bin/env python3
"""
Voice Assistant Visualizer
Beautiful Siri-like waveform visualization that responds to voice input
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
from wake_word_assistant import WakeWordAssistant

class VoiceVisualizer:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Voice Assistant - Visual Mode")
        self.root.geometry("800x600")
        self.root.configure(bg='#000000')
        
        # Make window always on top and remove decorations for a modern look
        self.root.attributes('-topmost', True)
        
        # Audio processing
        self.audio_queue = queue.Queue()
        self.is_listening = False
        self.is_processing = False
        self.wake_word_detected = False
        
        # Visualization parameters
        self.wave_amplitude = 0.0
        self.target_amplitude = 0.0
        self.wave_frequency = 1.0
        self.wave_phase = 0.0
        self.wave_color = "#00BFFF"  # Default blue
        self.background_color = "#000000"
        
        # Animation parameters
        self.animation_running = True
        self.pulse_intensity = 0.0
        self.breathing_phase = 0.0
        self.is_paused = False
        
        # Voice assistant
        self.assistant = None
        self.setup_assistant()
        
        self.setup_ui()
        self.start_audio_monitoring()
        self.start_animation()
        
    def setup_assistant(self):
        """Setup the voice assistant"""
        try:
            self.assistant = WakeWordAssistant()
            if self.assistant.use_custom_model:
                self.wake_word = self.assistant.custom_wake_word_model['word']
            else:
                self.wake_word = "hey assistant"
        except Exception as e:
            print(f"Error setting up assistant: {e}")
            self.wake_word = "hey assistant"
    
    def setup_ui(self):
        """Setup the user interface"""
        # Main canvas for visualization
        self.canvas = tk.Canvas(
            self.root, 
            width=800, 
            height=400, 
            bg=self.background_color,
            highlightthickness=0
        )
        self.canvas.pack(pady=50)
        
        # Status label
        self.status_label = tk.Label(
            self.root,
            text=f"Listening for '{self.wake_word}'...",
            font=("Arial", 16),
            fg="#FFFFFF",
            bg="#000000"
        )
        self.status_label.pack(pady=10)
        
        # Control frame
        control_frame = tk.Frame(self.root, bg="#000000")
        control_frame.pack(pady=20)
        
        # Control buttons with modern styling
        button_style = {
            'font': ('Arial', 12),
            'bg': '#333333',
            'fg': '#FFFFFF',
            'activebackground': '#555555',
            'activeforeground': '#FFFFFF',
            'relief': 'flat',
            'padx': 20,
            'pady': 10
        }
        
        self.listen_button = tk.Button(
            control_frame,
            text="🎤 Start Listening",
            command=self.toggle_listening,
            **button_style
        )
        self.listen_button.pack(side=tk.LEFT, padx=10)
        
        self.pause_button = tk.Button(
            control_frame,
            text="⏸️ Pause",
            command=self.pause_listening,
            **button_style
        )
        self.pause_button.pack(side=tk.LEFT, padx=10)
        
        tk.Button(
            control_frame,
            text="⚙️ Settings",
            command=self.show_settings,
            **button_style
        ).pack(side=tk.LEFT, padx=10)
        
        tk.Button(
            control_frame,
            text="❌ Exit",
            command=self.close_app,
            **button_style
        ).pack(side=tk.LEFT, padx=10)
        
        # Bind window close event
        self.root.protocol("WM_DELETE_WINDOW", self.close_app)
    
    def start_audio_monitoring(self):
        """Start monitoring audio input"""
        def audio_thread():
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
            
            # Configure for better wake word detection
            recognizer.energy_threshold = 4000  # Match assistant settings
            recognizer.dynamic_energy_threshold = True
            recognizer.pause_threshold = 0.8
            
            with microphone as source:
                print("Calibrating microphone...")
                recognizer.adjust_for_ambient_noise(source, duration=1)
                print(f"Energy threshold: {recognizer.energy_threshold}")
            
            # Dual-purpose audio processing
            audio_buffer = []
            last_wake_word_check = time.time()
            
            while self.animation_running:
                if self.is_listening and not self.is_paused:
                    try:
                        with microphone as source:
                            # Listen for longer phrases for wake word detection
                            audio = recognizer.listen(source, timeout=1, phrase_time_limit=4)
                            
                            # Calculate audio level for visualization
                            audio_data = np.frombuffer(audio.get_raw_data(), dtype=np.int16)
                            audio_level = np.sqrt(np.mean(audio_data**2)) / 2000.0
                            
                            # Update visualization immediately
                            self.audio_queue.put(('audio_level', audio_level))
                            
                            # Process for wake word detection if enough audio
                            if len(audio_data) > 8000:  # Substantial audio for wake word
                                threading.Thread(
                                    target=self.process_audio_for_wake_word,
                                    args=(audio,),
                                    daemon=True
                                ).start()
                                
                    except sr.WaitTimeoutError:
                        # No audio detected, reduce amplitude
                        self.audio_queue.put(('audio_level', 0.0))
                    except Exception as e:
                        print(f"Audio monitoring error: {e}")
                        time.sleep(0.1)
                else:
                    time.sleep(0.1)
        
        threading.Thread(target=audio_thread, daemon=True).start()
    
    def listen_for_command(self):
        """Listen for a command after wake word is detected"""
        try:
            recognizer = sr.Recognizer()
            
            # Use saved microphone
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
            
            # Configure for command listening
            recognizer.energy_threshold = 300  # More sensitive for commands
            recognizer.pause_threshold = 1.0   # Wait longer for complete command
            
            with microphone as source:
                recognizer.adjust_for_ambient_noise(source, duration=0.2)
                
            print("🎤 Listening for command...")
            self.audio_queue.put(('status', "Listening for command..."))
            
            with microphone as source:
                # Listen for command with longer timeout
                audio = recognizer.listen(source, timeout=5, phrase_time_limit=8)
            
            # Process command
            command_text = recognizer.recognize_google(audio)
            print(f"Command heard: '{command_text}'")
            
            if command_text.strip():
                self.audio_queue.put(('command_detected', command_text))
                
                # Process the command
                response = self.assistant.classify_and_execute_command(command_text)
                print(f"Response: '{response}'")
                self.audio_queue.put(('response', response))
            else:
                self.audio_queue.put(('response', "I didn't catch that. Please try again."))
                
        except sr.WaitTimeoutError:
            print("⏰ No command heard, going back to wake word listening")
            self.audio_queue.put(('response', "I'm still here. Say my wake word if you need me."))
        except sr.UnknownValueError:
            print("❓ Couldn't understand command")
            self.audio_queue.put(('response', "I didn't understand that. Please try again."))
        except Exception as e:
            print(f"❌ Command listening error: {e}")
            self.audio_queue.put(('response', "Sorry, there was an error. Please try again."))
    
    def process_audio_for_wake_word(self, audio):
        """Process audio for wake word detection"""
        if not self.assistant:
            return
            
        try:
            # Convert audio to text
            recognizer = sr.Recognizer()
            text = recognizer.recognize_google(audio)
            print(f"Heard: '{text}'")
            
            # Convert audio data to numpy array for wake word detection
            audio_data = np.frombuffer(audio.get_raw_data(), dtype=np.int16).astype(np.float32)
            
            # Check for wake word
            detected, wake_word = self.assistant.detect_wake_word(text, audio_data)
            
            if detected:
                print(f"✅ Wake word detected: '{wake_word}'")
                self.audio_queue.put(('wake_word_detected', wake_word))
                
                # Extract command after wake word
                command = self.assistant.extract_command_after_wake_word(text, wake_word)
                if command and command.strip():
                    print(f"Command: '{command}'")
                    self.audio_queue.put(('command_detected', command))
                    
                    # Process command
                    response = self.assistant.classify_and_execute_command(command)
                    print(f"Response: '{response}'")
                    self.audio_queue.put(('response', response))
                else:
                    # Just wake word, no command - listen for follow-up
                    print("Wake word detected, listening for command...")
                    self.audio_queue.put(('awaiting_command', wake_word))
                    # Start listening for command
                    threading.Thread(target=self.listen_for_command, daemon=True).start()
                    
        except sr.UnknownValueError:
            # Don't spam console with "couldn't understand" messages
            pass
        except sr.RequestError as e:
            print(f"❌ Speech recognition error: {e}")
        except Exception as e:
            print(f"❌ Wake word processing error: {e}")
    
    def start_animation(self):
        """Start the visualization animation"""
        def animate():
            while self.animation_running:
                # Process audio queue
                try:
                    while True:
                        event_type, data = self.audio_queue.get_nowait()
                        
                        if event_type == 'audio_level':
                            self.target_amplitude = min(1.0, data * 2.0)
                        elif event_type == 'wake_word_detected':
                            self.wake_word_detected = True
                            self.wave_color = "#00FF00"  # Green for wake word
                            self.root.after(0, lambda: self.status_label.config(
                                text=f"Wake word detected: '{data}'"
                            ))
                        elif event_type == 'awaiting_command':
                            self.wave_color = "#FFFF00"  # Yellow for awaiting command
                            self.root.after(0, lambda: self.status_label.config(
                                text="Listening for your command..."
                            ))
                        elif event_type == 'command_detected':
                            self.wave_color = "#FFD700"  # Gold for command
                            self.root.after(0, lambda: self.status_label.config(
                                text=f"Processing: '{data}'"
                            ))
                        elif event_type == 'response':
                            self.wave_color = "#FF69B4"  # Pink for response
                            response_text = data[:60] + "..." if len(data) > 60 else data
                            self.root.after(0, lambda: self.status_label.config(
                                text=f"{response_text}"
                            ))
                            # Reset after response
                            threading.Timer(4.0, self.reset_visualization).start()
                        elif event_type == 'status':
                            self.root.after(0, lambda: self.status_label.config(text=data))
                            
                except queue.Empty:
                    pass
                
                # Update animation
                self.update_visualization()
                time.sleep(1/60)  # 60 FPS
        
        threading.Thread(target=animate, daemon=True).start()
    
    def update_visualization(self):
        """Update the waveform visualization"""
        # Smooth amplitude transitions
        self.wave_amplitude += (self.target_amplitude - self.wave_amplitude) * 0.1
        
        # Update wave parameters
        self.wave_phase += 0.1
        self.breathing_phase += 0.05
        
        # Calculate breathing effect when idle
        if not self.is_listening:
            breathing_amplitude = 0.1 + 0.05 * math.sin(self.breathing_phase)
            self.wave_amplitude = max(self.wave_amplitude, breathing_amplitude)
        
        # Draw waveform
        self.root.after(0, self.draw_waveform)
    
    def draw_waveform(self):
        """Draw the animated waveform"""
        self.canvas.delete("all")
        
        width = 800
        height = 400
        center_y = height // 2
        
        # Draw multiple wave layers for depth
        layers = [
            {"amplitude_mult": 1.0, "frequency_mult": 1.0, "alpha": 1.0},
            {"amplitude_mult": 0.7, "frequency_mult": 1.5, "alpha": 0.6},
            {"amplitude_mult": 0.4, "frequency_mult": 2.0, "alpha": 0.3},
        ]
        
        for layer in layers:
            points = []
            
            # Generate wave points
            for x in range(0, width, 2):
                # Multiple sine waves for complexity
                y1 = math.sin((x * 0.02 + self.wave_phase) * layer["frequency_mult"]) * 50
                y2 = math.sin((x * 0.01 + self.wave_phase * 1.5) * layer["frequency_mult"]) * 30
                y3 = math.sin((x * 0.03 + self.wave_phase * 0.7) * layer["frequency_mult"]) * 20
                
                # Combine waves and apply amplitude
                y = (y1 + y2 + y3) * self.wave_amplitude * layer["amplitude_mult"]
                
                points.extend([x, center_y + y])
            
            # Draw the wave
            if len(points) >= 4:
                # Calculate color with alpha
                color = self.wave_color
                if layer["alpha"] < 1.0:
                    # Simulate alpha by blending with background
                    color = self.blend_colors(color, self.background_color, layer["alpha"])
                
                self.canvas.create_line(
                    points,
                    fill=color,
                    width=3,
                    smooth=True,
                    capstyle=tk.ROUND
                )
        
        # Draw center indicator
        if self.is_listening:
            # Pulsing center dot
            pulse_size = 5 + 10 * self.wave_amplitude
            self.canvas.create_oval(
                width//2 - pulse_size, center_y - pulse_size,
                width//2 + pulse_size, center_y + pulse_size,
                fill=self.wave_color,
                outline=""
            )
    
    def blend_colors(self, color1, color2, alpha):
        """Blend two hex colors with alpha"""
        # Simple color blending (not perfect but good enough)
        return color1  # For simplicity, just return the main color
    
    def toggle_listening(self):
        """Toggle listening state"""
        self.is_listening = not self.is_listening
        
        if self.is_listening:
            self.listen_button.config(text="🔇 Stop Listening")
            self.status_label.config(text=f"Listening for '{self.wake_word}'...")
            self.wave_color = "#00BFFF"  # Blue for listening
            self.is_paused = False
            self.pause_button.config(text="⏸️ Pause")
        else:
            self.listen_button.config(text="🎤 Start Listening")
            self.status_label.config(text="Click 'Start Listening' to begin")
            self.wave_color = "#666666"  # Gray for idle
            self.is_paused = False
    
    def pause_listening(self):
        """Pause/resume listening without stopping"""
        if not self.is_listening:
            return
            
        self.is_paused = not self.is_paused
        
        if self.is_paused:
            self.pause_button.config(text="▶️ Resume")
            self.status_label.config(text="Paused - Click Resume to continue")
            self.wave_color = "#FFA500"  # Orange for paused
        else:
            self.pause_button.config(text="⏸️ Pause")
            self.status_label.config(text=f"Listening for '{self.wake_word}'...")
            self.wave_color = "#00BFFF"  # Blue for listening
    
    def reset_visualization(self):
        """Reset visualization to listening state"""
        if self.is_listening:
            self.wave_color = "#00BFFF"
            self.wake_word_detected = False
            self.root.after(0, lambda: self.status_label.config(
                text=f"Listening for '{self.wake_word}'..."
            ))
    
    def show_settings(self):
        """Show settings dialog"""
        settings_window = tk.Toplevel(self.root)
        settings_window.title("Settings")
        settings_window.geometry("400x300")
        settings_window.configure(bg="#000000")
        settings_window.attributes('-topmost', True)
        
        # Settings content
        tk.Label(
            settings_window,
            text="Voice Assistant Settings",
            font=("Arial", 16, "bold"),
            fg="#FFFFFF",
            bg="#000000"
        ).pack(pady=20)
        
        # Wake word info
        if self.assistant and self.assistant.use_custom_model:
            wake_word_text = f"Custom wake word: '{self.wake_word}'"
        else:
            wake_word_text = f"Generic wake word: '{self.wake_word}'"
        
        tk.Label(
            settings_window,
            text=wake_word_text,
            font=("Arial", 12),
            fg="#FFFFFF",
            bg="#000000"
        ).pack(pady=10)
        
        # Buttons
        button_frame = tk.Frame(settings_window, bg="#000000")
        button_frame.pack(pady=20)
        
        button_style = {
            'font': ('Arial', 10),
            'bg': '#333333',
            'fg': '#FFFFFF',
            'activebackground': '#555555',
            'activeforeground': '#FFFFFF',
            'relief': 'flat',
            'padx': 15,
            'pady': 8
        }
        
        tk.Button(
            button_frame,
            text="🎓 Train Wake Word",
            command=self.open_wake_word_trainer,
            **button_style
        ).pack(pady=5)
        
        tk.Button(
            button_frame,
            text="🎤 Select Microphone",
            command=self.open_microphone_selector,
            **button_style
        ).pack(pady=5)
        
        tk.Button(
            button_frame,
            text="🔍 Test Wake Word",
            command=self.test_wake_word,
            **button_style
        ).pack(pady=5)
        
        tk.Button(
            button_frame,
            text="✅ Close",
            command=settings_window.destroy,
            **button_style
        ).pack(pady=5)
    
    def test_wake_word(self):
        """Test wake word detection manually"""
        if not self.assistant:
            print("❌ No assistant loaded")
            return
            
        print(f"\n🧪 Testing wake word: '{self.wake_word}'")
        print("Say your wake word now...")
        
        try:
            recognizer = sr.Recognizer()
            
            # Use same microphone as visualizer
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
            
            with microphone as source:
                recognizer.adjust_for_ambient_noise(source, duration=0.5)
                audio = recognizer.listen(source, timeout=5, phrase_time_limit=4)
            
            # Test recognition
            text = recognizer.recognize_google(audio)
            print(f"Recognized text: '{text}'")
            
            # Convert audio data to numpy array
            audio_data = np.frombuffer(audio.get_raw_data(), dtype=np.int16).astype(np.float32)
            
            # Test wake word detection
            detected, wake_word = self.assistant.detect_wake_word(text, audio_data)
            
            if detected:
                print(f"✅ SUCCESS: Wake word '{wake_word}' detected!")
                self.status_label.config(text=f"✅ Test successful: '{wake_word}' detected")
            else:
                print(f"❌ FAILED: Wake word not detected in '{text}'")
                self.status_label.config(text=f"❌ Test failed: No wake word in '{text}'")
                
        except sr.WaitTimeoutError:
            print("❌ No audio detected")
            self.status_label.config(text="❌ Test failed: No audio detected")
        except sr.UnknownValueError:
            print("❌ Could not understand audio")
            self.status_label.config(text="❌ Test failed: Could not understand audio")
        except Exception as e:
            print(f"❌ Test error: {e}")
            self.status_label.config(text=f"❌ Test error: {e}")
    
    def open_wake_word_trainer(self):
        """Open wake word trainer"""
        try:
            import subprocess
            subprocess.Popen(["py", "custom_wake_word_trainer.py"])
        except Exception as e:
            print(f"Error opening wake word trainer: {e}")
    
    def open_microphone_selector(self):
        """Open microphone selector"""
        try:
            import subprocess
            subprocess.Popen(["py", "microphone_selector.py"])
        except Exception as e:
            print(f"Error opening microphone selector: {e}")
    
    def close_app(self):
        """Close the application"""
        self.animation_running = False
        self.root.quit()
        self.root.destroy()
    
    def run(self):
        """Start the application"""
        # Auto-start listening
        self.toggle_listening()
        
        print("🎨 Voice Assistant Visualizer Starting...")
        print("Beautiful Siri-like visualization with real-time waveforms!")
        
        self.root.mainloop()

if __name__ == "__main__":
    app = VoiceVisualizer()
    app.run()