#!/usr/bin/env pybricks-micropython

from pybricks.hubs import EV3Brick
from pybricks.ev3devices import Motor, TouchSensor, ColorSensor
from pybricks.parameters import Port, Stop, Direction, Color, Button
from pybricks.tools import wait

ev3 = EV3Brick()

gripper_motor = Motor(Port.A)

elbow_motor = Motor(Port.B, Direction.COUNTERCLOCKWISE, [8, 40])

base_motor = Motor(Port.C, Direction.COUNTERCLOCKWISE, [12, 36])


elbow_motor.control.limits(speed=60, acceleration=120)
base_motor.control.limits(speed=60, acceleration=120)

touchsensor = TouchSensor(Port.S1)

colorsensor = ColorSensor(Port.S2)



def robot_calibrate():
    gripper_cal()
    arm_cal()
    base_cal()


def manual_move():
    pickup_zones = []
    putdown_zones = {}
    pressed = ev3.buttons.pressed()
    check = True
    while(check):
        was_pressed = pressed
        pressed = ev3.buttons.pressed()
        if Button.LEFT in pressed:
            base_motor.run(20)
            
        elif Button.RIGHT in pressed and base_motor.angle() >= 0:
            base_motor.run(-20)
            
        else:
            base_motor.hold()
            
        if Button.UP in pressed and Button.UP not in was_pressed:
            pickup_zones.append(base_motor.angle())
            print("pick has happened")

        if Button.DOWN in pressed and Button.DOWN not in was_pressed:
            
            ev3.screen.draw_text(10,10,"GREEN = UP")
            ev3.screen.draw_text(10,30,"RED = DOWN")
            ev3.screen.draw_text(10,50,"BLUE = LEFT")
            ev3.screen.draw_text(10,70,"YELLOW = RIGHT")
            wait(500)
            done = False
            while not done:
                was_pressed = pressed
                pressed = ev3.buttons.pressed()
                if Button.UP in pressed and Button.UP not in was_pressed:
                    done = True
                    putdown_zones["GREEN"] = base_motor.angle()
                elif Button.DOWN in pressed and Button.DOWN not in was_pressed:
                    done = True
                    putdown_zones["RED"] = base_motor.angle()
                elif Button.LEFT in pressed and Button.LEFT not in was_pressed:
                    done = True
                    putdown_zones["BLUE"] = base_motor.angle()
                elif Button.RIGHT in pressed and Button.RIGHT not in was_pressed:
                    done = True
                    putdown_zones["YELLOW"] = base_motor.angle()
            ev3.screen.clear()
        
        if Button.CENTER in pressed and Button.CENTER not in was_pressed:
            check = False

    return [pickup_zones, putdown_zones]

def arm_move(position):
    elbow_motor.run_target(60,position)
    return


def base_move(position):
    base_motor.run_target(60,position)


def arm_cal():
    if colorsensor.reflection() < 4:
        while colorsensor.reflection() < 4:
            elbow_motor.run(-5)
    elif colorsensor.reflection() > 3:
        while colorsensor.reflection() > 3:
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
    gripper_motor.run_until_stalled(200, then=Stop.COAST, duty_limit=75)
    gripper_motor.reset_angle(0)
    gripper_motor.run_target(200, -90)


def block_detect():
    color_list = []
    color_map = {
        Color.RED: "RED",
        Color.GREEN: "GREEN",
        Color.BLUE: "BLUE",
        Color.YELLOW: "YELLOW"
    }
    count = 0
    while count < 20:
        color_list.append(colorsensor.color())
        count += 1
    return color_map.get(most_frequent(color_list))

def most_frequent(List):
    return max(set(List), key = List.count)

def block_pickup(angle):
    base_move(angle)
    gripper_motor.run_target(50, -90)
    elbow_motor.run_until_stalled(-20,Stop.HOLD, duty_limit=10)
    gripper_motor.run_until_stalled(200, then=Stop.HOLD, duty_limit=75)
    elbow_motor.run_target(20, 0)


def block_putdown(angle):
    base_move(angle)
    elbow_motor.run_until_stalled(-20,Stop.HOLD,duty_limit=10)
    gripper_motor.run_target(50, -90)
    elbow_motor.run_target(20,0)


def robot_func(zones):
    pickup = zones[0][0]
    putdown = zones[1]
    block_pickup(pickup)
    if type(block_detect()) == type(""):
        block_putdown(putdown.get(block_detect()))
    else:
        block_putdown(base_motor.angle())

def main():
    robot_calibrate()
    notes = [ # Radera inte
    "E4/4", "E4/4", "F4/4", "G4/4", 
    "G4/4", "F4/4", "E4/4", "D4/4", 
    "C4/4", "C4/4", "D4/4", "E4/4",
    "E4/3", "D4/8", "D4/4"
    ]
    zones = manual_move()
    for x in range(100):
        robot_func(zones)
    ev3.speaker.play_notes(notes, tempo=800)
    

if __name__ == "__main__":
    main()