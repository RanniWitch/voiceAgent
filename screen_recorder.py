#!/usr/bin/env python3
"""
Screen Recording System
Continuously buffers screen recording and saves clips on command
"""

import cv2
import numpy as np
import threading
import time
from collections import deque
import os
from datetime import datetime
import pyautogui
import subprocess

class ScreenRecorder:
    def __init__(self, buffer_minutes=5, fps=30, monitor_index=None):
        """
        Initialize screen recorder
        
        Args:
            buffer_minutes: How many minutes to keep in memory buffer
            fps: Frames per second for recording
            monitor_index: Which monitor to record (None for all monitors, 0 for primary, 1+ for secondary)
        """
        self.buffer_minutes = buffer_minutes
        self.fps = fps
        self.is_recording = False
        self.frame_buffer = deque()
        self.max_frames = buffer_minutes * 60 * fps  # Total frames to keep
        self.monitor_index = monitor_index
        
        # Detect monitors
        self.monitors = self.detect_monitors()
        self.setup_recording_area()
        
        # Create recordings directory
        self.recordings_dir = "recordings"
        if not os.path.exists(self.recordings_dir):
            os.makedirs(self.recordings_dir)
        
        print(f"📹 Screen recorder initialized:")
        print(f"   Buffer: {buffer_minutes} minutes ({self.max_frames} frames)")
        print(f"   Monitors detected: {len(self.monitors)}")
        for i, monitor in enumerate(self.monitors):
            print(f"     Monitor {i+1}: {monitor['width']}x{monitor['height']} at ({monitor['left']}, {monitor['top']})")
        print(f"   Recording: {self.recording_description}")
        print(f"   FPS: {fps}")
    
    def detect_monitors(self):
        """Detect all available monitors"""
        try:
            import win32api
            import win32con
            
            monitors = []
            
            def enum_display_monitors(hdc, lprcClip, dwData):
                monitors.append(win32api.GetMonitorInfo(hdc))
                return True
            
            # Get all monitors
            win32api.EnumDisplayMonitors(None, None, enum_display_monitors, 0)
            
            # Convert to simpler format
            monitor_list = []
            for i, monitor in enumerate(monitors):
                rect = monitor['Monitor']
                monitor_info = {
                    'index': i,
                    'left': rect[0],
                    'top': rect[1], 
                    'width': rect[2] - rect[0],
                    'height': rect[3] - rect[1],
                    'right': rect[2],
                    'bottom': rect[3],
                    'is_primary': monitor.get('Flags', 0) == win32con.MONITORINFOF_PRIMARY
                }
                monitor_list.append(monitor_info)
            
            return monitor_list
            
        except ImportError:
            # Fallback to pyautogui for single monitor
            print("⚠️ win32api not available, using single monitor mode")
            width, height = pyautogui.size()
            return [{
                'index': 0,
                'left': 0,
                'top': 0,
                'width': width,
                'height': height,
                'right': width,
                'bottom': height,
                'is_primary': True
            }]
    
    def setup_recording_area(self):
        """Setup the recording area based on monitor selection"""
        if not self.monitors:
            # Fallback
            self.screen_width, self.screen_height = pyautogui.size()
            self.recording_bbox = (0, 0, self.screen_width, self.screen_height)
            self.recording_description = f"Full screen ({self.screen_width}x{self.screen_height})"
            return
        
        if self.monitor_index is None:
            # Record all monitors (full desktop)
            left = min(m['left'] for m in self.monitors)
            top = min(m['top'] for m in self.monitors)
            right = max(m['right'] for m in self.monitors)
            bottom = max(m['bottom'] for m in self.monitors)
            
            self.recording_bbox = (left, top, right, bottom)
            self.screen_width = right - left
            self.screen_height = bottom - top
            self.recording_description = f"All monitors ({self.screen_width}x{self.screen_height})"
            
        elif 0 <= self.monitor_index < len(self.monitors):
            # Record specific monitor
            monitor = self.monitors[self.monitor_index]
            self.recording_bbox = (monitor['left'], monitor['top'], monitor['right'], monitor['bottom'])
            self.screen_width = monitor['width']
            self.screen_height = monitor['height']
            
            monitor_name = "Primary" if monitor['is_primary'] else f"Monitor {self.monitor_index + 1}"
            self.recording_description = f"{monitor_name} ({self.screen_width}x{self.screen_height})"
            
        else:
            # Invalid monitor index, use primary
            primary = next((m for m in self.monitors if m['is_primary']), self.monitors[0])
            self.recording_bbox = (primary['left'], primary['top'], primary['right'], primary['bottom'])
            self.screen_width = primary['width']
            self.screen_height = primary['height']
            self.recording_description = f"Primary monitor ({self.screen_width}x{self.screen_height})"
    
    def set_monitor(self, monitor_index):
        """Change which monitor to record"""
        self.monitor_index = monitor_index
        self.setup_recording_area()
        print(f"📺 Switched to recording: {self.recording_description}")
        return f"Now recording {self.recording_description}"
    
    def start_recording(self):
        """Start continuous screen recording"""
        if self.is_recording:
            return
        
        self.is_recording = True
        print("🔴 Starting continuous screen recording...")
        
        # Start recording thread
        threading.Thread(target=self._recording_loop, daemon=True).start()
    
    def stop_recording(self):
        """Stop continuous screen recording"""
        self.is_recording = False
        print("⏹️ Stopping screen recording...")
    
    def _recording_loop(self):
        """Main recording loop"""
        frame_time = 1.0 / self.fps
        
        while self.is_recording:
            start_time = time.time()
            
            try:
                # Capture screenshot of specified area
                if hasattr(self, 'recording_bbox'):
                    screenshot = pyautogui.screenshot(region=self.recording_bbox)
                else:
                    screenshot = pyautogui.screenshot()
                frame = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
                
                # Add timestamp to frame
                timestamp = time.time()
                
                # Add to buffer
                self.frame_buffer.append((frame, timestamp))
                
                # Remove old frames if buffer is full
                while len(self.frame_buffer) > self.max_frames:
                    self.frame_buffer.popleft()
                
                # Maintain FPS
                elapsed = time.time() - start_time
                sleep_time = max(0, frame_time - elapsed)
                if sleep_time > 0:
                    time.sleep(sleep_time)
                    
            except Exception as e:
                print(f"Recording error: {e}")
                time.sleep(0.1)
    
    def save_clip(self, duration_seconds, filename=None):
        """
        Save a clip of the last N seconds
        
        Args:
            duration_seconds: How many seconds to save
            filename: Optional custom filename
            
        Returns:
            str: Path to saved file or None if failed
        """
        if not self.frame_buffer:
            print("❌ No frames in buffer to save")
            return None
        
        # Calculate how many frames we need
        frames_needed = min(duration_seconds * self.fps, len(self.frame_buffer))
        
        if frames_needed <= 0:
            print("❌ Invalid duration or no frames available")
            return None
        
        # Generate filename if not provided
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"clip_{duration_seconds}s_{timestamp}.mp4"
        
        filepath = os.path.join(self.recordings_dir, filename)
        
        print(f"💾 Saving {duration_seconds}s clip ({frames_needed} frames) to {filename}...")
        
        try:
            # Get the last N frames
            frames_to_save = list(self.frame_buffer)[-frames_needed:]
            
            # Setup video writer
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(filepath, fourcc, self.fps, 
                                (self.screen_width, self.screen_height))
            
            # Write frames
            for frame, timestamp in frames_to_save:
                out.write(frame)
            
            out.release()
            
            print(f"✅ Clip saved: {filepath}")
            return filepath
            
        except Exception as e:
            print(f"❌ Error saving clip: {e}")
            return None
    
    def get_buffer_info(self):
        """Get information about current buffer"""
        if not self.frame_buffer:
            return "Buffer is empty"
        
        buffer_seconds = len(self.frame_buffer) / self.fps
        buffer_minutes = buffer_seconds / 60
        
        return f"Buffer: {buffer_seconds:.1f}s ({buffer_minutes:.1f}m) - {len(self.frame_buffer)} frames"

