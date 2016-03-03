from test_model import *
import sys

if len(sys.argv) == 3:
    name, passw = sys.argv[1], sys.argv[2]
    print "use name: ", sys.argv[1]
    print "use job limit: 5"
    create_user(name, passw)
elif len(sys.argv) == 4:
    name, passw, limit = sys.argv[1], sys.argv[2], sys.argv[3]
    print "use name: ", sys.argv[1]
    print "use job limit: ", sys.argv[3]
    create_user(name, passw, limit)
else:
    print "usage: python add_user.py <name> <password> <job limit(int)>"
    sys.exit(1)

