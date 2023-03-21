import json
import base64
import os
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from ibm_cloud_sdk_core import ApiException
import time 
import logging
from logdna import LogDNAHandler

# Set up IAM authenticator and pull refresh token
authenticator = IAMAuthenticator(
    apikey=os.environ.get('IBMCLOUD_API_KEY'),
    client_id='bx',
    client_secret='bx'
    )

refreshToken = authenticator.token_manager.request_token()['refresh_token']

# Pull all Code Engine service variables
# Any services that are bound to the code engine app/job are exposed as CE_SERVICES
def pullallCeVars():
    ceVars = os.environ.get('CE_SERVICES')
    ceVarsToJson = json.loads(ceVars)
    allVars  = list(ceVarsToJson.values())    
    return  allVars

def getLogDNAIngestionKey():
    allVars = pullallCeVars()
    ingestionKey = allVars[1][0]['credentials']['ingestion_key']
    return ingestionKey

def logDnaLogger():
    key = getLogDNAIngestionKey()
    # key = os.environ.get('LOGDNA_INGESTION_KEY')
    log = logging.getLogger('logdna')
    log.setLevel(logging.INFO)

    options = {
        'app': 'pull-all-ce-vars',
        'url': 'https://logs.private.us-south.logging.cloud.ibm.com/logs/ingest',
    }

    logger = LogDNAHandler(key, options)
    log.addHandler(logger)
    return log

# Retrieve COS service variables
def getCosCeVars():
    allVars = pullallCeVars()
    cosVars = allVars[0][0]
    return cosVars

# Useful for debugging, prints all environment variables
# def getAllVars():
#     for name, value in os.environ.items():
#         print("{0}: {1}".format(name, value))

try:
    log = logDnaLogger()
    # print("Pulling all CE service bindings")
    # pullallCeVars()
    fVar = getCosCeVars()
    print("Pulling COS service variables: " + str(fVar))
    # sVar = getLogDNAIngestionKey()
    # print("Pulling ingestion key from second CE var in list: " + str(sVar))
    pullCosCrn = fVar['credentials']['resource_instance_id']
    print("Pulling COS CRN: " + str(pullCosCrn))
except Exception as e:
    log.error("Error: " + str(e))
# except ApiException as ae:
#     print("Schematics update and apply failed.")
#     print(" - status code: " + str(ae.code))
#     print(" - error message: " + ae.message)
#     if ("reason" in ae.http_response.json()):
#         print(" - reason: " + ae.http_response.json()["reason"])
