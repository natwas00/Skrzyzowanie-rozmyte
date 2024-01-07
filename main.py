import random
import time
import threading
import pygame
import sys
from simpful import *
from sterownik_v1_0 import create_FS
noOfSignals = 4
stoppingGap = 15
movingGap = 15
signals = []
currentGreen = 0
nextGreen = (currentGreen+1)%noOfSignals
currentYellow = False
signalText = ["","","",""]
x = {'right':[-80,-80,-80], 'down':[710,745,780], 'left':[1400,1400,1400], 'up':[590,625,660]}
y = {'right':[360,394,430], 'down':[-80,-80,-80], 'left':[470,505,540], 'up':[800,800,800]}
speeds = {'car':2.25, 'bus':1.8, 'truck':1.8, 'bike':2.5}
vehicles = {'right': {0:[], 1:[], 2:[],'cars':0, 'crossed':0, "time":0, 'index':0}, 'down': {0:[], 1:[], 2:[],'cars':0, 'crossed':0, "time":0, 'index':1}, 'left': {0:[], 1:[], 2:[], 'cars':0, 'crossed':0, "time":0, 'index':2}, 'up': {0:[], 1:[], 2:[],'cars':0, 'crossed':0, "time":0, 'index':3}}
priorities = [0,0,0,0]
directionNumbers = {0:'right', 1:'down', 2:'left', 3:'up'}
defaultStop = {'right': 550, 'down': 320, 'left': 840, 'up': 600}
stopLines = {'right': 560, 'down': 330, 'left': 830, 'up': 590}
vehicleTypes = {0:'car', 1:'bus', 2:'truck', 3:'bike'}
signalCoods = [(560,230),(810,230),(810,570),(560,570)]
signalTimerCoods = [(560,210),(810,210),(810,550),(560,550)]
signalCarsCoods = [(430,280),(850,280),(850,600),(430,600)]
signalTimeCoods = [(430,250),(850,250),(850,630),(430,630)]
signalPriorityCoods = [(430,220),(850,220),(850,660),(430,660)]
pygame.init()
simulation = pygame.sprite.Group()
ind = 0

def calculate_priority(cars, time):
    global fs
    fs.set_variable("number_of_cars", cars)
    fs.set_variable("waiting_time", time)
    priority = fs.inference()["priority"]
    return priority


def updateValues():
    if(currentYellow==False):
        signals[currentGreen][2]-=1
        signals[(currentGreen+2)%4][2] -= 1
    else:
        signals[currentGreen][1]-=1
        signals[(currentGreen+2)%4][1] -= 1
    signals[(currentGreen+1)%4][0]-=1
    signals[(currentGreen + 3) % 4][0] -= 1
def green():
    global currentGreen, currentYellow, nextGreen, priorities

    while True:

        signals[currentGreen][2]=15
        while (signals[currentGreen][2] > 0):  # while the timer of current green signal is not zero
            updateValues()
            time.sleep(1)
            vehicles[directionNumbers[(currentGreen+1)%4]]['time'] = vehicles[directionNumbers[(currentGreen+1)%4]]['time'] +1
            vehicles[directionNumbers[(currentGreen + 3) % 4]]['time'] = vehicles[directionNumbers[(currentGreen + 3) % 4]]['time'] + 1
            for dir in vehicles:
                priorities[vehicles[dir]['index']]=calculate_priority(vehicles[dir]['cars'], vehicles[dir]['time'])
        print(priorities)
        max_p = max(priorities)
        index_max = priorities.index(max_p)

        if index_max not in (currentGreen,(currentGreen+2)%4):
            currentYellow = True
            for i in range(0, 3):
                for vehicle in vehicles[directionNumbers[currentGreen]][i]:
                    vehicle.stop = defaultStop[directionNumbers[currentGreen]]
            while (signals[currentGreen][1] > 0):  # while the timer of current yellow signal is not zero
                updateValues()
                time.sleep(1)
            currentYellow = False  # set yellow signal off

            # reset all signal times of current signal to default times
            signals[currentGreen][2] = 15
            signals[currentGreen][1] = 3
            signals[currentGreen][0] = 150

            signals[(currentGreen + 2)% len(signals)][2] = 15
            signals[(currentGreen+2)% len(signals)][1] = 3
            signals[(currentGreen +2)% len(signals)][0] = 150
            currentGreen = index_max
            for dir in vehicles:
               # priorities[vehicles[dir]['index']] = 0
                vehicles[dir]['time']=0
        else:
            signals[currentGreen][2] = 15
            signals[(currentGreen + 2) % len(signals)][2] = 15


        # currentGreen = nextGreen  # set next signal as green signal
        # nextGreen = (currentGreen + 1) % noOfSignals  # set next green signal
        # signals[nextGreen][0]= signals[currentGreen][1] + signals[currentGreen][2]
