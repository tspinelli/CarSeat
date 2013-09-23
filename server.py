#!/usr/bin/python

import socket
import thread
import threading
import asyncore
import platform
import sys

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

hostnamestring = platform.node()

print "Running on %s" % hostnamestring
print "Listening on %s Sending on %s" % (sys.argv[1],sys.argv[2])

listenport = int(sys.argv[1])
sendport = int(sys.argv[2])

backlog = 5
bufsize = 1024
redirect = 0

rawsocket = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
#connectToClient( 'localhost', sendport )
 

a = asyncloc( listenport )
print "Listening..."

if listenport == 3106 :
    connectToClient( 'localhost', sendport )
    rawsocket.send( "This is the first write" )

if redirect: 
    fsock.flush()
asyncore.loop()

if redirect:
    fsock.close()

sys.exit()
