#!/usr/bin/env pybricks-micropython

from pybricks.hubs import EV3Brick
from pybricks.ev3devices import Motor, TouchSensor, ColorSensor
from pybricks.parameters import Port, Stop, Direction, Button
from pybricks.tools import wait
from pybricks.messaging import BluetoothMailboxServer, TextMailbox, BluetoothMailboxClient
import math
from pybricks.media.ev3dev import Font


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
pickup_angles = [2, 103, 148, 193]
connection_state = True
global schedule_wait
is_multiplayer = False
custom_font = Font(family=None, size=14, bold=True, monospace=False)
ev3.screen.set_font(custom_font)


def outlines(amount):
    ev3.screen.draw_box(2, 2, 176, 126, 3)
    for i in range(1, amount+1):
        ev3.screen.draw_line(7, 5 + i * 20, 178, 5 + i * 20, 2)
    for i in range(1, amount+1):
        ev3.screen.draw_circle(7, -2 + i * 20 , 3, True)
    if amount < 5:
        # flowerpower
        ev3.screen.draw_circle(90, 105, 6, True)  # middle
        ev3.screen.draw_circle(90, 115, 5)  # bottom
        ev3.screen.draw_circle(100, 105, 5)  # right
        ev3.screen.draw_circle(90, 95, 5)  # top
        ev3.screen.draw_circle(80, 105, 5)  # left
        ev3.screen.draw_circle(83, 98, 4)  # top left
        ev3.screen.draw_circle(97, 98, 4)  # top right
        ev3.screen.draw_circle(83, 112, 4)  # bottom left
        ev3.screen.draw_circle(97, 112, 4)  # bottom right

        # flower right
        ev3.screen.draw_circle(140, 105, 4, True)  # middle
        ev3.screen.draw_circle(140, 112, 3)  # bottom
        ev3.screen.draw_circle(147, 105, 3)  # right
        ev3.screen.draw_circle(140, 98, 3)  # top
        ev3.screen.draw_circle(133, 105, 3)  # left
        ev3.screen.draw_circle(136, 101, 2)  # top left
        ev3.screen.draw_circle(144, 101, 2)  # top right
        ev3.screen.draw_circle(136, 109, 2)  # bottom left
        ev3.screen.draw_circle(144, 109, 2)  # bottom right

        # flower left
        ev3.screen.draw_circle(40, 105, 4, True)  # middle
        ev3.screen.draw_circle(40, 112, 3)  # bottom
        ev3.screen.draw_circle(47, 105, 3)  # right
        ev3.screen.draw_circle(40, 98, 3)  # top
        ev3.screen.draw_circle(33, 105, 3)  # left
        ev3.screen.draw_circle(36, 101, 2)  # top left
        ev3.screen.draw_circle(44, 101, 2)  # top right
        ev3.screen.draw_circle(36, 109, 2)  # bottom left
        ev3.screen.draw_circle(44, 109, 2)  # bottom right


def closest_pudozone(angle):
    return pickup_angles[min(range(len(pickup_angles)), key=lambda i: abs(pickup_angles[i]-angle))]


def robot_calibrate():
    elbow_motor.run_until_stalled(60,then= Stop.HOLD, duty_limit= 25)
    base_cal()
    gripper_cal()
    base_move(90)
    arm_cal()
    base_move(0)


def block_select_screen(nr):
    ev3.screen.clear()
    ev3.screen.draw_text(12, 10, "Block height at zone")
    ev3.screen.draw_text(12, 30, "UP")
    ev3.screen.draw_text(12, 50, str(nr))
    ev3.screen.draw_text(12, 70, "DOWN")
    outlines(4)


