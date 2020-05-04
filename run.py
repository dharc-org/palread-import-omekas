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

# 7. call properties, classes and resource templates APIs, store ids in dedicated json files, return dictionaries 'resource_classes','properties','resource_templates'
#--- e.g. dict_ids["resource_classes"] -> a dict of all the resource_classes in Omeka
dict_ids = m.get_ids(c.CONF["OMEKA_API_URL"],['resource_classes','properties','resource_templates'])
#print(dict_ids)

# 8. open vocabularies.json
with open(c.VOCABULARIES_INDEX) as json_file:
    vocabularies_ids = json.load(json_file)
#print("\n\n\nvocab_ids",vocabularies_ids)

# 9, 10, 11. create the item-sets (in this case only 1 itemset called "palread") and get its id
for itemset_val in c.ITEM_SETS:
    itemset_id,payload = m.prepare_item_set(itemset_val, dict_ids["properties"])
    if itemset_id == "none":
        response = REQ_SESSION.post('{}/item_sets/'.format(c.CONF["OMEKA_API_URL"]), json=payload, params=params)
        if response.status_code == 200:
            ids_dict = {}
            omeka_res_data = response.json()
            itemset_id = omeka_res_data['o:id']
            ids_dict[itemset_val] = itemset_id
            with open(c.ITEM_SETS_INDEX,"w") as itemsets_file:
                itemsets_file.write(json.dumps(ids_dict))
            itemsets_file.close()
        else:
            #an error occured STOP the process
            sys.exit("Error while creating the Item-set!")


# 12. query tables, create payloads, wherein substitute all properties IDs, classes and vocabularies IDs with the one mapped in the json files
data = m.read_tables(dict_ids["properties"],dict_ids["resource_classes"],dict_ids["resource_templates"],vocabularies_ids, "create")
##print("\n\n\n\ndata",data)

# 13. iterate over payloads and upload
for payload in data:
    response = REQ_SESSION.post('{}/items/'.format(c.CONF["OMEKA_API_URL"]), json=payload, params=params)

# 14. dump data created in "created_items.json"
dataset = REQ_SESSION.get('{}/items/'.format(c.CONF["OMEKA_API_URL"]))
m.backup_items(dataset.json(), dict_ids["resource_classes"])

# 15. lookup for certain tables/rows
# 16. if entities do not exist, create them
# 17. dump (overwrite) data created in "created_items.json"



# 18. query again tables and create payloads
# update_data = m.read_tables("item_sets_id.json", "update")

# 19. iterate over payloads and upload
# for payload, resource_id in update_data:
#     response = REQ_SESSION.patch('{}/items/{}'.format(c.CONF["OMEKA_API_URL"],resource_id), json=payload, params=params)

# 20. dump (overwrite) data created in "created_items.json"

# 21. remove temporary properties (or not?)