class VoiceControlledRecorder:
    """Voice-controlled interface for screen recording"""
    
    def __init__(self):
        self.recorder = ScreenRecorder(buffer_minutes=15, fps=20)  # 15 min buffer, 20 FPS for efficiency
        self.recorder.start_recording()
        self.current_monitor = None  # Track current monitor setting
    
    def process_recording_command(self, command_text):
        """
        Process voice commands for screen recording
        
        Args:
            command_text: The voice command text
            
        Returns:
            str: Response message
        """
        command_lower = command_text.lower().strip()
        
        # Extract duration from command
        duration = self.extract_duration(command_lower)
        
        if any(word in command_lower for word in ['record', 'save', 'clip', 'capture']):
            # Check if monitor is specified in the command
            monitor_specified = self.extract_monitor_from_command(command_lower)
            if monitor_specified is not None:
                # Temporarily switch to specified monitor
                original_monitor = self.current_monitor
                self.set_monitor_by_number(monitor_specified) if isinstance(monitor_specified, int) else self.set_monitor_by_type(monitor_specified)
            
            if duration > 0:
                filepath = self.recorder.save_clip(duration)
                result = f"Saved {duration} second clip from {self.recorder.recording_description} to {os.path.basename(filepath)}" if filepath else "Failed to save clip"
            else:
                # Default to 30 seconds if no duration specified
                filepath = self.recorder.save_clip(30)
                result = f"Saved 30 second clip from {self.recorder.recording_description} to {os.path.basename(filepath)}" if filepath else "Failed to save clip"
            
            # Restore original monitor if we switched
            if monitor_specified is not None and 'original_monitor' in locals():
                if original_monitor is not None:
                    self.set_monitor_by_number(original_monitor + 1)
                else:
                    self.set_monitor_by_type('all')
            
            return result
        
        elif 'buffer' in command_lower or 'status' in command_lower:
            return self.recorder.get_buffer_info()
        
        elif 'stop recording' in command_lower:
            self.recorder.stop_recording()
            return "Screen recording stopped"
        
        elif 'start recording' in command_lower:
            self.recorder.start_recording()
            return "Screen recording started"
        
        elif any(word in command_lower for word in ['monitor', 'screen', 'display']):
            return self.handle_monitor_command(command_lower)
        
        return None  # Not a recording command
    
    def handle_monitor_command(self, command_text):
        """Handle monitor selection commands"""
        # Extract monitor number or keywords
        import re
        
        if 'list monitors' in command_text or 'show monitors' in command_text:
            return self.list_monitors()
        
        elif 'primary monitor' in command_text or 'main monitor' in command_text:
            return self.set_monitor_by_type('primary')
        
        elif 'secondary monitor' in command_text or 'second monitor' in command_text:
            return self.set_monitor_by_type('secondary')
        
        elif 'all monitors' in command_text or 'both monitors' in command_text:
            return self.set_monitor_by_type('all')
        
        else:
            # Look for monitor number
            number_match = re.search(r'monitor (\d+)', command_text)
            if number_match:
                monitor_num = int(number_match.group(1))
                return self.set_monitor_by_number(monitor_num)
        
        return "Monitor command not recognized. Try 'list monitors', 'primary monitor', 'monitor 2', or 'all monitors'."
    
    def list_monitors(self):
        """List available monitors"""
        if not self.recorder.monitors:
            return "No monitors detected"
        
        monitor_info = []
        for i, monitor in enumerate(self.recorder.monitors):
            status = " (Primary)" if monitor['is_primary'] else ""
            monitor_info.append(f"Monitor {i+1}: {monitor['width']}x{monitor['height']}{status}")
        
        current = f"Currently recording: {self.recorder.recording_description}"
        return f"Available monitors:\n" + "\n".join(monitor_info) + f"\n\n{current}"
    
    def set_monitor_by_type(self, monitor_type):
        """Set monitor by type (primary, secondary, all)"""
        if monitor_type == 'primary':
            primary_index = next((i for i, m in enumerate(self.recorder.monitors) if m['is_primary']), 0)
            result = self.recorder.set_monitor(primary_index)
            self.current_monitor = primary_index
            return result
        
        elif monitor_type == 'secondary':
            if len(self.recorder.monitors) < 2:
                return "No secondary monitor detected"
            secondary_index = next((i for i, m in enumerate(self.recorder.monitors) if not m['is_primary']), 1)
            result = self.recorder.set_monitor(secondary_index)
            self.current_monitor = secondary_index
            return result
        
        elif monitor_type == 'all':
            result = self.recorder.set_monitor(None)  # None means all monitors
            self.current_monitor = None
            return result
        
        return "Invalid monitor type"
    
    def set_monitor_by_number(self, monitor_num):
        """Set monitor by number (1-based)"""
        monitor_index = monitor_num - 1  # Convert to 0-based
        
        if 0 <= monitor_index < len(self.recorder.monitors):
            result = self.recorder.set_monitor(monitor_index)
            self.current_monitor = monitor_index
            return result
        else:
            return f"Monitor {monitor_num} not found. Available monitors: 1-{len(self.recorder.monitors)}"
    
    def extract_duration(self, command_text):
        """
        Extract duration in seconds from voice command
        
        Args:
            command_text: The command text
            
        Returns:
            int: Duration in seconds, or 0 if not found
        """
        import re
        
        # Look for patterns like "30 seconds", "2 minutes", "1 minute 30 seconds"
        
        # Seconds pattern
        seconds_match = re.search(r'(\d+)\s*(?:second|sec)', command_text)
        minutes_match = re.search(r'(\d+)\s*(?:minute|min)', command_text)
        
        total_seconds = 0
        
        if seconds_match:
            total_seconds += int(seconds_match.group(1))
        
        if minutes_match:
            total_seconds += int(minutes_match.group(1)) * 60
        
        # If no specific time mentioned, look for just numbers
        if total_seconds == 0:
            number_match = re.search(r'(\d+)', command_text)
            if number_match:
                num = int(number_match.group(1))
                # Assume seconds if number is reasonable for seconds (1-300)
                # Assume minutes if larger
                if 1 <= num <= 300:
                    total_seconds = num
                elif num > 300:
                    total_seconds = num * 60
        
        return total_seconds
    
    def extract_monitor_from_command(self, command_text):
        """Extract monitor specification from command"""
        import re
        
        if 'primary monitor' in command_text or 'main monitor' in command_text:
            return 'primary'
        elif 'secondary monitor' in command_text or 'second monitor' in command_text:
            return 'secondary'
        elif 'all monitors' in command_text or 'both monitors' in command_text:
            return 'all'
        else:
            # Look for monitor number
            monitor_match = re.search(r'monitor (\d+)', command_text)
            if monitor_match:
                return int(monitor_match.group(1))
        
        return None

# Test the recorder
if __name__ == "__main__":
    print("🎬 Voice-Controlled Screen Recorder Test")
    print("="*50)
    
    recorder = VoiceControlledRecorder()
    
    print("\nTesting voice commands:")
    
    test_commands = [
        "save the last 30 seconds",
        "record the past 2 minutes", 
        "clip the last 45 seconds",
        "save 1 minute 30 seconds",
        "capture last 10 seconds",
        "buffer status",
        "record 60 seconds"
    ]
    
    for cmd in test_commands:
        print(f"\nCommand: '{cmd}'")
        response = recorder.process_recording_command(cmd)
        if response:
            print(f"Response: {response}")
        else:
            print("Not a recording command")
    
    print(f"\n{recorder.recorder.get_buffer_info()}")
    
    # Keep recording for a bit
    print("\nRecording for 10 seconds...")
    time.sleep(10)
    
    # Save a test clip
    print("\nSaving test clip...")
    recorder.process_recording_command("save last 5 seconds")
    
    print("\nTest complete!")