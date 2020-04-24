from argparse import ArgumentParser
import json
import os
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
 
#Configuration
# These values might be redefined when calling the script
CONF ={
    "CONTENT_TYPE": "application/json",
    "KEY_IDENTITY": -1,
    "KEY_CREDENTIALS": -1,
    "OMEKA_API_URL": -1
}
# CONST
REQ_SESSION = requests.Session()

def check_omeka_conf():
    if (CONF["OMEKA_API_URL"] == -1) or (CONF["KEY_CREDENTIALS"] == -1) or (CONF["KEY_IDENTITY"] == -1):
        print("Error: Please define Omeka's configurations using the '-conf' argument, or a combination of the '-url', '-kid', and '-kcr' arguments")
        return False
    #Check if the URL exists
    request = requests.get(CONF["OMEKA_API_URL"])
    if request.status_code == 404:
        print('Error: Omeka-S URL does not exist')
        return False
    #all fine return True
    print('Omeka-S configuration is done!')
    return True

# Checks if <func_name> is a function handled (exists) and if the given <param> are suitable for it.
# It runs <func_name> in case everything is fine, otherwise it returns an error
def check_and_run(func_name, param):

    def is_int(s):
        try:
            int(s)
            return True
        except ValueError:
            return False

    if func_name == "get_rsctemp_class":
        if len(param) > 0:
            if is_int(param[0]):
                print(get_resource_class(param[0]))
                return True
        print("Error: the operation '"+func_name+"' takes 1 parameter:\n+ <resource_template_id>:integer")
        return False

    elif func_name == "get_rsctemp_prop":
        if len(param) > 0:
            if is_int(param[0]):
                print(get_resource_properties(param[0]))
                return True
        print("Error: the operation '"+func_name+"' takes 1 parameter:\n+ <resource_template_id>:integer")
        return False

    elif func_name == "prepare_payload":
        if len(param) > 0:
            if is_int(param[0]):
                print(prepare_payload(param[0]))
                return True
        print("Error: the operation '"+func_name+"' takes 1 parameter:\n+ <resource_template_id>:integer")
        return False

    elif func_name == "get_rsctemp_id":
        if len(param) > 0:
            print(get_template_id(param[0]))
            return True
        print("Error: the operation '"+func_name+"' takes 1 parameter:\n+ <template_label>:string")
        return False

    elif func_name == "get_item":
        if len(param) > 1:
            if (is_int(param[0])) and (is_int(param[1])):
                print(get_item(param[0], param[1])["data"])
                return True
        print("Error: the operation '"+func_name+"' takes 2 parameters:\n+ <item_id>:integer\n+ <template_resource_id>:integer ")
        return False

    elif func_name == "add_item":
        if len(param) > 1:
            if os.path.isfile(param[0]):
                with open(param[0]) as json_file:
                    item_data = json.load(json_file)
                    return add_item(item_data, param[1])
        print("Error: the operation '"+func_name+"' takes 2 parameters:\n+ <item_data>:string (path to .json file)\n+ <template_label>:string ")
        return False

    else:
        print("Error: the operation '"+omeka_fun+"' doesn't exist")
        return False

### Omeka's functions
### --------------------------

## Gets the resource class of a given <resource_template_id>
## Is called using "... -opr get_rsctemp_class"
def get_resource_class(resource_template_id):
    response = REQ_SESSION.get('{}/resource_templates/{}'.format(CONF["OMEKA_API_URL"], resource_template_id))
    if response.status_code == 404:
        return None
    return response.json()['o:resource_class']


## Gets basic info about the properties in a resource template including: property term, property id, data type
## Is called using "... -opr get_rsctemp_prop"
def get_resource_properties(resource_template_id):
    properties = []
    response = REQ_SESSION.get('{}/resource_templates/{}'.format(CONF["OMEKA_API_URL"], resource_template_id))
    if response.status_code == 404:
        return None
    data = response.json()
    for prop in data['o:resource_template_property']:
        prop_url = prop['o:property']['@id']
        # The resource template doesn't include property terms, so we have to go to the property data
        prop_response = REQ_SESSION.get(prop_url)
        prop_data = prop_response.json()
        # Give a default data type of literal if there's not one defined in the resource template
        data_type = 'literal' if prop['o:data_type'] is None else prop['o:data_type']
        properties.append({'term': prop_data['o:term'], 'property_id': prop_data['o:id'], 'type': data_type})
    return properties


