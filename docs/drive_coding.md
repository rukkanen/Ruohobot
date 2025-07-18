# Ruohobot Drive Coding SDK Guide

Welcome to the Ruohobot Motor Control SDK! This guide will help you build amazing autonomous features on top of the solid motor control foundation.

## 🚀 Quick Start

### Basic Motor Control

```python
from core.motors import MotorController

# Initialize with default config
config = {'pololu_m3h550': {}}
mc = MotorController(config)

# Move individual motors
mc.set_speed(1, 400)    # Motor 1 forward at speed 400
mc.set_speed(2, -200)   # Motor 2 reverse at speed 200
mc.stop()               # Stop all motors

# Differential drive (robot movement)
mc.set_velocity(0.5, 0.0)   # Move forward
mc.set_velocity(0.0, 0.5)   # Turn right
mc.set_velocity(0.3, -0.2)  # Move forward while turning left
```

## ⚙️ Configuration Guide

### Motor Configuration

Edit your configuration to match your robot layout:

```python
config = {
    'pololu_m3h550': {
        'i2c_bus': 1,                    # I2C bus number
        'i2c_address': 16,               # Motoron I2C address
        'max_speed': 800,                # Global speed limit
        
        # Motor 1 (e.g., Left Drive Wheel)
        'motor_1_acceleration': 100,     # Acceleration rate (0-6400)
        'motor_1_deceleration': 200,     # Deceleration rate (0-6400)
        'motor_1_reversed': False,       # Reverse motor direction
        
        # Motor 2 (e.g., Right Drive Wheel)
        'motor_2_acceleration': 100,
        'motor_2_deceleration': 200,
        'motor_2_reversed': True,        # If wired backwards
        
        # Motor 3 (e.g., Cutting Deck Motor - DISABLED for safety)
        'motor_3_acceleration': 50,
        'motor_3_deceleration': 100,
        'motor_3_reversed': False,
    }
}
```

### Understanding Acceleration Values

- **Low values (50-100)**: Gentle, smooth motion - good for precision
- **Medium values (100-200)**: Balanced performance
- **High values (200-400)**: Aggressive acceleration - good for quick maneuvers
- **Maximum (6400)**: Nearly instantaneous - use carefully!

## 🎯 Common Patterns

### 1. Precise Movement Control

```python
class PreciseMovement:
    def __init__(self, motor_controller):
        self.mc = motor_controller
        
    def move_distance(self, distance_meters, speed=0.3):
        """Move forward a specific distance"""
        # Calculate movement time based on speed
        # This is approximate - you'll want encoders for precision
        movement_time = distance_meters / (speed * 0.5)  # Rough calibration
        
        self.mc.set_velocity(speed, 0.0)
        time.sleep(movement_time)
        self.mc.stop()
        
    def turn_angle(self, angle_degrees, turn_speed=0.3):
        """Turn by a specific angle"""
        # Calculate turn time (needs calibration for your robot)
        turn_time = abs(angle_degrees) / 90.0 * 1.5  # Rough: 1.5s for 90 degrees
        
        direction = 1.0 if angle_degrees > 0 else -1.0
        self.mc.set_velocity(0.0, direction * turn_speed)
        time.sleep(turn_time)
        self.mc.stop()
```

### 2. Speed Ramping

```python
class SmoothMovement:
    def __init__(self, motor_controller):
        self.mc = motor_controller
        
    def ramp_to_speed(self, target_linear, target_angular, ramp_time=2.0):
        """Gradually ramp up to target speed"""
        steps = 20
        sleep_time = ramp_time / steps
        
        for i in range(steps + 1):
            factor = i / steps
            current_linear = target_linear * factor
            current_angular = target_angular * factor
            
            self.mc.set_velocity(current_linear, current_angular)
            time.sleep(sleep_time)
```

### 3. Obstacle Avoidance Pattern

```python
class ObstacleAvoidance:
    def __init__(self, motor_controller, distance_sensor):
        self.mc = motor_controller
        self.sensor = distance_sensor
        
    def avoid_obstacle(self):
        """Basic obstacle avoidance behavior"""
        distance = self.sensor.get_distance()
        
        if distance < 0.5:  # 50cm threshold
            # Stop and back up
            self.mc.stop()
            self.mc.set_velocity(-0.3, 0.0)  # Reverse
            time.sleep(1.0)
            
            # Turn right
            self.mc.set_velocity(0.0, 0.5)   # Turn
            time.sleep(1.5)
            
            # Continue forward
            self.mc.set_velocity(0.3, 0.0)   # Forward
        else:
            # Normal forward movement
            self.mc.set_velocity(0.4, 0.0)
```

