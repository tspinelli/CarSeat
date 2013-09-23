#!/usr/bin/python

# Create sensor thread

# Create listen thread (to receive car status information)
from Shared import *
from time import strftime
from Phidgets.PhidgetException import *
from Phidgets.Events.Events import *
from Phidgets.Devices.InterfaceKit import *
import socket
import thread
import threading
import sys
from bluetooth import *
import time
#import usb.core
#import usb.util



motionDetected = False
babyDetected = False
temperatureF = 0

class ServerThread(threading.Thread):
    def __init__(self, listenPort):
        threading.Thread.__init__(self)
        self.port = listenPort
        self.socket=socket.socket()
        self.socket.settimeout(5)
        host = socket.gethostname() # Get local machine name
        self.socket.bind((host, listenPort))        # Bind to the port
        self.socket.listen(1)
        print "Server> Listening on %s..." % (self.port)
    def run(self):
        self.running = True
        while (self.running == True):
            try:
#                print 'Server> Waiting for connection'
                c, addr = self.socket.accept()     # Establish connection with client.
                if c:
                    print 'Server> Got connection from', addr
        #           c.send('Thank you for connecting')
                    while 1:
                        data = c.recv(1024)
                        if not data:
                            break
                        print 'Received > %s' % (data)
                    c.close()
            except socket.timeout:
                pass
    def stop(self):
        self.running = False

class ClientThread(threading.Thread):
    def __init__(self, sendPort):
        threading.Thread.__init__(self)
        self.port = sendPort
        self.socket = None
    def send(self,msg):
        notSent = True
        if (self.socket == None):
            print 'Not currently connected'
            return
        while (notSent == True):
            try:
                sent = self.socket.send(msg)
                if sent == 0:
                    print 'not sent'
                    raise socket.error
                else:
                    print 'notsent = false; sent = %d' % (sent)
                    notSent = False
            except socket.error as e:
                print "Error: %d (No longer connected)" % (e.errno)
                self.socket.close()
                self.socket = None
                self.reconnect = True
                time.sleep(3)
#                break
 #               self.socket = socket.socket()
 #               self.host = socket.gethostname()
 #               self.socket.connect((self.host, self.port))
    def run(self):
        self.running = True
        while (self.running == True):
            try:
                self.socket = socket.socket()
                self.host = socket.gethostname()
                self.socket.connect((self.host, self.port))
                self.reconnect = False
                while (self.running == True and self.reconnect == False):
                    pass
            except socket.error as msg:
                self.socket.close()
                self.socket = None
                time.sleep(5)
    def stop(self):
        if (self.socket != None):
            try:
                self.socket.shutdown(socket.SHUT_RDWR)
                self.socket.close()
            except socket.error as e:
                pass
        self.running = False

class SensorThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        # Create
        try:
            print "Setting up sensor interface"
            self.device = InterfaceKit()	
        except RuntimeError as e:
            print("Runtime Error: %s" % e.message)
         
        # Open
        try:
            # Hook our function above into the device object
            self.device.setOnSensorChangeHandler(sensorChanged)
            self.device.openPhidget()
        except PhidgetException as e:
            print ("Phidget Exception %i: %s" % (e.code, e.detail))		
            exit(1)

    def run(self):
        self.running = True
        print "Sensors> Waiting for attach"
        try:
            self.device.setOnAttachHandler(AttachHandler)
        except PhidgetException as e:
            print "Phidget Exception %i" % (e.code)		
        pass
    
    def stop(self):
        self.running = False
        self.device.closePhidget()




def AttachHandler(event):
    attachedDevice = event.device
    serialNumber = attachedDevice.getSerialNum()
    deviceName = attachedDevice.getDeviceName()
    print("Sensor Device Attached:" + str(deviceName) + ", Serial Number: " + str(serialNumber))

def sensorChanged(e):
    global motionDetected
    global babyDetected
    global temperatureF
    notify = False

    if (e.index == 0):
        if (e.value <= 400 or e.value >= 600):
            if (motionDetected == False):
                print "(%s) Motion sensor: motion detected" % (strftime("%Y-%m-%d %H:%M:%S"))
                motionDetected = True
        else:
            if (motionDetected == True):
                print "(%s) Motion sensor: no motion detected" % (strftime("%Y-%m-%d %H:%M:%S"))
                motionDetected = False
    if (e.index == 4):
        weight = e.value/14.0 - 50/7
        print "(%s) Weight: %.2f" % (strftime("%Y-%m-%d %H:%M:%S"),weight)
        if (weight >= BABY_WEIGHT):
            if (babyDetected == False):
                print "(%s) Baby Detected" % (strftime("%Y-%m-%d %H:%M:%S"))
                notify = True
            babyDetected = True
        else:
            if (babyDetected == True):
                print "(%s) Baby No Longer Detected" % (strftime("%Y-%m-%d %H:%M:%S"))
                notify = True
            babyDetected = False
    if (e.index == 7):
        temperature = (e.value * 0.2222) - 61.111
        temperatureF = (temperature*1.8)+32
        print "(%s) Temperature Sensor %i: %.2f Celcius   %.2f Fahrenheit" % (strftime("%Y-%m-%d %H:%M:%S"),e.index, temperature, temperatureF)
        if (temperatureF >= TEMP_THRESHOLD_1):
            notify = True

    jsonString = "{'BABY_PRESENT':'%s','TEMP':'%.2f'}" % (babyDetected,temperatureF)
    clientThread.send(jsonString)

# start listening thread
serverThread = ServerThread(SEAT_LISTEN_PORT)
serverThread.start()

# start sensor thread
sensorThread = SensorThread()
sensorThread.start()

#start client thread
clientThread = ClientThread(CAR_LISTEN_PORT)
clientThread.start()

# Main thread

try:
    print 'press Ctrl-C to stop'
    while True:
        nb = raw_input('Enter a string to send >')
        clientThread.send(nb)
        pass
except KeyboardInterrupt:
    print 'Stopping threads...'
    serverThread.stop()
    sensorThread.stop()
    clientThread.stop()
