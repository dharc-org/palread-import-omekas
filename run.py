import requests , json , os , sys
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
#print("\nc.CONF",c.CONF)
print("\n")

########################
############ manually
########################

# 1. upload ontologies
# 2. upload custom controlled vocabularies: use the same names as in vocabularies.json
# 3. copy the ids of vocabularies in vocabularies.json and substitute IDs in "templates" folder (except for City,District,Country)
# 4. reconcile City,District,Country to geonames and save mappings in vocabularies.json
# 5. upload templates where vocabularies are already selected (import in next instances -- control vocab ids match with correct number)
# 6. download google spreadsheet tables as tsv in "tables" folder

# !!! doublecheck API url and credentials in conf.py

########################
############ import
########################

# 7. call properties, classes and resource templates APIs, store ids in dedicated json files, return dictionaries 'resource_classes','properties','resource_templates'
#--- e.g. dict_ids["resource_classes"] -> a dict of all the resource_classes in Omeka
print("Get from Omeka the 'resource_classes', 'properties', and 'resource_templates' ...")
dict_ids = m.get_ids(c.CONF["OMEKA_API_URL"],['resource_classes','properties','resource_templates'])
print("-> Done\n")

# 8. open vocabularies.json
with open(c.VOCABULARIES_INDEX) as json_file:
    vocabularies_ids = json.load(json_file)


# 9, 10, 11. create the item-sets and get the ids
print("Add item-sets ...")
all_item_sets = dict()
response = REQ_SESSION.get('{}/item_sets/'.format(c.CONF["OMEKA_API_URL"]))
for an_items_set in response.json():
    all_item_sets[an_items_set["o:title"]] = an_items_set["o:id"]

my_item_sets = {}
for itemset_val in c.ITEM_SETS:
    if itemset_val not in all_item_sets:
        payload = m.prepare_item_set(itemset_val, dict_ids["properties"])
        response = REQ_SESSION.post('{}/item_sets/'.format(c.CONF["OMEKA_API_URL"]), json=payload, params=params)
        if response.status_code == 200:
            omeka_res_data = response.json()
            itemset_id = omeka_res_data['o:id']
        else:
            #an error occured STOP the process
            sys.exit("Error while creating the Item-set!")
    else:
        itemset_id = all_item_sets[itemset_val]
    my_item_sets[itemset_val] = itemset_id

with open(c.ITEM_SETS_INDEX,"w") as itemsets_file:
    itemsets_file.write(json.dumps(my_item_sets))
itemsets_file.close()

print("-> Done\n")

## -------
## CREATE
## -------
print("Add items ...")
# 12. query tables, create payloads, wherein substitute all properties IDs, classes and vocabularies IDs with the one mapped in the json files
data = m.read_tables(dict_ids["properties"],dict_ids["resource_classes"],dict_ids["resource_templates"],vocabularies_ids, "create")
print("-> tables read")

# 13. iterate over payloads and upload
print("-> add [",len(data), "] item/s to Omeka")
for payload in data:
    response = REQ_SESSION.post('{}/items/'.format(c.CONF["OMEKA_API_URL"]), json=payload, params=params)

# 14. dump data created in "created_items.json"
print("-> backup all the items in Omeka")
dataset = REQ_SESSION.get('{}/items/'.format(c.CONF["OMEKA_API_URL"]))
dataset = m.get_from_omeka(c.CONF["OMEKA_API_URL"], "items")
m.backup_items(dataset)

## -------
## Lookup
## -------
print("Items lookup ...")
# 15. lookup for certain tables/rows following the rules in mapping.json; if entities do not exist, create them
print("-> read the tables")
data = m.read_tables(dict_ids["properties"],dict_ids["resource_classes"],dict_ids["resource_templates"],vocabularies_ids, "lookup")

# 16. iterate over payloads and upload
print("-> add [",len(data), "] new item/s to Omeka")
for payload in data:
    response = REQ_SESSION.post('{}/items/'.format(c.CONF["OMEKA_API_URL"]), json=payload, params=params)

# 17. dump data created in "created_items.json"
print("-> backup all the items in Omeka")
dataset = REQ_SESSION.get('{}/items/'.format(c.CONF["OMEKA_API_URL"]))
dataset = m.get_from_omeka(c.CONF["OMEKA_API_URL"], "items")
m.backup_items(dataset)
print("-> Done\n")


## -------
## Update
## -------

# 18. update data
print("Update items...")
updated_data = m.read_tables(dict_ids["properties"],dict_ids["resource_classes"],dict_ids["resource_templates"],vocabularies_ids, "update")
print("-> tables read")
for update_payload in updated_data:
    res_id = update_payload["o:item"][0]["o:id"]

    # get item payload to be updated
    response = REQ_SESSION.get('{}/items/{}'.format(c.CONF["OMEKA_API_URL"],res_id))
    current_data = response.json()
    for k,v in update_payload.items():
        print("\nTO BE ADDED",k,v)
        current_data[k] = v

    print(current_data)
    resp = REQ_SESSION.put('{}/items/{}'.format(c.CONF["OMEKA_API_URL"],res_id), json=current_data, params=params)
    print(resp)
print("-> data updated!")

# 19. dump data created in "created_items.json"
print("-> backup all the items in Omeka")
dataset = REQ_SESSION.get('{}/items/'.format(c.CONF["OMEKA_API_URL"]))
dataset = m.get_from_omeka(c.CONF["OMEKA_API_URL"], "items")
m.backup_items(dataset)
print("-> Done\n")

# TODO
# 20. remove temporary properties (or not?)