## 📏 Distance and Position Tracking

### Option 1: Time-Based Estimation (Simple)

```python
class SimpleOdometry:
    def __init__(self, motor_controller):
        self.mc = motor_controller
        self.x = 0.0
        self.y = 0.0
        self.heading = 0.0  # radians
        self.last_time = time.time()
        
        # Calibration constants (measure these for your robot!)
        self.wheel_base = 0.3    # Distance between wheels (meters)
        self.speed_calibration = 0.5  # Speed factor (tune this)
        
    def update_position(self, linear_speed, angular_speed):
        """Update position based on commanded speeds"""
        current_time = time.time()
        dt = current_time - self.last_time
        
        # Update heading
        self.heading += angular_speed * dt
        
        # Update position
        distance = linear_speed * dt * self.speed_calibration
        self.x += distance * math.cos(self.heading)
        self.y += distance * math.sin(self.heading)
        
        self.last_time = current_time
        
    def get_position(self):
        return (self.x, self.y, self.heading)
        
    def reset_position(self):
        self.x = self.y = self.heading = 0.0
```

### Option 2: Encoder-Based (Accurate)

```python
class EncoderOdometry:
    def __init__(self, motor_controller, left_encoder, right_encoder):
        self.mc = motor_controller
        self.left_encoder = left_encoder
        self.right_encoder = right_encoder
        
        # Robot parameters (measure these!)
        self.wheel_diameter = 0.2      # meters
        self.wheel_base = 0.3          # meters
        self.encoder_ticks_per_rev = 1000  # encoder resolution
        
        self.x = 0.0
        self.y = 0.0
        self.heading = 0.0
        
        self.last_left_ticks = 0
        self.last_right_ticks = 0
        
    def update_odometry(self):
        """Update position from encoder readings"""
        left_ticks = self.left_encoder.get_ticks()
        right_ticks = self.right_encoder.get_ticks()
        
        # Calculate wheel distances
        left_distance = self.ticks_to_distance(left_ticks - self.last_left_ticks)
        right_distance = self.ticks_to_distance(right_ticks - self.last_right_ticks)
        
        # Calculate robot motion
        distance = (left_distance + right_distance) / 2.0
        angle_change = (right_distance - left_distance) / self.wheel_base
        
        # Update position
        self.heading += angle_change
        self.x += distance * math.cos(self.heading)
        self.y += distance * math.sin(self.heading)
        
        # Store current readings
        self.last_left_ticks = left_ticks
        self.last_right_ticks = right_ticks
        
    def ticks_to_distance(self, ticks):
        """Convert encoder ticks to distance"""
        revolutions = ticks / self.encoder_ticks_per_rev
        return revolutions * math.pi * self.wheel_diameter
```

## 🛡️ Safety and Error Handling

### Emergency Stop Integration

```python
class SafeMovement:
    def __init__(self, motor_controller):
        self.mc = motor_controller
        self.emergency_active = False
        
    def safe_move(self, linear, angular):
        """Move with safety checks"""
        # Check for emergency conditions
        if self.check_emergency_conditions():
            self.emergency_stop()
            return False
            
        # Check motor status
        status = self.mc.get_status()
        if status.get('motor_fault', False):
            self.handle_motor_fault()
            return False
            
        # Safe to move
        self.mc.set_velocity(linear, angular)
        return True
        
    def check_emergency_conditions(self):
        """Override this with your safety checks"""
        # Examples:
        # - Low battery
        # - Tilt sensor triggered
        # - Lost communication
        # - Manual stop button
        return False
        
    def emergency_stop(self):
        """Emergency stop procedure"""
        self.emergency_active = True
        self.mc.emergency_stop()
        # Add other safety actions (alarms, logging, etc.)
        
    def reset_emergency(self):
        """Reset after emergency"""
        if self.emergency_active:
            self.mc.reset_emergency_stop()
            self.emergency_active = False
```

## 🤖 Building Autonomous Behaviors

### Simple State Machine

