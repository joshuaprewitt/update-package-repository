import requests
import sys
import json
import systemlink
import systemlink.clientconfig
import urllib3
import time
import random

# disable https warnings
urllib3.disable_warnings()
    
# load SystemLink HTTP configuration 
configuration = systemlink.clientconfig.get_configuration('nirepo')
host = configuration.host

# disable cache to prevent getting stale data
def dc():
    return '?_dc='+str(random.randrange(10000000))

def job_status(job_id):
    # wait for the job to complete
    for i in range(10):
        # create a random number to avoid getting cached server results
        rand = str(random.randrange(100000))
        job_url =  host+'/v1/jobs'+dc()+'&id='+job_id
        response = requests.get(job_url, headers=configuration.api_key, verify=False)
        status = json.loads(response.text)["jobs"][0]["status"]
        if status == "SUCCEEDED":
            print('SUCCEEDED = ', response.text)
            update_id = json.loads(response.text)["jobs"][0]["resourceId"]
            break
        if status == "FAILED":
            print('FAILED = ', response.text)
            break      
        print(status)
        time.sleep(1)
    return response

def main():
    # get feed ids
    feeds_url = host+"/v1/feeds"
    response = requests.get(feeds_url, headers=configuration.api_key, verify=False)

    feeds = json.loads(response.text)
    feed_ids = []
    for feed in feeds["feeds"]:
        feed_ids.append(feed["id"])
        
    print("Feed IDs = ",feed_ids)

    # check for updates
    # todo: hard code feed ID for now, but will utlimately iterate over every feed
    feed_id = '5f518c1ba9460dbc70490640'
    check_url = host+'/v1/feeds/'+feed_id+'/update-check'
    response = requests.post(check_url, headers=configuration.api_key, verify=False)
    job_id = json.loads(response.text)["jobId"]
    print("Job ID = ",job_id)

    status = job_status(job_id)
    update_id = json.loads(status.text)["jobs"][0]["resourceId"]

    # if the feed wasn't updated after 10 seconds move to the next feed
    #if status != "SUCCEEDED"
    #    break

    # get list of updates
    update_url =  host+'/v1/updates/'+update_id+dc()
    response = requests.get(update_url, headers=configuration.api_key, verify=False)
    updates = response.text
    print('Updates = ', response.text)

    # apply updates
    update_url =  host+'/v1/feeds/'+feed_id+'/update-apply?ignoreImportErrors=false&shouldOverwrite=false'
    headers = {'Content-type': 'application/json'}
    headers.update(configuration.api_key)
    response = requests.post(update_url, verify=False, data=updates, headers=headers)
    job_id = json.loads(response.text)["jobId"]
    print('Update response = ',response.text)

    status = job_status(job_id)

if __name__ == "__main__":
    main()



