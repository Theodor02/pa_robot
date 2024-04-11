#!/usr/bin/env pybricks-micropython

from pybricks.hubs import EV3Brick
from pybricks.ev3devices import Motor, TouchSensor, ColorSensor
from pybricks.parameters import Port, Stop, Direction, Button
from pybricks.tools import wait
from pybricks.messaging import BluetoothMailboxServer, TextMailbox, BluetoothMailboxClient
import math

# Ev3 Motor stuff
ev3 = EV3Brick()
gripper_motor = Motor(Port.A)
elbow_motor = Motor(Port.B, Direction.COUNTERCLOCKWISE, [8, 40])
base_motor = Motor(Port.C, Direction.COUNTERCLOCKWISE, [12, 36])
elbow_motor.control.limits(speed=60, acceleration=120)
base_motor.control.limits(speed=60, acceleration=120)
touchsensor = TouchSensor(Port.S1)
colorsensor = ColorSensor(Port.S2)



# Global Variables
blocks_at_zone = [0, 0, 0, 0]
pickup_angles = [4, 105, 150, 196]
connection_state = True
global schedule_wait
is_multiplayer = False

def closest_pudozone(angle):

    return pickup_angles[min(range(len(pickup_angles)), key=lambda i: abs(pickup_angles[i]-angle))]


def robot_calibrate():
    gripper_cal()
    arm_cal()
    base_cal()


def blockselectscreen(nr):
    ev3.screen.clear()
    ev3.screen.draw_text(60, 10, "Select the amount of blocks currently at the zone")
    ev3.screen.draw_text(60, 30, "UP")
    ev3.screen.draw_text(60, 50, str(nr))
    ev3.screen.draw_text(60, 70, "DOWN")


def nrofblockssel():
    ev3.screen.clear()
    nrofblocks = 0
    blockselectscreen(nrofblocks)
    done = False
    while not done:
        pressed = ev3.buttons.pressed()
        if Button.UP in pressed:
            nrofblocks += 1
            blockselectscreen(nrofblocks)
            wait(500)
        if Button.DOWN in pressed:
            nrofblocks -= 1
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
            base_motor.run(60)

        elif Button.RIGHT in pressed and base_motor.angle() >= 0:
            base_motor.run(-60)

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


def schedule():
    global schedule_wait
    schedule_wait = 20000
    ev3.screen.clear()
    pressed = ev3.buttons.pressed()
    while not Button.CENTER in pressed:
        pressed = ev3.buttons.pressed()
        ev3.screen.draw_text(10, 10, "Set wait time")
        ev3.screen.draw_text(10, 30, "Center to confirm")
        ev3.screen.draw_text(10, 50, "Wait time:" + str(schedule_wait/1000) + "s")
        ev3.screen.draw_text(10, 70, "UP = +1s")
        ev3.screen.draw_text(10, 90, "DOWN = -1s")
        if Button.UP in pressed:
            schedule_wait += 1000
            wait(100)
            ev3.screen.clear()
        if Button.DOWN in pressed:
            schedule_wait -= 1000
            wait(100)
            ev3.screen.clear()
    ev3.screen.clear()


def arm_move(position, speed=60):
    elbow_motor.run_target(speed, position, wait=False)
    while elbow_motor.angle() != round(position):

        ev3.screen.draw_text(10, 10, "Center button to abort")
        pressed = ev3.buttons.pressed()
        if Button.CENTER in pressed:
            shutdown_button()
            elbow_motor.run_target(speed, position, wait=False)
    ev3.screen.clear()


def base_move(position, speed=60):
    base_motor.run_target(speed, position, wait=False)
    while base_motor.angle() != position:
        ev3.screen.draw_text(10, 10, "Center button to abort")
        pressed = ev3.buttons.pressed()
        if Button.CENTER in pressed:
            shutdown_button()
            base_motor.run_target(speed, position, wait=False)
        if is_multiplayer:
            if base_motor.angle() < 30:
                send_occupied(mbox)
            else:
                send_unoccupied(mbox)
            if recieve_occupied(mbox):
                while recieve_occupied == True:
                    base_motor.hold()
    ev3.screen.clear()


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
    # wait(750)
    # print("\n\n\n\n\n\n\n\n\n\n\n")
    # print(red_original, green_original, blue_original)
    # print(red, green, blue)
    if red > 4:
        return "RED"

    elif red > 1 and green > 1.3 and blue < 1:
        return "YELLOW"

    elif red < 1 and green > 0.8 and blue > 2:
        return "GREEN"

    elif red < 1 and green < 0.8 and blue > 2 and (red_original <=2 or blue_original > 30):
        return "BLUE"

    else:
        return "WHITE"


