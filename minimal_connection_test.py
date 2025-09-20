#!/usr/bin/env py
"""
Minimal WebSocket connection test with no external dependencies.
Tests basic connectivity without any of the voice processing components.
"""

import asyncio
import json
import logging
import time
import uuid
from datetime import datetime
from typing import Dict

try:
    from fastapi import FastAPI, WebSocket, WebSocketDisconnect
    from fastapi.responses import HTMLResponse
    import uvicorn
    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False
    print("❌ FastAPI not available. Install with: pip install fastapi uvicorn")

# Simple logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)


if FASTAPI_AVAILABLE:
    # Create FastAPI app
    app = FastAPI(title="Minimal Connection Test")
    
    # Connection tracking
    connections: Dict[str, WebSocket] = {}
    connection_stats = {
        "total_connections": 0,
        "total_disconnections": 0,
        "messages_received": 0,
        "start_time": time.time()
    }
    
    # Simple test page
    TEST_PAGE = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Minimal Connection Test</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; background: #222; color: white; }
            .status { padding: 10px; margin: 10px 0; border-radius: 5px; font-weight: bold; }
            .connected { background: #4caf50; }
            .disconnected { background: #f44336; }
            .connecting { background: #ff9800; }
            button { padding: 10px 20px; margin: 5px; font-size: 16px; cursor: pointer; border: none; border-radius: 3px; }
            .btn-primary { background: #2196f3; color: white; }
            .btn-success { background: #4caf50; color: white; }
            .btn-danger { background: #f44336; color: white; }
            .btn-disabled { background: #666; color: #ccc; cursor: not-allowed; }
            #log { background: #333; padding: 15px; border-radius: 5px; height: 400px; overflow-y: auto; font-family: monospace; font-size: 14px; }
            .log-entry { margin: 2px 0; }
            .log-info { color: #4caf50; }
            .log-error { color: #f44336; }
            .log-warn { color: #ff9800; }
        </style>
    </head>
    <body>
        <h1>🔌 Minimal WebSocket Connection Test</h1>
        
        <div id="status" class="status disconnected">Status: Disconnected</div>
        
        <div>
            <button id="connectBtn" class="btn-primary" onclick="connect()">Connect</button>
            <button id="disconnectBtn" class="btn-danger btn-disabled" onclick="disconnect()">Disconnect</button>
            <button id="pingBtn" class="btn-success btn-disabled" onclick="sendPing()">Ping</button>
            <button onclick="clearLog()" class="btn-primary">Clear Log</button>
        </div>
        
        <div id="log"></div>
        
        <script>
            let ws = null;
            let connectionId = null;
            let pingCount = 0;
            
            function log(message, type = 'info') {
                const logEl = document.getElementById('log');
                const entry = document.createElement('div');
                entry.className = 'log-entry log-' + type;
                entry.textContent = new Date().toLocaleTimeString() + ' - ' + message;
                logEl.appendChild(entry);
                logEl.scrollTop = logEl.scrollHeight;
            }
            
            function updateStatus(status) {
                const statusEl = document.getElementById('status');
                const connectBtn = document.getElementById('connectBtn');
                const disconnectBtn = document.getElementById('disconnectBtn');
                const pingBtn = document.getElementById('pingBtn');
                
                statusEl.className = 'status ' + status;
                
                if (status === 'connected') {
                    statusEl.textContent = 'Status: Connected ✅';
                    connectBtn.className = 'btn-primary btn-disabled';
                    disconnectBtn.className = 'btn-danger';
                    pingBtn.className = 'btn-success';
                } else if (status === 'connecting') {
                    statusEl.textContent = 'Status: Connecting...';
                    connectBtn.className = 'btn-primary btn-disabled';
                    disconnectBtn.className = 'btn-danger btn-disabled';
                    pingBtn.className = 'btn-success btn-disabled';
                } else {
                    statusEl.textContent = 'Status: Disconnected ❌';
                    connectBtn.className = 'btn-primary';
                    disconnectBtn.className = 'btn-danger btn-disabled';
                    pingBtn.className = 'btn-success btn-disabled';
                }
            }
            
            function connect() {
                if (ws && ws.readyState === WebSocket.OPEN) {
                    log('Already connected', 'warn');
                    return;
                }
                
                updateStatus('connecting');
                log('Connecting to ws://localhost:8008/ws/test');
                
                ws = new WebSocket('ws://localhost:8008/ws/test');
                
                ws.onopen = function() {
                    updateStatus('connected');
                    log('WebSocket connected successfully!', 'info');
                };
                
                ws.onmessage = function(event) {
                    try {
                        const data = JSON.parse(event.data);
                        log('Received: ' + data.type, 'info');
                        
                        if (data.type === 'welcome') {
                            connectionId = data.connection_id;
                            log('Connection ID: ' + connectionId, 'info');
                        } else if (data.type === 'pong') {
                            const latency = Date.now() - data.ping_time;
                            log('Pong received! Latency: ' + latency + 'ms', 'info');
                        }
                    } catch (e) {
                        log('Received: ' + event.data, 'info');
                    }
                };
                
                ws.onclose = function(event) {
                    updateStatus('disconnected');
                    log('Connection closed. Code: ' + event.code, 'error');
                };
                
                ws.onerror = function(error) {
                    updateStatus('disconnected');
                    log('WebSocket error occurred', 'error');
                };
            }
            
            function disconnect() {
                if (ws) {
                    ws.close();
                    ws = null;
                    log('Disconnected by user', 'warn');
                }
            }
            
            function sendPing() {
                if (ws && ws.readyState === WebSocket.OPEN) {
                    pingCount++;
                    const message = {
                        type: 'ping',
                        ping_time: Date.now(),
                        ping_count: pingCount
                    };
                    ws.send(JSON.stringify(message));
                    log('Ping sent (#' + pingCount + ')', 'info');
                } else {
                    log('Cannot ping - not connected', 'error');
                }
            }
            
            function clearLog() {
                document.getElementById('log').innerHTML = '';
            }
            
            // Auto-connect on load
            window.onload = function() {
                log('Page loaded. Click Connect to test WebSocket.', 'info');
            };
        </script>
    </body>
    </html>
    """
    
    @app.get("/")
    async def get_test_page():
        return HTMLResponse(content=TEST_PAGE)
    
    @app.get("/api/status")
    async def get_status():
        runtime = time.time() - connection_stats["start_time"]
        return {
            "status": "running",
            "active_connections": len(connections),
            "runtime_seconds": runtime,
            **connection_stats
        }
    
    @app.websocket("/ws/test")
    async def websocket_test(websocket: WebSocket):
        # Accept connection
        await websocket.accept()
        connection_id = str(uuid.uuid4())[:8]
        connections[connection_id] = websocket
        connection_stats["total_connections"] += 1
        
        logger.info(f"✅ Connection {connection_id} established (Total: {len(connections)})")
        
        try:
            # Send welcome message
            await websocket.send_text(json.dumps({
                "type": "welcome",
                "connection_id": connection_id,
                "timestamp": time.time()
            }))
            
            # Handle messages
            while True:
                data = await websocket.receive_text()
                connection_stats["messages_received"] += 1
                
                try:
                    message = json.loads(data)
                    msg_type = message.get("type", "unknown")
                    
                    logger.info(f"📨 {connection_id}: {msg_type}")
                    
                    if msg_type == "ping":
                        # Send pong response
                        await websocket.send_text(json.dumps({
                            "type": "pong",
                            "ping_time": message.get("ping_time", 0),
                            "server_time": time.time()
                        }))
                    
                except json.JSONDecodeError:
                    logger.warning(f"Invalid JSON from {connection_id}")
                
        except WebSocketDisconnect:
            logger.info(f"❌ Connection {connection_id} disconnected normally")
        except Exception as e:
            logger.error(f"❌ Connection {connection_id} error: {e}")
        finally:
            connections.pop(connection_id, None)
            connection_stats["total_disconnections"] += 1
            logger.info(f"🧹 Connection {connection_id} cleaned up (Remaining: {len(connections)})")


async def run_minimal_test():
    """Run the minimal connection test."""
    if not FASTAPI_AVAILABLE:
        print("Cannot run test - FastAPI not available")
        return
    
    logger.info("🚀 Starting Minimal WebSocket Connection Test")
    logger.info("This tests ONLY basic WebSocket connectivity")
    logger.info("")
    logger.info("🌐 Open browser: http://localhost:8008")
    logger.info("🔌 WebSocket: ws://localhost:8008/ws/test")
    logger.info("📊 Status API: http://localhost:8008/api/status")
    logger.info("")
    logger.info("🎯 What this tests:")
    logger.info("   ✅ WebSocket connection establishment")
    logger.info("   ✅ Message sending/receiving")
    logger.info("   ✅ Ping/pong keepalive")
    logger.info("   ✅ Connection cleanup")
    logger.info("")
    logger.info("🛑 Press Ctrl+C to stop")
    logger.info("")
    
    try:
        config = uvicorn.Config(
            app=app,
            host="localhost",
            port=8008,
            log_level="warning"  # Reduce uvicorn noise
        )
        server = uvicorn.Server(config)
        await server.serve()
    except KeyboardInterrupt:
        logger.info("Test stopped by user")
    finally:
        # Final stats
        runtime = time.time() - connection_stats["start_time"]
        logger.info("")
        logger.info("📊 FINAL STATS:")
        logger.info(f"   Runtime: {runtime:.1f} seconds")
        logger.info(f"   Total connections: {connection_stats['total_connections']}")
        logger.info(f"   Total disconnections: {connection_stats['total_disconnections']}")
        logger.info(f"   Messages received: {connection_stats['messages_received']}")
        logger.info(f"   Active at end: {len(connections)}")
        
        if connection_stats["total_connections"] > 0:
            stability = (connection_stats["total_connections"] - connection_stats["total_disconnections"]) / connection_stats["total_connections"]
            logger.info(f"   Connection stability: {stability:.1%}")
        
        logger.info("✅ Minimal test completed")


if __name__ == "__main__":
    if FASTAPI_AVAILABLE:
        asyncio.run(run_minimal_test())
    else:
        print("❌ Missing dependencies. Install with:")
        print("pip install fastapi uvicorn")
        print("")
        print("Or check if you have a virtual environment activated.")