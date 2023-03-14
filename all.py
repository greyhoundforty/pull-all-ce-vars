import sys
import json
import os

def getAllVars():
    for name, value in os.environ.items():
        print("{0}: {1}".format(name, value))



try:
    getAllVars()
except Exception as e:
    print("Unable to read environment variables: " + str(e))
    
