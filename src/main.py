#!/usr/bin/env python3
"""
Ruohobot Main Entry Point

This is the main entry point for the Ruohobot autonomous lawnmower bot.
Handles initialization, main control loop, and graceful shutdown.
"""

import sys
import signal
import logging
from pathlib import Path

# Add src directory to path
sys.path.append(str(Path(__file__).parent))

from core.robot import Robot
from core.config_manager import ConfigManager
from utils.logger import setup_logging


def signal_handler(sig, frame):
    """Handle shutdown signals gracefully"""
    logging.info("Received shutdown signal, stopping robot...")
    if 'robot' in globals():
        robot.shutdown()
    sys.exit(0)


def main():
    """Main application entry point"""
    # Setup logging
    setup_logging()
    logger = logging.getLogger(__name__)
    
    # Setup signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        # Load configuration
        config = ConfigManager()
        
        # Initialize robot
        logger.info("Initializing Ruohobot...")
        robot = Robot(config)
        
        # Start the robot
        logger.info("Starting robot main loop...")
        robot.run()
        
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        raise
    finally:
        if 'robot' in locals():
            robot.shutdown()
        logger.info("Ruohobot shutdown complete")


if __name__ == "__main__":
    main()
