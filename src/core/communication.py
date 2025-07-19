"""
Communication Manager for Ruohobot

Handles WiFi communication, remote control, and telemetry.
"""

import logging
import json
import time
import threading
from typing import Dict, Any, Callable, Optional
try:
    import socket
    import socketserver
    from http.server import HTTPServer, BaseHTTPRequestHandler
    NETWORKING_AVAILABLE = True
except ImportError:
    NETWORKING_AVAILABLE = False


class CommunicationManager:
    """Manages robot communication interfaces"""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize communication manager"""
        self.logger = logging.getLogger(__name__)
        self.config = config
        
        # Configuration
        self.wifi_enabled = config.get('wifi_enabled', True) and NETWORKING_AVAILABLE
        self.telemetry_port = config.get('telemetry_port', 8080)
        
        # Command callback
        self.command_callback: Optional[Callable] = None
        
        # Telemetry data
        self.telemetry_data = {}
        self.last_telemetry_update = time.time()
        
        # HTTP server for web interface
        self.http_server = None
        self.server_thread = None
        
        # Status
        self.is_running = False
        self.start_time = time.time()  # Track when communication system started
        
        if not NETWORKING_AVAILABLE:
            self.logger.warning("Networking libraries not available - communication disabled")
            self.wifi_enabled = False
        
        if self.wifi_enabled:
            self._start_http_server()
        
        self.logger.info(f"Communication manager initialized (WiFi: {self.wifi_enabled})")
    
    def set_command_callback(self, callback: Callable):
        """Set callback for received commands"""
        self.logger.info(f"Setting command callback: {callback}")
        self.command_callback = callback
        self.logger.debug(f"Command callback set successfully: {self.command_callback}")
    
    
    def update(self):
        """Update communication system"""
        if not self.is_running:
            return
        
        # Update telemetry periodically
        current_time = time.time()
        if current_time - self.last_telemetry_update > 1.0:  # Every second
            self._update_telemetry()
            self.last_telemetry_update = current_time
    
    def _start_http_server(self):
        """Start HTTP server for web interface"""
        if not self.wifi_enabled:
            return
        
        try:
            # Create custom handler class with access to this instance
            comm_manager = self
            
            class RobotHTTPHandler(BaseHTTPRequestHandler):
                def do_GET(self):
                    if self.path == '/':
                        self._serve_main_page()
                    elif self.path == '/status':
                        self._serve_status()
                    elif self.path.startswith('/api/'):
                        self._handle_api_get()
                    else:
                        self._serve_404()
                
                def do_POST(self):
                    comm_manager.logger.info(f"POST request to {self.path}")
                    if self.path.startswith('/api/'):
                        self._handle_api_post()
                    else:
                        self._serve_404()
                
                def _serve_main_page(self):
                    html = comm_manager._get_main_page_html()
                    self.send_response(200)
                    self.send_header('Content-type', 'text/html')
                    self.end_headers()
                    self.wfile.write(html.encode())
                
                def _serve_status(self):
                    self.send_response(200)
                    self.send_header('Content-type', 'application/json')
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.end_headers()
                    json_data = json.dumps(comm_manager.telemetry_data)
                    self.wfile.write(json_data.encode())
                
                def _handle_api_get(self):
                    self.send_response(200)
                    self.send_header('Content-type', 'application/json')
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.end_headers()
                    response = {"status": "ok", "data": comm_manager.telemetry_data}
                    self.wfile.write(json.dumps(response).encode())
                
                def _handle_api_post(self):
                    comm_manager.logger.info(f"Handling API POST to {self.path}")
                    content_length = int(self.headers['Content-Length'])
                    post_data = self.rfile.read(content_length)
                    
                    try:
                        command = json.loads(post_data.decode())
                        comm_manager._handle_command(command)
                        
                        self.send_response(200)
                        self.send_header('Content-type', 'application/json')
                        self.send_header('Access-Control-Allow-Origin', '*')
                        self.end_headers()
                        response = {"status": "ok", "message": "Command received"}
                        self.wfile.write(json.dumps(response).encode())
                        
                    except Exception as e:
                        self.send_response(400)
                        self.send_header('Content-type', 'application/json')
                        self.end_headers()
                        response = {"status": "error", "message": str(e)}
                        self.wfile.write(json.dumps(response).encode())
                
                def _serve_404(self):
                    self.send_response(404)
                    self.send_header('Content-type', 'text/html')
                    self.end_headers()
                    self.wfile.write(b'<h1>404 Not Found</h1>')
                
                def log_message(self, format, *args):
                    # Suppress default HTTP server logging
                    pass
            
            # Start server in separate thread
            self.http_server = HTTPServer(('0.0.0.0', self.telemetry_port), RobotHTTPHandler)
            self.server_thread = threading.Thread(target=self.http_server.serve_forever)
            self.server_thread.daemon = True
            self.server_thread.start()
            
            self.is_running = True
            self.logger.info(f"HTTP server started on port {self.telemetry_port}")
            
        except Exception as e:
            self.logger.error(f"Failed to start HTTP server: {e}")
            self.wifi_enabled = False
    
    def _get_main_page_html(self) -> str:
        """Generate main web interface HTML"""
        return """
