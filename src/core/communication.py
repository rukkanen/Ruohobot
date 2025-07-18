"""
Communication Manager

Handles WiFi communication, telemetry, and remote control commands.
"""

import logging
import time
import json
import socket
import threading
from typing import Dict, Any, Callable, Optional, List
from queue import Queue, Empty


class CommunicationManager:
    """
    Manages robot communication including WiFi, telemetry, and command processing.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the communication manager.
        
        Args:
            config: Communication configuration
        """
        self.logger = logging.getLogger(__name__)
        self.config = config
        
        # Configuration
        self.wifi_enabled = config.get('wifi_enabled', True)
        self.telemetry_port = config.get('telemetry_port', 8080)
        
        # Communication state
        self.is_connected = False
        self.last_heartbeat = time.time()
        
        # Command processing
        self.command_queue = Queue()
        self.command_callback: Optional[Callable] = None
        
        # Telemetry
        self.telemetry_data = {}
        self.telemetry_clients = []
        
        # Network components
        self.server_socket = None
        self.server_thread = None
        self.running = False
        
        # Initialize communication
        if self.wifi_enabled:
            self._initialize_wifi_communication()
        
        self.logger.info("Communication manager initialized")
    
    def _initialize_wifi_communication(self):
        """Initialize WiFi communication server"""
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind(('0.0.0.0', self.telemetry_port))
            self.server_socket.listen(5)
            
            self.running = True
            self.server_thread = threading.Thread(target=self._server_loop, daemon=True)
            self.server_thread.start()
            
            self.is_connected = True
            self.logger.info(f"WiFi communication server started on port {self.telemetry_port}")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize WiFi communication: {e}")
            self.is_connected = False
    
    def _server_loop(self):
        """Main server loop for handling client connections"""
        while self.running:
            try:
                client_socket, address = self.server_socket.accept()
                self.logger.info(f"Client connected from {address}")
                
                # Handle client in a separate thread
                client_thread = threading.Thread(
                    target=self._handle_client,
                    args=(client_socket, address),
                    daemon=True
                )
                client_thread.start()
                
            except Exception as e:
                if self.running:
                    self.logger.error(f"Error in server loop: {e}")
                break
    
    def _handle_client(self, client_socket, address):
        """Handle individual client connection"""
        try:
            self.telemetry_clients.append(client_socket)
            
            while self.running:
                # Receive data from client
                data = client_socket.recv(1024)
                if not data:
                    break
                
                try:
                    # Parse command
                    command = json.loads(data.decode('utf-8'))
                    self._process_command(command)
                    
                    # Send acknowledgment
                    response = {'status': 'ok', 'timestamp': time.time()}
                    client_socket.send(json.dumps(response).encode('utf-8'))
                    
                except json.JSONDecodeError:
                    self.logger.warning(f"Invalid JSON received from {address}")
                except Exception as e:
                    self.logger.error(f"Error processing command from {address}: {e}")
        
        except Exception as e:
            self.logger.error(f"Error handling client {address}: {e}")
        finally:
            if client_socket in self.telemetry_clients:
                self.telemetry_clients.remove(client_socket)
            client_socket.close()
            self.logger.info(f"Client {address} disconnected")
    
    def _process_command(self, command: Dict[str, Any]):
        """
        Process incoming command.
        
        Args:
            command: Command dictionary
        """
        self.logger.info(f"Received command: {command}")
        
        # Add to command queue for processing by main thread
        self.command_queue.put(command)
        
        # Update heartbeat
        self.last_heartbeat = time.time()
    
    def update(self):
        """Update communication system - process pending commands"""
        try:
            # Process pending commands
            while not self.command_queue.empty():
                try:
                    command = self.command_queue.get_nowait()
                    if self.command_callback:
                        self.command_callback(command)
                except Empty:
                    break
                except Exception as e:
                    self.logger.error(f"Error processing command: {e}")
            
            # Send telemetry to connected clients
            self._send_telemetry()
            
            # Check connection health
            self._check_connection_health()
            
        except Exception as e:
            self.logger.error(f"Error in communication update: {e}")
    
    def _send_telemetry(self):
        """Send telemetry data to connected clients"""
        if not self.telemetry_clients:
            return
        
        try:
            telemetry_message = json.dumps(self.telemetry_data).encode('utf-8')
            
            # Send to all connected clients
            disconnected_clients = []
            for client in self.telemetry_clients:
                try:
                    client.send(telemetry_message)
                except Exception:
                    disconnected_clients.append(client)
            
            # Remove disconnected clients
            for client in disconnected_clients:
                self.telemetry_clients.remove(client)
                
        except Exception as e:
            self.logger.error(f"Error sending telemetry: {e}")
    
    def _check_connection_health(self):
        """Check communication health"""
        current_time = time.time()
        time_since_heartbeat = current_time - self.last_heartbeat
        
        # Consider connection lost if no heartbeat for 30 seconds
        if time_since_heartbeat > 30.0 and self.is_connected:
            self.logger.warning("Communication heartbeat lost")
            # Could trigger autonomous mode or safety measures
    
    def set_command_callback(self, callback: Callable):
        """
        Set callback function for processing commands.
        
        Args:
            callback: Function to call with received commands
        """
        self.command_callback = callback
    
    def update_telemetry(self, data: Dict[str, Any]):
        """
        Update telemetry data.
        
        Args:
            data: Dictionary with telemetry information
        """
        self.telemetry_data.update(data)
        self.telemetry_data['timestamp'] = time.time()
    
    def send_status_update(self, status: Dict[str, Any]):
        """
        Send status update to connected clients.
        
        Args:
            status: Status information to broadcast
        """
        try:
            message = {
                'type': 'status_update',
                'data': status,
                'timestamp': time.time()
            }
            
            message_json = json.dumps(message).encode('utf-8')
            
            disconnected_clients = []
            for client in self.telemetry_clients:
                try:
                    client.send(message_json)
                except Exception:
                    disconnected_clients.append(client)
            
            # Remove disconnected clients
            for client in disconnected_clients:
                self.telemetry_clients.remove(client)
                
        except Exception as e:
            self.logger.error(f"Error sending status update: {e}")
    
    def get_communication_status(self) -> Dict[str, Any]:
        """
        Get current communication status.
        
        Returns:
            Dictionary with communication information
        """
        return {
            'wifi_enabled': self.wifi_enabled,
            'connected': self.is_connected,
            'clients_connected': len(self.telemetry_clients),
            'last_heartbeat': self.last_heartbeat,
            'port': self.telemetry_port
        }
    
    def shutdown(self):
        """Shutdown communication system"""
        self.logger.info("Shutting down communication system...")
        self.running = False
        
        # Close all client connections
        for client in self.telemetry_clients:
            try:
                client.close()
            except Exception:
                pass
        self.telemetry_clients.clear()
        
        # Close server socket
        if self.server_socket:
            try:
                self.server_socket.close()
            except Exception:
                pass
        
        # Wait for server thread to finish
        if self.server_thread and self.server_thread.is_alive():
            self.server_thread.join(timeout=1.0)
        
        self.logger.info("Communication system shutdown complete")