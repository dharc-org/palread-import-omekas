import requests
import mapping as m

# prepare session
# TODO remove CONF
CONF = {
    "CONTENT_TYPE": "application/json",
    "KEY_IDENTITY": "MY_IDENTITY",
    "KEY_CREDENTIALS": "MY_CREDENTIALS",
    "OMEKA_API_URL": "http://http://137.204.168.20/api"
}

REQ_SESSION = requests.Session()
retries = Retry(total=10, backoff_factor=1, status_forcelist=[ 502, 503, 504, 524 ])
REQ_SESSION.mount('http://', HTTPAdapter(max_retries=retries))
REQ_SESSION.mount('https://', HTTPAdapter(max_retries=retries))

params = {
    'key_identity': CONF["KEY_IDENTITY"],
    'key_credential': CONF["KEY_CREDENTIALS"]
}

# upload ontology (manually)

# call properties API
classes_ids, property_ids = m.get_ids(CONF["OMEKA_API_URL"])[0], m.get_ids(CONF["OMEKA_API_URL"])[1]

# create itemsets
items_sets = ["person", "life event", "organisation", "publisher", "literary event"]
ids_dict = {}
for item_set in item_sets:
    payload = {
        "dcterms:title": [{
            "type": "literal",
            "property_id": int(property_ids["dcterms:title"]["id"]),
            "@value": item_set
        }]
    }

    response = REQ_SESSION.post('{}/item_sets/'.format(CONF["OMEKA_API_URL"]), json=payload, params=params)
    omeka_res_data = response.json()
    itemset_id = omeka_res_data['o:id']
    ids_dict[item_set] = itemset_id

itemsets_ids = open("item_sets_ids.json")
itemsets_ids.write(json.dumps(ids_dict))
itemsets_ids.close()

# upload templates (automatically or automatically)

# upload controlled vocabularies (automatically or automatically)

###### vocabularies
# TODO new payload for these vocabularies/itemsets
# reconcile geonames and leave string if palestine (to be reconciled later by Majd)
# upload vocabularies that are itemsets
# save results in vocabularies.json

# download google spreadsheet tables as tsv in tables folder (manually)

data = m.read_tables("tables", "item_sets_id.json", "create")
# TODO substitute all properties IDs in the payload

# iterate over payloads and upload
for payload in data:
    response = REQ_SESSION.post('{}/items/'.format(CONF["OMEKA_API_URL"]), json=payload, params=params)
    # return response and save the dictionary in a json

# TODO preliminary update

# patch
update_data = m.read_tables("tables", "item_sets_id.json", "update")
for payload, resource_id in update_data:
    response = REQ_SESSION.patch('{}/items/{}'.format(CONF["OMEKA_API_URL"],resource_id), json=payload, params=params)
