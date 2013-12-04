
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

def connectionFailed(f):
    print "Connection Failed:", f
    reactor.stop()

def set_globals():
    global username, machine_name, client_full_path
    username, hashedpassword = user_account_library.login()
    machine_name = machine_library.get_machine_name()
    print "Machine Name: " + str(machine_name)
    client_full_path = db_calls.get_client_folder_path(username, machine_name)
    if not client_full_path:
        print "No folder path found, please install first"
        exit()
    client_full_path = os.path.abspath(client_full_path)
    print "Client Folder Path: " + str(client_full_path)

class OneDirEventHandler(FileSystemEventHandler):
    def __init__(self, ftpClient, client_folder, server_folder, flag):
        FileSystemEventHandler.__init__(self)
        self.ftpClient = ftpClient
        self.client_folder = client_folder
        self.server_folder = server_folder
        self.flag = flag

    def on_created(self, event):
        if self.flag.is_set() or event.src_path == None:
            return
        if not event.is_directory:
            # Commenting this because it causes double-uploads
            pass
        else:
            path = event.src_path[event.src_path.find(self.client_folder) + len(self.client_folder) + 1:]
            reactor.callFromThread(makeDirectory, self.ftpClient, path)
            pass

    def on_deleted(self, event):
        if self.flag.is_set() or event.src_path == None:
            return
        if not event.is_directory:
            path = event.src_path[event.src_path.find(self.client_folder) + len(self.client_folder) + 1:]
            reactor.callFromThread(deleteFile, self.ftpClient, path)
        else:
            path = event.src_path[event.src_path.find(self.client_folder) + len(self.client_folder) + 1:]
            reactor.callFromThread(removeDirectory, self.ftpClient, path)
            pass

    def on_modified(self, event):
        if self.flag.is_set() or event.src_path == None:
            return
        if not event.is_directory:
            path = event.src_path[event.src_path.find(self.client_folder) + len(self.client_folder) + 1:]
            reactor.callFromThread(storeFile, self.ftpClient, path)
        else:
            pass

    def on_moved(self, event):
        if self.flag.is_set() or event.src_path == None or event.dest_path == None:
            return
        if not event.is_directory:
            path1 = event.src_path[event.src_path.find(self.client_folder) + len(self.client_folder) + 1:]
            path2 = event.dest_path[event.dest_path.find(self.client_folder) + len(self.client_folder) + 1:]
            reactor.callFromThread(renameFile, self.ftpClient, path1, path2)
        else:
            path1 = event.src_path[event.src_path.find(self.client_folder) + len(self.client_folder) + 1:]
            path2 = event.dest_path[event.dest_path.find(self.client_folder) + len(self.client_folder) + 1:]
            reactor.callFromThread(renameFile, self.ftpClient, path1, path2)
            pass

def connectionMade(ftpClient):
    getDirectory(ftpClient)
    makeDirectory(ftpClient, username)
    changeDirectory(ftpClient, username)
    flag = threading.Event()
    onedirEvents = OneDirEventHandler(ftpClient, client_full_path, username, flag)
    onedirObserver = Observer()
    direc = client_full_path
    onedirObserver.schedule(onedirEvents, path=direc, recursive=True)
    onedirObserver.start()

    LoopRC = LoopingCall(getChanges, ftpClient, flag)
    LoopRC.start(20)

def storeFile(ftpClient, filename):
    global file_to_store
    file_to_store = filename

    d1,d2 = ftpClient.storeFile(filename)
    d1.addCallback(cbStore)
    d2.addCallback(cbFinish)
    d2.addErrback(cbDir)

def cbStore(sender):
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
    d.addCallback(cbFinish)

def makeDirectory(ftpClient, path):
    db_calls.update_cache(username, machine_name, path, "AddedDirectory")
    d = ftpClient.makeDirectory(path)
    d.addCallback(cbFinish)
    d.addErrback(cbErrback)

def removeDirectory(ftpClient, path):
    db_calls.update_cache(username, machine_name, path, "RemovedDirectory")
    d = ftpClient.removeDirectory(path)
    d.addCallback(cbFinish)
    d.addErrback(cbErrback)

class FileWriterProtocol(Protocol):
    def __init__(self, filename):
        self.file = open(filename, 'w')

    def dataReceived(self, data):
        self.file.write(data)
        self.file.close()

def getFile(ftpClient, path):
    protocol = FileWriterProtocol(client_full_path + '/' + path)
    d = ftpClient.retrieveFile(path, protocol)
    d.addCallbacks(cbFinish)
    d.addErrback(cbErrback)

def renameFile(ftpClient, oldPath, newPath):
    db_calls.update_cache(username, machine_name, oldPath, "Renamed", newPath)
    d = ftpClient.rename(oldPath, newPath)
    d.addCallback(cbFinish)
    d.addErrback(cbErrback)

def deleteFile(ftpClient, path):
    db_calls.update_cache(username, machine_name, path, "Removed")
    ftpClient.removeFile(path).addCallbacks(cbFinish).addErrback(cbErrback)

def cbErrback(sender):
    #print sender
    return

def cbFinish(sender):
    return

def getChanges(ftpClient, flag):
    changes = db_calls.get_updates(username, machine_name)
    retVal = False
    for row in changes:
        flag.set()
        filename = row[0]
        if row[1] == "Removed":
            try:
                os.remove(client_full_path + '/' + row[0])
            except:
                pass
            retVal = True
        elif row[1] == "Added":
            reactor.callFromThread(getFile, ftpClient, filename)
            retVal = True
        elif row[1] == "Renamed":
            try:
                os.rename(client_full_path + '/' + row[0], client_full_path + '/' + row[2])
            except:
                pass
        elif row[1] == "AddedDirectory":
            try:
                os.mkdir(client_full_path + '/' + row[0])
            except:
                pass
        elif row[1] == "RemovedDirectory":
            try:
                os.rmdir(client_full_path + '/' + row[0])
            except:
                pass
    if retVal:
        db_calls.clear_cache(username, machine_name)
    time.sleep(1)
    flag.clear()
    return retVal

class Sauron(Daemon):
    def __init__(self, file):
        Daemon.__init__(self, file, sys.stdin, sys.stdout, sys.stderr)

    def run(self):
        FTPClient.debug = 1
        creator = ClientCreator(reactor, FTPClient, 'anonymous',
                                'twisted@', 1)
        #ec2
        #creator.connectTCP('54.201.56.235', 21).addCallback(connectionMade).addErrback(connectionFailed)

        #matt
        creator.connectTCP('172.25.203.215', 21).addCallback(connectionMade).addErrback(connectionFailed)

        #local
        #creator.connectTCP('localhost', 21).addCallback(connectionMade).addErrback(connectionFailed)
        reactor.run()

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
        print "usage: %s start|stop" % sys.argv[0]