```python
from enum import Enum

class RobotState(Enum):
    IDLE = "idle"
    EXPLORING = "exploring"
    AVOIDING = "avoiding"
    RETURNING = "returning"
    EMERGENCY = "emergency"

class AutonomousRobot:
    def __init__(self, motor_controller, sensors):
        self.mc = motor_controller
        self.sensors = sensors
        self.state = RobotState.IDLE
        self.state_timer = 0
        
    def update(self):
        """Main control loop - call this repeatedly"""
        if self.state == RobotState.IDLE:
            self.idle_behavior()
        elif self.state == RobotState.EXPLORING:
            self.explore_behavior()
        elif self.state == RobotState.AVOIDING:
            self.avoid_behavior()
        elif self.state == RobotState.RETURNING:
            self.return_behavior()
        elif self.state == RobotState.EMERGENCY:
            self.emergency_behavior()
            
        self.state_timer += 1
        
    def idle_behavior(self):
        """Wait for commands or start exploring"""
        self.mc.stop()
        # Transition to exploring after timeout
        if self.state_timer > 100:  # 10 seconds at 10Hz
            self.change_state(RobotState.EXPLORING)
            
    def explore_behavior(self):
        """Random exploration"""
        distance = self.sensors.get_front_distance()
        
        if distance < 0.5:  # Obstacle detected
            self.change_state(RobotState.AVOIDING)
        else:
            # Move forward with slight random turning
            turn_bias = random.uniform(-0.1, 0.1)
            self.mc.set_velocity(0.3, turn_bias)
            
    def avoid_behavior(self):
        """Obstacle avoidance"""
        # Back up and turn
        if self.state_timer < 20:  # Back up for 2 seconds
            self.mc.set_velocity(-0.2, 0.0)
        elif self.state_timer < 35:  # Turn for 1.5 seconds
            self.mc.set_velocity(0.0, 0.5)
        else:
            self.change_state(RobotState.EXPLORING)
            
    def change_state(self, new_state):
        """Change robot state"""
        self.state = new_state
        self.state_timer = 0
```

## 🔧 Calibration and Tuning

### Motor Calibration Script

```python
def calibrate_motors():
    """Interactive motor calibration"""
    mc = MotorController(config)
    
    print("Motor Calibration Tool")
    print("1. Test acceleration settings")
    print("2. Measure speed calibration")
    print("3. Test turning radius")
    
    choice = input("Select option: ")
    
    if choice == "1":
        # Test different acceleration values
        for accel in [50, 100, 200, 400]:
            print(f"Testing acceleration: {accel}")
            mc.motor_config[1]['max_acceleration'] = accel
            mc._initialize_controller()
            
            mc.set_speed(1, 400)
            time.sleep(2)
            mc.stop()
            time.sleep(1)
            
            feedback = input("Smooth? (y/n): ")
            if feedback.lower() == 'y':
                print(f"Good acceleration value: {accel}")
                break
                
    elif choice == "2":
        # Measure actual speed
        distance = float(input("Mark a distance (meters): "))
        
        mc.set_velocity(0.5, 0.0)
        start_time = time.time()
        input("Press Enter when robot reaches the mark...")
        end_time = time.time()
        mc.stop()
        
        actual_speed = distance / (end_time - start_time)
        expected_speed = 0.5 * 0.5  # Rough estimation
        calibration_factor = actual_speed / expected_speed
        
        print(f"Calibration factor: {calibration_factor}")
        print(f"Update your speed_calibration to: {calibration_factor}")
```

## 📊 Debugging and Monitoring

### Motor Status Dashboard

```python
class MotorDashboard:
    def __init__(self, motor_controller):
        self.mc = motor_controller
        
    def print_status(self):
        """Print comprehensive motor status"""
        status = self.mc.get_status()
        
        print("\n=== Motor Status Dashboard ===")
        print(f"Emergency Stop: {status['emergency_stop_active']}")
        print(f"Motor Speeds: {status['current_speeds']}")
        print(f"Motor Fault: {status['motor_fault']}")
        print(f"No Power: {status['no_power']}")
        print(f"Command Timeout: {status['command_timeout']}")
        
        # Motor currents (if available)
        for motor_id in [1, 2, 3]:
            current = self.mc.get_motor_current(motor_id)
            print(f"Motor {motor_id} Current: {current:.2f}")
            
    def log_performance(self, filename="motor_log.csv"):
        """Log motor performance to file"""
        status = self.mc.get_status()
        timestamp = time.time()
        
        with open(filename, "a") as f:
            f.write(f"{timestamp},{status['current_speeds'][1]},{status['current_speeds'][2]},{status['current_speeds'][3]}\n")
```

