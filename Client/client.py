
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
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from twisted.internet.task import LoopingCall
import Tkinter
from daemon import Daemon

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
file_to_store = ""
file_to_get = ""

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

    #optParameters = [['host', 'h', '54.201.56.235'],
    #             ['port', 'p', 21],
    #             ['username', 'alex', 'anonymous'],
    #             ['password', 'test', 'twisted@'],
    #             ['passive', None, 1],
    #             ['debug', 'd', 1],
    #            ]

def run():
    FTPClient.debug = 1
    creator = ClientCreator(reactor, FTPClient, 'anonymous',
                            'twisted@', 0)

    creator.connectTCP('localhost', 21).addCallback(connectionMade).addErrback(connectionFailed)
    reactor.run()

    ## Get config
    #config = Options()
    #config.parseOptions()
    #config.opts['port'] = int(config.opts['port'])
    #config.opts['passive'] = int(config.opts['passive'])
    #config.opts['debug'] = int(config.opts['debug'])
    #
    ## Create the client
    #FTPClient.debug = config.opts['debug']
    #creator = ClientCreator(reactor, FTPClient, config.opts['username'],
    #                        config.opts['password'], passive=config.opts['passive'])
    #
    #creator.connectTCP(config.opts['host'], config.opts['port']).addCallback(connectionMade).addErrback(connectionFailed)
    #reactor.run()

def connectionFailed(f):
    print "Connection Failed:", f
    reactor.stop()

def set_globals():
    global username, machine_name, client_full_path
    username, hashedpassword = user_account_library.login()
    machine_name = machine_library.get_machine_name()
    print "Machine Name: " + str(machine_name)
    client_full_path = db_calls.get_client_folder_path(username, machine_name)
    client_full_path = os.path.abspath(client_full_path)
    if not client_full_path:
        print "No folder path found, please install first"
        exit()
    print "Client Folder Path: " + str(client_full_path)

class OneDirEventHandler(FileSystemEventHandler):
    def __init__(self, ftpClient, client_folder, server_folder, flag):
        FileSystemEventHandler.__init__(self)
        self.ftpClient = ftpClient
        self.client_folder = client_folder
        self.server_folder = server_folder
        self.flag = flag

    def on_created(self, event):
        if self.flag.is_set():
            return
        if not event.is_directory:
            # Commenting this because it causes double-uploads
            pass   # file_upload(event.src_path, self.user)
        else:
            path = event.src_path[event.src_path.find(self.client_folder) + len(self.client_folder) + 1:]
            #print 'watchdog creating folder: ' + path
            reactor.callFromThread(makeDirectory, self.ftpClient, path)
            # Do we need to handle directories?
            pass

    def on_deleted(self, event):
        if self.flag.is_set():
            return
        if not event.is_directory:
            path = event.src_path[event.src_path.find(self.client_folder) + len(self.client_folder) + 1:]
            #print 'watchdog deleted: ' + path
            reactor.callFromThread(deleteFile, self.ftpClient, path)
        else:
            path = event.src_path[event.src_path.find(self.client_folder) + len(self.client_folder) + 1:]
            #print 'watchdog deleting folder: ' + path
            reactor.callFromThread(removeDirectory, self.ftpClient, path)
            # Do we need to handle directories?
            pass

    def on_modified(self, event):
        if self.flag.is_set():
            return
        if not event.is_directory:
            path = event.src_path[event.src_path.find(self.client_folder) + len(self.client_folder) + 1:]
            #print 'watchdog modified: ' + path
            reactor.callFromThread(storeFile, self.ftpClient, path)
        else:
            path = event.src_path[event.src_path.find(self.client_folder) + len(self.client_folder) + 1:]
            #print 'watchdog modifying folder: ' + path
            # Do we need to handle directories?
            pass

    def on_moved(self, event):
        if self.flag.is_set():
            return
        if not event.is_directory:
            path1 = event.src_path[event.src_path.find(self.client_folder) + len(self.client_folder) + 1:]
            path2 = event.dest_path[event.dest_path.find(self.client_folder) + len(self.client_folder) + 1:]
            #print 'watchdog moved: ' + path1 + ' to ' + path2
            reactor.callFromThread(renameFile, self.ftpClient, path1, path2)
        else:
            path1 = event.src_path[event.src_path.find(self.client_folder) + len(self.client_folder) + 1:]
            path2 = event.dest_path[event.dest_path.find(self.client_folder) + len(self.client_folder) + 1:]
            #print 'watchdog moving folder: ' + path1 + ' to ' + path2
            # Do we need to handle directories?
            reactor.callFromThread(renameFile, self.ftpClient, path1, path2)
            pass

