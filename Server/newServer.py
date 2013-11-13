__author__ = 'masudurrahman'

import sys
from twisted.protocols import ftp
from twisted.protocols.ftp import FTPFactory, FTPAnonymousShell, FTPRealm, FTP, FTPShell, IFTPShell
from twisted.cred.portal import Portal
from twisted.cred import checkers
from twisted.cred.checkers import AllowAnonymousAccess, FilePasswordDB
from twisted.internet import reactor
from twisted.python import log
from twisted.internet.defer import succeed, failure
from twisted.cred.checkers import InMemoryUsernamePasswordDatabaseDontUse

def opsCall(obj):
    print "Processing", obj.fObj.name
    return "Completed"

class MyFTPRealm(FTPRealm):

    def __init__(self, anonymousRoot):
        self.anonymousRoot = filepath.FilePath(anonymousRoot)

    def requestAvatar(self, avatarId, mind, *interfaces):
        for iface in interfaces:

            if iface is IFTPShell:

                if avatarId is checkers.ANONYMOUS:
                    avatar = FTPAnonymousShell(self.anonymousRoot)

                else:
                    avatar = FTPShell(filepath.FilePath("/home/") + avatarId)

                return (IFTPShell, avatar,
                        getattr(avatar, 'logout', lambda: None))

        raise NotImplementedError("Only IFTPShell interface is supported by this realm")

if __name__ == "__main__":
    
    # Try#1
    # p = Portal(MyFTPRealm('./'),[AllowAnonymousAccess(), FilePasswordDB("pass.dat")])
    
    # Try#2
    # p = Portal(MyFTPRealm('/no_anon_access/', userHome="/tmp/", callback=opsCall),[FilePasswordDB("pass.dat", ":", 0, 0, True, None, False)])
    
    # Try#3
    # checker = checkers.InMemoryUsernamePasswordDatabaseDontUse()
    # check.addUser("guest", "password")
    # realm = MyFTPRealm()
    # p = portal.Portal(realm, [checker])

    # f = ftp.FTPFactory(p)
    # f.welcomeMessage = "CS3240 Team 4 Project"

    # log.startLogging(sys.stdout)

    # reactor.listenTCP(21, f)
    # reactor.run()

    PASSWORD = ''
 
    users = {
        os.environ['USER']: PASSWORD
    }
     
    p = Portal(FTPRealm('./', userHome='/Users'), 
        (   AllowAnonymousAccess(),
            InMemoryUsernamePasswordDatabaseDontUse(**users),)
        )
     
    f = FTPFactory(p)
     
    reactor.listenTCP(21, f)
    reactor.run()
