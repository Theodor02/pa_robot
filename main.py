#!/usr/bin/env pybricks-micropython

from pybricks.hubs import EV3Brick
from pybricks.ev3devices import Motor, TouchSensor, ColorSensor
from pybricks.parameters import Port, Stop, Direction, Button
from pybricks.tools import wait
import math


ev3 = EV3Brick()

gripper_motor = Motor(Port.A)

elbow_motor = Motor(Port.B, Direction.COUNTERCLOCKWISE, [8, 40])

base_motor = Motor(Port.C, Direction.COUNTERCLOCKWISE, [12, 36])


elbow_motor.control.limits(speed=60, acceleration=120)
base_motor.control.limits(speed=60, acceleration=120)

touchsensor = TouchSensor(Port.S1)

colorsensor = ColorSensor(Port.S2)
blocks_at_zone = [0,0,0,0]
pickup_angles = [4,105,150,196]


def closest_pudozone(angle):

    return pickup_angles[min(range(len(pickup_angles)), key = lambda i: abs(pickup_angles[i]-angle))]


def robot_calibrate():
    gripper_cal()
    arm_cal()
    base_cal()

def blockselectscreen(nr):
    ev3.screen.clear()
    ev3.screen.draw_text(60,10,"Select the amount of blocks currently at the zone")
    ev3.screen.draw_text(60,30,"UP")
    ev3.screen.draw_text(60,50,str(nr))
    ev3.screen.draw_text(60,70,"DOWN")

def nrofblockssel():
    ev3.screen.clear()
    nrofblocks = 0
    blockselectscreen(nrofblocks)
    done = False
    while not done:
        pressed = ev3.buttons.pressed()
        if Button.UP in pressed:
            nrofblocks +=1
            blockselectscreen(nrofblocks)
            wait(500)
            
        if Button.DOWN in pressed:
            nrofblocks -=1
            blockselectscreen(nrofblocks)
            wait(500)
            
        if Button.CENTER in pressed:
            done = True
            wait(1000)
            ev3.screen.clear()
            
    return nrofblocks
            


    


def manual_move():
    pickup_zones = []
    putdown_zones = {}
    pressed = ev3.buttons.pressed()
    check = True
    while (check):
        was_pressed = pressed
        pressed = ev3.buttons.pressed()
        ev3.screen.draw_text(10, 10, 'DONE = CENTER')
        ev3.screen.draw_text(10, 30, 'PICKUP = UP')
        ev3.screen.draw_text(10, 50, 'DROPOFF = DOWN')
        if Button.LEFT in pressed:
            base_motor.run(20)

        elif Button.RIGHT in pressed and base_motor.angle() >= 0:
            base_motor.run(-20)

        else:
            base_motor.hold()

        if Button.UP in pressed and Button.UP not in was_pressed:
            curangle = closest_pudozone(base_motor.angle())
            pickup_zones.append(curangle)
            blocks_at_zone[pickup_angles.index(curangle)] = nrofblockssel()


        if Button.DOWN in pressed and Button.DOWN not in was_pressed:
            ev3.screen.clear()
            ev3.screen.draw_text(10, 10, "GREEN = UP")
            ev3.screen.draw_text(10, 30, "RED = DOWN")
            ev3.screen.draw_text(10, 50, "BLUE = LEFT")
            ev3.screen.draw_text(10, 70, "YELLOW = RIGHT")
            wait(500)
            done = False
            while not done:
                was_pressed = pressed
                pressed = ev3.buttons.pressed()
                if Button.UP in pressed and Button.UP not in was_pressed:
                    done = True
                    curangle = closest_pudozone(base_motor.angle())
                    putdown_zones["GREEN"] = curangle
                    pickup_zones.append(curangle)
                    wait(10)
                    blocks_at_zone[pickup_angles.index(curangle)] = nrofblockssel()
                elif Button.DOWN in pressed and Button.DOWN not in was_pressed:
                    done = True
                    curangle = closest_pudozone(base_motor.angle())
                    putdown_zones["RED"] = curangle
                    pickup_zones.append(curangle)
                    wait(10)
                    blocks_at_zone[pickup_angles.index(curangle)] = nrofblockssel()
                elif Button.LEFT in pressed and Button.LEFT not in was_pressed:
                    done = True
                    curangle = closest_pudozone(base_motor.angle())
                    putdown_zones["BLUE"] = curangle
                    pickup_zones.append(curangle)
                    wait(10)
                    blocks_at_zone[pickup_angles.index(curangle)] = nrofblockssel()
                elif Button.RIGHT in pressed and Button.RIGHT not in was_pressed:
                    done = True
                    curangle = closest_pudozone(base_motor.angle())
                    putdown_zones["YELLOW"] = curangle
                    pickup_zones.append(curangle)
                    wait(10)
                    blocks_at_zone[pickup_angles.index(curangle)] = nrofblockssel()
            ev3.screen.clear()
        if Button.CENTER in pressed and Button.CENTER not in was_pressed:
            check = False
    ev3.screen.clear()
    wait(1000)
    return [pickup_zones, putdown_zones]