#main function for running stuff
def connectionMade(ftpClient):
    # Get the current working directory
    #print "CONNECTED"

    #set_globals()
    #ftpClient.pwd().addCallbacks(cbFinish)

    getDirectory(ftpClient)
    makeDirectory(ftpClient, username)
    changeDirectory(ftpClient, username)

    #print "Got FTP Client"
    #print client_full_path
    #fol_mon = Folder_Monitor(path)
    flag = threading.Event()
    onedirEvents = OneDirEventHandler(ftpClient, client_full_path, username, flag)
    onedirObserver = Observer()
    direc = client_full_path
    onedirObserver.schedule(onedirEvents, path=direc, recursive=True)
    onedirObserver.start()

    LoopRC = LoopingCall(getChanges, ftpClient, flag)
    LoopRC.start(20)

    #LoopRC = LoopingCall(runClient, ftpClient, fol_mon)

    #LoopRC.start(10)

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
    global file_to_store
    #db_calls.update_cache(username, machine_name, filename, "Added")
    #full_path = client_full_path + filename
    #full_path = os.path.abspath(full_path)
    #print "Storing:"
    #print full_path
    file_to_store = filename

    d1,d2 = ftpClient.storeFile(filename)
    d1.addCallback(cbStore)
    d2.addCallback(cbFinish)
    d2.addErrback(cbDir)

##Closes the deferred object
def cbStore(sender):
    #print "SUCCESSFULLY STORED: " + file_to_store
    fp = open(client_full_path + "/" + str(file_to_store), 'r')
    towrite = fp.read()
    sender.transport.write(towrite)
    fp.close()
    sender.finish()

def getDirectory(ftpClient):
    d = ftpClient.getDirectory()
    d.addCallback(cbDir)

def cbDir(result):
    return


def changeDirectory(ftpClient, path):
    d = ftpClient.cwd(path)
    d.addCallback(cbCWD)

def makeDirectory(ftpClient, path):
    db_calls.update_cache(username, machine_name, path, "AddedDirectory")
    d = ftpClient.makeDirectory(path)
    d.addCallback(cbMakeDir)
    d.addErrback(cbMakeDir)

def removeDirectory(ftpClient, path):
    db_calls.update_cache(username, machine_name, path, "RemovedDirectory")
    d = ftpClient.removeDirectory(path)
    d.addCallback(cbMakeDir)

def cbMakeDir(res):
    return

def cbCWD(res):
    return


class FileWriterProtocol(Protocol):
    def __init__(self, filename):
        self.file = open(filename, 'w')

    def dataReceived(self, data):
        self.file.write(data)
        self.file.close()


## prompts the ftpClient to get a file from server
##@ftpClient -- the ftp client instance
#@path -- path to the file on server
## returns a Deferred object -- becomes the file if file exists
#need callback for an incorrect file
##@Lenny --> If you want to add database logic when calling get, put it here before the ftpClient call to get
def getFile(ftpClient, path):
    #print "Getting File: "
    #print path
    protocol = FileWriterProtocol(client_full_path + '/' + path)
    d = ftpClient.retrieveFile(path, protocol)
    d.addCallbacks(cbGET)
    d.addErrback(ebGET)

def ebGET(receiver):
    return

def cbGET(receiver):
    return


