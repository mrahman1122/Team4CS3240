
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
import db_calls
import user_account_library
import machine_library
import time, os

# Standard library imports
import string
import threading
import sys
try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

username = ""
machine_name = ""
client_full_path = ""

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

def set_globals():
    global username, machine_name, client_full_path
    username, hashedpassword = user_account_library.login()
    machine_name = machine_library.get_machine_name()
    print "Machine Name: " + machine_name
    client_full_path = db_calls.get_client_folder_path(username, machine_name)
    if not client_full_path:
        print "No folder path found, please install first"
        exit()
    print "Client Folder Path: " + client_full_path


#main function for running stuff
def connectionMade(ftpClient):
    # Get the current working directory
    print "CONNECTED"

    set_globals()
    #ftpClient.pwd().addCallbacks(cbFinish)

    path = client_full_path
    print "Path: " + path

    getDirectory(ftpClient)

    print "Got FTP Client"
    fol_mon = Folder_Monitor(path)

    #checks for changes in tandem with the client/folder monitor, waits 5 seconds until next check
    while (1):
        t = threading.Thread(target=clientTask, args = (ftpClient, fol_mon))
        t.start()
        time.sleep(5)

        #ftpClient.pwd().addCallbacks(success, fail)
    ##Previous test methods, not reached from while loop

    # Get a detailed listing of the current directory
   # fileList = FTPFileListProtocol()
   #d = ftpClient.list('.', fileList)
   #d.addCallbacks(showFiles, fail, callbackArgs=(fileList,))

    # Change to the parent directory
    #ftpClient.cdup().addCallbacks(success, fail)

def clientTask(ftpClient, fol_mon):
    if getChanges(ftpClient, fol_mon):
        fol_mon.check_changes()

    #checks the client for changes and pushes them
    runClient(ftpClient, fol_mon)
    return

##Prompts the ftpClient to Store to Server
#@ftpClient == the ftp client instance
#@ filename == path of file to be stored
##@Lenny --> If you want to add database logic when calling store, put it here before the ftpClient call to store
def storeFile(ftpClient, filename):
    db_calls.update_cache(username, machine_name, filename, "Added")
    full_path = client_full_path + filename
    full_path = os.path.abspath(full_path)
    print "Storing:"
    print full_path
    d1,d2 = ftpClient.storeFile(full_path)
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
    db_calls.update_cache(username, machine_name, oldPath, "Removed")
    db_calls.update_cache(username, machine_name, newPath, "Added")
    d = ftpClient.rename(oldPath, newPath)

##Returns a deferred object that indicates success/failure
##@Lenny --> If you want to add database logic when calling delete, put it here before the ftpClient call to delete
def deleteFile(ftpClient, path):
    print "Deleting " + path
    db_calls.update_cache(username, machine_name, path, "Removed")
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
    for row in changes:
        if row[2] == "Removed":
            deleteFile(ftpClient, row[0])

        if row[2] == "Added":
            storeFile(ftpClient, row[0])

        if row[2] == "Updated":
            print ftpClient
            print row[0]
            deleteFile(ftpClient, row[0])
            storeFile(ftpClient, row[0])

        if row[2] == "Renamed":
            renameFile(ftpClient, row[0], row[3])


def getChanges(ftpClient, fol_mon):
    changes = db_calls.get_updates(username, machine_name) #row[0] is filename, row[1] is change
    retVal = False
    for row in changes:
        filename = row[0]
        filepath = client_full_path + filename
        if row[1] == "Removed":
            os.remove(filepath)
            retVal = True
        elif row[1] == "Added":
            getFile(ftpClient, filename)
            retVal = True
    return retVal

# this only runs if the module was *not* imported
if __name__ == '__main__':
    run()

