import requests , json
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

# 1. upload ontologies
# 2. upload custom controlled vocabularies: use the same names as in vocabularies.json
# 3. copy the ids of vocabularies in vocabularies.json (except for City,District,Country)
# 4. reconcile City,District,Country to geonames and save mappings in vocabularies.json
# 5. upload templates where vocabularies are already selected (manually the first time and import in next instances)
# 6. download google spreadsheet tables as tsv in "tables" folder

########################
############ import
########################

# 7. call properties, classes and resource templates APIs, store ids in dedicated json files, return dictionaries "classes_ids", "property_ids","resource_templates_ids"
classes_ids, property_ids,resource_templates_ids = m.get_ids(c.CONF["OMEKA_API_URL"])[0], m.get_ids(c.CONF["OMEKA_API_URL"])[1], m.get_ids(c.CONF["OMEKA_API_URL"])[2]

# 8. open vocabularies.json
with open("vocabularies.json") as json_file:
    vocabularies_ids = json.load(json_file)

# 9. create 1 itemset called "palread"
ids_dict = {}
item_set = "palread"
payload = {
    "dcterms:title": [{
        "type": "literal",
        "property_id": int(property_ids["dcterms:title"]["id"]),
        "@value": item_set
    }]
}

# 10. return the itemset id
response = REQ_SESSION.post('{}/item_sets/'.format(c.CONF["OMEKA_API_URL"]), json=payload, params=params)
omeka_res_data = response.json()
itemset_id = omeka_res_data['o:id']
ids_dict[item_set] = itemset_id

# 11. store the itemset id in "item_sets_ids.json"
itemsets_ids = open("item_sets_ids.json")
itemsets_ids.write(json.dumps(ids_dict))
itemsets_ids.close()

# 12. query tables, create payloads, wherein substitute all properties IDs, classes and vocabularies IDs with the one mapped in the json files
data = m.read_tables("tables", "item_sets_id.json", "create",property_ids,classes_ids,resource_templates_ids,vocabularies_ids)

# 13. iterate over payloads and upload
for payload in data:
    response = REQ_SESSION.post('{}/items/'.format(c.CONF["OMEKA_API_URL"]), json=payload, params=params)

# 14. dump data created in "created_items.json"
data = REQ_SESSION.get('{}/item_sets/'.format(c.CONF["OMEKA_API_URL"]))
items = open("created_items.json")
items.write(json.dumps(data))
items.close()

# TODO lookup update

# patch
# update_data = m.read_tables("tables", "item_sets_id.json", "update")
# for payload, resource_id in update_data:
#     response = REQ_SESSION.patch('{}/items/{}'.format(c.CONF["OMEKA_API_URL"],resource_id), json=payload, params=params)
