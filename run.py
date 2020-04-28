import requests
import mapping as m
import conf as c


REQ_SESSION = requests.Session()
retries = Retry(total=10, backoff_factor=1, status_forcelist=[ 502, 503, 504, 524 ])
REQ_SESSION.mount('http://', HTTPAdapter(max_retries=retries))
REQ_SESSION.mount('https://', HTTPAdapter(max_retries=retries))

params = {
    'key_identity': c.CONF["KEY_IDENTITY"],
    'key_credential': c.CONF["KEY_CREDENTIALS"]
}

########################
############ manually
########################

# 1. upload ontology
### TODO add classes to the ontology

# 2. upload custom controlled vocabularies
### put the ids of vocabularies in vocabularies.json
### reconcile geonames and save mapping in vocabularies.json

# 3. upload templates where also vocabularies are selected
### put the ids of templates in templates_ids.json

# 4. download google spreadsheet tables as tsv in tables folder (manually)

########################
############ import
########################


# 1. call properties and classes API, store ids in dedicated json files, return dictionaries "classes_ids", "property_ids"
classes_ids, property_ids,resource_templates_ids = m.get_ids(c.CONF["OMEKA_API_URL"])[0], m.get_ids(c.CONF["OMEKA_API_URL"])[1]

# 2. create 1 itemset, return its id "itemset_id"
ids_dict = {}
item_set = "palread"
payload = {
    "dcterms:title": [{
        "type": "literal",
        "property_id": int(property_ids["dcterms:title"]["id"]),
        "@value": item_set
    }]
}

response = REQ_SESSION.post('{}/item_sets/'.format(c.CONF["OMEKA_API_URL"]), json=payload, params=params)
omeka_res_data = response.json()
itemset_id = omeka_res_data['o:id']
ids_dict[item_set] = itemset_id

itemsets_ids = open("item_sets_ids.json")
itemsets_ids.write(json.dumps(ids_dict))
itemsets_ids.close()

# query tables, create payloads, and substitute all properties IDs with the one mapped in the properties file
data = m.read_tables("tables", "item_sets_id.json", "create",property_ids,classes_ids,resource_templates_ids)

# iterate over payloads and upload
for payload in data:
    response = REQ_SESSION.post('{}/items/'.format(c.CONF["OMEKA_API_URL"]), json=payload, params=params)
    # return response and save the dictionary in a json

# TODO preliminary update

# patch
update_data = m.read_tables("tables", "item_sets_id.json", "update")
for payload, resource_id in update_data:
    response = REQ_SESSION.patch('{}/items/{}'.format(c.CONF["OMEKA_API_URL"],resource_id), json=payload, params=params)
