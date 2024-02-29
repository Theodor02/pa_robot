#!/usr/bin/env pybricks-micropython

"""
Building instructions can be found at:
https://education.lego.com/en-us/support/mindstorms-ev3/building-instructions#building-core
"""

from pybricks.hubs import EV3Brick
from pybricks.ev3devices import Motor, TouchSensor, ColorSensor
from pybricks.parameters import Port, Stop, Direction, Color
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

# Limit the elbow and base accelerations. This results in
# very smooth motion. Like an industrial robot.
elbow_motor.control.limits(speed=60, acceleration=120)
base_motor.control.limits(speed=60, acceleration=120)

touchsensor = TouchSensor(Port.S1)

colorsensor = ColorSensor(Port.S2)



# Variables.
base_colour = 0
first_colour = 0
second_colour = 0
third_colour = 0
arm_origin = NotImplemented
base_origin = NotImplemented




def robot_calibrate():
    gripper_cal()
    arm_cal()
    base_cal()

    return base_colour, first_colour, second_colour, third_colour


# Robot arm funcs
def arm_move(position):
    elbow_motor.run_target(60,position)
    return


def arm_cal():
    if colorsensor.reflection() == 0:
        while colorsensor.reflection() == 0:
            elbow_motor.run(-5)
    elif colorsensor.reflection() != 0:
        while colorsensor.reflection() != 0:
            elbow_motor.run(5)   
    elbow_motor.reset_angle(-10)
    arm_move(0)
    

def base_cal():
    base_motor.run(-60)
    while not touchsensor.pressed():
        wait(10)
    base_motor.hold()
    base_motor.reset_angle(-7)
    base_move(0)

def gripper_cal():
    arm_move(20)
    gripper_motor.run_until_stalled(200, then=Stop.COAST, duty_limit=50)
    gripper_motor.reset_angle(0)
    gripper_motor.run_target(200, -90)




def base_move(position):
    base_motor.run_target(60,position)




# Robot object functions
def block_detect():
    rgb = colorsensor.rgb()

    # if colorsensor.color() == Color.RED:
    #     color = "RED"
    # elif colorsensor.color() == Color.GREEN:
    #     color = "GREEN"
    # elif colorsensor.color() == Color.BLUE:
    #     color = "BLUE"
    # elif colorsensor.color() == Color.YELLOW:
    #     color = "YELLOW"
    # else:
    #     color = "NO COLOR"
    return rgb


def block_pickup():
    gripper_motor.run_target(50, -90)
    elbow_motor.run_until_stalled(-20,Stop.HOLD,5)
    gripper_motor.run_until_stalled(200, then=Stop.HOLD, duty_limit=50)
    elbow_motor.run_target(20, 0)
    return


def block_putdown():
    elbow_motor.run_until_stalled(-20,Stop.HOLD,duty_limit=10)
    gripper_motor.run_target(50, -90)
    elbow_motor.run_target(20,0)

    return


# Robot calibration and failsafe, "Essential"


def robot_failsafe(): 
    
    return

# robot_calibrate()

# block_pickup()

# print(block_detect())
# wait(1000)
# block_putdown()

# base_move(200)
# block_pickup()
# print(block_detect())
# block_putdown()

# ev3.speaker.say("DONE")


while True:
    wait(250)
    print(colorsensor.reflection())
