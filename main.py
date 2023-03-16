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
    schClient = SchematicsV1(authenticator=authenticator)
    schematicsURL = "https://private-us-east.schematics.cloud.ibm.com"
    schClient.set_service_url(schematicsURL)
    return schClient

def pullAllWorkspaceOutputs():
    client = schematicsClient()
    wsOutputs = client.get_workspace_outputs(
        w_id=workspaceId,
    ).get_result()

    outputs = wsOutputs[0]['output_values'][0]
    # dumpOutputs = json.dumps(outputs)
    # wsOutput = json.loads(outputs)
    # getAllOutputs = list(wsOuput.values())[1]
    return outputs

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

# def logDnaLogger():
#     allCeVars = pullallCeVars()
#     logDnaVars = allCeVars[2][0]['credentials']['ingestion_key']
#     log = logging.getLogger('logdna')
#     log.setLevel(logging.INFO)

#     options = {
#     'hostname': 'pytest',
#     'ip': '10.0.1.1',
#     'mac': 'C0:FF:EE:C0:FF:EE'
#     }

#     # Defaults to False; when True meta objects are searchable
#     options['index_meta'] = True
#     options['custom_fields'] = 'meta'


#     logger = LogDNAHandler(key, options)

#     log.addHandler(logger)

#     return log
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

def getLogDNAIngestionKey():
    allVars = pullallCeVars()
    ingestionKey = allVars[2][0]['credentials']['ingestion_key']
    ingestionKey 


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

# Write Schematics output IDs to etcd service
def etcdWrite(key, value):
    client = etcdClient()
    writeKey = client.put(key, value)

try:
    # allOutputs = pullAllWorkspaceOutputs()
    print("Pulling Centos server ID from workspace output:")
    centosServerId = getWorkspaceOutputs(instance='centos_server_id')
    print("Server ID pulled. Writing to etcd instance:")
    writeCentos = etcdWrite('/current-servers/centos_id', value=centosServerId)
    print("Server ID written to etcd instance. Now attempting to read from etcd instance:")
    centosId = etcdRead(key='/current-servers/centos_server_id')
    print(centosId)
    # print("Centos Server ID pulled from etcd: " + str(transformedId))
    
    # print("output type is: " + str(type(allOutputs)))
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
    
