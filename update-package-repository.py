import json
import random
import requests
import sys
import systemlink.clientconfig
import time
import urllib3

# disable https warnings
urllib3.disable_warnings()
    
# load SystemLink HTTP configuration 
configuration = systemlink.clientconfig.get_configuration('nirepo')
host = configuration.host

def dc():
    # disable cache to prevent getting stale data
    return '?_dc='+str(random.randrange(10000000))

def job_status(job_id):
    # poll for the job to complete
    for i in range(10):
        job_url =  host+'/v1/jobs'+dc()+'&id='+job_id
        response = requests.get(job_url, headers=configuration.api_key, verify=False)
        status = json.loads(response.text)["jobs"][0]["status"]
        if status == "SUCCEEDED":
            break
        if status == "FAILED":
            break      
        print(status)
        time.sleep(1)
    return response

def check_for_updates(feed_id):
    check_url = host+'/v1/feeds/'+feed_id+'/update-check'
    response = requests.post(check_url, headers=configuration.api_key, verify=False)
    job_id = json.loads(response.text)["jobId"]
    print("JOB ID = ",job_id)
    status = job_status(job_id)
    return status

def get_updates(update_id):
    update_url =  host+'/v1/updates/'+update_id+dc()
    response = requests.get(update_url, headers=configuration.api_key, verify=False)
    updates = response.text
    return updates

def update_feed(feed_id, updates):
    update_url =  host+'/v1/feeds/'+feed_id+'/update-apply?ignoreImportErrors=false&shouldOverwrite=false'
    headers = {'Content-type': 'application/json'}
    headers.update(configuration.api_key)
    response = requests.post(update_url, verify=False, data=updates, headers=headers)
    job_id = json.loads(response.text)["jobId"]
    status = job_status(job_id)
    return status

def main():
    # updates all of the feeds in the package repository based on the feeds they were replicated from
    # get feed ids
    feeds_url = host+"/v1/feeds"
    response = requests.get(feeds_url, headers=configuration.api_key, verify=False)

    feeds = json.loads(response.text)
    feed_ids = []
    for feed in feeds["feeds"]:
        feed_ids.append(feed["id"])
    
    print("FEED IDS = ",feed_ids)   

    # check for updates
    # todo: hard code feed ID for now, but will utlimately iterate over every feed
    feed_id = '5f518c1ba9460dbc70490640'        
    status = check_for_updates(feed_id)
    print('CHECK STATUS = ', status.text)
    update_id = json.loads(status.text)["jobs"][0]["resourceId"]

    # todo: continue if there are no updates or the job failed

    # get list of updates
    updates = get_updates(update_id)
    print('UPDATES = ', updates)

    # apply updates
    status = update_feed(feed_id,updates)
    print('APPLY STATUS = ', status.text)


if __name__ == "__main__":
    main()



