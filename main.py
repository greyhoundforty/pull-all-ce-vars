import json
import base64
import os
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from ibm_cloud_sdk_core import ApiException
import time 
import logging
from logdna import LogDNAHandler
import ibm_boto3
from ibm_botocore.client import Config, ClientError
from haikunator import Haikunator
from datetime import datetime, timedelta

today = datetime.now()
versionYear = today.strftime("%Y")
versionMonth = today.strftime("%m")
versionDay = today.strftime("%d")



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

def cosClient():
    pullCosVars = getCosCeVars()
    cosInstanceCrn = pullCosVars['credentials']['resource_instance_id']
    cosApiKey = pullCosVars['credentials']['apikey']
    cosEndpoint = ('https://s3.private.us-south.cloud-object-storage.appdomain.cloud')
    cos = ibm_boto3.resource("s3",
        ibm_api_key_id=cosApiKey,
        ibm_service_instance_id=cosInstanceCrn,
        config=Config(signature_version="oauth"),
        endpoint_url=cosEndpoint
    )
    return cos

def writeCosFile():
    client = cosClient()
    haikunator = Haikunator()
    basename = haikunator.haikunate(token_length=0, delimiter='')
    cosBucket = 'dummy-us-south-cancel-bucket'
    cosFilePath = str(versionYear + '/' + versionMonth + '/' + versionDay + '/')
    cosFile = cosFilePath + 'test.txt'
    return cosFile
    # cosFileContents = basename

    # client.Object(cosBucket, cosFile).put(Body=cosFileContents)

def listBuckets():
    client = cosClient()
    for bucket in client.buckets.all():
        print(bucket.name)


# Useful for debugging, prints all environment variables
# def getAllVars():
#     for name, value in os.environ.items():
#         print("{0}: {1}".format(name, value))

try:
    # log = logDnaLogger()
    # log.debug("Pulling all buckets and testing debug logging")
    print("Pulling all buckets")
    listBuckets()
    print("Finished pulling all buckets")
    print("Starting write to COS")
    writeCosFile()
    print("Finished write to COS")
except Exception as e:
    log.error("Error: " + str(e))
# except ApiException as ae:
#     print("Schematics update and apply failed.")
#     print(" - status code: " + str(ae.code))
#     print(" - error message: " + ae.message)
#     if ("reason" in ae.http_response.json()):
#         print(" - reason: " + ae.http_response.json()["reason"])
