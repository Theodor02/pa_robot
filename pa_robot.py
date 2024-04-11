print("Hello world")

x = [1,2,3,4,5,6,7,8,9]
for i in x:
    print(f"Hello {i} Worlds")

print("Super Earth needs YOU!", "\n"
      "Sign up to fight for DEMOCRACY, LIBERTY and JUSTICE NOW!", "\n"
      "JOIN THE HELLDIVERS!")

#Hello i am not.

from pybricks.hubs import EV3Brick
from pybricks.ev3devices import Motor, TouchSensor, ColorSensor
from pybricks.parameters import Port, Stop, Direction, Button
from pybricks.tools import wait
from pybricks.messaging import BluetoothMailboxServer, TextMailbox, BluetoothMailboxClient
import math


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

def receive_location(mbox): # supposed to recieve true of location is occupied
        location_msg = mbox.wait_new()
        if location_msg == "False":
            return False
        else:
            return True


def send_occupied(mbox): # supposed to send true if location is occupied
    msg = "True"
    mbox.send(msg)
    return


def server_main(state):
    safe_to_move = False

    mbox = establish_connection(state)
    if safe_to_move == False:
        send_occupied(mbox)
        safe_to_move = receive_location(mbox)
    safe_to_move = receive_location(mbox)
    
    return safe_to_move
