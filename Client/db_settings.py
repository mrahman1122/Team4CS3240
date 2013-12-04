__author__ = 'zheng_000'

import hashlib

is_production = True

if is_production:
    db_server = "stardock.cs.virginia.edu"
    db_username = "cs4720zl8pj"
    db_password = "password"
    db_database = "cs4720zl8pj"
    db_usertable = "cs3240Users"
    db_machinestable = "cs3240Machines"
    db_cachetable = "cs3240Cache"
    db_logtable = "cs3240Log"
else:
    db_server = "localhost"
    db_username = "zl8pj"
    db_password = "hjlujafdsy"
    db_database = "cs3240"
    db_usertable = "cs3240Users"
    db_machinestable = "cs3240Machines"
    db_cachetable = "cs3240Cache"
    db_logtable = "cs3240Log"

