import math
import socket
import time
import select

pi = math.pi

G = 9.80665
time = 0


def throttleToThrust(x):
    P = 0.015 * ((x * 10.0) ** 3.2)
    T = ((pi / 2.0) * (0.25 ** 2) * 1.225 * P ** 2) ** (1.0 / 3.0)
    return (T * 8.0) - G


def thrustToThrottle(x):
    P = ((((((float(x) + G) / 8.0) ** 3.0) / (pi / 2.0)) / (0.25 ** 2.0)) / 1.225) ** (1 / 2.0)
    return ((P / 0.015) ** (1.0 / 3.2)) / 10.0


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


def updatePos(x):
    global curPos
    s.send("STATUS " + str(x) + "\n")
    curPos[x] = getData().split()


# def flyTo(drone, x, y, z):



TCP_IP = 'localhost'
TCP_PORT = 7000
BUFFER_SIZE = 1024

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((TCP_IP, TCP_PORT))

data = getData()
area = data.split()
print("Area:", area)

data = getData().split("\r\n")
print "data:", data
nrOfDrones = int(data[0])
coords = data[1]
print("amount: ", nrOfDrones)

curPos = []  # x y z vx vy vz rx ry r
for i in range(nrOfDrones):
    curPos.append([])

printData()
for i in range(nrOfDrones):
    updatePos(i)
    print(curPos[i])

# print("thrott to thrust", throttleToThrust(0))
# print("thrust to throttle", thrustToThrottle(0))

timeInAir = 0
timeLength = 1

while timeInAir < 10:

    if float(curPos[0][2]) > 20 and float(curPos[0][2]) < 40:
        timeInAir += timeLength

    for i in range(nrOfDrones):
        updatePos(i)
        print(i, curPos[i])
        if float(curPos[i][2]) > 20:
            sendThrottle(i, thrustToThrottle(-1.0 * float(curPos[i][5])))
        else:
            sendThrottle(i, thrustToThrottle(-1.0 * float(curPos[i][5]) + 10))

    tick(timeLength)

while float(curPos[0][2]) > 0.3:
    for i in range(nrOfDrones):
        updatePos(i)
        print("l", i, curPos[i])
        if float(curPos[i][2]) > 5:
            sendThrottle(i, thrustToThrottle(-1.0 * float(curPos[i][5]) - 2))
        elif float(curPos[i][2]) > 0.3:
            sendThrottle(i, thrustToThrottle(-1.0 * float(curPos[i][5]) - 0.2))
        else:
            sendThrottle(i, 0)
            s.send("LAND " + str(i) + "\n")
            printData()

    tick(timeLength)
tick(1)
'''

t = 0.5
while float(float(curPos[5]) <= 0):
	t += 0.01
	print("cur", curPos[5])
	sendThrottle(0, t)
	tick(1)
	updatePos(0)
	print("while", curPos)

print("endwhile ")
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
