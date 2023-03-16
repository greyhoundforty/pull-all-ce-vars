import sys
import json
import base64
import os
import etcd3
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from ibm_cloud_sdk_core import ApiException
from ibm_schematics.schematics_v1 import SchematicsV1

# Set up IAM authenticator and pull refresh token
authenticator = IAMAuthenticator(
    apikey=os.environ.get('IBMCLOUD_API_KEY'),
    client_id='bx',
    client_secret='bx'
    )

refreshToken = authenticator.token_manager.request_token()['refresh_token']

workspaceId = os.environ.get('WORKSPACE_ID')
# Set up Schematics service client and declare workspace ID
def schematicsClient():
    schematicsService = SchematicsV1(authenticator=authenticator)
    schematicsURL = "https://us.schematics.cloud.ibm.com"
    schematicsService.set_service_url(schematicsURL)
    return client

def pullAllWorkspaceOutputs():
    client = schematicsClient()
    wsOutputs = client.get_workspace_outputs(
        w_id=workspaceId,
    ).get_result()

    getAllOutputs = (wsOutputs[0]['output_values'][0])
    wsOuput = json.loads(getAllOutputs)
    getAllOutputs = list(wsOuput.values())[1]
    return getAllOutputs

def getWorkspaceOutputs(instance):
    client = schematicsClient()
    wsOutputs = client.get_workspace_outputs(
        w_id=workspaceId,
    ).get_result()

    getWsOutput = (wsOutputs[0]['output_values'][0][instance]['value'])
    return getWsOutput

# Pull all Code Engine service variables
# Any services that are bound to the code engine app/job are exposed as CE_SERVICES
def pullallCeVars():
    etcdServiceVars = os.environ.get('CE_SERVICES')
    connectionJson = json.loads(etcdServiceVars)
    allVars  = list(connectionJson.values())    
    return  allVars

# Retrieve etcd service variables
def getEtcdVars():
    allVars = pullallCeVars()
    etcdVars = allVars[1][0]['credentials']['connection']['grpc']
    return etcdVars

# Retrieve COS service variables
def cosVars():
    allVars = pullallCeVars()
    cosVars = allVars[0]
    return cosVars

# Define etcd client
def etcdClient():
    etcdServiceVars = getEtcdVars()
    connectVars = etcdServiceVars['hosts'][0]
    authVars    = etcdServiceVars['authentication']
    certName = etcdServiceVars['certificate']['name']
    encodedCert = base64.b64decode(etcdServiceVars['certificate']['certificate_base64'])
    decodedCert = encodedCert.decode('utf-8')
    etcdCert = '/usr/src/app/' + certName
    with open(etcdCert, 'w+') as output_file:
        output_file.write(decodedCert)

    client = etcd3.client(
        host=connectVars['hostname'],
        port=connectVars['port'], 
        ca_cert=etcdCert, 
        timeout=10, 
        user=authVars['username'], 
        password=authVars['password']
        )
    return client

# Useful for debugging, prints all environment variables
def getAllVars():
    for name, value in os.environ.items():
        print("{0}: {1}".format(name, value))
    return allVars

# Read from etcd service
def etcdRead(key):
    client = etcdClient()
    keyValue = client.get(key)
    return keyValue

# Write nonsense to etcd service
def etcdWrite():
    client = etcdClient()
    print("Attempting to write to etcd instance:")
    firstKey = client.put('/nonsense/id/1', '1234567890')
    secondKey = client.put('/nonsense/id/2', '0987654321')

try:
    allOutputs = pullAllWorkspaceOutputs()
    print(allOutputs)
    # Everything below this is working 
    # print("Attempting to write to etcd instance with updated connection client:")
    # etcdWrite()
    # print("Attempting to read from etcd instance:")
    # nonsenseId1 = etcdRead(key='/nonsense/id/1')
    # print("")
    # print(nonsenseId1)
    # transformedId = nonsenseId1[0].decode('utf-8')
    # print(transformedId)
except KeyError():
    print("Key error")
    