##Create a skeleton payload for the creation of a new item based on the given resource template.
## Is called using "... -opr prepare_payload"
def prepare_payload(resource_template_id):
    resource_class = get_resource_class(resource_template_id)
    properties = get_resource_properties(resource_template_id)
    payload = {
        'o:resource_class': {
            '@id': resource_class['@id'],
            'o:id': resource_class['o:id']
        },
        'o:resource_template': {
            '@id': '{}/resource_templates/{}'.format(CONF["OMEKA_API_URL"], resource_template_id),
            'o:id': resource_template_id
        },
        "o:thumbnail": None,
        "o:media": [ ],
        "o:item_set": [ ]
    }
    for prop in properties:
        payload[prop['term']] = [{
            'type': prop['type'],
            'property_id': prop['property_id']
        }]
    return payload

## Is called using "... -opr get_rsctemp_id"
def get_template_id(template_label):
    params = {'label': template_label}
    response = REQ_SESSION.get('{}/resource_templates/'.format(CONF["OMEKA_API_URL"]), params=params)
    res = None
    if len(response.json()) > 1:
        res = response.json()[0]['o:id']
    return res


## Is called using "... -opr get_item"
def get_item(item_id, template_resource_id):
    id_prop = get_template_id(template_resource_id)
    item_class_id = get_resource_class(template_resource_id)
    params = {
        'property[0][joiner]': 'and', # and / or joins multiple property searches
        'property[0][property]': id_prop, # property id
        'property[0][type]': 'eq', # See above for options
        'property[0][text]': item_id,
        'resource_class_id': [item_class_id],
        'item_set_id': []
    }
    response = REQ_SESSION.get('{}/items'.format(CONF["OMEKA_API_URL"]), params=params)
    if response.status_code == 404:
        return None
    data = response.json()
    try:
        item_id = data[0]['o:id']
    except (IndexError, KeyError):
        item_id = None
    return {"id": item_id, "data": data}

def _populate_data(payload):
    #payload['schema:identifier'][0]['@value'] = item_data['id']
    #payload['schema:name'][0]['@value'] = item_data['value']
    #payload['schema:url'][0]['@id'] = 'http://nla.gov.au/nla.news-title{}'.format(item_data['id'])
    return payload

## Adds an item with the given <data> to Omeka. if <data> contains an "id" already in Omeka, then it updates it
## Is called using "... -opr add_item"
def add_item(item_data, template_label=""):
    template_id = get_template_id(template_label)
    item_id = get_item(item_data['id'], template_id)["id"]
    if not item_id:
        payload = prepare_payload(template_id)

        ### Populate the DATA to POST
        payload = _populate_data(payload)

        params = {
            'key_identity': CONF["KEY_IDENTITY"],
            'key_credential': CONF["KEY_CREDENTIALS"]
        }
        response = REQ_SESSION.post('{}/items/'.format(CONF["OMEKA_API_URL"]), json=payload, params=params)
        omeka_res_data = response.json()
        item_id = omeka_res_data['o:id']
    return item_id

### --------------------------
### --------------------------


if __name__ == "__main__":
    arg_parser = ArgumentParser("omekas_handler.py", description="")
    # Configuration Flags
    arg_parser.add_argument("-conf", "--configuration", dest="conf", required=False, help="A .json file holding Omeka's configurations")
    arg_parser.add_argument("-api", "--omekaurl", dest="api", required=False, help="Omeka base URL")
    arg_parser.add_argument("-kid", "--identity", dest="kid", required=False, help="The value of the Omeka's <KEY_IDENTITY>")
    arg_parser.add_argument("-kcr", "--credentials", dest="kcr", required=False, help="The value of the Omeka's <KEY_CREDENTIALS>")
    # -------------------
    arg_parser.add_argument("-opr", "--operation", dest="opr", nargs="+", required=True, help="An operation: 'create'\/'update'\/'delete'")


    args = arg_parser.parse_args()

    # Update the configuration variables and check if the given values are correct
    omeka_conf = {}
    if args.conf:
        with open(args.conf) as json_conf:
            CONF.update(json.load(json_conf))
    if args.api:
        CONF["OMEKA_API_URL"] = args.api
    if args.kid:
        CONF["KEY_IDENTITY"] = args.kid
    if args.kcr:
        CONF["KEY_CREDENTIALS"] = args.kcr
    if not check_omeka_conf():
        exit()
    # -------------------

    # Build request session
    retries = Retry(total=10, backoff_factor=1, status_forcelist=[ 502, 503, 504, 524 ])
    REQ_SESSION.mount('http://', HTTPAdapter(max_retries=retries))
    REQ_SESSION.mount('https://', HTTPAdapter(max_retries=retries))

    #Call an operation
    if args.opr:
        omeka_fun = None
        omeka_param = []
        if len(args.opr) > 0:
            omeka_fun = args.opr[0]
        if len(args.opr) > 1:
            omeka_param = args.opr[1:]

        check_and_run(omeka_fun, omeka_param)
