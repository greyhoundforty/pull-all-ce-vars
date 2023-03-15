import sys
import json
import base64
import os
import etcd3
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from ibm_cloud_sdk_core import ApiException
from ibm_schematics.schematics_v1 import SchematicsV1
import logging
from logdna import LogDNAHandler

# Useful for debugging, prints all environment variables
# for name, value in os.environ.items():
#     print("{0}: {1}".format(name, value))

# Set up IAM authenticator and pull refresh token
authenticator = IAMAuthenticator(
    apikey=os.environ.get('IBMCLOUD_API_KEY'),
    client_id='bx',
    client_secret='bx'
    )

refreshToken = authenticator.token_manager.request_token()['refresh_token']

# Set up Schematics service client and declare workspace ID
workspaceId = os.environ.get('WORKSPACE_ID')
schematicsService = SchematicsV1(authenticator=authenticator)
schematicsURL = "https://us.schematics.cloud.ibm.com"
schematicsService.set_service_url(schematicsURL)


# # Set up etcd service client
def etcdClient():
    etcdServiceVars = os.environ.get('CE_SERVICES')
    connectionJson = json.loads(etcdServiceVars)
    connectionVars = list(connectionJson.values())[1]
    dbCertInfo = connectionVars[0]['credentials']['connection']['certifiicate']
    # dbVars = connectionVars[0]
    # cert = dbVars['credentials']['connection']

    # certName = connectionVars['certificate']['name']
    # certFileName = certName + '.crt'
    # ca_cert=base64.b64decode(encodedCert)
    # decodedCert = ca_cert.decode('utf-8')

    # etcdCert = '/usr/src/app/' + certFileName
    # with open(etcdCert, 'w+') as output_file:
    #     output_file.write(decodedCert)

    # client = etcd3.client(
    #     host=connectionVars['hosts'][0]['hostname'],
    #     port=connectionVars['hosts'][0]['port'], 
    #     ca_cert=etcdCert, 
    #     timeout=10, 
    #     user=connectionVars['authentication']['username'], 
    #     password=connectionVars['authentication']['password']
    #     )
    return dbCertInfo

def getCeVars():
    getAllCeVars = os.environ.get('CE_SERVICES')
    return getAllCeVars

def ceVarsToJson():
    allVars = getCeVars()
    ceVarsJson = json.loads(allVars)
    return ceVarsJson

def ceVarsToList():
    jsonVars = ceVarsToJson()
    ceVarsList = list(jsonVars.values())
    return ceVarsList


def get_logger():
    listVars = ceVarsToList()
    logDnaVars = listVars[2]
    loggingKey = logDnaVars[0]['credentials']['ingestion_key']
    log = logging.getLogger('logdna')
    log.setLevel(logging.INFO)

    options = {
        'env': 'code-engine',
        'tags': 'python-etcd',
        'app': 'python-etcd-app',
        'url': 'https://logs.private.us-south.logging.cloud.ibm.com/logs/ingest',
        'log_error_response': True
    }
    logger = LogDNAHandler(loggingKey, options)
    log.addHandler(logger)

    return log


def getAllVars():
    for name, value in os.environ.items():
        print("{0}: {1}".format(name, value))
    return allVars

# def etcdRead(etcdClient, etcdKey):
#     etcdValue = etcdClient.get(etcdKey)
#     return etcdValue

# Write nonsense to etcd service
def etcdWrite(etcdClient):
    client = etcdClient()
    print("Attempting to write to etcd instance:")
    firstKey = client.put('/nonsense/id/1', '1234567890')
    secondKey = client.put('/nonsense/id/2', '0987654321')

try:
    dbVars = etcdClient()
    print("var type is: " + str(type(dbVars)))
    print(dbVars)
except KeyError():
    print("Key error")
    
