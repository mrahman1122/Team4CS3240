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

def opsCall(obj):
    print "Processing", obj.fObj.name
    return "Completed"

## EITHER WE USE THE PRE-MADE FTP SHELL, WHICH COULD WORK, OR:
## MAKE AN FTP SHELL TO HANDLE THE REQUESTS FOR FILES
## METHODS NEEDED: CREATE, RENAME, UPDATE, DELETE for files
## METHODS NEEDED: access, list, changeDir, makeDir

class MyFTPRealm(FTPRealm):

    def __init__( self, anonymousRoot, userHome="/home", callback=None ):
        FTPRealm.__init__( self, anonymousRoot, userHome=userHome )
        self.callback = callback

    def requestAvatar(self, avatarId, mind, *interfaces):
        print "TRYING TO LOG IN"
        for iface in interfaces:
            if iface is IFTPShell:

                if avatarId is checkers.ANONYMOUS:
                    avatar = FTPShell(self.anonymousRoot)

                else:
                    avatar = FTPShell(self.getHomeDirectory(avatarId))

                return (IFTPShell, avatar,
                        getattr(avatar, 'logout', lambda: None))

        raise NotImplementedError("Only IFTPShell interface is supported by this realm")


if __name__ == "__main__":

    p = Portal(MyFTPRealm('./'),[AllowAnonymousAccess(), FilePasswordDB("pass1.dat")])
    #p = Portal(MyFTPRealm('/no_anon_access/', userHome="/tmp/", callback=opsCall),[FilePasswordDB("pass.dat"), ])
    f = ftp.FTPFactory(p)
    f.welcomeMessage = "CS3240 Team 4 Project"

    log.startLogging(sys.stdout)

    reactor.listenTCP(21, f)
    reactor.run()
