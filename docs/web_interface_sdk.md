# Ruohobot Web Interface SDK Guide

**Version:** 1.0  
**Date:** July 18, 2025  
**Author:** Ruohobot Development Team

## Table of Contents

1. [Overview](#overview)
2. [Getting Started](#getting-started)
3. [API Reference](#api-reference)
4. [Web Interface Components](#web-interface-components)
5. [Real-time Communication](#real-time-communication)
6. [Development Examples](#development-examples)
7. [Custom Extensions](#custom-extensions)
8. [Troubleshooting](#troubleshooting)

---

## Overview

The Ruohobot Web Interface provides a comprehensive HTTP-based API and web dashboard for controlling and monitoring your autonomous robot. Built with Python's built-in HTTP server, it offers both human-friendly web controls and programmatic API access.

### Key Features

- **Real-time Robot Control**: Direct motor control via web buttons or API calls
- **Live Telemetry**: Continuous status updates including uptime, safety status, and sensor data
- **Safety Management**: Emergency stop controls and safety monitoring
- **State Management**: Robot state transitions (idle, manual, autonomous, emergency)
- **Sensor Integration**: Access to distance sensors, environmental data, and system status
- **RESTful API**: Clean HTTP endpoints for programmatic control

### Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Web Browser   │◄──►│  HTTP Server     │◄──►│  Robot Core     │
│                 │    │  (Port 8080)     │    │                 │
├─────────────────┤    ├──────────────────┤    ├─────────────────┤
│ • Control Panel │    │ • REST API       │    │ • Motor Control │
│ • Status Display│    │ • WebSocket      │    │ • Safety System │
│ • Emergency Stop│    │ • Static Files   │    │ • Navigation    │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

---

## Getting Started

### Prerequisites

- **Python 3.8+** with Ruohobot environment activated
- **Network Access** to the robot (local network or direct connection)
- **Modern Web Browser** (Chrome, Firefox, Safari, Edge)

### Quick Start

1. **Start the Robot System**:
   ```bash
   cd /path/to/Ruohobot
   source .venv/bin/activate
   python src/main.py
   ```

2. **Access Web Interface**:
   ```
   http://localhost:8080/          # Local access
   http://ROBOT_IP:8080/           # Network access
   http://10.0.0.78:8080/          # Example IP
   ```

3. **Test API Connectivity**:
   ```bash
   curl http://ROBOT_IP:8080/status
   ```

### Default Configuration

- **Port**: 8080
- **Host**: 0.0.0.0 (all interfaces)
- **Protocol**: HTTP (consider HTTPS for production)
- **Update Frequency**: 1 second for telemetry

---

## API Reference

### Base URL
```
http://ROBOT_IP:8080
```

### Authentication
Currently no authentication required (add for production use).

### Response Format
All API responses use JSON format:
```json
{
    "status": "ok|error",
    "message": "Human readable message",
    "data": {...}  // Optional data payload
}
```

### Core Endpoints

#### **GET /** - Main Dashboard
Returns the complete web interface HTML page.

**Response**: HTML page with JavaScript controls

#### **GET /status** - Robot Status
Get current robot status and telemetry.

**Response**:
```json
{
    "timestamp": 1752869783.746935,
    "uptime": 60.326526165008545,
    "communication_status": "active"
}
```

#### **POST /api/command** - Send Command
Send control commands to the robot.

**Request Body**:
```json
{
    "type": "command_type",
    "data": {...}  // Command-specific data
}
```

**Supported Commands**:

##### Movement Commands
```json
{
    "type": "move",
    "data": {
        "speed": 400,        // -800 to 800
        "direction": 0       // -800 to 800 (turning)
    }
}
```

##### State Changes
```json
{
    "type": "state_change",
    "state": "idle|manual_control|autonomous|emergency_stop"
}
```

##### Emergency Controls
```json
{
    "type": "emergency_stop"
}
```

##### Stop Command
```json
{
    "type": "stop"
}
```

**Response**:
```json
{
    "status": "ok",
    "message": "Command received"
}
```

#### **GET /api/telemetry** - Extended Telemetry
Get comprehensive robot telemetry data.

**Response**:
```json
{
    "robot_state": "idle",
    "safety": {
        "is_safe": true,
        "emergency_active": false,
        "violations": []
    },
    "motors": {
        "status": "ready",
        "speeds": [0, 0, 0]
    },
    "sensors": {
        "front_distance": 2.5,
        "battery_voltage": 12.4,
        "temperature": 23.5
    },
    "timestamp": 1752869783.746935
}
```

#### **GET /api/safety** - Safety Status
Get detailed safety system status.

**Response**:
```json
{
    "is_safe": true,
    "emergency_active": false,
    "safety_violations": [],
    "emergency_stop_enabled": true,
    "last_safety_check": 1752869783.0,
    "violation_counts": {}
}
```

---

## Web Interface Components

### Control Panel

The web interface includes these interactive elements:

#### **Movement Controls**
- **Forward Button**: Moves robot forward at default speed
- **Backward Button**: Moves robot backward
- **Left/Right Buttons**: Turns robot left or right
- **Stop Button**: Immediately stops all motors

#### **Safety Controls**
- **Emergency Stop**: Large red button for immediate halt
- **State Selector**: Dropdown to change robot operating mode

#### **Status Display**
- **Uptime Counter**: Shows robot operational time
- **Connection Status**: Real-time communication status
- **Safety Indicator**: Green/red status indicator
- **Current State**: Displays active robot mode

#### **Telemetry Panel**
- **Motor Status**: Speed and direction feedback
- **Sensor Readings**: Distance, temperature, battery
- **System Health**: CPU, memory, temperature

### JavaScript API

The web interface includes a JavaScript library for easier integration:

```javascript
// Robot control class
class RobotController {
    constructor(baseUrl = '') {
        this.baseUrl = baseUrl;
    }
    
    // Send movement command
    async move(speed, direction) {
        return await this.sendCommand('move', {speed, direction});
    }
    
    // Emergency stop
    async emergencyStop() {
        return await this.sendCommand('emergency_stop');
    }
    
    // Change robot state
    async setState(state) {
        return await this.sendCommand('state_change', {state});
    }
    
    // Get current status
    async getStatus() {
        const response = await fetch(`${this.baseUrl}/status`);
        return await response.json();
    }
    
    // Internal command sender
    async sendCommand(type, data = {}) {
        const response = await fetch(`${this.baseUrl}/api/command`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({type, data})
        });
        return await response.json();
    }
}

// Usage example
const robot = new RobotController();
robot.move(400, 0);  // Move forward
robot.emergencyStop();  // Stop immediately
```

---

## Real-time Communication

### Polling Strategy

The web interface uses HTTP polling for real-time updates:

```javascript
// Auto-updating status display
function startStatusUpdates() {
    setInterval(async () => {
        try {
            const status = await robot.getStatus();
            updateDisplay(status);
        } catch (error) {
            console.error('Status update failed:', error);
        }
    }, 1000);  // Update every second
}
```

### WebSocket Enhancement (Future)

For higher frequency updates, consider WebSocket implementation:

```python
# Future WebSocket endpoint
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        telemetry = get_robot_telemetry()
        await websocket.send_json(telemetry)
        await asyncio.sleep(0.1)  # 10Hz updates
```

---

## Development Examples

### Basic Robot Control Script

```python
#!/usr/bin/env python3
"""
Simple robot control script using the HTTP API
"""
import requests
import time
import json

class RobotHTTPClient:
    def __init__(self, base_url="http://localhost:8080"):
        self.base_url = base_url
        
    def send_command(self, command_type, data=None):
        """Send command to robot"""
        payload = {"type": command_type}
        if data:
            payload["data"] = data
            
        response = requests.post(
            f"{self.base_url}/api/command",
            headers={"Content-Type": "application/json"},
            json=payload
        )
        return response.json()
    
    def get_status(self):
        """Get robot status"""
        response = requests.get(f"{self.base_url}/status")
        return response.json()
    
    def move_forward(self, speed=400, duration=2.0):
        """Move forward for specified duration"""
        self.send_command("move", {"speed": speed, "direction": 0})
        time.sleep(duration)
        self.send_command("stop")
    
    def turn_left(self, speed=300, duration=1.0):
        """Turn left for specified duration"""
        self.send_command("move", {"speed": 0, "direction": -speed})
        time.sleep(duration)
        self.send_command("stop")

# Example usage
if __name__ == "__main__":
    robot = RobotHTTPClient("http://10.0.0.78:8080")
    
    # Check robot status
    status = robot.get_status()
    print(f"Robot uptime: {status['uptime']:.1f} seconds")
    
    # Perform simple movement pattern
    robot.move_forward(400, 2.0)   # Forward 2 seconds
    robot.turn_left(300, 1.0)      # Turn left 1 second
    robot.move_forward(400, 2.0)   # Forward 2 seconds
    
    print("Movement sequence complete")
```

### Autonomous Patrol Script

```python
#!/usr/bin/env python3
"""
Autonomous patrol using distance sensors and HTTP API
"""
import requests
import time
import json

class PatrolBot:
    def __init__(self, robot_url="http://localhost:8080"):
        self.robot = RobotHTTPClient(robot_url)
        self.min_distance = 0.5  # meters
        
    def get_sensor_data(self):
        """Get sensor readings"""
        response = requests.get(f"{self.robot.base_url}/api/telemetry")
        return response.json().get('sensors', {})
    
    def patrol_step(self):
        """Single patrol step with obstacle avoidance"""
        sensors = self.get_sensor_data()
        front_distance = sensors.get('front_distance', float('inf'))
        
        if front_distance > self.min_distance:
            # Path clear - move forward
            self.robot.send_command("move", {"speed": 300, "direction": 0})
            time.sleep(0.5)
        else:
            # Obstacle detected - turn right
            print(f"Obstacle at {front_distance:.2f}m - turning")
            self.robot.send_command("stop")
            time.sleep(0.2)
            self.robot.turn_right(400, 0.8)
            time.sleep(0.2)
    
    def start_patrol(self, duration=60):
        """Start autonomous patrol for specified duration"""
        print(f"Starting patrol for {duration} seconds...")
        start_time = time.time()
        
        try:
            while time.time() - start_time < duration:
                self.patrol_step()
                time.sleep(0.1)
        except KeyboardInterrupt:
            print("Patrol interrupted by user")
        finally:
            self.robot.send_command("stop")
            print("Patrol complete")

# Run patrol
if __name__ == "__main__":
    patrol = PatrolBot("http://10.0.0.78:8080")
    patrol.start_patrol(30)  # 30 second patrol
```

### Custom Web Dashboard

```html
<!DOCTYPE html>
<html>
<head>
    <title>Custom Ruohobot Dashboard</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .status-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; }
        .status-card { border: 1px solid #ccc; padding: 15px; border-radius: 8px; }
        .control-buttons button { margin: 5px; padding: 10px 20px; font-size: 16px; }
        .emergency { background-color: #ff4444; color: white; }
        .safe { background-color: #44ff44; color: black; }
    </style>
</head>
<body>
    <h1>Ruohobot Custom Dashboard</h1>
    
    <div class="control-buttons">
        <button onclick="moveForward()">Forward</button>
        <button onclick="moveBackward()">Backward</button>
        <button onclick="turnLeft()">Left</button>
        <button onclick="turnRight()">Right</button>
        <button onclick="stopRobot()">Stop</button>
        <button onclick="emergencyStop()" class="emergency">EMERGENCY STOP</button>
    </div>
    
    <div class="status-grid">
        <div class="status-card">
            <h3>System Status</h3>
            <p>Uptime: <span id="uptime">--</span></p>
            <p>State: <span id="state">--</span></p>
            <p>Safety: <span id="safety">--</span></p>
        </div>
        
        <div class="status-card">
            <h3>Sensors</h3>
            <p>Front Distance: <span id="front-dist">--</span> m</p>
            <p>Battery: <span id="battery">--</span> V</p>
            <p>Temperature: <span id="temp">--</span> °C</p>
        </div>
        
        <div class="status-card">
            <h3>Motors</h3>
            <p>Motor 1: <span id="motor1">--</span></p>
            <p>Motor 2: <span id="motor2">--</span></p>
            <p>Motor 3: <span id="motor3">--</span></p>
        </div>
    </div>

    <script>
        // Robot control functions
        const ROBOT_URL = 'http://10.0.0.78:8080';
        
        async function sendCommand(type, data = {}) {
            try {
                const response = await fetch(`${ROBOT_URL}/api/command`, {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({type, data})
                });
                return await response.json();
            } catch (error) {
                console.error('Command failed:', error);
            }
        }
        
        function moveForward() { sendCommand('move', {speed: 400, direction: 0}); }
        function moveBackward() { sendCommand('move', {speed: -400, direction: 0}); }
        function turnLeft() { sendCommand('move', {speed: 0, direction: -400}); }
        function turnRight() { sendCommand('move', {speed: 0, direction: 400}); }
        function stopRobot() { sendCommand('stop'); }
        function emergencyStop() { sendCommand('emergency_stop'); }
        
        // Status updates
        async function updateStatus() {
            try {
                const [status, telemetry] = await Promise.all([
                    fetch(`${ROBOT_URL}/status`).then(r => r.json()),
                    fetch(`${ROBOT_URL}/api/telemetry`).then(r => r.json())
                ]);
                
                // Update display
                document.getElementById('uptime').textContent = 
                    Math.floor(status.uptime) + 's';
                document.getElementById('state').textContent = 
                    telemetry.robot_state || 'unknown';
                
                const safetyEl = document.getElementById('safety');
                if (telemetry.safety?.is_safe) {
                    safetyEl.textContent = 'SAFE';
                    safetyEl.className = 'safe';
                } else {
                    safetyEl.textContent = 'UNSAFE';
                    safetyEl.className = 'emergency';
                }
                
                // Update sensor data
                const sensors = telemetry.sensors || {};
                document.getElementById('front-dist').textContent = 
                    sensors.front_distance?.toFixed(2) || '--';
                document.getElementById('battery').textContent = 
                    sensors.battery_voltage?.toFixed(1) || '--';
                document.getElementById('temp').textContent = 
                    sensors.temperature?.toFixed(1) || '--';
                
            } catch (error) {
                console.error('Status update failed:', error);
            }
        }
        
        // Start auto-updates
        setInterval(updateStatus, 1000);
        updateStatus(); // Initial update
    </script>
</body>
</html>
```

---

## Custom Extensions

### Adding New API Endpoints

Extend the web interface by modifying the HTTP handler:

```python
def _handle_api_get(self):
    """Handle API GET requests"""
    if self.path == '/api/custom-endpoint':
        # Your custom logic here
        data = {"custom": "response"}
        self._send_json_response(data)
    elif self.path == '/api/sensor-history':
        # Return sensor history
        history = self._get_sensor_history()
        self._send_json_response(history)
    else:
        self._serve_404()
```

### Custom Command Types

Add new command types in the robot's command handler:

```python
def _handle_command(self, command: Dict[str, Any]):
    """Handle commands from communication system"""
    cmd_type = command.get('type')
    
    if cmd_type == 'custom_dance':
        self._perform_dance_routine(command.get('data', {}))
    elif cmd_type == 'set_led_color':
        self._set_led_color(command['data']['color'])
    elif cmd_type == 'take_photo':
        photo_path = self._capture_photo()
        return {'photo_url': f'/photos/{photo_path}'}
```

### Data Logging Integration

Add automatic data logging to your telemetry:

```python
import csv
import json
from datetime import datetime

class TelemetryLogger:
    def __init__(self, log_file="robot_telemetry.csv"):
        self.log_file = log_file
        self.fieldnames = ['timestamp', 'state', 'x', 'y', 'heading', 
                          'battery', 'front_distance']
        
    def log_telemetry(self, telemetry_data):
        """Log telemetry data to CSV file"""
        with open(self.log_file, 'a', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=self.fieldnames)
            
            # Write header if file is empty
            if csvfile.tell() == 0:
                writer.writeheader()
            
            # Extract and log relevant data
            row = {
                'timestamp': datetime.now().isoformat(),
                'state': telemetry_data.get('robot_state'),
                'battery': telemetry_data.get('sensors', {}).get('battery_voltage'),
                'front_distance': telemetry_data.get('sensors', {}).get('front_distance'),
                # Add more fields as needed
            }
            writer.writerow(row)
```

---

## Troubleshooting

### Common Issues

#### **Cannot Connect to Web Interface**

1. **Check Robot Status**:
   ```bash
   ps aux | grep python.*main.py
   ```

2. **Verify Port Binding**:
   ```bash
   netstat -tln | grep 8080
   ```

3. **Check Firewall**:
   ```bash
   sudo ufw status
   sudo ufw allow 8080
   ```

4. **Test Local Connection**:
   ```bash
   curl http://localhost:8080/status
   ```

#### **Commands Not Working**

1. **Check Robot State**: Robot must be in appropriate state (not emergency stop)
2. **Verify JSON Format**: Ensure proper Content-Type header
3. **Check Safety System**: Safety violations prevent movement
4. **Monitor Logs**: Check robot logs for error messages

#### **Slow Response Times**

1. **Network Latency**: Use wired connection if possible
2. **Robot Load**: Check CPU usage on robot
3. **Polling Frequency**: Reduce update frequency if needed
4. **Browser Console**: Check for JavaScript errors

#### **Emergency Stop Issues**

1. **Reset State**: Use state change API to exit emergency
2. **Check Safety Violations**: Resolve any active safety issues
3. **Motor Controller**: Verify motor controller is responsive
4. **Power Cycle**: Restart robot system if needed

### Debug Commands

```bash
# Check robot status
curl -s http://ROBOT_IP:8080/status | python3 -m json.tool

# Test movement command
curl -X POST http://ROBOT_IP:8080/api/command \
  -H "Content-Type: application/json" \
  -d '{"type": "move", "data": {"speed": 200, "direction": 0}}'

# Get detailed telemetry
curl -s http://ROBOT_IP:8080/api/telemetry | python3 -m json.tool

# Check safety status
curl -s http://ROBOT_IP:8080/api/safety | python3 -m json.tool

# Emergency stop
curl -X POST http://ROBOT_IP:8080/api/command \
  -H "Content-Type: application/json" \
  -d '{"type": "emergency_stop"}'
```

### Development Tools

1. **Browser Developer Tools**: Use F12 to debug JavaScript
2. **Network Tab**: Monitor HTTP requests and responses
3. **Postman/Insomnia**: Test API endpoints
4. **Robot Logs**: Monitor `/home/pi/Ruohobot/logs/ruohobot.log`

---

## Security Considerations

### Production Deployment

For production use, consider these security enhancements:

1. **HTTPS**: Use SSL/TLS encryption
2. **Authentication**: Add user authentication
3. **Authorization**: Role-based access control
4. **Rate Limiting**: Prevent API abuse
5. **Input Validation**: Sanitize all inputs
6. **Network Isolation**: Use VPN or private networks

### Sample Security Implementation

```python
import hashlib
import jwt
from functools import wraps

class SecurityManager:
    def __init__(self, secret_key):
        self.secret_key = secret_key
        self.users = {
            'admin': 'hashed_password_here',
            'operator': 'hashed_password_here'
        }
    
    def authenticate(self, username, password):
        """Authenticate user credentials"""
        if username in self.users:
            hashed = hashlib.sha256(password.encode()).hexdigest()
            return hashed == self.users[username]
        return False
    
    def require_auth(self, f):
        """Decorator for endpoints requiring authentication"""
        @wraps(f)
        def decorated_function(*args, **kwargs):
            token = self.get_auth_token()
            if not self.verify_token(token):
                return self.unauthorized_response()
            return f(*args, **kwargs)
        return decorated_function
```

---

## Performance Optimization

### Caching Strategy

```python
import time
from functools import lru_cache

class CachedTelemetry:
    def __init__(self, cache_duration=0.1):  # 100ms cache
        self.cache_duration = cache_duration
        self.last_update = 0
        self.cached_data = {}
    
    def get_telemetry(self):
        """Get cached telemetry data"""
        now = time.time()
        if now - self.last_update > self.cache_duration:
            self.cached_data = self._generate_telemetry()
            self.last_update = now
        return self.cached_data
```

### Async Implementation (Future)

```python
import asyncio
import aiohttp
from aiohttp import web

async def handle_command(request):
    """Async command handler"""
    data = await request.json()
    result = await process_command_async(data)
    return web.json_response(result)

# WebSocket for real-time updates
async def websocket_handler(request):
    ws = web.WebSocketResponse()
    await ws.prepare(request)
    
    async for msg in ws:
        if msg.type == aiohttp.MsgType.TEXT:
            # Handle real-time command
            await handle_realtime_command(msg.data)
    
    return ws
```

---

## Conclusion

The Ruohobot Web Interface SDK provides a powerful, flexible platform for robot control and monitoring. Whether you're building simple control scripts or complex autonomous behaviors, the HTTP API and web interface give you the tools you need.

### Next Steps

1. **Explore the Examples**: Try the provided code samples
2. **Build Custom Dashboards**: Create interfaces for your specific needs
3. **Integrate with Other Systems**: Use the API with external applications
4. **Contribute**: Help improve the interface with new features

### Resources

- **GitHub Repository**: [Ruohobot Project](https://github.com/rukkanen/Ruohobot)
- **Motor Control SDK**: `docs/drive_coding.md`
- **Safety Documentation**: `src/core/safety.py`
- **Configuration Guide**: `config/robot_config.yaml`

### Support

For questions, issues, or contributions:
- **Issues**: Use GitHub Issues for bug reports
- **Discussions**: Join the community discussions
- **Documentation**: This guide and inline code comments

Happy roboting! 🤖🚀

---

*This SDK guide is part of the Ruohobot project. For the latest updates and examples, check the official repository.*
