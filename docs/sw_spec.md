
# Ruohobot Software System: Student Guide

This guide explains the Ruohobot robot software for first-year students. It covers every major file, the overall architecture, and the key algorithms (especially SLAM). The goal is to help you understand how the robot works, how the code is organized, and how you can extend or debug it.

---

## 1. Project Structure & Main Files

- **src/main.py**: The main entry point. Starts the robot, loads configuration, and runs the main loop.
- **src/core/robot.py**: The central robot logic. Handles state (manual, autonomous, emergency), safety, and coordinates all subsystems.
- **src/core/slam.py**: Implements SLAM (Simultaneous Localization and Mapping). Builds a map from LiDAR and odometry, tracks robot position.
- **src/core/lidar.py**: Reads and parses data from the LD19 LiDAR sensor (or simulation). Handles protocol details and scan callbacks.
- **src/core/motors.py**: Controls the Pololu Motoron M3H550 motor controller via I2C. Converts velocity commands to motor speeds.
- **src/core/hardware_manager.py**: Initializes and manages all hardware (motors, sensors, encoders, etc.).
- **src/core/communication.py**: Runs the web server (HTTPServer), serves the dashboard, and handles API requests (move, status, telemetry, etc.).
- **src/utils/**: Utility functions and helpers (logging, math, etc.).
- **config/robot_config.yaml**: Main configuration file (hardware, debug, SLAM settings).
- **scripts/encoder_tester.py**: Standalone script to test encoders and motors.
- **docs/**: Documentation, guides, and specifications.

---

## 2. How the Robot Works (High-Level)

- The robot starts by running `src/main.py`.
- It loads configuration, initializes hardware, and enters its main loop.
- Sensors (LiDAR, encoders, etc.) feed data into the SLAM system.
- The SLAM system builds a map and tracks the robot’s position.
- The robot can be controlled via the web interface (WASD, buttons) or API.
- Safety features (emergency stop, state management) ensure safe operation.

---

## 3. SLAM: Algorithms & Implementation

**SLAM (Simultaneous Localization and Mapping)** means the robot builds a map of its environment while keeping track of its own position.

### Occupancy Grid Mapping
- The map is a 2D grid (numpy array) where each cell represents free, unknown, or occupied space.
- LiDAR scans are used to update the grid: each scan point marks an obstacle, and the space between the robot and the obstacle is marked as free.
- The algorithm uses Bresenham’s line algorithm to trace rays from the robot to each LiDAR point, updating the grid cells along the way.

### Pose Tracking & Odometry
- The robot’s position (x, y, θ) is tracked using encoder data (wheel rotations) and optionally IMU.
- The pose is updated using simple dead reckoning:
  - Linear velocity moves the robot forward/backward.
  - Angular velocity rotates the robot.
  - The pose is updated every time new odometry data arrives.

### SLAMSystem Class (src/core/slam.py)
- `occupancy_grid`: The map itself (2D numpy array).
- `current_pose`: The robot’s current position and orientation.
- `_update_occupancy_grid(scan)`: Updates the map with new LiDAR data.
- `_update_ray(start_x, start_y, end_x, end_y)`: Uses Bresenham’s algorithm to mark free/occupied cells.
- `update_odometry(linear_vel, angular_vel)`: Updates the robot’s pose from encoder/IMU data.
- `get_map_image()`: Converts the grid to an image for visualization and debugging.

---

## 4. Web Interface & API

- The web server runs on port 8080 (see src/core/communication.py).
- Main dashboard: `/` (HTML page with controls and status)
- API endpoints:
  - `/status`: Robot status (JSON)
  - `/api/command`: Send movement or state commands (POST)
  - `/api/slam_map`: Get the current SLAM map (PNG image)
  - `/api/telemetry`: Extended telemetry (JSON)
  - `/api/safety`: Safety status (JSON)
- WASD controls and buttons send commands to the robot via JavaScript and API calls.

---

## 5. Motor & Encoder Control

- Motors are controlled via the Motoron M3H550 (I2C, see src/core/motors.py).
- Velocity commands are converted to left/right motor speeds.
- Encoders are read via GPIO event detection (see scripts/encoder_tester.py and src/core/slam.py for odometry integration).
- Odometry is used for pose tracking in SLAM.

---

## 6. Configuration & Extensibility

- All hardware and debug settings are in `config/robot_config.yaml`.
- You can add new sensors or hardware in `src/core/hardware_manager.py`.
- New API endpoints can be added in `src/core/communication.py`.
- Control logic and states can be extended in `src/core/robot.py`.

---

## 7. Debugging & Safety

- Logging is centralized (see logs/ruohobot.log).
- Emergency stop can be triggered via web, API, or hardware.
- SLAM map is saved to disk for inspection.
- Debug flags in config enable extra logging and map saving.

---

## 8. Algorithms: Bresenham’s Line (SLAM)

- Bresenham’s algorithm is used to efficiently trace a straight line between two points on a grid.
- In SLAM, it marks all cells between the robot and a detected obstacle as free, and the obstacle cell as occupied.
- This is crucial for building an accurate map from LiDAR data.

---

## 9. How to Explore the Code

- Start with `src/main.py` to see how the robot is started.
- Follow initialization into `robot.py`, then hardware and communication modules.
- Look at `slam.py` for mapping and pose tracking.
- Use the web interface to send commands and view the map.
- Read the comments and docstrings in each file for more details.

---

## 10. Tips for Students

- Don’t be afraid to experiment—try changing parameters in the config and see how the robot behaves.
- Use the encoder tester and web interface for hands-on debugging.
- If you get stuck, check the logs and error messages—they’re there to help!
- Ask questions and collaborate—robotics is a team effort.

---

For more details, see the docs folder and code comments. Happy hacking!