<!DOCTYPE html>
<html>
<head>
    <title>Ruohobot Control</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background: #f0f0f0; }
        .container { max-width: 800px; margin: 0 auto; background: white; padding: 20px; border-radius: 10px; }
        .status { background: #e8f5e8; padding: 15px; border-radius: 5px; margin: 10px 0; }
        .controls { display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; margin: 20px 0; }
        button { padding: 15px; font-size: 16px; border: none; border-radius: 5px; cursor: pointer; }
        .btn-primary { background: #007bff; color: white; }
        .btn-danger { background: #dc3545; color: white; }
        .btn-success { background: #28a745; color: white; }
        .btn-warning { background: #ffc107; color: black; }
        #status-data { font-family: monospace; font-size: 12px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🤖 Ruohobot Control Panel</h1>
        
        <div class="status">
            <h3>Robot Status</h3>
            <div id="status-data">Loading...</div>
        </div>
        
        <div class="controls">
            <button class="btn-primary" onclick="sendCommand('state_change', 'manual_control')">Manual Control</button>
            <button class="btn-success" onclick="sendCommand('state_change', 'autonomous')">Start Autonomous</button>
            <button class="btn-warning" onclick="sendCommand('state_change', 'idle')">Stop/Idle</button>
            
            <button class="btn-primary" onclick="sendCommand('move', {speed: 300, direction: 0})">Forward</button>
            <button class="btn-primary" onclick="sendCommand('move', {speed: -300, direction: 0})">Backward</button>
            <button class="btn-primary" onclick="sendCommand('move', {speed: 0, direction: 0})">Stop Motors</button>
            
            <button class="btn-warning" onclick="sendCommand('navigation', 'explore')">Explore Mode</button>
            <button class="btn-warning" onclick="sendCommand('navigation', 'return_home')">Return Home</button>
            <button class="btn-danger" onclick="sendCommand('emergency_stop', null)">EMERGENCY STOP</button>
        </div>
        
        <div class="status">
            <h3>Manual Controls</h3>
            <p><strong>Click this area and use WASD keys:</strong></p>
            <div id="control-area" tabindex="0" style="border: 2px solid #007bff; padding: 20px; background: #f8f9fa; border-radius: 5px; text-align: center; font-weight: bold; cursor: pointer;" onclick="this.focus()">
                <p>🎮 WASD Control Zone - Click to Focus</p>
                <div style="margin-top: 10px;">
                    <div>W - Forward</div>
                    <div>S - Backward</div>
                    <div>A - Turn Left</div>
                    <div>D - Turn Right</div>
                    <div>Space - Stop</div>
                </div>
            </div>
            <p style="color: #666; font-size: 12px; margin-top: 10px;">Make sure robot is in Manual Control mode first!</p>
        </div>
    </div>
    
    <script>
        function sendCommand(type, data) {
            fetch('/api/command', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({type: type, data: data})
            })
            .then(response => response.json())
            .then(data => console.log('Command sent:', data))
            .catch(error => console.error('Error:', error));
        }
        
        function updateStatus() {
            fetch('/status')
            .then(response => response.json())
            .then(data => {
                document.getElementById('status-data').innerHTML = 
                    '<pre>' + JSON.stringify(data, null, 2) + '</pre>';
            })
            .catch(error => console.error('Status update error:', error));
        }
        
        // Keyboard controls - enhanced with better focus handling
        document.addEventListener('keydown', function(event) {
            // Prevent default behavior for WASD and space to avoid page scrolling
            if (['w', 'a', 's', 'd', ' '].includes(event.key.toLowerCase())) {
                event.preventDefault();
            }
            
            switch(event.key.toLowerCase()) {
                case 'w': 
                    sendCommand('move', {speed: 400, direction: 0}); 
                    console.log('W pressed - Forward');
                    break;
                case 's': 
                    sendCommand('move', {speed: -400, direction: 0}); 
                    console.log('S pressed - Backward');
                    break;
                case 'a': 
                    sendCommand('move', {speed: 0, direction: -400}); 
                    console.log('A pressed - Turn Left');
                    break;
                case 'd': 
                    sendCommand('move', {speed: 0, direction: 400}); 
                    console.log('D pressed - Turn Right');
                    break;
                case ' ': 
                    sendCommand('move', {speed: 0, direction: 0}); 
                    console.log('Space pressed - Stop');
                    break;
            }
        });
        
        // Add visual feedback for the control area
        const controlArea = document.getElementById('control-area');
        if (controlArea) {
            controlArea.addEventListener('focus', function() {
                this.style.backgroundColor = '#e7f3ff';
                this.innerHTML = '<p>🎮 WASD Control Zone - ACTIVE</p><div style="margin-top: 10px;"><div>W - Forward</div><div>S - Backward</div><div>A - Turn Left</div><div>D - Turn Right</div><div>Space - Stop</div></div>';
            });
            
            controlArea.addEventListener('blur', function() {
                this.style.backgroundColor = '#f8f9fa';
                this.innerHTML = '<p>🎮 WASD Control Zone - Click to Focus</p><div style="margin-top: 10px;"><div>W - Forward</div><div>S - Backward</div><div>A - Turn Left</div><div>D - Turn Right</div><div>Space - Stop</div></div>';
            });
        }
        
        // Update status every 2 seconds
        setInterval(updateStatus, 2000);
        updateStatus(); // Initial load
    </script>
</body>
</html>
        """
    
    def _handle_command(self, command: Dict[str, Any]):
        """Handle received command"""
        self.logger.info(f"Received command: {command}")
        
        if self.command_callback:
            self.logger.info(f"Command callback exists, calling it with: {command}")
            try:
                self.command_callback(command)
                self.logger.info("Command callback executed successfully")
            except Exception as e:
                self.logger.error(f"Error executing command: {e}")
        else:
            self.logger.warning("No command callback set - command not processed")
    
    def _update_telemetry(self):
        """Update telemetry data"""
        # This will be populated by the robot's main systems
        self.telemetry_data.update({
            'timestamp': time.time(),
            'uptime': time.time() - self.start_time,
            'communication_status': 'active' if self.is_running else 'inactive'
        })
    
    def update_telemetry(self, data: Dict[str, Any]):
        """Update telemetry with new data"""
        self.telemetry_data.update(data)
    
    def send_message(self, message: str):
        """Send message (placeholder for future implementation)"""
        self.logger.info(f"Message: {message}")
    
    def get_status(self) -> Dict[str, Any]:
        """Get communication system status"""
        return {
            'wifi_enabled': self.wifi_enabled,
            'http_server_running': self.is_running,
            'telemetry_port': self.telemetry_port,
            'last_telemetry_update': self.last_telemetry_update
        }
    
    def shutdown(self):
        """Shutdown communication system"""
        self.logger.info("Shutting down communication system...")
        self.is_running = False
        
        if self.http_server:
            try:
                self.http_server.shutdown()
                self.http_server.server_close()
            except Exception as e:
                self.logger.error(f"Error shutting down HTTP server: {e}")
        
        if self.server_thread and self.server_thread.is_alive():
            self.server_thread.join(timeout=2.0)
        
        self.logger.info("Communication system shutdown complete")