def initialize():
    global currentGreen, priorities, vehicles

    ts1 = [0,3,15]  ### 0 - czerwony 1 - zółty 10 - zielony
    signals.append(ts1)
    ts2 = [150,3,15]
    signals.append(ts2)
    ts3 = [0,3,15]
    signals.append(ts3)
    ts4 = [150,3,15]
    signals.append(ts4)

    for dir in vehicles:
        priorities[vehicles[dir]['index']] = calculate_priority(vehicles[dir]['cars'], vehicles[dir]['time'])
    max_p = max(priorities)
    index_max = priorities.index(max_p)
    currentGreen = index_max

    green()

class Vehicle(pygame.sprite.Sprite):
    def __init__(self, lane, vehicleClass, direction_number, direction):
        pygame.sprite.Sprite.__init__(self)
        global ind
        self.ind = ind
        ind = ind +1
        self.lane = lane
        self.speed = speeds[vehicleClass]
        self.direction_number = direction_number
        self.direction = direction
        self.x = x[direction][lane]
        self.y = y[direction][lane]
        self.crossed = 0
        vehicles[direction][lane].append(self)
        self.index = len(vehicles[direction][lane]) - 1
        path = "images/" + direction + "/" + vehicleClass + ".png"
        self.image = pygame.image.load(path)
        self.stop = defaultStop[direction]

        if(len(vehicles[direction][lane])>1 and vehicles[direction][lane][self.index-1].crossed==0):    # if more than 1 vehicle in the lane of vehicle before it has crossed stop line
            if(direction=='right'):
                self.stop = vehicles[direction][lane][self.index-1].stop - vehicles[direction][lane][self.index-1].image.get_rect().width - stoppingGap         # setting stop coordinate as: stop coordinate of next vehicle - width of next vehicle - gap
            elif(direction=='left'):
                self.stop = vehicles[direction][lane][self.index-1].stop + vehicles[direction][lane][self.index-1].image.get_rect().width + stoppingGap
            elif(direction=='down'):
                self.stop = vehicles[direction][lane][self.index-1].stop - vehicles[direction][lane][self.index-1].image.get_rect().height - stoppingGap
            elif(direction=='up'):
                self.stop = vehicles[direction][lane][self.index-1].stop + vehicles[direction][lane][self.index-1].image.get_rect().height + stoppingGap
        else:
            self.stop = defaultStop[direction]
        simulation.add(self)

    def render(self, screen):
            screen.blit(self.image, (self.x, self.y))

    def move(self):
            global vehicles
            if (self.direction == 'right'):
                if (self.crossed == 0 and self.x + self.image.get_rect().width > stopLines[
                    self.direction]):  # if the image has crossed stop line now
                    self.crossed = 1
                    vehicles['right']['cars'] = vehicles['right']['cars'] - 1
                if ((self.x + self.image.get_rect().width <= self.stop or self.crossed == 1 or (
                        currentGreen in (0,2) and currentYellow == False)) and (
                        self.index == 0 or self.x + self.image.get_rect().width < (
                        vehicles[self.direction][self.lane][self.index - 1].x - movingGap))):
                    # (if the image has not reached its stop coordinate or has crossed stop line or has green signal) and (it is either the first vehicle in that lane or it is has enough gap to the next vehicle in that lane)
                    self.x += self.speed  # move the vehicle
            elif (self.direction == 'down'):
                if (self.crossed == 0 and self.y + self.image.get_rect().height > stopLines[self.direction]):
                    self.crossed = 1
                    vehicles['down']['cars'] = vehicles['down']['cars'] - 1
                if ((self.y + self.image.get_rect().height <= self.stop or self.crossed == 1 or (
                        currentGreen in (1,3) and currentYellow == False)) and (
                        self.index == 0 or self.y + self.image.get_rect().height < (
                        vehicles[self.direction][self.lane][self.index - 1].y - movingGap))):
                    self.y += self.speed
            elif (self.direction == 'left'):
                if (self.crossed == 0 and self.x < stopLines[self.direction]):
                    self.crossed = 1
                    vehicles['left']['cars'] = vehicles['left']['cars'] - 1
                if ((self.x >= self.stop or self.crossed == 1 or (currentGreen in (0,2) and currentYellow == False)) and (
                        self.index == 0 or self.x > (
                        vehicles[self.direction][self.lane][self.index - 1].x + vehicles[self.direction][self.lane][
                    self.index - 1].image.get_rect().width + movingGap))):
                    self.x -= self.speed
            elif (self.direction == 'up'):
                if (self.crossed == 0 and self.y < stopLines[self.direction]):
                    self.crossed = 1
                    vehicles['up']['cars'] = vehicles['up']['cars'] - 1
                if ((self.y >= self.stop or self.crossed == 1 or (currentGreen in (1,3) and currentYellow == False)) and (
                        self.index == 0 or self.y > (
                        vehicles[self.direction][self.lane][self.index - 1].y + vehicles[self.direction][self.lane][
                    self.index - 1].image.get_rect().height + movingGap))):
                    self.y -= self.speed

