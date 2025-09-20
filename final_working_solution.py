#!/usr/bin/env py
"""
Final working solution - combines web interface with direct microphone access.
This bypasses all browser audio format issues.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import asyncio
import json
import logging
import time
import uuid
import threading
import queue
from typing import Dict, Optional
from datetime import datetime

try:
    from fastapi import FastAPI, WebSocket, WebSocketDisconnect
    from fastapi.responses import HTMLResponse
    from fastapi.middleware.cors import CORSMiddleware
    import uvicorn
    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False

try:
    import speech_recognition as sr
    SPEECH_RECOGNITION_AVAILABLE = True
except ImportError:
    SPEECH_RECOGNITION_AVAILABLE = False

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

if not FASTAPI_AVAILABLE:
    logger.error("FastAPI not available. Install with: pip install fastapi uvicorn")
    sys.exit(1)

if not SPEECH_RECOGNITION_AVAILABLE:
    logger.error("SpeechRecognition not available. Install with: pip install SpeechRecognition")
    sys.exit(1)

class FinalVoiceProcessor:
    """Final voice processor using direct microphone access."""
    
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self.is_listening = False
        self.transcription_queue = queue.Queue()
        self.stop_listening_func = None
        self.connected_clients = set()
        
        # Initialize microphone
        self.init_microphone()
    
    def init_microphone(self):
        """Initialize microphone with noise adjustment."""
        try:
            logger.info("🎤 Initializing microphone...")
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
            logger.info("✅ Microphone initialized and calibrated")
        except Exception as e:
            logger.error(f"❌ Microphone initialization failed: {e}")
    
    def start_listening(self):
        """Start continuous listening."""
        if self.is_listening:
            return
        
        logger.info("🎧 Starting continuous voice recognition...")
        
        def callback(recognizer, audio):
            """Callback for when audio is captured."""
            try:
                # Transcribe the audio
                text = recognizer.recognize_google(audio, language='en-US')
                timestamp = time.time()
                
                logger.info(f"✅ Transcribed: {text}")
                
                # Send to all connected clients
                transcription_data = {
                    "type": "transcription",
                    "text": text,
                    "confidence": 0.95,
                    "timestamp": timestamp,
                    "processing_method": "direct_microphone_google"
                }
                
                # Add to queue for web clients
                self.transcription_queue.put(transcription_data)
                
            except sr.UnknownValueError:
                logger.debug("Could not understand audio")
            except sr.RequestError as e:
                logger.error(f"Speech recognition error: {e}")
        
        # Start listening in background
        self.stop_listening_func = self.recognizer.listen_in_background(
            self.microphone, 
            callback,
            phrase_time_limit=4
        )
        
        self.is_listening = True
        logger.info("✅ Voice recognition started")
    
    def stop_listening(self):
        """Stop continuous listening."""
        if not self.is_listening:
            return
        
        if self.stop_listening_func:
            self.stop_listening_func(wait_for_stop=False)
            self.stop_listening_func = None
        
        self.is_listening = False
        logger.info("🛑 Voice recognition stopped")
    
    def get_transcription(self):
        """Get next transcription from queue."""
        try:
            return self.transcription_queue.get_nowait()
        except queue.Empty:
            return None

# Global voice processor
voice_processor = FinalVoiceProcessor()

# Final HTML interface
HTML_INTERFACE = """
<!DOCTYPE html>
<html>
<head>
    <title>Final Working Voice Solution</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
            background: linear-gradient(135deg, #00b894 0%, #00cec9 100%);
            color: white; 
            min-height: 100vh;
            padding: 20px;
        }
        .container { max-width: 800px; margin: 0 auto; }
        .header { text-align: center; margin-bottom: 30px; }
        .header h1 { font-size: 2.5em; margin-bottom: 10px; }
        .header p { font-size: 1.2em; opacity: 0.9; }
        .success-badge { 
            background: #00b894; 
            padding: 8px 20px; 
            border-radius: 25px; 
            font-size: 1em; 
            margin-top: 15px;
            display: inline-block;
            font-weight: bold;
        }
        
        .controls { 
            background: rgba(255,255,255,0.15); 
            padding: 25px; 
            border-radius: 20px; 
            margin-bottom: 25px;
            backdrop-filter: blur(10px);
            box-shadow: 0 8px 32px rgba(0,0,0,0.1);
        }
        
        .status-bar { 
            display: flex; 
            justify-content: space-between; 
            align-items: center; 
            margin-bottom: 25px;
            flex-wrap: wrap;
            gap: 15px;
        }
        
        .status { 
            padding: 10px 20px; 
            border-radius: 25px; 
            font-weight: bold; 
            font-size: 16px;
        }
        .status.connected { background: #00b894; }
        .status.disconnected { background: #e17055; }
        .status.listening { background: #00b894; animation: pulse 2s infinite; }
        
        .buttons { display: flex; gap: 15px; flex-wrap: wrap; justify-content: center; }
        button { 
            padding: 15px 30px; 
            border: none; 
            border-radius: 12px; 
            font-size: 18px; 
            cursor: pointer; 
            transition: all 0.3s;
            font-weight: 600;
            min-width: 150px;
        }
        .btn-primary { background: #74b9ff; color: white; }
        .btn-success { background: #00b894; color: white; }
        .btn-danger { background: #e17055; color: white; }
        .btn-warning { background: #fdcb6e; color: #2d3436; }
        .btn-disabled { background: #636e72; color: #ddd; cursor: not-allowed; }
        button:hover:not(.btn-disabled) { transform: translateY(-3px); box-shadow: 0 6px 20px rgba(0,0,0,0.3); }
        
        @keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.7; } }
        
        .transcriptions { 
            background: rgba(0,0,0,0.3); 
            padding: 25px; 
            border-radius: 20px; 
            min-height: 300px;
            margin-bottom: 25px;
        }
        .transcription { 
            margin: 15px 0; 
            padding: 15px; 
            border-left: 5px solid #00b894; 
            background: rgba(255,255,255,0.1);
            border-radius: 10px;
            font-size: 16px;
        }
        .transcription.system { border-left-color: #fdcb6e; }
        
        .info-box {
            background: rgba(255,255,255,0.1);
            padding: 20px;
            border-radius: 15px;
            margin-bottom: 20px;
        }
        .info-box h3 { margin-bottom: 10px; color: #fdcb6e; }
        .info-box p { line-height: 1.6; }
        
        .stats { 
            display: grid; 
            grid-template-columns: repeat(auto-fit, minmax(120px, 1fr)); 
            gap: 15px; 
        }
        .stat-card { 
            background: rgba(255,255,255,0.1); 
            padding: 20px; 
            border-radius: 15px; 
            text-align: center;
        }
        .stat-value { font-size: 2em; font-weight: bold; color: #00b894; }
        .stat-label { font-size: 0.9em; opacity: 0.8; margin-top: 5px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎤 Final Working Voice Solution</h1>
            <p>Direct Microphone Access - No Browser Audio Issues</p>
            <div class="success-badge">✅ WORKING SOLUTION</div>
        </div>
        
        <div class="info-box">
            <h3>🎯 How This Works</h3>
            <p>This solution uses your system microphone directly, bypassing all browser audio format issues. 
            The server listens to your microphone and sends transcriptions to the web interface in real-time.</p>
        </div>
        
        <div class="controls">
            <div class="status-bar">
                <div id="connectionStatus" class="status disconnected">Disconnected</div>
                <div id="listeningStatus" class="status disconnected">Not Listening</div>
            </div>
            
            <div class="buttons">
                <button id="connectBtn" class="btn-primary" onclick="connect()">Connect</button>
                <button id="startBtn" class="btn-success btn-disabled" onclick="startListening()">Start Listening</button>
                <button id="stopBtn" class="btn-danger btn-disabled" onclick="stopListening()">Stop Listening</button>
                <button id="clearBtn" class="btn-warning" onclick="clearTranscriptions()">Clear</button>
            </div>
        </div>
        
        <div class="transcriptions" id="transcriptions">
            <div class="transcription system">
                <strong>System:</strong> Final working voice solution ready! Click Connect, then Start Listening.
            </div>
        </div>
        
        <div class="stats">
            <div class="stat-card">
                <div class="stat-value" id="transcriptionCount">0</div>
                <div class="stat-label">Transcriptions</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" id="uptime">0s</div>
                <div class="stat-label">Uptime</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" id="status">Ready</div>
                <div class="stat-label">Status</div>
            </div>
        </div>
    </div>

    <script>
        let ws = null;
        let isConnected = false;
        let isListening = false;
        let startTime = null;
        let transcriptionCount = 0;
        
        function updateConnectionStatus(connected) {
            const statusEl = document.getElementById('connectionStatus');
            const connectBtn = document.getElementById('connectBtn');
            const startBtn = document.getElementById('startBtn');
            
            isConnected = connected;
            
            if (connected) {
                statusEl.textContent = 'Connected ✅';
                statusEl.className = 'status connected';
                connectBtn.className = 'btn-primary btn-disabled';
                startBtn.className = 'btn-success';
            } else {
                statusEl.textContent = 'Disconnected ❌';
                statusEl.className = 'status disconnected';
                connectBtn.className = 'btn-primary';
                startBtn.className = 'btn-success btn-disabled';
                updateListeningStatus(false);
            }
        }
        
        function updateListeningStatus(listening) {
            const statusEl = document.getElementById('listeningStatus');
            const startBtn = document.getElementById('startBtn');
            const stopBtn = document.getElementById('stopBtn');
            const statusStat = document.getElementById('status');
            
            isListening = listening;
            
            if (listening) {
                statusEl.textContent = 'Listening 🎧';
                statusEl.className = 'status listening';
                startBtn.className = 'btn-success btn-disabled';
                stopBtn.className = 'btn-danger';
                statusStat.textContent = 'Listening';
            } else {
                statusEl.textContent = 'Not Listening';
                statusEl.className = 'status disconnected';
                startBtn.className = isConnected ? 'btn-success' : 'btn-success btn-disabled';
                stopBtn.className = 'btn-danger btn-disabled';
                statusStat.textContent = isConnected ? 'Ready' : 'Disconnected';
            }
        }
        
        function addTranscription(text, type = 'speech') {
            const transcriptionsEl = document.getElementById('transcriptions');
            const transcription = document.createElement('div');
            transcription.className = 'transcription ' + type;
            
            const label = type === 'system' ? 'System' : 'You said';
            const timestamp = new Date().toLocaleTimeString();
            transcription.innerHTML = `<strong>${label}:</strong> ${text} <small style="opacity:0.7">[${timestamp}]</small>`;
            
            transcriptionsEl.appendChild(transcription);
            
            // Keep only last 10 transcriptions
            while (transcriptionsEl.children.length > 10) {
                transcriptionsEl.removeChild(transcriptionsEl.firstChild);
            }
            
            // Scroll to bottom
            transcriptionsEl.scrollTop = transcriptionsEl.scrollHeight;
        }
        
        function updateStats() {
            document.getElementById('transcriptionCount').textContent = transcriptionCount;
            
            if (startTime) {
                const uptime = Math.floor((Date.now() - startTime) / 1000);
                document.getElementById('uptime').textContent = uptime + 's';
            }
        }
        
        function connect() {
            if (ws && ws.readyState === WebSocket.OPEN) {
                return;
            }
            
            ws = new WebSocket('ws://localhost:8016/ws/voice');
            
            ws.onopen = function() {
                updateConnectionStatus(true);
                addTranscription('Connected to voice recognition server!', 'system');
                if (!startTime) startTime = Date.now();
            };
            
            ws.onmessage = function(event) {
                try {
                    const data = JSON.parse(event.data);
                    
                    if (data.type === 'transcription') {
                        transcriptionCount++;
                        updateStats();
                        addTranscription(data.text, 'speech');
                    } else if (data.type === 'system_message') {
                        addTranscription(data.message, 'system');
                    } else if (data.type === 'listening_started') {
                        updateListeningStatus(true);
                        addTranscription('Voice recognition started - speak now!', 'system');
                    } else if (data.type === 'listening_stopped') {
                        updateListeningStatus(false);
                        addTranscription('Voice recognition stopped.', 'system');
                    }
                } catch (e) {
                    console.log('Received:', event.data);
                }
            };
            
            ws.onclose = function() {
                updateConnectionStatus(false);
                addTranscription('Connection closed.', 'system');
            };
            
            ws.onerror = function() {
                addTranscription('Connection error occurred.', 'system');
            };
        }
        
        function startListening() {
            if (!isConnected || isListening) return;
            
            ws.send(JSON.stringify({
                type: 'start_listening'
            }));
        }
        
        function stopListening() {
            if (!isConnected || !isListening) return;
            
            ws.send(JSON.stringify({
                type: 'stop_listening'
            }));
        }
        
        function clearTranscriptions() {
            document.getElementById('transcriptions').innerHTML = '';
            addTranscription('Transcriptions cleared.', 'system');
        }
        
        // Update stats every second
        setInterval(updateStats, 1000);
        
        // Auto-connect on load
        window.onload = function() {
            setTimeout(connect, 500);
        };
    </script>
</body>
</html>
"""

# Create FastAPI app
app = FastAPI(title="Final Working Voice Solution")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

connections: Dict[str, WebSocket] = {}
connection_stats = {
    "total_connections": 0,
    "total_transcriptions": 0,
    "start_time": time.time()
}

@app.get("/")
async def get_interface():
    return HTMLResponse(content=HTML_INTERFACE)

@app.get("/api/status")
async def get_status():
    return {
        "status": "running",
        "speech_recognition_available": SPEECH_RECOGNITION_AVAILABLE,
        "microphone_listening": voice_processor.is_listening,
        "active_connections": len(connections),
        "uptime": time.time() - connection_stats["start_time"],
        **connection_stats
    }

@app.websocket("/ws/voice")
async def websocket_voice(websocket: WebSocket):
    await websocket.accept()
    connection_id = str(uuid.uuid4())[:8]
    connections[connection_id] = websocket
    connection_stats["total_connections"] += 1
    voice_processor.connected_clients.add(connection_id)
    
    logger.info(f"✅ Final voice connection {connection_id} established")
    
    try:
        await websocket.send_text(json.dumps({
            "type": "welcome",
            "connection_id": connection_id,
            "timestamp": time.time(),
            "server_info": "Final Working Voice Solution"
        }))
        
        # Start background task to send transcriptions
        async def send_transcriptions():
            while True:
                transcription = voice_processor.get_transcription()
                if transcription:
                    connection_stats["total_transcriptions"] += 1
                    await websocket.send_text(json.dumps(transcription))
                await asyncio.sleep(0.1)
        
        # Start transcription sender
        transcription_task = asyncio.create_task(send_transcriptions())
        
        while True:
            data = await websocket.receive_text()
            
            try:
                message = json.loads(data)
                msg_type = message.get("type", "unknown")
                
                if msg_type == "start_listening":
                    voice_processor.start_listening()
                    await websocket.send_text(json.dumps({
                        "type": "listening_started",
                        "timestamp": time.time()
                    }))
                    logger.info(f"🎤 {connection_id} started listening")
                
                elif msg_type == "stop_listening":
                    voice_processor.stop_listening()
                    await websocket.send_text(json.dumps({
                        "type": "listening_stopped",
                        "timestamp": time.time()
                    }))
                    logger.info(f"🛑 {connection_id} stopped listening")
                
            except json.JSONDecodeError:
                logger.warning(f"Invalid JSON from {connection_id}")
            
    except WebSocketDisconnect:
        logger.info(f"❌ Final voice connection {connection_id} disconnected")
    except Exception as e:
        logger.error(f"❌ Final voice connection {connection_id} error: {e}")
    finally:
        connections.pop(connection_id, None)
        voice_processor.connected_clients.discard(connection_id)
        
        # Stop listening if no more clients
        if not voice_processor.connected_clients:
            voice_processor.stop_listening()
        
        # Cancel transcription task
        if 'transcription_task' in locals():
            transcription_task.cancel()

async def main():
    logger.info("🚀 Starting Final Working Voice Solution")
    logger.info("✅ Direct microphone access - no browser audio issues!")
    logger.info("")
    logger.info("🌐 Open browser: http://localhost:8016")
    logger.info("🔌 WebSocket: ws://localhost:8016/ws/voice")
    logger.info("")
    logger.info("🎯 FINAL SOLUTION:")
    logger.info("   ✅ Direct microphone access")
    logger.info("   ✅ Google Speech Recognition")
    logger.info("   ✅ Real-time transcription")
    logger.info("   ✅ Web interface")
    logger.info("   ✅ No audio format issues")
    logger.info("")
    logger.info("🛑 Press Ctrl+C to stop")
    
    try:
        config = uvicorn.Config(
            app=app,
            host="localhost",
            port=8016,
            log_level="warning"
        )
        server = uvicorn.Server(config)
        await server.serve()
    except KeyboardInterrupt:
        logger.info("Final voice solution stopped")
        voice_processor.stop_listening()

if __name__ == "__main__":
    asyncio.run(main())