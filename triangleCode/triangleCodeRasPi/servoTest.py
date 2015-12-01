#!/usr/bin/python
# Test Servos
# written by Kayla Nguyen'18

# import servo driver
from Adafruit_PWM_Servo_Driver import PWM
import time

# variables
forwardPulse = 150  # Min pulse length out of 4096
backwardPulse = 600  # Max pulse length out of 4096
stopValue = 0

# Initialise the PWM device using the default address
# pwm = PWM(0x40)
# Note if you'd like more debug output you can instead run:
pwm = PWM(0x40, debug=True)
pwm.setPWMFreq(60)                        # Set frequency to 60 Hz

# main method
def main():
    # move forward for 2 seconds
    moveForward()
    time.sleep(5)
    # move backward for 2 seconds
    moveBackward()
    time.sleep(5)
    # turn left for 2 seconds
    turnLeft()
    time.sleep(5)
    # turn right for 2 seconds
    turnRight()
    time.sleep(5)
    # stop moving
    stopMoving()

# pin 0 is left servo, pin 1 is right servo
# method to move the robot forward
# pwm.setPWM(channel, 0, pulse)
def moveForward():
    # move forward
    pwm.setPWM(0, 0, backwardPulse)
    pwm.setPWM(1, 0, forwardPulse)

# method to move the robot backward
# pwm.setPWM(channel, 0, pulse)
def moveBackward():
    # move backward
    pwm.setPWM(0, 0, forwardPulse)
    pwm.setPWM(1, 0, backwardPulse)
    time.sleep(2)

# method to stop the robot
# pwm.setPWM(channel, 0, pulse)
def stopMoving():
    # stop
    pwm.setPWM(0, 0, stopValue)
    pwm.setPWM(1, 0, stopValue)

# method to turn left
# pwm.setPWM(channel, 0, pulse)
def turnLeft():
    # move right servo, stop left servo
    pwm.setPWM(0, 0, stopValue)
    pwm.setPWM(1, 0, forwardPulse)

# method to turn right
# pwm.setPWM(channel, 0, pulse)
def turnRight():
    # move left servo, stop right servo
    pwm.setPWM(0, 0, backwardPulse)
    pwm.setPWM(1, 0, stopValue)

# run the main method
if __name__ == '__main__':
    pressedKey = raw_input("Press enter to start")
    if pressedKey is not None:
        main()