def nr_of_blocks_sel():
    ev3.screen.clear()
    nrofblocks = 0
    block_select_screen(nrofblocks)
    done = False
    wait(300)
    while not done:
        pressed = ev3.buttons.pressed()
        if Button.UP in pressed:
            nrofblocks += 1
            block_select_screen(nrofblocks)
            wait(500)
        if Button.DOWN in pressed:
            nrofblocks -= 1
            block_select_screen(nrofblocks)
            wait(500)
        if Button.CENTER in pressed:
            done = True
            wait(500)
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
        ev3.screen.draw_text(12, 10, 'DONE = CENTER')
        ev3.screen.draw_text(12, 30, 'PICKUP = UP')
        ev3.screen.draw_text(12, 50, 'DROPOFF = DOWN')
        outlines(3)
        if Button.LEFT in pressed:
            base_motor.run(60)

        elif Button.RIGHT in pressed and base_motor.angle() >= 0:
            base_motor.run(-60)

        else:
            base_motor.hold()

        if Button.UP in pressed and Button.UP not in was_pressed:
            curangle = closest_pudozone(base_motor.angle())
            pickup_zones.append(curangle)
            blocks_at_zone[pickup_angles.index(curangle)] = nr_of_blocks_sel()

        if Button.DOWN in pressed and Button.DOWN not in was_pressed:
            ev3.screen.clear()
            ev3.screen.draw_text(12, 10, "GREEN = UP")
            ev3.screen.draw_text(12, 30, "RED = DOWN")
            ev3.screen.draw_text(12, 50, "BLUE = LEFT")
            ev3.screen.draw_text(12, 70, "YELLOW = RIGHT")
            outlines(4)
            wait(100)
            done = False
            while not done:
                was_pressed = pressed
                pressed = ev3.buttons.pressed()
                if Button.UP in pressed and Button.UP not in was_pressed:
                    done = True
                    curangle = closest_pudozone(base_motor.angle())   
                    size = size_button() 
                    if type(size) == type(""):
                        putdown_zones["GREEN"+ size] = curangle
                    else:
                        putdown_zones["GREEN"+ size[0]] = curangle
                        putdown_zones["GREEN"+ size[1]] = curangle
                    pickup_zones.append(curangle)
                    wait(10)
                    blocks_at_zone[pickup_angles.index(curangle)] = nr_of_blocks_sel()
                elif Button.DOWN in pressed and Button.DOWN not in was_pressed:
                    done = True
                    curangle = closest_pudozone(base_motor.angle())
                    size = size_button() 
                    if type(size) == type(""):
                        putdown_zones["RED"+ size] = curangle
                    else:
                        putdown_zones["RED"+ size[0]] = curangle
                        putdown_zones["RED"+ size[1]] = curangle
                    
                    pickup_zones.append(curangle)
                    wait(10)
                    blocks_at_zone[pickup_angles.index(curangle)] = nr_of_blocks_sel()
                elif Button.LEFT in pressed and Button.LEFT not in was_pressed:
                    done = True
                    curangle = closest_pudozone(base_motor.angle())
                    size = size_button() 
                    if type(size) == type(""):
                        putdown_zones["BLUE"+ size] = curangle
                    else:
                        putdown_zones["BLUE"+ size[0]] = curangle
                        putdown_zones["BLUE"+ size[1]] = curangle
                    
                    pickup_zones.append(curangle)
                    wait(10)
                    blocks_at_zone[pickup_angles.index(curangle)] = nr_of_blocks_sel()
                elif Button.RIGHT in pressed and Button.RIGHT not in was_pressed:
                    done = True
                    curangle = closest_pudozone(base_motor.angle())
                    size = size_button() 
                    if type(size) == type(""):
                        putdown_zones["YELLOW"+size] = curangle
                    else:
                        putdown_zones["YELLOW"+size[0]] = curangle
                        putdown_zones["YELLOW"+size[1]] = curangle
                    
                    pickup_zones.append(curangle)
                    wait(10)
                    blocks_at_zone[pickup_angles.index(curangle)] = nr_of_blocks_sel()
            ev3.screen.clear()
        if Button.CENTER in pressed and Button.CENTER not in was_pressed:
            check = False
    ev3.screen.clear()
    wait(1000)
    return [pickup_zones, putdown_zones]


def size_button():
    size = ""
    ev3.screen.clear()
    outlines(3)
    ev3.screen.draw_text(12, 10, "Large = UP")
    ev3.screen.draw_text(12, 30, "Both = Center")
    ev3.screen.draw_text(12, 50, "Small = Down")
    done = False
    pressed = ev3.buttons.pressed()
    while not done:
        was_pressed = pressed
        pressed = ev3.buttons.pressed()
        if Button.UP in pressed and Button.UP not in was_pressed:
            size = "LARGE"
            done = True
        elif Button.DOWN in pressed and Button.DOWN not in was_pressed:
            size = "SMALL"
            done = True
        elif Button.CENTER in pressed and Button.CENTER not in was_pressed:
            return ["LARGE","SMALL"]
    return size


def schedule():
    global schedule_wait
    schedule_wait = 10000
    ev3.screen.clear()
    pressed = ev3.buttons.pressed()
    while not Button.CENTER in pressed:
        pressed = ev3.buttons.pressed()
        ev3.screen.draw_text(12, 10, "Set wait time")
        ev3.screen.draw_text(12, 30, "Center to confirm")
        ev3.screen.draw_text(12, 50, "Wait time:" + str(schedule_wait/1000) + "s")
        ev3.screen.draw_text(12, 70, "UP = +1s, DOWN = -1s")
        outlines(4)
        if Button.UP in pressed:
            if schedule_wait >= 0:
                schedule_wait += 1000
                wait(100)
                ev3.screen.clear()
        if Button.DOWN in pressed:
            if schedule_wait >= 0:
                schedule_wait -= 1000
                wait(100)
                ev3.screen.clear()
    ev3.screen.clear()