##Returns a deferred object that indicates success/failure
##@Lenny --> If you want to add database logic when calling rename, put it here before the ftpClient call to rename
def renameFile(ftpClient, oldPath, newPath):
    #print "Renaming"
    #print oldPath
    #print "to "
    #print newPath
    db_calls.update_cache(username, machine_name, oldPath, "Renamed", newPath)
    d = ftpClient.rename(oldPath, newPath)
    d.addCallback(cbFinish)


##Returns a deferred object that indicates success/failure
##@Lenny --> If you want to add database logic when calling delete, put it here before the ftpClient call to delete
def deleteFile(ftpClient, path):
    #print "Deleting " + path
    db_calls.update_cache(username, machine_name, path, "Removed")
    ftpClient.removeFile(path).addCallbacks(cbFinish)

##Closes the deferred object
def cbFinish(sender):
    return

#The main method where we monitor everything after a connection between client/server is established
#Uses utility functions/protocols of store, get, rename, delete
#Changing directories is implemented though we have yet to successfully create multiple directories.
def runClient(ftpClient, fol_mon):
    'Check for Changes'
    if(getChanges(ftpClient)):
        fol_mon.check_changes
    changes = fol_mon.check_changes()
    for row in changes:
        row[0] = row[0][1:]
        if row[2] == "Removed":
            deleteFile(ftpClient, row[0])

        if row[2] == "Added":
            storeFile(ftpClient, row[0])

        if row[2] == "Updated":
            #print ftpClient
            #print row[0]
            deleteFile(ftpClient, row[0])
            storeFile(ftpClient, row[0])

        if row[2] == "Renamed":
            renameFile(ftpClient, row[0], row[3][1:])


def getChanges(ftpClient, flag):
    #print username, machine_name, client_full_path
    changes = db_calls.get_updates(username, machine_name) #row[0] is filename, row[1] is change
    retVal = False
    for row in changes:
        filename = row[0]
        if row[1] == "Removed":
            #print row
            flag.set()
            try:
                os.remove(client_full_path + '/' + row[0])
            except:
                pass
            retVal = True
        elif row[1] == "Added":
            #print row
            flag.set()
            reactor.callFromThread(getFile, ftpClient, filename)
            retVal = True
        elif row[1] == "Renamed":
            #print row
            flag.set()
            try:
                os.rename(client_full_path + '/' + row[0], client_full_path + '/' + row[2])
            except:
                pass
        elif row[1] == "AddedDirectory":
            #print row
            flag.set()
            try:
                os.mkdir(client_full_path + '/' + row[0])
            except:
                pass
        elif row[1] == "RemovedDirectory":
            #print row
            flag.set()
            try:
                os.rmdir(client_full_path + '/' + row[0])
            except:
                pass
    if retVal:
        db_calls.clear_cache(username, machine_name)
    time.sleep(3)
    flag.clear()
    return retVal

class Sauron(Daemon):
    def __init__(self, file):
        Daemon.__init__(self, file, sys.stdin, sys.stdout, sys.stderr)

    def run(self):
        # Create the client
        FTPClient.debug = 1
        creator = ClientCreator(reactor, FTPClient, 'anonymous',
                                'twisted@', 1)

        creator.connectTCP('54.201.56.235', 21).addCallback(connectionMade).addErrback(connectionFailed)
        reactor.run()

# this only runs if the module was *not* imported
if __name__ == '__main__':
    file = os.path.abspath('onedir.pid')
    if len(sys.argv) == 2:
        if 'start' == sys.argv[1]:
            daemon = Sauron(file)
            set_globals()
            daemon.start()
        elif 'stop' == sys.argv[1]:
            daemon = Sauron(file)
            daemon.stop()
        else:
            print "Unknown command"
            sys.exit(2)
        sys.exit(0)
    else:
        try:
            set_globals()
            run()
        except:
            exit(0)
        #print "usage: %s start|stop" % sys.argv[0]
        #sys.exit(2)

