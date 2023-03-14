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

def getCeVars():
    getAllCeVars = os.environ.get('CE_SERVICES')
    ceVars = list(connectionJson.values())
    return ceVars

def getAllVars():
    for name, value in os.environ.items():
        print("{0}: {1}".format(name, value))

def etcdRead(etcdClient, etcdKey):
    etcdValue = etcdClient.get(etcdKey)
    return etcdValue

# Write instance IDs to etcd service
def etcdWrite(etcdClient):
    print("Attempting to write Schematics instance IDs to etcd:")
    ubuntuToCancel = etcdRead(etcdClient, '/current-servers/bare-metal/ubuntu-server-id')


try:
    
    # print("Attempting to pull all environment variables")
    # allVars = getAllVars()
    # print("All Vars type: " + str(type(allVars)))
    # print(allVars)
    print("Attempting to pull CE service variables")
    ceVars = getCeVars()
    print("CE Vars type: " + str(type(ceVars)))
    print(ceVars)
    print("CE service variables pulled")
except Exception as e:
    print("Error writing to etcd service: " + str(e))
    
