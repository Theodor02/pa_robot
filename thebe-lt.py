#!/usr/bin/env pybricks-micropython
from pybricks.ev3devices import Motor
from pybricks.parameters import Direction, Port, Stop, Button, Color
from pybricks.hubs import EV3Brick
from pybricks.tools import wait
from pybricks.messaging import BluetoothMailboxServer, TextMailbox, BluetoothMailboxClient


ev3 = EV3Brick()

# Load belt
belt = Motor(Port.D, Direction.CLOCKWISE)
belt.control.limits(speed=150, acceleration=60)


def establish_connection():
    bla = 0
    client = BluetoothMailboxClient()
    while bla != 10:
        try:
            client.connect("ev3dev")
            mbox = TextMailbox("mbox", client)
            bla =+ 1
            while True:
                wait(2000)
                mbox.send("ping")
                msg = mbox.wait_new()
                if msg == "pong":
                    return mbox
        except:
            print("Connection error!!!!!")


def change_speed(change, speed):
    if -150 < speed + change <= 150:
        speed += change
        ev3.screen.print("Speed:", speed)
        belt.run(speed)
        wait(300)
    return speed

def main():
    mbox = establish_connection()
    speed = 50
    belt_on = True
    belt.run(speed)
    ev3.screen.print("Speed:", speed)
    while True:
        if mbox.read() == "True":
            if Button.CENTER in ev3.buttons.pressed():
                if belt_on:
                    ev3.light.on(Color.RED)
                    belt.hold()
                    ev3.screen.print("STOP")
                else:
                    ev3.light.on(Color.GREEN)
                    belt.run(speed)
                    ev3.screen.print("Speed:", speed)
                belt_on = not belt_on
                wait(2000)
            if Button.UP in ev3.buttons.pressed() and belt_on:
                speed = change_speed(10, speed)
            if Button.DOWN in ev3.buttons.pressed() and belt_on:
                speed = change_speed(-10, speed)
            wait(100)
        else:
            belt.stop()


if __name__ == '__main__':
    main()

