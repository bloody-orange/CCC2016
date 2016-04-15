import math
import socket
import time
import select

pi = math.pi

G = 9.80665


def throttleToThrust(x):
	global G
	P = 0.015 * ((x * 10) ** 3.2)
	T = ((pi / 2) * (0.25**2) * 1.225 * P**2) ** 1/3
	return (T * 8 - G) / 2#2kg heavy
	
def thrustToThrottle(x):
	P = ((((x + G) / 8 * 2) ** 3) / (pi / 2) / (0.025**2) / 1.225)
	return ((P / 0.015) ** 1/3.2 ) / 10
		
	


def sendThrottle(id, x):
	thr = str(id) + " " + str(x)
	print("THROTTLE " + thr)
	s.send("THROTTLE " + thr + "\n")

def tick(x):
	print("TICK " + str(x))
	s.send("TICK " + str(x) + "\n")

def getData():
	global s, BUFFER_SIZE
	s.setblocking(0)
	data = ""
	ready = select.select([s], [], [], 1)
	if ready[0]:
		data = s.recv(BUFFER_SIZE)
	return data
	
def printData():
	print getData()
	

def updatePos():
	global curPos
	s.send("STATUS 0\n")
	curPos = getData().split()

curPos = []
#x y z vx vy vz rx ry r

TCP_IP = 'localhost'
TCP_PORT = 7000
BUFFER_SIZE = 1024
 
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((TCP_IP, TCP_PORT))


printData()

printData()
updatePos()
print(curPos)

print("k", throttleToThrust(0.7))
print("k", thrustToThrottle(11.9))


while float(curPos[2]) < 50:
	sendThrottle(0, 0.6)
	time.sleep(0.5)
	printData()
	tick(1)

	printData()
	updatePos()
	print(curPos)
tick(1)

printData()
updatePos()
print(curPos)


s.close()