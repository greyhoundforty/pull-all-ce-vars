import sys
import json
import base64
import os
import etcd3
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from ibm_cloud_sdk_core import ApiException
from ibm_schematics.schematics_v1 import SchematicsV1
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

    return outputs

def getWorkspaceOutputs(instance):
    client = schematicsClient()
    wsOutputs = client.get_workspace_outputs(
        w_id=workspaceId,
    ).get_result()

    getWsOutput = (wsOutputs[0]['output_values'][0][instance]['value'])
    return getWsOutput

def updateWorkspace():
    log = logDnaLogger()
    client = schematicsClient()# Construct the terraform taint command model
    terraform_command_model = {
        'command': 'taint',
        'command_params': 'random_integer.location',
        'command_name': 'location-taint',
        'command_desc': 'Run taint on location resource',
    }

    log.info("Tainting location resource in Workspace.")

    wsUpdate = client.run_workspace_commands(
        w_id=workspaceId,
        refresh_token=refreshToken,
        commands=[terraform_command_model],
        operation_name='taint-location',
        description='taint-location'
    ).get_result()

    updateActivityId = wsUpdate.get('activityid')

    while True:
        jobStatus = client.get_job(job_id=updateActivityId).get_result()['status']['workspace_job_status']['status_code']
        if (jobStatus == 'job_in_progress' or jobStatus == 'job_pending'):
            log.info("Workspace update in progress. Checking again in 30 seconds...")
            time.sleep(30)
        elif (jobStatus == 'job_cancelled' or jobStatus == 'job_failed'):
            log.error("Workspace update failed. Please check the logs by running the following command: ibmcloud schematics job logs --id " + updateActivityId)
            break
        else:
            print("Workspace update complete. Proceeding to Workspace plan.")
            break

def planWorkspace():
    log = logDnaLogger()
    client = schematicsClient()
    wsPlan = client.plan_workspace_command(
        w_id=workspaceId,
        refresh_token=refreshToken,
    ).get_result()

    planActivityId = wsPlan.get('activityid')

    while True:
        planStatus = client.get_job(job_id=planActivityId).get_result()['status']['workspace_job_status']['status_code']
        if (planStatus == 'job_in_progress' or planStatus == 'job_pending'):
            log.info("Workspace plan in progress. Checking again in 30 seconds...")
            time.sleep(30)
        elif (planStatus == 'job_cancelled' or planStatus == 'job_failed'):
            log.error("Workspace plan failed. Please check the logs by running the following command: ibmcloud schematics job logs --id " + planActivityId)
            break
        else:
            log.info("Workspace plan complete. Proceeding to Workspace apply.")
            break

def applyWorkspace():
    log = logDnaLogger()
    client = schematicsClient()
    wsApply = client.apply_workspace_command(
        w_id=workspaceId,
        refresh_token=refreshToken,
    ).get_result()

    applyActivityId = wsApply.get('activityid')

    while True:
        applyStatus = client.get_job(job_id=applyActivityId).get_result()['status']['workspace_job_status']['status_code']
        if (applyStatus == 'job_in_progress' or applyStatus == 'job_pending'):
            log.info("Workspace apply in progress. Checking again in 1 minute...")
            time.sleep(60)
        elif (applyStatus == 'job_cancelled' or applyStatus == 'job_failed'):
            log.error("Workspace apply failed. Please check the logs by running the following command: ibmcloud schematics job logs --id " + applyActivityId)
            break
        else:
            log.info("Workspace apply complete. Gathering workspace outputs.")
            break

# Pull all Code Engine service variables
# Any services that are bound to the code engine app/job are exposed as CE_SERVICES
def pullallCeVars():
    etcdServiceVars = os.environ.get('CE_SERVICES')
    connectionJson = json.loads(etcdServiceVars)
    allVars  = list(connectionJson.values())    
    return  allVars

def logDnaLogger():
    key = getLogDNAIngestionKey()
    log = logging.getLogger('logdna')
    log.setLevel(logging.INFO)

    options = {
        'app': 'rolling-iaas',
        'url': 'https://logs.us-south.logging.cloud.ibm.com/logs/ingest',
    }

    logger = LogDNAHandler(key, options)

    log.addHandler(logger)

    return log

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
    allCeVars = pullallCeVars()
    logDnaKey = allCeVars[2][0]['credentials']['ingestion_key']
    return logDnaKey

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

def etcdgetPrefix(prefix):
    client = etcdClient()
    prefixKeys = client.get_prefix(prefix)
    return prefixKeys


try:
    log = logDnaLogger()
    currentCentosServerId = getWorkspaceOutputs(instance='centos_server_id')
    currentUbuntuServerId = getWorkspaceOutputs(instance='ubuntu_server_id')
    currentWindowsServerId = getWorkspaceOutputs(instance='windows_server_id')
    log.info("The following server IDs were pulled from Schematics output.")
    log.info("CentOS Server ID: " + currentCentosServerId)
    log.info("Ubuntu Server ID: " + currentUbuntuServerId)
    log.info("Windows Server ID: " + currentWindowsServerId)
    
    log.info("Writing Server IDs to cancellation queue '/update-cancel-ticket/' in etcd.")
    writeCentos = etcdWrite('/update-cancel-ticket/centos_server_id', value=currentCentosServerId)
    writeUbuntu = etcdWrite('/update-cancel-ticket/ubuntu_server_id', value=currentUbuntuServerId)
    writeWindows = etcdWrite('/update-cancel-ticket/windows_server_id', value=currentWindowsServerId)
    
    log.info("Server IDs written to cancellation queue in etcd instance. Starting Schematics Workspace update")
    updateWorkspace()
    log.info("Workspace update complete. Proceeding to Workspace plan.")
    
    planWorkspace()
    log.info("Workspace plan complete. Proceeding to Workspace apply.")
    
    applyWorkspace()
    log.info("Workspace apply complete. Proceeding to Workspace output pull.")
    
    log.info("Pulling newly deployed server IDs from Schematics workspace output.")
    newCentosServerId = getWorkspaceOutputs(instance='centos_server_id')
    newUbuntuServerId = getWorkspaceOutputs(instance='ubuntu_server_id')
    newWindowsServerId = getWorkspaceOutputs(instance='windows_server_id')
    
    log.info("Server IDs pulled from Schematics output.")
    log.info("CentOS Server ID: " + newCentosServerId)
    log.info("Ubuntu Server ID: " + newUbuntuServerId)
    log.info("Windows Server ID: " + newWindowsServerId)
    
    log.info("Writing new server IDs to etcd instance.")
    writeCentos = etcdWrite('/current-servers/centos_server_id', value=newCentosServerId)
    writeUbuntu = etcdWrite('/current-servers/ubuntu_server_id', value=newUbuntuServerId)
    writeWindows = etcdWrite('/current-servers/windows_server_id', value=newWindowsServerId)
    
    print("Server IDs written to etcd instance.")
except ApiException as ae:
    print("Schematics update and apply failed.")
    print(" - status code: " + str(ae.code))
    print(" - error message: " + ae.message)
    if ("reason" in ae.http_response.json()):
        print(" - reason: " + ae.http_response.json()["reason"])
