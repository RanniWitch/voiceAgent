#!/usr/bin/env python3
"""
Simple HTTP Server for Audio Visualizer
Run this to view the visualizer in your browser
"""

import http.server
import socketserver
import webbrowser
import os
import sys

PORT = 8000

class MyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        # Add CORS headers for audio/video access
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()

def start_server():
    # Change to visualizer directory
    visualizer_path = os.path.join(os.path.dirname(__file__), 'visualizer')

    if not os.path.exists(visualizer_path):
        print(f"❌ Error: Visualizer directory not found at {visualizer_path}")
        sys.exit(1)

    os.chdir(visualizer_path)

    print("=" * 60)
    print("🎨 AUDIO VISUALIZER SERVER")
    print("=" * 60)
    print(f"\n✅ Server starting on http://localhost:{PORT}")
    print(f"📁 Serving files from: {os.getcwd()}")
    print(f"\n🌐 Opening browser automatically...")
    print(f"\n⚠️  IMPORTANT: Allow microphone access when prompted!")
    print(f"\n🛑 Press Ctrl+C to stop the server\n")
    print("=" * 60 + "\n")

    # Open browser after a short delay
    import threading
    def open_browser():
        import time
        time.sleep(1.5)
        webbrowser.open(f'http://localhost:{PORT}')

    threading.Thread(target=open_browser, daemon=True).start()

    # Start server
    with socketserver.TCPServer(("", PORT), MyHTTPRequestHandler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n\n🛑 Server stopped")
            sys.exit(0)

if __name__ == "__main__":
    start_server()