def arm_move(position, speed=60):
    elbow_motor.run_target(speed, position, wait=False)
    while elbow_motor.angle() != round(position):
        ev3.screen.draw_text(12, 10, "Center button to pause")
        ev3.screen.draw_text(12, 30, "UP button for emergency shutdown")
        outlines(2)
        pressed = ev3.buttons.pressed()
        if Button.CENTER in pressed:
            pause_button()
            elbow_motor.run_target(speed, position, wait=False)
        if Button.UP in pressed:
            emergency_button()
    ev3.screen.clear()


def base_move(position, speed=60):
    while base_motor.angle() != position:
        base_motor.run_target(speed, position, wait=False)
        ev3.screen.draw_text(12, 10, "Center: pause")
        ev3.screen.draw_text(12, 30, "UP: Emergency Shutdown")
        outlines(2)
        pressed = ev3.buttons.pressed()
        if Button.CENTER in pressed:
            pause_button()
            base_motor.run_target(speed, position, wait=False)
        if Button.UP in pressed:
            emergency_button()
        if is_multiplayer:
            if base_motor.angle() < 45:
                sentmsg = send_occupied(mbox)
            else:
                sentmsg = send_unoccupied(mbox)
            if recieve_occupied(mbox) and sentmsg:
                base_motor.run_target(speed, 60)
            if recieve_occupied(mbox):
                while recieve_occupied(mbox):
                    print(recieve_occupied(mbox))
                    if base_motor.angle() > 45:
                        base_motor.run_target(speed, 50)
                    else:
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


# LR = 66
# SR = 12
# LY = 80
# SY = 20
# LGR = 10
# SGR = 2
# LB = 9
# SB = 2


def size_detect(color):
    if color == "BLUE":
        if colorsensor.reflection() > 5:
            return "LARGE"
        return "SMALL"
    if color == "RED":
        if colorsensor.reflection() > 40:
            return "LARGE"
        return "SMALL"        
    if color == "YELLOW":
        if colorsensor.reflection() > 40:
            return "LARGE"
        return "SMALL"
    if color == "GREEN":
        if colorsensor.reflection() > 5:
            return "LARGE"
        return "SMALL"
    else:
        return "SMALL"


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


def block_pickup_belt(angle):
    arm_move(20)
    base_move(angle)
    gripper_motor.run_target(50, -90)
    while colorsensor.reflection() <= 2:
        print("")
    arm_move(-5,150)
    gripper_motor.run_until_stalled(200, then=Stop.HOLD, duty_limit=75)


def block_putdown(angle):
    base_move(angle)
    arm_move(math.degrees(math.atan(blocks_at_zone[pickup_angles.index(angle)]*1.9/10))-30, 30)
    blocks_at_zone[pickup_angles.index(angle)] += 1
    gripper_motor.run_target(50, -90)
    arm_move(30, 20)


def robot_func(zones, belt):
    pickup = zones[0][0]
    putdown = zones[1]
    if belt:
        block_pickup_belt(pickup)
    else:
        block_pickup(pickup)
    bd = block_detect()
    arm_move(30, 20)
    ev3.speaker.say(bd)
    if bd == "WHITE":
        wait(schedule_wait)
    # print(putdown)
    # print(bd)
    # print(bd + size_detect(bd))
    try:
        block_putdown(putdown.get(bd + size_detect(bd)))
    except:
        if belt:  # snubben fick bältet
            elbow_motor.run_target(60,0)
            gripper_motor.run_target(50, -90)
        else:
            block_putdown(base_motor.angle())


def pause_button():
    wait(300)
    pressed = ev3.buttons.pressed()
    ev3.screen.clear()
    while not Button.CENTER in pressed:
        ev3.screen.draw_text(12, 10, "Center: resume")
        ev3.screen.draw_text(12, 30, "UP: change schedule")
        ev3.screen.draw_text(12, 50, "DOWN: change zones")
        ev3.screen.draw_text(12, 70, "RIGHT: emergency shutdown")
        outlines(4)
        pressed = ev3.buttons.pressed()
        if Button.UP in pressed:
            schedule()
            wait(300)
        if Button.DOWN in pressed:
            global zones
            zones = manual_move()
            wait(300)
        if Button.RIGHT in pressed:
            emergency_button()
        elbow_motor.hold()
        gripper_motor.hold()
        base_motor.hold()
    wait(300)


