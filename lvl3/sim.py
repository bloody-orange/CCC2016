import math
import select
import socket


class Drone:
    def __init__(self, id, x, y, z):
        self.id = id
        self.x = x
        self.y = y
        self.z = z
        self.dx = 0
        self.dy = 0
        self.dz = 0
        self.vx = 0
        self.vy = 0
        self.vz = 1
        self.target = [10, 10]

    def stop(self):
        x = 0

    def setSpeed(self, speed):
        sendThrottle(self.id, thrustToThrottle(-1.0 * float(self.dz) + speed))

    def setDir(self, x, y, z):
        s.send("TURN " + self.id + " " + x + " " + y + " " + z + "\n")

    def flyTo(self, target):
        updatePos(self)
        print("ok", i, self.x, self.y, self.z)
        if self.z < 20:
            self.setDir(0, 1, 0)
            self.setSpeed(13)
            # elif:  TODO


drones = []
time = 0

pi = math.pi
G = 9.80665

def throttleToThrust(x):
    P = 0.015 * ((x * 10.0) ** 3.2)
    T = ((pi / 2.0) * (0.25 ** 2) * 1.225 * P ** 2) ** (1.0 / 3.0)
    return (T * 8.0) - G


def thrustToThrottle(x):
    if float(x) + G < 0:
        return 0
    P = ((((((float(x) + G) / 8.0) ** 3.0) / (pi / 2.0)) / (0.25 ** 2.0)) / 1.225) ** (1 / 2.0)
    return ((P / 0.015) ** (1.0 / 3.2)) / 10.0


def calcForce(drone):
    return (drone.dx ** 2 + drone.dy ** 2 + drone.dz ** 2) ** 0.5


def sendThrottle(id, x):
    thr = str(id) + " " + str(x)
    print("THROTTLE " + thr)
    s.send("THROTTLE " + thr + "\n")
    printData()


def tick(x):
    global time
    time += x
    print("TICK " + str(x))
    s.send("TICK " + str(x) + "\n")
    printData()


def getData():
    global s, BUFFER_SIZE
    s.setblocking(0)
    data = ""
    ready = select.select([s], [], [], 1)
    if ready[0]:
        data = s.recv(BUFFER_SIZE)
    return data


def printData():
    print(getData())


def createDrones():
    for i in range(nrOfDrones):
        s.send("STATUS " + str(i) + "\n")
        drones.append(drone)


def updatePos(drone):
    s.send("STATUS " + str(drone.id) + "\n")
    curPos = getData().strip().split()
    drone.x = curPos[0]
    drone.y = curPos[1]
    drone.z = curPos[2]
    drone.dx = curPos[3]
    drone.dy = curPos[4]
    drone.dz = curPos[5]
    drone.vx = curPos[6]
    drone.vy = curPos[7]
    drone.vz = curPos[8]






# def flyTo(drone, x, y, z):


TCP_IP = 'localhost'
TCP_PORT = 7000
BUFFER_SIZE = 1024

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((TCP_IP, TCP_PORT))

# data = getData()
# area = data.split()
# print("Area:", area)
# data = getData().split("\r\n")
nrOfDrones = int(float(getData()))
print("amount: ", nrOfDrones)

# curPos = []  # x y z vx vy vz rx ry r
createDrones()

target = []
for i in range(nrOfDrones):
    drones[i].target = (getData().strip().split(" "))

print("target", target)
printData()
for drone in drones:
    updatePos(drone)

# print("thrott to thrust", throttleToThrust(0))
# print("thrust to throttle", thrustToThrottle(0))

dTime = 0.1

while True:
    tick(dTime)
    for drone in drones:
        drone.flyTo(target[drone.id])

# landing
'''
while float(curPos[0][2]) > 0.3:
    for i in range(nrOfDrones):
        updatePos(i)
        print("curPos", i, curPos[i])

        if float(curPos[i][2]) > 5:
            sendThrottle(i, thrustToThrottle(-1.0 * float(curPos[i][5]) - 2))
        elif float(curPos[i][2]) > 0.3:
            sendThrottle(i, thrustToThrottle(-1.0 * float(curPos[i][5]) - 0.2))
        else:
            sendThrottle(i, 0)
            s.send("LAND " + str(i) + "\n")
            printData()

    tick(dTime)
tick(1)

t = 0.5
while float(float(curPos[5]) <= 0):
    t += 0.01
    print("cur", curPos[5])
    sendThrottle(0, t)
    tick(1)
    updatePos(0)
    print("while", curPos)

print("endwhile")
print t

tick(1)
printData()
updatePos(0)
print(curPos)

tick(1)
printData()
updatePos(0)
print(curPos)
'''

s.close()
