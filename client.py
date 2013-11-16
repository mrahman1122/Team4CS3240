
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
    #d = ftpClient.getDirectory()

    #ftpClient.pwd().addCallbacks(success, fail)
    filename = "FtpUpload.txt"
    storeFile(ftpClient, filename)
    renameFile(ftpClient, filename, "foo.txt")
    getFile(ftpClient, "foo.txt")
   # deleteFile(ftpClient, "foo.txt")


    # Get a detailed listing of the current directory
   # fileList = FTPFileListProtocol()
   #d = ftpClient.list('.', fileList)
   #d.addCallbacks(showFiles, fail, callbackArgs=(fileList,))

    # Change to the parent directory
    #ftpClient.cdup().addCallbacks(success, fail)


##Prompts the ftpClient to Store to Server
#@ftpClient == the ftp client instance
#@ filename == path of file to be stored
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

## prompts the ftpClient to get a file from server
##@ftpClient -- the ftp client instance
#@path -- path to the file on server
## returns a Deferred object -- becomes the file if file exists
#need callback for an incorrect file
def getFile(ftpClient, path):
    print "Getting File: "
    print path
    protocol = Protocol()
    ftpClient.retrieveFile(path, protocol).addCallbacks(cbGET)

def cbGET(sender):
    print sender


##Returns a deferred object that indicates success/failure
def renameFile(ftpClient, oldPath, newPath):
    print "Renaming"
    print oldPath
    print "to "
    print newPath
    d = ftpClient.rename(oldPath, newPath)

##Returns a deferred object that indicates success/failure
def deleteFile(ftpClient, path):
    print "Deleting " + path
    ftpClient.removeFile(path).addCallbacks(cbFinish)



##Closes the deferred object
def cbFinish(sender):
    print sender


def fileTransferFail(failure):
    print "Transfer failed"
    failure.printTraceback()
    reactor.stop()


# this only runs if the module was *not* imported
if __name__ == '__main__':
    run()

