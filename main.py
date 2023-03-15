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
import ibm_boto3
from ibm_botocore.client import Config, ClientError


# Useful for debugging, prints all environment variables
# for name, value in os.environ.items():
#     print("{0}: {1}".format(name, value))

# loggingIngestionKey = os.environ.get('LOGDNA_INGESTION_KEY')

# log = logging.getLogger('logdna')
# log.setLevel(logging.INFO)

# options = {
#   'env': 'code-engine',
#   'tags': 'python-etcd',
#   'app': 'python-etcd-app',
#   'url': 'https://logs.private.us-south.logging.cloud.ibm.com/logs/ingest',
#   'log_error_response': True
# }

# logAnalysis = LogDNAHandler(loggingIngestionKey, options)

# log.addHandler(logAnalysis)

# log.warning("Warning message", extra={'app': 'bloop'})
# log("Info message from " + str(os.environ.get('HOSTNAME')))


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

etcdServiceVars = os.environ.get('DB_CONNECTION_CONNECTION')
connectionJson = json.loads(etcdServiceVars)
connectionVars = list(connectionJson.values())[1]
encodedCert = connectionVars['certificate']['certificate_base64']
certName = connectionVars['certificate']['name']
certFileName = certName + '.crt'
ca_cert=base64.b64decode(encodedCert)
decodedCert = ca_cert.decode('utf-8')

etcdCert = '/usr/src/app/' + certFileName
with open(etcdCert, 'w+') as output_file:
    output_file.write(decodedCert)

# Set up etcd service client
etcdClient = etcd3.client(
    host=connectionVars['hosts'][0]['hostname'],
    port=connectionVars['hosts'][0]['port'], 
    ca_cert=etcdCert, 
    timeout=10, 
    user=connectionVars['authentication']['username'], 
    password=connectionVars['authentication']['password']
)

# Get COS credentials from Schematics workspace
# listVars = ceVarsToList()
# CosAPIKey = listVars[0]['credentials']['apikey']


# # Constants for IBM COS values
# COS_ENDPOINT = "<endpoint>" # Current list avaiable at https://control.cloud-object-storage.cloud.ibm.com/v2/endpoints
# COS_API_KEY_ID = "<api-key>" # eg "W00YixxxxxxxxxxMB-odB-2ySfTrFBIQQWanc--P3byk"
# COS_INSTANCE_CRN = "<service-instance-id>" # eg "crn:v1:bluemix:public:cloud-object-storage:global:a/3bf0d9003xxxxxxxxxx1c3e97696b71c:d6f04d83-6c4f-4a62-a165-696756d63903::"

# # Create resource
# cos = ibm_boto3.resource("s3",
#     ibm_api_key_id=CosAPIKey,
#     ibm_service_instance_id=COS_INSTANCE_CRN,
#     config=Config(signature_version="oauth"),
#     endpoint_url=COS_ENDPOINT
# )

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

def getAllVars():
    for name, value in os.environ.items():
        print("{0}: {1}".format(name, value))
    return allVars

# def etcdRead(etcdClient, etcdKey):
#     etcdValue = etcdClient.get(etcdKey)
#     return etcdValue

# Write nonsense to etcd service
def etcdWrite(etcdClient):
    print("Attempting to write to etcd instance:")
    firstKey = etcdClient.put('/nonsense/id/1', '1234567890')
    secondKey = etcdClient.put('/nonsense/id/2', '0987654321')

try:
    

    listVars = ceVarsToList()
    # print("List Vars type: " + str(type(listVars)))
    # print(listVars)
    print("printing COS list var")
    cosVars = listVars[0]
    print("var type: " + str(type(cosVars)))
    print(cosVars)
    interatedList = cosVars[0]
    print("iterated list type: " + str(type(interatedList)))
    print(interatedList)
    # print("pull credentials from COS list")
    # print(interatedList['credentials']['apikey'])
    # print("printing Etcd list var")
    # print(listVars[1])
    # print("printing LogDNA list var")
    # print(listVars[2])
    # print("attempting etcd write")
    etcdWrite(etcdClient)
except Exception as e:
    print("Error writing to etcd service: " + str(e))
    
