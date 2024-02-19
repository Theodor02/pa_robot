#!/usr/bin/env pybricks-micropython

"""
Building instructions can be found at:
https://education.lego.com/en-us/support/mindstorms-ev3/building-instructions#building-core
"""

from pybricks.hubs import EV3Brick
from pybricks.ev3devices import Motor, TouchSensor, ColorSensor
from pybricks.parameters import Port, Stop, Direction
from pybricks.tools import wait

# Initialize the EV3 Brick
ev3 = EV3Brick()

# Configure the gripper motor on Port A with default settings.
gripper_motor = Motor(Port.A)

# Configure the elbow motor. It has an 8-teeth and a 40-teeth gear
# connected to it. We would like positive speed values to make the
# arm go upward. This corresponds to counterclockwise rotation
# of the motor.
elbow_motor = Motor(Port.B, Direction.COUNTERCLOCKWISE, [8, 40])

# Configure the motor that rotates the base. It has a 12-teeth and a
# 36-teeth gear connected to it. We would like positive speed values
# to make the arm go away from the Touch Sensor. This corresponds
# to counterclockwise rotation of the motor.
base_motor = Motor(Port.C, Direction.COUNTERCLOCKWISE, [12, 36])


# Main robot functions.

def arm_move(position):

    return

def arm_return(origin):

    return

def arm_max():
    
    return

def block_detect():

    return

def block_pickup():

    return

def block_putdown():

    return

def robot_calibrate():
    base_colour = 0
    first_colour = 0
    second_colour = 0
    third_colour = 0

    return base_colour, first_colour, second_colour, third_colour

def robot_failsafe():

    return


# Main loop, actual code.
while True:
    base_motor.run(600)
    for i in range(100):
        ev3.speaker.beep(2000,10)
        ev3.speaker.say(" DI DI ID ID ID ID ID ID ID DI DIDIDI DIDI DI WOWOWOWOWWOWOWOWOWOWOWWO")