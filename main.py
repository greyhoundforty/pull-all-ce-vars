import json
import os
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from ibm_cloud_sdk_core import ApiException, BaseService
import logging
from logdna import LogDNAHandler
import ibm_boto3
from ibm_botocore.client import Config, ClientError
from haikunator import Haikunator
from datetime import datetime

today = datetime.now()

def cosPath():
    today = datetime.now()
    cosPath = today.strftime("%Y") + '/' + today.strftime("%m") + '/' + today.strftime("%d") + '/'
    return cosPath

def iamAuthenticator():
    authenticator = IAMAuthenticator(
        apikey=os.environ.get('IBMCLOUD_API_KEY'),
        client_id='bx',
        client_secret='bx'
        )
    
    refreshToken = authenticator.token_manager.request_token()['refresh_token']
    
    return authenticator, refreshToken

def logDnaLogger():
    key = os.environ.get('LOG_INGESTION_KEY')
    log = logging.getLogger('logdna')
    log.setLevel(logging.INFO)

    options = {
        'app': 'pull-all-ce-vars',
        'url': 'https://logs.private.us-south.logging.cloud.ibm.com/logs/ingest',
        'index_meta': True,
        'tags': 'pull-all-ce-vars'
    }

    logger = LogDNAHandler(key, options)
    log.addHandler(logger)
    return log

def cosClient():
    cosInstanceCrn = os.environ.get('CLOUD_OBJECT_STORAGE_RESOURCE_INSTANCE_ID')
    cosApiKey = os.environ.get('CLOUD_OBJECT_STORAGE_APIKEY')
    cosEndpoint = 'https://s3.direct.us-south.cloud-object-storage.appdomain.cloud'
    # cosEndpoint = ("https://" + os.environ.get('COS_ENDPOINT'))
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
    cosBucket = "dummy-us-south-cancel-bucket"
    cosFile = cosPath + basename + ".txt"
    cosFileContents = basename

    print("Writing test content " + basename + " to file at: " + cosFile)
    client.Object(cosBucket, cosFile).put(Body=cosFileContents)

def listBuckets():
    client = cosClient()
    for bucket in client.buckets.all():
        print(bucket.name)


# Useful for debugging, prints all environment variables
def getAllVars():
    for name, value in os.environ.items():
        print("{0}: {1}".format(name, value))

try:
    log = logDnaLogger()
    log.debug("Attempting to write file to COS")
    writeCosFile()
    log.debug("Attempting to list buckets")
    listBuckets()
except Exception as e:
    log.error("Error: " + str(e))