def emergency_button():
    base_motor.hold()
    ev3.screen.clear()
    ev3.screen.draw_text(12, 10, "Emergency stop")
    ev3.screen.draw_text(12, 30, "Shutting down...")
    outlines(2)
    # for x in pickup_angles:
    #     if math.isclose(x, base_motor.angle(),abs_tol=10):
    #         block_putdown(x)
    #         exit(0)
    block_putdown(base_motor.angle())
    exit(0)


# Robot messaging system
# multi robot code, two states either server or client
# if SERVER it will wait for the message "ping" and when it recieves it will send "pong"
# this is to ensure connection between robots. 
# if CLIENT it will try to connect to a server/robot called "EV3dev" then it will send "ping" and then wait for "pong"
# this is to ensure connection between robots.
# does not have any error checks or things


def establish_connection(state):
    ev3.screen.clear()
    if state is True:
        server = BluetoothMailboxServer()
        ev3.screen.draw_text(12, 10, "Waiting for connection...")
        outlines(1)
        server.wait_for_connection(1)
        ev3.screen.clear()
        ev3.screen.draw_text(12, 10, "Server established!")
        outlines(1)
        mbox = TextMailbox("mbox", server)
        while True:
            wait(2000)
            msg = mbox.wait_new()
            if msg == "ping":
                ev3.screen.clear()
                ev3.screen.draw_text(12, 30, "Message recieved")
                outlines(1)
                mbox.send("pong")
                wait(1000)
                return mbox
    else:
        client = BluetoothMailboxClient()
        client.connect("ev3dev")
        mbox = TextMailbox("mbox", client)
        while True:
            wait(2000)
            mbox.send("ping")
            msg = mbox.wait_new()
            if msg == "pong":
                return mbox


def recieve_occupied(mbox):  # supposed to recieve true of location is occupied
    location_msg = mbox.read()
    if location_msg == "False":
        return False
    else:
        return True


def send_occupied(mbox):  # supposed to send true if location is occupied
    msg = "True"
    mbox.send(msg)
    return True


def send_unoccupied(mbox):  # supposed to send false if location is unoccupied
    msg = "False"
    mbox.send(msg)
    return False


def server_or_client(connection_state):
    ev3.screen.clear()
    ev3.screen.draw_text(12, 10, "UP for server")
    ev3.screen.draw_text(12, 30, "DOWN for client")
    outlines(2)
    wait(300)
    while True:
        pressed = ev3.buttons.pressed()
        if Button.UP in pressed:
            connection_state = True
            ev3.screen.clear()
            return connection_state
        if Button.DOWN in pressed:
            connection_state = False
            ev3.screen.clear()
            return connection_state


def multiplayer():
    while True:
        ev3.screen.draw_text(12, 10, "UP for multirobot")
        ev3.screen.draw_text(12, 30, "DOWN for single robot")
        outlines(2)
        pressed = ev3.buttons.pressed()
        if Button.UP in pressed:
            return True
        if Button.DOWN in pressed:
            return False


replay = "Shawtys like a melody in my head That I cant keep out, got me singing like Na-na-na-na, every day Its like my iPod stuck on replay, replay-ay-ay-ay"
funny_images = ["shawty1", "shawty2"]


def funny(text, images):  # viktigaste functionen av dem alla.
    text_list = text.split() or []
    images_list = images or []
    image_index = 0
    for i in text_list:
        if image_index == len(images_list):
            image_index = 0
        ev3.screen.clear()
        if images_list != []:
            ev3.screen.draw_image(0, 0, images_list[image_index])
        ev3.speaker.say(i)
        image_index += 1


def choose_belt():
    ev3.screen.clear()
    wait(300)
    while True:
        ev3.screen.draw_text(12, 10, "UP for belt")
        ev3.screen.draw_text(12, 30, "DOWN for no belt")
        outlines(2)
        pressed = ev3.buttons.pressed()
        if Button.UP in pressed:
            wait(300)
            ev3.screen.clear()
            return True
        if Button.DOWN in pressed:
            wait(300)
            ev3.screen.clear()
            return False


# Main function
def main():
    global zones
    global mbox
    global is_multiplayer
    belt = False
    # funny(replay,funny_images)
    robot_calibrate()
    is_multiplayer = multiplayer()
    if is_multiplayer:
        server_or_client(connection_state)
        mbox = establish_connection(connection_state)
    belt = choose_belt()
    schedule()
    zones = manual_move()
    while True:
        robot_func(zones, belt)


if __name__ == "__main__":
    main()
