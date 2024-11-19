import Jetson.GPIO as GPIO
import time

# Pin setup for two Rhino motor drivers
motor_pins = {
    "front_right": {"DIR": 12, "PWM": 32, "EN": 18},
    "front_left": {"DIR": 16, "PWM": 33, "EN": 22},
    "rear_right": {"DIR": 24, "PWM": 35, "EN": 26},
    "rear_left": {"DIR": 29, "PWM": 37, "EN": 31},
}

# Initialize GPIO
GPIO.setmode(GPIO.BOARD)
for motor, pins in motor_pins.items():
    GPIO.setup(pins["DIR"], GPIO.OUT)
    GPIO.setup(pins["PWM"], GPIO.OUT)
    GPIO.setup(pins["EN"], GPIO.OUT)
    GPIO.output(pins["EN"], GPIO.HIGH)  # Enable all motors
    pins["pwm"] = GPIO.PWM(pins["PWM"], 100)  # 100 Hz frequency
    pins["pwm"].start(0)

def set_motor_speed(motor, speed):
    """Set motor direction and speed."""
    pins = motor_pins[motor]
    if speed > 0:
        GPIO.output(pins["DIR"], GPIO.HIGH)
    elif speed < 0:
        GPIO.output(pins["DIR"], GPIO.LOW)
    else:
        GPIO.output(pins["DIR"], GPIO.LOW)  # Brake or stop
    
    pins["pwm"].ChangeDutyCycle(abs(speed))

def calculate_wheel_speeds(x, y, z):
    """Calculate wheel speeds for Mecanum drive."""
    width = 0.275
    length = 0.575
    mat = [
        [1, 1, (width + length)],
        [1, -1, -(width + length)],
        [1, -1, (width + length)],
        [1, 1, -(width + length)],
    ]
    velocities = [x, y, z]
    wheel_speeds = [sum(v * m for v, m in zip(velocities, row)) for row in mat]
    return wheel_speeds

def move_robot(x, y, z, duration):
    """Move the robot with given x, y, z velocities for a duration."""
    speeds = calculate_wheel_speeds(x, y, z)
    motors = ["front_right", "front_left", "rear_right", "rear_left"]
    
    # Normalize speeds to prevent exceeding 100% PWM
    max_speed = max(abs(speed) for speed in speeds)
    if max_speed > 1:
        speeds = [speed / max_speed for speed in speeds]
    
    # Set speeds for each motor
    for motor, speed in zip(motors, speeds):
        set_motor_speed(motor, speed * 100)  # Scale to 0-100% for PWM

    time.sleep(duration)
    
    # Stop all motors after movement
    for motor in motors:
        set_motor_speed(motor, 0)

if __name__ == "__main__":
    try:
        # Example: Move forward with x=1, y=0, z=0 for 5 seconds
        move_robot(1, 0, 0, 5)
    finally:
        GPIO.cleanup()
