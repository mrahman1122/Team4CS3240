
# Copyright (c) Twisted Matrix Laboratories.
# See LICENSE for details.


"""
An example of using the FTP client
"""

# Twisted imports
from twisted.protocols.ftp import FTPClient, FTPFileListProtocol
from twisted.protocols import ftp
from twisted.internet.protocol import Protocol, ClientCreator
from twisted.python import usage
from twisted.internet import reactor
from twisted.protocols.basic import FileSender
from Folder_Monitor import *
import time

# Standard library imports
import string
import sys
try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO


class BufferingProtocol(Protocol):
    """Simple utility class that holds all data written to it in a buffer."""
    def __init__(self):
        self.buffer = StringIO()

    def dataReceived(self, data):
        self.buffer.write(data)

# Define some callbacks

def success(response):
    print 'Success!  Got response:'
    print '---'
    if response is None:
        print None
    else:
        print string.join(response, '\n')
    print '---'


def fail(error):
    print 'Failed.  Error was:'
    print error

def showFiles(result, fileListProtocol):
    print 'Processed file listing:'
    for file in fileListProtocol.files:
        print '    %s: %d bytes, %s' \
              % (file['filename'], file['size'], file['date'])
    print 'Total: %d files' % (len(fileListProtocol.files))

def showBuffer(result, bufferProtocol):
    print 'Got data:'
    print bufferProtocol.buffer.getvalue()


class Options(usage.Options):
    optParameters = [['host', 'h', 'localhost'],
                     ['port', 'p', 21],
                     ['username', 'alex', 'anonymous'],
                     ['password', 'test', 'twisted@'],
                     ['passive', None, 0],
                     ['debug', 'd', 1],
                    ]

def run():
    # Get config
    config = Options()
    config.parseOptions()
    config.opts['port'] = int(config.opts['port'])
    config.opts['passive'] = int(config.opts['passive'])
    config.opts['debug'] = int(config.opts['debug'])
    
    # Create the client
    FTPClient.debug = config.opts['debug']
    creator = ClientCreator(reactor, FTPClient, config.opts['username'],
                            config.opts['password'], passive=config.opts['passive'])
    creator.connectTCP(config.opts['host'], config.opts['port']).addCallback(connectionMade).addErrback(connectionFailed)
    reactor.run()

def connectionFailed(f):
    print "Connection Failed:", f
    reactor.stop()

def connectionMade(ftpClient):
    # Get the current working directory
    print "CONNECTED"
    #ftpClient.pwd().addCallbacks(cbFinish)
    getDirectory(ftpClient)
    path = "../Team4CS3240/Client"
    fol_mon = Folder_Monitor(path)
    #checks for changes in tandem with the client/folder monitor, waits 5 seconds until next check
    while (1):
        runClient(ftpClient, fol_mon)
        time.sleep(5)
        #ftpClient.pwd().addCallbacks(success, fail)
    ##Previous test methods, not reached from while loop
    filename = "FtpUpload.txt"
    storeFile(ftpClient, filename)
    renameFile(ftpClient, filename, "foo.txt")
    getFile(ftpClient, filename)
    getDirectory(ftpClient)

    # Get a detailed listing of the current directory
   # fileList = FTPFileListProtocol()
   #d = ftpClient.list('.', fileList)
   #d.addCallbacks(showFiles, fail, callbackArgs=(fileList,))

    # Change to the parent directory
    #ftpClient.cdup().addCallbacks(success, fail)


##Prompts the ftpClient to Store to Server
#@ftpClient == the ftp client instance
#@ filename == path of file to be stored
##@Lenny --> If you want to add database logic when calling store, put it here before the ftpClient call to store
def storeFile(ftpClient, filename):
    print "Storing:"
    print filename
    d1, d2 = ftpClient.storeFile(filename)
    d1.addCallback(cbStore)
    d2.addCallback(cbFinish)
##Closes the deferred object
def cbStore(sender):
    print "SUCCESSFULLY STORED"
    sender.transport.write("This file was empty, and then we wrote to it")
    sender.finish()

def getDirectory(ftpClient):
    d = ftpClient.getDirectory()
    d.addCallback(cbDir)
def cbDir(result):
    print result


def changeDirectory(ftpClient, path):
    d = ftpClient.cwd(path)
    d.addCallback(cbCWD)

def cbCWD(res):
    print res


## prompts the ftpClient to get a file from server
##@ftpClient -- the ftp client instance
#@path -- path to the file on server
## returns a Deferred object -- becomes the file if file exists
#need callback for an incorrect file
##@Lenny --> If you want to add database logic when calling get, put it here before the ftpClient call to get
def getFile(ftpClient, path):
    print "Getting File: "
    print path
    protocol = Protocol()
    ftpClient.retrieveFile(path, protocol).addCallbacks(cbGET)

def cbGET(sender):
    print sender


##Returns a deferred object that indicates success/failure
##@Lenny --> If you want to add database logic when calling rename, put it here before the ftpClient call to rename
def renameFile(ftpClient, oldPath, newPath):
    print "Renaming"
    print oldPath
    print "to "
    print newPath
    d = ftpClient.rename(oldPath, newPath)

##Returns a deferred object that indicates success/failure
##@Lenny --> If you want to add database logic when calling delete, put it here before the ftpClient call to delete
def deleteFile(ftpClient, path):
    print "Deleting " + path
    ftpClient.removeFile(path).addCallbacks(cbFinish)

##Closes the deferred object
def cbFinish(sender):
    print sender

#The main method where we monitor everything after a connection between client/server is established
#Uses utility functions/protocols of store, get, rename, delete
#Changing directories is implemented though we have yet to successfully create multiple directories.
def runClient(ftpClient, fol_mon):
    'Check for Changes'
    changes = fol_mon.check_changes()
    
    'Something else asserts a change is made'
    'Handle Event'

# this only runs if the module was *not* imported
if __name__ == '__main__':
    run()