def block_detect():
    color_list = []
    count = 0
    while count < 20:
        color_list.append(rgb_detection())
        count += 1
    return most_frequent(color_list)


def most_frequent(List):
    return max(set(List), key=List.count)


def block_pickup(angle):
    base_move(angle)
    gripper_motor.run_target(50, -90)
    arm_move(math.degrees(math.atan(blocks_at_zone[pickup_angles.index(angle)]*1.9/10))-30)
    gripper_motor.run_until_stalled(200, then=Stop.HOLD, duty_limit=75)
    arm_move(0, 20)
    if blocks_at_zone[pickup_angles.index(angle)] > 0:
        blocks_at_zone[pickup_angles.index(angle)] -= 1


def block_putdown(angle):
    base_move(angle)
    arm_move(math.degrees(math.atan(blocks_at_zone[pickup_angles.index(angle)]*1.9/10))-30, 30)
    blocks_at_zone[pickup_angles.index(angle)] += 1
    gripper_motor.run_target(50, -90)
    arm_move(30, 20)


def robot_func(zones):
    pickup = zones[0][0]
    putdown = zones[1]
    block_pickup(pickup)
    bd = block_detect()
    arm_move(30, 20)
    if type(bd) is type(""):
        if bd == "WHITE":
            wait(schedule_wait)
        else:
            block_putdown(putdown.get(bd))
    else:
        wait(1000)
        block_putdown(base_motor.angle())


def shutdown_button():
    wait(300)
    pressed = ev3.buttons.pressed()
    ev3.screen.clear()
    while not Button.CENTER in pressed:
        ev3.screen.draw_text(10, 10, "Center button to resume")
        ev3.screen.draw_text(10, 30, "UP to change schedule")
        ev3.screen.draw_text(10, 50, "DOWN to change zones")
        pressed = ev3.buttons.pressed()
        if Button.UP in pressed:
            schedule()
            ev3.screen.clear()
            wait(300)
        if Button.DOWN in pressed:
            global zones
            zones = manual_move()
            ev3.screen.clear()
            wait(300)
        elbow_motor.hold()
        gripper_motor.hold()
        base_motor.hold()
    wait(300)

# Robot messaging system


# Robot messaging system
def establish_connection(state):
    if state is True:
        server = BluetoothMailboxServer()
        server.wait_for_connection(1)
        print("Server established!")
        mbox = TextMailbox("mbox", server)
        while True:
            msg = mbox.wait_new()
            if msg == "ping":
                mbox.send("pong")
                return mbox
    else:
        client = BluetoothMailboxClient()
        client.connect("EV3")
        mbox = TextMailbox("mbox", client)
        while True:
            mbox.send("ping")
            msg = mbox.wait_new()
            if msg == "pong":
                return mbox

def recieve_occupied(mbox): # supposed to recieve true of location is occupied
        location_msg = mbox.wait_new()
        if location_msg == "False":
            return False
        else:
            return True


def send_occupied(mbox): # supposed to send true if location is occupied
    msg = "True"
    mbox.send(msg)

def send_unoccupied(mbox): # supposed to send false if location is unoccupied
    msg = "False"
    mbox.send(msg)


def server_or_client(connection_state):
    while True:
        ev3.screen.draw_text(10, 10, "UP for server")
        ev3.screen.draw_text(10, 30, "DOWN for client")
        pressed = ev3.buttons.pressed()
        if Button.UP in pressed:
            connection_state = True
            return connection_state
        if Button.DOWN in pressed:
            connection_state = False
            return connection_state


def multiplayer():
    while True:
        ev3.screen.draw_text(10, 10, "UP for multirobot")
        ev3.screen.draw_text(10, 30, "DOWN for single robot")
        pressed = ev3.buttons.pressed()
        if Button.UP in pressed:
            return True
        if Button.DOWN in pressed:
            return False



# Main function
def main():
    global zones
    global mbox
    is_multiplayer = multiplayer()
    if is_multiplayer:
        server_or_client(connection_state)
        mbox = establish_connection(connection_state)
    robot_calibrate()
    schedule()
    zones = manual_move()
    while True:
        robot_func(zones)



if __name__ == "__main__":
    main()