def generateVehicles():
    while(True):
        global vehicles

        vehicle_type = random.randint(0,3)
        lane_number = random.randint(0,2)
        direction_number = random.randint(0,3)

        vehicles[directionNumbers[direction_number]]['cars']= vehicles[directionNumbers[direction_number]]['cars']+1
        vehicles['right']['cars'] = vehicles['right']['cars'] + 1
#
        Vehicle(lane_number, vehicleTypes[vehicle_type], 0, 'right')
        Vehicle(lane_number, vehicleTypes[vehicle_type], direction_number, directionNumbers[direction_number])

        time.sleep(1)






fs = create_FS()

thread1 = threading.Thread(name="initialization", target=initialize, args=())  # initialization
thread1.daemon = True
thread1.start()

screenWidth = 1400
screenHeight = 800
screenSize = (screenWidth, screenHeight)

# Setting background image i.e. image of intersection
background = pygame.image.load('images/intersection.png')

screen = pygame.display.set_mode(screenSize)

redSignal = pygame.image.load('images/signals/red.png')
yellowSignal = pygame.image.load('images/signals/yellow.png')
greenSignal = pygame.image.load('images/signals/green.png')
font = pygame.font.Font(None, 30)


thread2 = threading.Thread(name="generateVehicles", target=generateVehicles, args=())  # Generating vehicles
thread2.daemon = True
thread2.start()

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()
    screen.blit(background,(0,0))
    #for i in range(0, noOfSignals):  # display signal and set timer according to current status: green, yello, or red
     #   if (i == currentGreen) or (i == (currentGreen+2)%4):
    # print(signals)
    # print(currentYellow)
    if (currentYellow == True):
        signalText[currentGreen] = signals[currentGreen][1]
        signalText[(currentGreen+2)%4] = signals[(currentGreen+2)%4][1]
        screen.blit(yellowSignal, signalCoods[currentGreen])
        screen.blit(yellowSignal, signalCoods[(currentGreen+2)%4])
        k = (currentGreen+1) % noOfSignals
        screen.blit(yellowSignal, signalCoods[k])
        screen.blit(yellowSignal, signalCoods[(k+2)%4])
    else:
        signalText[(currentGreen+2)%4] = signals[(currentGreen+2)%4][2]
        screen.blit(greenSignal, signalCoods[(currentGreen+2)%4])
        signalText[currentGreen] = signals[currentGreen][2]
        screen.blit(greenSignal, signalCoods[currentGreen])
        screen.blit(redSignal, signalCoods[(currentGreen+1)%4])
        screen.blit(redSignal, signalCoods[(currentGreen + 3) % 4])

    signalTexts = ["", "", "", ""]
    #for i in range(0,noOfSignals):
    signalTexts[currentGreen] = font.render(str(signalText[currentGreen]), True, (0, 0, 0), (255, 255, 255))
    screen.blit(signalTexts[currentGreen],signalTimerCoods[currentGreen])
    signalTexts[(currentGreen+2)%4] = font.render(str(signalText[(currentGreen+2)%4]), True, (0, 0, 0), (255, 255, 255))
    screen.blit(signalTexts[(currentGreen+2)%4],signalTimerCoods[(currentGreen+2)%4])
    for dir in directionNumbers:
        carsq = font.render("cars:"+str(vehicles[directionNumbers[dir]]['cars']), True, (0, 0, 0),(255, 255, 255))
        screen.blit(carsq, signalCarsCoods[dir])
        timeq = font.render("waiting:"+str(vehicles[directionNumbers[dir]]['time']), True, (0, 0, 0),(255, 255, 255))
        screen.blit(timeq, signalTimeCoods[dir])
        priorityq = font.render("priority:"+str(round(priorities[dir],2)), True, (0, 0, 0),(255, 255, 255))
        screen.blit(priorityq, signalPriorityCoods[dir])

    if (currentYellow == False):
        signalTexts[(currentGreen+1)%4] = font.render("", True, (0, 0, 0), (255, 255, 255))
        screen.blit(signalTexts[(currentGreen+1)%4],signalTimerCoods[(currentGreen+1)%4])
        signalTexts[(currentGreen+3)%4] = font.render("", True, (0, 0, 0), (255, 255, 255))
        screen.blit(signalTexts[(currentGreen+3)%4],signalTimerCoods[(currentGreen+3)%4])
    else:
        signalTexts[(currentGreen+1)%4] = font.render(str(signalText[currentGreen]), True, (0, 0, 0), (255, 255, 255))
        screen.blit(signalTexts[(currentGreen+1)%4], signalTimerCoods[(currentGreen+1)%4])
        signalTexts[(currentGreen+3)%4] = font.render(str(signalText[currentGreen]), True, (0, 0, 0), (255, 255, 255))
        screen.blit(signalTexts[(currentGreen+3)%4], signalTimerCoods[(currentGreen+3)%4])
            # display the vehicles
    for vehicle in simulation:
            screen.blit(vehicle.image, [vehicle.x, vehicle.y])
            vehicle.move()
    pygame.display.update()