## 🚀 Advanced Features

### PID Controller for Precise Movement

```python
class PIDController:
    def __init__(self, kp, ki, kd):
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.previous_error = 0
        self.integral = 0
        
    def update(self, setpoint, measured_value, dt):
        """Calculate PID output"""
        error = setpoint - measured_value
        self.integral += error * dt
        derivative = (error - self.previous_error) / dt
        
        output = (self.kp * error + 
                 self.ki * self.integral + 
                 self.kd * derivative)
        
        self.previous_error = error
        return output

class PreciseNavigation:
    def __init__(self, motor_controller, odometry):
        self.mc = motor_controller
        self.odometry = odometry
        self.heading_pid = PIDController(2.0, 0.1, 0.5)
        self.distance_pid = PIDController(1.0, 0.05, 0.2)
        
    def go_to_point(self, target_x, target_y):
        """Navigate to specific coordinates"""
        while True:
            current_x, current_y, current_heading = self.odometry.get_position()
            
            # Calculate distance and angle to target
            dx = target_x - current_x
            dy = target_y - current_y
            distance = math.sqrt(dx*dx + dy*dy)
            target_heading = math.atan2(dy, dx)
            
            if distance < 0.1:  # Close enough
                self.mc.stop()
                break
                
            # PID control for heading and speed
            heading_error = target_heading - current_heading
            angular_cmd = self.heading_pid.update(0, heading_error, 0.1)
            linear_cmd = self.distance_pid.update(0, -distance, 0.1)
            
            # Limit commands
            angular_cmd = max(-1.0, min(1.0, angular_cmd))
            linear_cmd = max(-0.5, min(0.5, linear_cmd))
            
            self.mc.set_velocity(linear_cmd, angular_cmd)
            time.sleep(0.1)
```

## 🎯 Example Projects

### 1. Lawn Mowing Pattern

```python
def mowing_pattern():
    """Create a systematic mowing pattern"""
    mc = MotorController(config)
    
    # Define mowing area (rectangle)
    width = 10.0  # meters
    height = 8.0  # meters
    stripe_width = 0.5  # 50cm stripes
    
    y = 0
    direction = 1
    
    while y < height:
        # Move across the width
        mc.set_velocity(0.3 * direction, 0.0)
        time.sleep(width / 0.3)  # Time to cross
        
        # Turn around at end
        mc.set_velocity(0.0, 0.5)
        time.sleep(3.0)  # 180 degree turn
        
        # Move to next stripe
        mc.set_velocity(0.3, 0.0)
        time.sleep(stripe_width / 0.3)
        
        y += stripe_width
        direction *= -1  # Alternate direction
```

### 2. Perimeter Following

```python
def follow_perimeter():
    """Follow the edge of the lawn"""
    mc = MotorController(config)
    
    while True:
        # Use distance sensor to maintain distance from edge
        edge_distance = sensors.get_right_distance()
        target_distance = 0.3  # 30cm from edge
        
        error = edge_distance - target_distance
        
        # Adjust steering to maintain distance
        steering = error * 0.5  # Simple proportional control
        mc.set_velocity(0.3, steering)
        
        time.sleep(0.1)
```

## 📚 Next Steps

1. **Add Sensors**: Integrate distance sensors, IMU, GPS
2. **Implement Encoders**: For precise position tracking
3. **Create Mapping**: Build a map of your lawn
4. **Add Remote Control**: WiFi interface for monitoring
5. **Weather Integration**: Stop operation in rain
6. **Charging Station**: Automatic return and docking

## 🔗 Integration Points

- **Distance Scanner**: Connect to Arduino module for obstacle detection
- **Sentinel Module**: Add environmental monitoring and low-power management
- **GPS Module**: For absolute positioning and return-to-base
- **Camera**: Visual navigation and lawn condition monitoring

Happy coding! 🤖🚀

---

*Remember: Always test new code in a safe environment with emergency stop readily available!*
