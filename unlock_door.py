from __future__ import print_function

from RPIO import PWM
import time

servo_pin = 27
servo_range = [800, 1400]  # Left, Right (2300 Max, 500 Min)

PWM.set_loglevel(PWM.LOG_LEVEL_ERRORS)
servo = PWM.Servo()

def unlock_door():
    print('Unlocking...')
    servo.set_servo(servo_pin, servo_range[1])
    time.sleep(2.5)
    print('Locking...')
    servo.set_servo(servo_pin, servo_range[0])
    time.sleep(1)
    servo.stop_servo(servo_pin)
if __name__ == '__main__':
    try:
        unlock_door()
    except Exception as e:
        servo.stop_servo(servo_pin)
        print(e)
