#!/usr/bin/python

import socket
import thread
import threading
import asyncore
import platform
import sys
from bluetooth import *
import time
import usb.core
import usb.util

# search for the SampleServer service
uuid = "94f39d29-7d6d-437d-973b-fba39e49d4ee"

class ServerThread(threading.Thread):
    def __init__(self, listenPort):
        threading.Thread.__init__(self)
        self.port = listenPort
        self.socket=socket.socket()
        host = socket.gethostname() # Get local machine name
        self.socket.bind((host, listenPort))        # Bind to the port
        self.socket.listen(1)
        print "Server> Listening on %s..." % (self.port)
        
    def run(self):
        while (1):
            c, addr = self.socket.accept()     # Establish connection with client.
            print 'Server> Got connection from', addr
            c.send('Thank you for connecting')
            c.close()                # Close the connection
            print 'Server> Closed connection'

class ClientThread(threading.Thread):
    def __init__(self, sendPort):
        threading.Thread.__init__(self)
        self.port = sendPort
        self.socket = socket.socket()         # Create a socket object
        self.host = socket.gethostname() # Get local machine name
    def run(self):
        while (1):
            try:
                self.socket.connect((self.host, self.port))
                print "Client> Connecting to %s on %s..." % (self.host,self.port)
                print "Client Recv> %s" % (self.socket.recv(1024))
                self.socket.close                     # Close the socket when done
                print 'Server> Closed connection'
            except socket.timeout:
    #            pass
                time.sleep(5);

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

def connectToClient( host, port ):
    theHost = ( host, port )
    try:
        rawsocket.connect( theHost)
    except Exception, e:
        try:
            errno, errtxt = e
            print "Errno %d errtxt %s" % (errno,errtxt)
        except ValueError:
            print "Cannot connect to " + host + " on port: " + str(port)
        else:
            if errno == 107:
                print "Success connecting to " + host + " on UDP port: " + str(port)
            else:
                if errno == 56:
                    print "Already connected"
                else:
                    print "Cannot connect to " + host + " on port: " + str(port)
                    print e


#
# Async Core
#
class asyncloc( asyncore.dispatcher ):
    def __init__(self, port):
        asyncore.dispatcher.__init__(self)
        self.create_socket( socket.AF_INET, socket.SOCK_STREAM)
        self.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.bind(('', port))
        self.listen(backlog)
    def handle_accept(self):
        client,addr = self.accept()
        print 'Connection from ',addr
        return asyncLocHandler( client )

class asyncLocHandler(asyncore.dispatcher):
    def __init__(self, sock=None):
        asyncore.dispatcher.__init__(self, sock)
        self.is_writable = False
        self.loggedInitialPoint = False
        self.client = sock
        self.TripStartDate = ''
        
 
    def handle_read(self):
        data = self.client.recv( bufsize )
        if data == '':
            print "Lost Connection"
            print "Closing connection to this client"
            self.close()
        else:
            print "Read '%s'" % (data)
#            reader = data.split( "," )
#            print "Don't know what to do with %s '%s'" % (reader[0], data)
            connectToClient( 'localhost', sendport )
            rawsocket.send( "This ia test write")    
            
            if redirect:
                fsock.flush()
    def readable(self):
        return True;
    def writable(self):
        return self.is_writable
    def handle_write(self):
        pass
    def handle_connect(self):
        pass
    def handle_close(self):
        print "Closed connection to %s" % addr
        self.close()
    def handle_error(self):
        print "Handling Error... ", sys.exc_info()
        self.close()

#
# Main
#




def main():
    hostnamestring = platform.node()
    print "Running on %s" % hostnamestring
    print "Listening on %s Sending on %s" % (sys.argv[1],sys.argv[2])

    listenport = int(sys.argv[1])
    sendport = int(sys.argv[2])

    print 'Starting Server'
    serverThread = ServerThread(listenport)
    serverThread.start()
    
    time.sleep(5)
    print 'Starting Client'
    clientThread = ClientThread(listenport)
    clientThread.start()

    try:
        print 'press Ctrl-C to stop'
    except KeyboardInterrupt:
        print 'Exiting, please wait...'
    
if __name__ == '__main__':
    main()
