import sys
import json
import base64
import os
import etcd3

etcdServiceVars = os.environ.get('DB_CONNECTION')
connectionJson = json.loads(etcdServiceVars)
connectionVars = list(connectionJson.values())[1]
# encodedCert = connectionVars['certificate']['certificate_base64']
# certName = connectionVars['certificate']['name']
# certFileName = certName + '.crt'
# ca_cert=base64.b64decode(encodedCert)
# decodedCert = ca_cert.decode('utf-8')

# etcdCert = '/usr/src/app/' + certFileName
# print(etcdCert)
# with open(etcdCert, 'w+') as output_file:
#     output_file.write(decodedCert)

# # Set up etcd service client
# etcdClient = etcd3.client(
#     host=connectionVars['hosts'][0]['hostname'], 
#     port=connectionVars['hosts'][0]['port'], 
#     ca_cert=certname, 
#     timeout=10, 
#     user=connectionVars['authentication']['username'], 
#     password=connectionVars['authentication']['password']
# )

# # Write instance IDs to etcd service
# def etcdWrite(etcdClient):
#     log.info("Connected to etcd service...")
#     print("Attempting to write albumns to etcd:")
#     etcdClient.put('/radiohead/albums/1', 'pablo-honey')
#     etcdClient.put('/radiohead/albums/2', 'the-bends')
#     etcdClient.put('/radiohead/albums/3', 'ok-computer')
#     etcdClient.put('/radiohead/albums/4', 'kid-a')
#     etcdClient.put('/radiohead/albums/5', 'amnesiac')
#     etcdClient.put('/radiohead/albums/6', 'hail-to-the-thief')
#     etcdClient.put('/radiohead/albums/7', 'in-rainbows')
#     etcdClient.put('/radiohead/albums/8', 'the-king-of-limbs')
#     etcdClient.put('/radiohead/albums/9', 'a-moon-shaped-pool')
#     print("Albums written to etcd")
print(connectionVars)