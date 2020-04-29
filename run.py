import requests , json , os
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
import mapping.mapping as m
import conf as c


REQ_SESSION = requests.Session()
retries = Retry(total=10, backoff_factor=1, status_forcelist=[ 502, 503, 504, 524 ])
REQ_SESSION.mount('http://', HTTPAdapter(max_retries=retries))
REQ_SESSION.mount('https://', HTTPAdapter(max_retries=retries))

params = {
    'key_identity': c.CONF["KEY_IDENTITY"],
    'key_credential': c.CONF["KEY_CREDENTIALS"]
}
print("\nc.CONF",c.CONF)
########################
############ manually
########################

# 1. upload ontologies
# 2. upload custom controlled vocabularies: use the same names as in vocabularies.json
# 3. copy the ids of vocabularies in vocabularies.json and substitute IDs in "templates" folder (except for City,District,Country)
# 4. reconcile City,District,Country to geonames and save mappings in vocabularies.json
# 5. upload templates where vocabularies are already selected (import in next instances -- control vocab ids)
# 6. download google spreadsheet tables as tsv in "tables" folder

########################
############ import
########################

# 7. call properties, classes and resource templates APIs, store ids in dedicated json files, return dictionaries "classes_ids", "property_ids","resource_templates_ids"
res_cl = os.path.isfile('resource_classes_ids.json')
prop = os.path.isfile('properties_ids.json')
res_tpl = os.path.isfile('resource_templates_ids.json')
if res_cl:
    with open('resource_classes_ids.json') as json_file:
        classes_ids = json.load(json_file)

else:
    classes_ids = m.get_ids(c.CONF["OMEKA_API_URL"], 'resource_classes')
if prop:
    with open('properties_ids.json') as json_file:
        property_ids = json.load(json_file)
else:
    property_ids = m.get_ids(c.CONF["OMEKA_API_URL"],'properties')
if res_tpl:
    with open('resource_templates_ids.json') as json_file:
        resource_templates_ids = json.load(json_file)
else:
    resource_templates_ids = m.get_ids(c.CONF["OMEKA_API_URL"],'resource_templates')


# 8. open vocabularies.json
with open("vocabularies.json") as json_file:
    vocabularies_ids = json.load(json_file)

print("\n\n\nvocab_ids",vocabularies_ids)
# 9. create 1 itemset called "palread"
# TODO method to avoid to create it twice (read in the json)
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
print(response)
omeka_res_data = response.json()
print("\nomeka_res_data",omeka_res_data)
itemset_id = omeka_res_data['o:id']
ids_dict[item_set] = itemset_id

# 11. store the itemset id in "item_sets_ids.json"
with open("item_sets_ids.json","w") as itemsets_ids:
    itemsets_ids.write(json.dumps(ids_dict))
itemsets_ids.close()

# 12. query tables, create payloads, wherein substitute all properties IDs, classes and vocabularies IDs with the one mapped in the json files
data = m.read_tables("tables", "item_sets_ids.json",property_ids,classes_ids,resource_templates_ids,vocabularies_ids, "create")
print("\n\n\n\ndata",data)
# 13. iterate over payloads and upload
for payload in data:
    response = REQ_SESSION.post('{}/items/'.format(c.CONF["OMEKA_API_URL"]), json=payload, params=params)
print("\n\n\n\nresponse",response.json())
# 14. dump data created in "created_items.json"
dataset = REQ_SESSION.get('{}/items/'.format(c.CONF["OMEKA_API_URL"]))
with open("created_items.json","w") as items:
    items.write(json.dumps(dataset.json()))
items.close()
print("\n\n\n\nresponse dataset",dataset.json())
# 15. lookup for certain tables/rows

# ti passo: filename, value_string, property

# check in created_items.json property:value_string

# 16. if entities do not exist, create them

### ---> template_id = map_to_entity(filename,resource_templates_ids)
### prepare payload
# payload = {
#         "@type":["o:Item"],
#         "o:resource_class": {
#             "o:id": resource_class_id,
#             '@id': '{}/resource_class/{}'.format(c.CONF["OMEKA_API_URL"], resource_class_id)},
#         "o:item_set": [{"o:id": int(item_set_id)}],
#         "o:resource_template": {
#             "o:id": template_id,
#             '@id': '{}/resource_templates/{}'.format(c.CONF["OMEKA_API_URL"], template_id)
#             }
#           PAYLOAD PROPERTIES
#          }

# upload

# 17. dump (overwrite) data created in "created_items.json"

# dataset = REQ_SESSION.get('{}/items/'.format(c.CONF["OMEKA_API_URL"]))
# with open("created_items.json","w") as items:
#     items.write(json.dumps(dataset.json()))
# items.close()
# print("\n\n\n\nresponse dataset",dataset.json())



# 18. query again tables and create payloads
# update_data = m.read_tables("tables", "item_sets_id.json", "update")

# 19. iterate over payloads and upload
# for payload, resource_id in update_data:
#     response = REQ_SESSION.patch('{}/items/{}'.format(c.CONF["OMEKA_API_URL"],resource_id), json=payload, params=params)

# 20. dump (overwrite) data created in "created_items.json"

# 21. remove temporary properties (or not?)
