import sys
import json
import os

def getAllVars():
    for name, value in os.environ.items():
        print("{0}: {1}".format(name, value))

# etcdWrite(etcdClient)
# print("Pulling all ce vars")
# allVars = getAllVars()
# print(allVars)
# get_logger()
# log.warning("Warning message", extra={'app': 'bloop'})
# log("Info message from " + str(hst))
# log.error("This is an Error message")
# print("Pulling all CE vars")
# unalteredCeVars = getCeVars()
# print(unalteredCeVars)
# print("Pulling all CE vars as JSON")
# ceVarsJson = ceVarsToJson()
# print(ceVarsJson)
# print("Pulling all CE vars as list")
# ceVarsList = ceVarsToList()
# # print(ceVarsList)
# print("Pulling COS vars from list")
# cosVars = ceVarsList[0]
# print(cosVars)

# print("pulling db details from ce services var")
# etcdVars = ceVarsList[1]
# print(etcdVars)
# # # print("List Vars type: " + str(type(listVars)))
# # # print(listVars)
# # print("printing COS list var")
# # cosVars = listVars[0]
# # print("var type: " + str(type(cosVars)))
# # print(cosVars)
# # interatedList = cosVars[0]
# # print("iterated list type: " + str(type(interatedList)))
# # print(interatedList)
# # # print("pull credentials from COS list")
# # # print(interatedList['credentials']['apikey'])
# # # print("printing Etcd list var")
# # # print(listVars[1])
# logDnaVars = listVars[2]
# print("Getting LogDNA ingestion key")
# loggingKey = logDnaVars[0]['credentials']['ingestion_key']
# print("logging key: " + loggingKey)
# listVars = ceVarsToList()
# print(listVars)

try:
    getAllVars()
except Exception as e:
    print("Unable to read environment variables: " + str(e))
    
