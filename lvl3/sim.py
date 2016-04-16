import math
import select
import socket


class Drone:
    def __init__(self, id, x, y, z, height):
        self.id = id
        self.x = x
        self.y = y
        self.z = z
        self.height = height
        self.dx = 0
        self.dy = 0
        self.dz = 0
        self.vx = 0
        self.vy = 0
        self.vz = 1
        self.landed = False
        self.target = [10, 10]

    def stop(self):
        self.setDir(-self.dx / calcForce(self), -self.dy / calcForce(self), -self.dz / calcForce(self))
        print("stop", calcForce(self))
        speed = (calcForce(self) * math.floor(1 / dTime))
        print "speed", speed + -1.0 * float(calcForce(self))
        thr = str(self.id) + " " + str(thrustToThrottle((-1.0 * float(calcForce(self)) + speed)))
        print("THROTTLE " + thr)
        s.send("THROTTLE " + thr + "\n")
        printData()

    def land(self):
        force = calcForce(self)
        if force > 0:
            print "force ", force
            self.setDir(-self.dx / force, -self.dy / force, 1)
        if float(drone.z) > 3:
            sendThrottle(self.id, thrustToThrottle(-1.0 * float(self.dz) - 2))
        elif float(drone.z) > 0.3:
            sendThrottle(self.id, thrustToThrottle(-1.0 * float(self.dz) - 0.2))
        else:
            sendThrottle(self.id, 0)
            print "LAND", self.id
            s.send("LAND " + str(self.id) + "\n")
            printData()
            self.landed = True

    def setNormSpeed(self):
        # sendThrottle(self.id, thrustToThrottle(-1.0 * float(calcForce(self)) + speed))
        # print "speed", speed + -1.0 * float(calcForce(self))
        # thr = (-1.0 * float(calcForce(self)) + speed) * calcForce(self)
        speed = G / self.vz + (-1.0 * float(self.dz)) / self.vz
        print "speed", speed

        print("THROTTLE " + str(self.id) + " " + str(thrustToThrottleFlight(speed)))
        s.send("THROTTLE " + str(self.id) + " " + str(thrustToThrottleFlight(speed)) + "\n")
        printData()
        # self.setSpeedRaw(thr)

    def setSpeed(self, speed):
        self.setSpeedRaw(speed + -1.0 * float(calcForce(self)))

    def setSpeedRaw(self, speed):
        print("THROTTLE " + str(self.id) + " " + str(thrustToThrottle(speed)))
        s.send("THROTTLE " + str(self.id) + " " + str(thrustToThrottle(speed)) + "\n")
        printData()

    def setDir(self, x, y, z):
        print("TURN " + str(self.id) + " " + str(x) + " " + str(y) + " " + str(z))
        s.send("TURN " + str(self.id) + " " + str(x) + " " + str(y) + " " + str(z) + "\n")
        printData()

    def flyTo(self):
        updatePos(self)
        print("curPos", self.x, self.y, self.z)
        if self.z < self.height and (abs(self.x - self.target[0]) > 2 or abs(self.y - self.target[1]) > 2):
            print("< 20")
            self.setDir(0, 0, 1)
            self.setSpeed(9)
        elif (abs(self.x - self.target[0]) > 2 or abs(
                    self.y - self.target[1]) > 2) and self.dx == 0 and self.dy == 0 and abs(self.dz) > 1:
            print("stopping", self.z)
            self.stop()
        elif (abs(self.x - self.target[0]) > 2 or abs(self.y - self.target[1]) > 2) and abs(self.dz) > 6:
            print("dz>1")
            self.stop()
        elif (abs(self.x - self.target[0]) > 2 or abs(self.y - self.target[1]) > 2) and (
                        drone.dx ** 2 + drone.dy ** 2) ** 0.5 < 6:
            dir = normalizeVec([self.target[0] - self.x, self.target[1] - self.y,
                                max(self.target[0] - self.x, self.target[1] - self.y) + 5])
            print("purrfect", dir)
            self.setDir(dir[0], dir[1], dir[2])
            self.setNormSpeed()
        elif abs(self.x - self.target[0]) > 2 or abs(self.y - self.target[1]) > 2:
            self.setDir(0, 0, 1)
            self.setNormSpeed()
            print("purrfect2")
        elif self.dx > 0.05 or self.dy > 0.05:
            print("final stop")
            self.stop()
        else:
            self.land()

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
    ret = ((P / 0.015) ** (1.0 / 3.2)) / 10.0
    return ret if ret <= 1 else 1


def thrustToThrottleFlight(x):
    if float(x) < 0:
        return 0
    P = ((((((float(x)) / 8.0) ** 3.0) / (pi / 2.0)) / (0.25 ** 2.0)) / 1.225) ** (1 / 2.0)
    ret = ((P / 0.015) ** (1.0 / 3.2)) / 10.0
    return ret if ret <= 1 else 1


def calcForce(drone):
    return (drone.dx ** 2 + drone.dy ** 2 + drone.dz ** 2) ** 0.5


def normalizeVec(vec):
    length = 0
    for i in vec:
        length += i ** 2
    length **= 0.5

    for i in range(len(vec)):
        if (length > 0):
            vec[i] /= length

    return vec


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
    print("curTime"),
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
    # print("data:")
    data = getData()
    print(data.strip())
    # print("end data")
    return data


def createDrones():
    height = 20
    for i in range(nrOfDrones):
        s.send("STATUS " + str(i) + "\n")
        data = printData().strip().split(" ")
        drones.append(Drone(i, float(data[1]), float(data[2]), float(data[3]), height))
        height += 1


def updatePos(drone):
    print("STATUS " + str(drone.id) + "\n")
    s.send("STATUS " + str(drone.id) + "\n")
    curPos = printData().strip().split()
    drone.x = float(curPos[0])
    drone.y = float(curPos[1])
    drone.z = float(curPos[2])
    drone.dx = float(curPos[3])
    drone.dy = float(curPos[4])
    drone.dz = float(curPos[5])
    drone.vx = float(curPos[6])
    drone.vy = float(curPos[7])
    drone.vz = float(curPos[8])


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

nrOfDrones = int(float(printData()))
print("amount: ", nrOfDrones)

targetString = ""
for i in range(nrOfDrones):
    targetString += getData()
# curPos = []  # x y z vx vy vz rx ry r
createDrones()

for i in range(nrOfDrones):
    targets = (targetString.strip().split("\r\n"))
    drones[i].target[0] = float(targets[i].split()[0])
    drones[i].target[1] = float(targets[i].split()[1])
    print drones[i].target

# printData()
for drone in drones:
    updatePos(drone)

# print("thrott to thrust", throttleToThrust(0))
# print("thrust to throttle", thrustToThrottle(0))

dTime = 0.03

while True:
    tick(dTime)
    for drone in drones:
        if not drone.landed:
            drone.flyTo()

# landing