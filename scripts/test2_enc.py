from core.motors import MotorController
import yaml

motor_config = {}
try:
    motors = MotorController({'pololu_m3h550': motor_config})
    print("MotorController initialized.")
except Exception as e:
    print("MotorController setup failed:", e)