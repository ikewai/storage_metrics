# requires python 3.7+

# This script acquires disk usage metrics from the cistore and updates the ike wai database with this information.

# requires the following environment variables:
# -IKE_SERVER: the subdomain [IKE_SERVER].its.hawaii.edu. ikeauth for prod.
# -IKE_TOKEN: the authentication token for the api that the gateway interfaces with.
# -METRICS_UUID: the uuid of the database object that stores the metrics.


# Begin Libraries
import os
import subprocess
import requests
import json
# End Libraries

# Begin Constants
ike_token   = os.environ.get('IKE_TOKEN')
ike_server  = os.environ.get('IKE_SERVER')
ike_api_url = 'https://'+ike_server+'.its.hawaii.edu/meta/v2/data/'
ike_db_uuid = os.environ.get('METRICS_UUID')
requests.packages.urllib3.disable_warnings() # pylint: disable=no-member
# End Constants

# Begin Bash Command Definitions:
sh__storage_space_all = "du -sh /mnt/netapp/ikewai | head -n1 | awk '{print $1;}'" # Storage Space used by All (human-readable string eg. 4.9T)
sh__storage_space_annotated = "du -sh /mnt/netapp/ikewai/annotated | head -n1 | awk '{print $1;}'" # Storage Space used by Annotated Data (human-readable string eg. 32G)
sh__file_count_all = "find /mnt/netapp/ikewai/annotated /mnt/netapp/ikewai/working -type f | wc -l" # File count in Annotated and Working (integer of files eg. 302941)
sh__file_count_annotated = "find /mnt/netapp/ikewai/annotated -type f | wc -l" # File count in Annotated Data (integer of files eg. 3505)
# End Bash Command Definitions


# Step 1: Data Ingestion
# subprocess.run() yields a CompletedProcess object, with stdout as a member "bytes" variable.
# to turn that to text (JSON-friendly), I'm using decode('utf8'), then stripping the newline at the end.
storage_space_all        = subprocess.run(["/bin/bash", "-c", sh__storage_space_all],       capture_output=True).stdout.decode('utf8').strip('\n')
storage_space_annotated  = subprocess.run(["/bin/bash", "-c", sh__storage_space_annotated], capture_output=True).stdout.decode('utf8').strip('\n')
file_count_all           = subprocess.run(["/bin/bash", "-c", sh__file_count_all],          capture_output=True).stdout.decode('utf8').strip('\n')
file_count_annotated     = subprocess.run(["/bin/bash", "-c", sh__file_count_annotated],    capture_output=True).stdout.decode('utf8').strip('\n')

# Step 2: Get UsageData from database
def getIkeDbDocument(ike_token, ike_api_url, ike_db_uuid):
    headers = {
        'authorization' : "Bearer " + ike_token,
        'content-type'  : "application/json"  ,
    }
    res = requests.get(
        ike_api_url+ike_db_uuid,
        headers=headers,
        verify=False
    )
    print("Requesting Document: " +ike_api_url+ike_db_uuid)
    resp = json.loads(res.content)
    if resp['status'] == 'success':
        return resp['result']
    else:
        return resp

UsageData = getIkeDbDocument(ike_token=ike_token, ike_api_url=ike_api_url, ike_db_uuid=ike_db_uuid)
print(UsageData)
# Step 3: Modify UsageData in memory
UsageData['value']['allStorage']            = storage_space_all
UsageData['value']['annotatedStorage']      = storage_space_annotated
UsageData['value']['allFilesCount']         = file_count_all
UsageData['value']['annotatedFilesCount']   = file_count_annotated

# Step 4: Update UsageData in database
def updateIkeDbDocument(ike_token, ike_api_url, ike_db_uuid, usage_data):
    print(ike_api_url)
    print(ike_db_uuid)
    print(usage_data)
    headers = {
        'authorization' : "Bearer " + ike_token,
        'content-type'  : "application/json"   ,
    }
    res = requests.post(
        ike_api_url+ike_db_uuid,
        json        = usage_data,
        headers     = headers,
        verify      = False
    )
    resp = json.loads(res.content)
    if resp['status'] == 'success':
        return resp['result']
    else:
        return resp
        
usage_data_update_results = updateIkeDbDocument(ike_token=ike_token, ike_api_url=ike_api_url, ike_db_uuid=ike_db_uuid, usage_data=UsageData)

print(usage_data_update_results)