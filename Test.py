from bluetooth import *
import threading, time
import usb.core
import usb.util
import sys


def FindUsbDevices():
    devices = usb.core.find(find_all=True)
 #   print "Number of USB devices detected: {}".format(len(devices))
    return devices

class SeatSendThread(threading.Thread):
    def __init__(self, infile, outfile):
        threading.Thread.__init__(self)
        print 'Starting Seat Thread'
    def run(self):
        service_matches = find_service( uuid = uuid, address = addr )
        if len(service_matches) == 0:
            print "couldn't find the SampleServer service =("
            sys.exit(0)
        first_match = service_matches[0]
        port = first_match["port"]
        name = first_match["name"]
        host = first_match["host"]
        print "connecting to \"%s\" on %s port %s" % (name, host, port)

        # Create the client socket
        sock=BluetoothSocket( RFCOMM )
        sock.connect((host, port))
        print "connected.  type stuff"
        while True:
            data = raw_input()
            if len(data) == 0: break
            sock.send(data)       
        sock.close()

#        while (1):
#            print 'AsyncTest run called'
#            time.sleep(1);

class AsyncTest(threading.Thread):
    def __init__(self, infile, outfile):
        threading.Thread.__init__(self)
        print 'AsyncTest init called'
    def run(self):
        while (1):
            print 'AsyncTest run called'
            time.sleep(1);


#determine which device I am, the seat or the car
print 'Determine device type'
usbDevices = FindUsbDevices()
print "Number of USB devices detected: {}".format(len(usbDevices))



print 'Establish bluetooth socket'
receiveThread = ReceiveThread()
receiveThread.start()






#background = AsyncTest('mydata.txt', 'myarchive.zip')
#background.start()
#print 'The main program continues to run in foreground.'
#background2 = AsyncTest('mydata.txt', 'myarchive.zip')
#background2.start()

receiveThread.join()    # Wait for the background task to finish
print 'Main program waited until background was done.'