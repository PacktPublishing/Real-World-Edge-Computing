#
# util.py
#

import requests

def inference_publish(url, inference_data_json):
    req = {}
    try:
        header = {"Content-type": "application/json", "Accept": "text/plain"} 
        req = requests.post(url, data=inference_data_json, headers=header)
    except requests.exceptions.RequestException as err:
        print ("inference_publish: Something Else",err)
    except requests.exceptions.HTTPError as errh:
        print ("inference_publish: Http Error:",errh)
    except requests.exceptions.ConnectionError as errc:
        print ("inference_publish: Error Connecting:",errc)
    except requests.exceptions.Timeout as errt:
        print ("inference_publish: Timeout Error:",errt) 

    return ""

def isIterable(var):
    return isinstance(var, list) or isinstance(var, tuple)
