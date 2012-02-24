import sys
import os
import htmlr

filename = sys.argv[1]
if os.path.exists(filename):
    module = os.path.basename(filename).split('.')[0]
    __import__(module)
    htmlr.render(format=True)
