#!/usr/bin/python

from Shared import *
import serial
import socket
import thread
import threading
import json
import select

class ServerThread(threading.Thread):
    def __init__(self, listenPort):
        threading.Thread.__init__(self)
        self.port = listenPort
        self.socket=socket.socket()
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
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
                        ready = select.select([c], [], [], 5)
                        if ready[0]:
                            data = c.recv(4096)
                            if (data[0]=='{'):
                                #process JSON
#                                print 'JSON: %s' % (data)
                                jsonData = json.loads(data)
                                for k, v in jsonData.iteritems():
                                    print 'Received Key:%s  Value:%s' % (k,v)
#                            break
                            else:
                                print 'Received> %s' % (data)
#                        else:
#                            print 'no data'
                        data = None
#                        json_object = json.load(data)
#                        for key, value in json_object.iteritems():
#                            print key, value
#                   print 'closing connection'
#                   c.close()
            except Exception as e:
                pass
    def stop(self):
        if (self.socket != None):
#            try:
                print 'stopping server'
                self.socket.shutdown(socket.SHUT_RDWR)
                self.socket.close()
#            except socket.error as e:
#                pass
        self.running = False


class SerialThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.ser = None
#        self.ser = serial.Serial(0,timeout = 2,baudrate=38400)  # open first serial port
    def run(self):
        self.running = True
        while (self.running == True):
            try:
                self.ser = serial.Serial('/dev/ttyUSB0',timeout = 2,baudrate=38400)  # open first serial port
                print "Listening on %s" % (self.ser.portstr)       # check which port was really used
                while (self.running == True):
                    try:
                        s = self.ser.read(100)        # read up to ten bytes (timeout)
                        if s:
                            print s
                    except serial.SerialException as e:
                        print "Serial device disconnected?"
                        self.ser = None
                        break
            except serial.SerialException as e:
                self.ser = None
                pass
    def send(self,msg):
        if (self.ser == None):
            return
        notSent = True
        while (notSent == True):
            try:
                self.ser.write(msg)
                notSent = False
            except serial.SerialTimeoutException as e:
                print "Error: %d" % (e.string)
#                self.ser = serial.Serial('/dev/ttyUSB0',timeout = 2)  # open first serial port
    def stop(self):
        self.running = False   
        if (self.ser != None):
            self.ser.close()

# start listening thread
serverThread = ServerThread(CAR_LISTEN_PORT)
serverThread.start()

# start serial thread
serialThread = SerialThread()
serialThread.start()

# Main thread
try:
    print 'press Ctrl-C to stop'
    while True:
        nb = raw_input('>')
        serialThread.send(nb+'\r\n')
        pass
except KeyboardInterrupt:
    print 'Stopping threads...'
    serverThread.stop()
    serialThread.stop()