def arm_move(position):
    elbow_motor.run_target(60, position)
    return


def base_move(position):
    base_motor.run_target(60, position)


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


def rgb_detection():
    rgb_value = colorsensor.rgb()
    red_original, green_original, blue_original = rgb_value
    red = red_original / (green_original + 0.001)
    green = green_original / (blue_original + 0.001)
    blue = blue_original / (red_original + 0.001)
    if red > 4:
        return "RED"

    elif red > 1.3 and green > 1.3 and blue < 1:
        return "YELLOW"

    elif red < 1 and green > 0.8 and blue > 2:
        return "GREEN"

    elif red < 1 and green < 0.8 and blue > 2:
        return "BLUE"
    
    elif red > 2 and green > 2 and blue > 2:
        return "WHITE"
    
    else:
        return 1


def block_detect():
    color_list = []
    count = 0
    while count < 20:
        color_list.append(rgb_detection())
        count += 1
    return most_frequent(color_list)


def most_frequent(List):
    key = List.count
    return max(set(List), key)


def block_pickup(angle):
    anglecounter = base_motor.angle()
    while anglecounter != angle:
        base_motor.run_target(60,anglecounter)
        anglecounter += 1
        pressed = ev3.buttons.pressed()
        if Button.CENTER in pressed:
            shutdown_button()
    gripper_motor.run_target(50, -90)
    arm_move(math.degrees(math.atan(blocks_at_zone[pickup_angles.index(angle)]*1.9/10))-30)
    gripper_motor.run_until_stalled(200, then=Stop.HOLD, duty_limit=75)
    elbow_motor.run_target(20, 0)
    blocks_at_zone[pickup_angles.index(angle)]-=1


def block_putdown(angle):
    base_move(angle)
    # elbow_motor.run_angle(200,-20,Stop.COAST)

    arm_move(math.degrees(math.atan(blocks_at_zone[pickup_angles.index(angle)]*1.9/10))-30)
    # elbow_motor.run_until_stalled(-20,Stop.COAST,duty_limit=10)
    # elbow_motor.hold()
    blocks_at_zone[pickup_angles.index(angle)]+=1
    gripper_motor.run_target(50, -90)
    elbow_motor.run_target(20, 30)


def robot_func(zones):
    pickup = zones[0][0]
    putdown = zones[1]
    block_pickup(pickup)
    bd = block_detect()
    elbow_motor.run_target(20,30)
    if type(bd) == type(""):
        if bd == "WHITE":
            wait(1000)
        else:
            block_putdown(putdown.get(bd))
    else:
        wait(1000)
        block_putdown(base_motor.angle())

def shutdown_button():
    while not Button.CENTER in pressed:
        ev3.screen.draw_text(10,10,"Press the center button to resume")
        pressed = ev3.buttons.pressed()
        elbow_motor.hold()
        gripper_motor.hold()
        base_motor.hold()

def main():
    robot_calibrate()
    notes = [
        "F#/3,A/3,C#/4",  # F#m chord
        "A/3,C#/4,E/4",   # A major chord
        "B/3,D#/4,F#/4",  # B major chord
        "D/3,F#/3,A/3",   # D major chord
        "C#/3,E/3,G#/3"   # C# minor chord
    ]

    # lyrics = "Ill take you to the candy shop  Ill let you lick the lollypop  Go ahead girl and dont you stop  Keep going till you hit the spot, WHOA!  (Ill take you to the candy shop)  (Boy one taste of what I got)  (Ill have you spending all you got)  (Keep going till you hit the spot, WHOA!)"
    zones = manual_move()
    ev3.speaker.play_notes(notes, tempo=117)
    # ev3.speaker.say(lyrics)
    for x in range(100):
        robot_func(zones)


if __name__ == "__main__":
    main()
