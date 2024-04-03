#!/usr/bin/env pybricks-micropython

from pybricks.hubs import EV3Brick
from pybricks.ev3devices import Motor, TouchSensor, ColorSensor
from pybricks.parameters import Port, Stop, Direction, Button
from pybricks.tools import wait


ev3 = EV3Brick()

gripper_motor = Motor(Port.A)

elbow_motor = Motor(Port.B, Direction.COUNTERCLOCKWISE, [8, 40])

base_motor = Motor(Port.C, Direction.COUNTERCLOCKWISE, [12, 36])


elbow_motor.control.limits(speed=60, acceleration=120)
base_motor.control.limits(speed=60, acceleration=120)

touchsensor = TouchSensor(Port.S1)

colorsensor = ColorSensor(Port.S2)

pickup_angles = [0, 102, 148, 196]


def closest_pudozone(angle):

    return pickup_angles[min(range(len(pickup_angles)), key = lambda i: abs(pickup_angles[i]-angle))]


def robot_calibrate():
    gripper_cal()
    arm_cal()
    base_cal()


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
            pickup_zones.append(closest_pudozone(base_motor.angle()))

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
                    putdown_zones["GREEN"] = closest_pudozone(base_motor.angle())
                elif Button.DOWN in pressed and Button.DOWN not in was_pressed:
                    done = True
                    putdown_zones["RED"] = closest_pudozone(base_motor.angle())
                elif Button.LEFT in pressed and Button.LEFT not in was_pressed:
                    done = True
                    putdown_zones["BLUE"] = closest_pudozone(base_motor.angle())
                elif Button.RIGHT in pressed and Button.RIGHT not in was_pressed:
                    done = True
                    putdown_zones["YELLOW"] = closest_pudozone(base_motor.angle())
            ev3.screen.clear()
        if Button.CENTER in pressed and Button.CENTER not in was_pressed:
            check = False
    ev3.screen.clear()
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
    base_move(angle)
    gripper_motor.run_target(50, -90)
    elbow_motor.run_until_stalled(-20, Stop.HOLD, duty_limit=10)
    gripper_motor.run_until_stalled(200, then=Stop.HOLD, duty_limit=75)
    elbow_motor.run_target(20, 0)


def block_putdown(angle):
    base_move(angle)
    elbow_motor.run_angle(200, -20, Stop.COAST)
    # elbow_motor.run_until_stalled(-20,Stop.COAST,duty_limit=10)
    wait(10000)
    elbow_motor.hold()
    gripper_motor.run_target(50, -90)
    elbow_motor.run_target(20, 30)


def robot_func(zones):
    pickup = zones[0][0]
    putdown = zones[1]
    block_pickup(pickup)
    bd = block_detect()
    elbow_motor.run_target(20,30)
    if type(bd) == type(""):
        block_putdown(putdown.get(bd))
    else:
        wait(1000)
        block_putdown(base_motor.angle())


def emergency_stop(emergency):
    if emergency:
        print("L Bozo")
    return


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
