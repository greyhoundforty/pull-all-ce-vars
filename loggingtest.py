import logging
from logdna import LogDNAHandler
import os
import json
from haikunator import Haikunator
from datetime import datetime, timedelta

today = datetime.now()
version_date = today.strftime("%Y-%m-%d")

haikunator = Haikunator()
basename = haikunator.haikunate(token_length=0, delimiter='')


def logDnaLogger():
    key = getLogDNAIngestionKey()
    log = logging.getLogger('logdna')
    log.setLevel(logging.INFO)

    options = {
        'hostname': 'europa',
        'app': 'pytest',
        'url': 'https://logs.us-south.logging.cloud.ibm.com/logs/ingest',
    }

    logger = LogDNAHandler(key, options)

    log.addHandler(logger)

    return log

def pullallCeVars():
    allVars = os.environ.get('CE_SERVICES')
    connectionJson = json.loads(allVars)
    listVars  = list(connectionJson.values())    
    return  listVars

def getLogDNAIngestionKey():
    allCeVars = pullallCeVars()
    logDnaKey = allCeVars[2][0]['credentials']['ingestion_key']
    return logDnaKey

def newFancyService():
    log = logDnaLogger()
    log.warning("Warning message from europa at " + version_date, extra={'app': 'europa-py'})
    log.error("Error message from randomly generated name: " + basename)

try:
    newFancyService()
    # print(getKey)
    # getVars = pullallCeVars()
    # print(getVars)
    # logDnaLogger()
    # log.warning("Warning message", extra={'app': 'bloop'})
    # log.info("Info message from " + basename)
except:
    print("No logdna vars")


# loggingIngestionKey = os.environ.get('LOGDNA_INGESTION_KEY')

# log = logging.getLogger('logdna')
# log.setLevel(logging.INFO)

# options = {
#   'hostname': 'europa',
#   'env': 'testlocal-app',
#   'url': 'https://logs.us-south.logging.cloud.ibm.com/logs/ingest',
#   'log_error_response': True
# }

# logAnalysis = LogDNAHandler(loggingIngestionKey, options)

# log.addHandler(logAnalysis)

# log.warning("Warning message", extra={'app': 'bloop'})
# log.info("Info message from " + basename)



