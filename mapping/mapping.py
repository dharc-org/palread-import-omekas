import os , json , csv ,re , itertools , pprint , requests
import mapping.preprocessing as p
import conf as c
from langdetect import detect
from collections import defaultdict

pp = pprint.PrettyPrinter(indent=4)

# prepare the item-set payload
def prepare_item_set(a_value, property_ids):
    with open(c.ITEM_SETS_INDEX) as json_file:
        item_sets_ids = json.load(json_file)
    item_set_id = "none"
    payload = {
        "dcterms:title": [{
            "type": "literal",
            "property_id": int(property_ids["dcterms:title"]["id"]),
            "@value": a_value
        }]
    }
    print(a_value,item_sets_ids)
    if a_value in item_sets_ids:
        item_set_id = item_sets_ids[a_value]

    return (item_set_id,payload)

# POST /api/:api_resource
def create_item(item_class,template_id, data_row, item_set_id=None, item_type=None,property_ids=None,classes_ids=None,vocabularies_ids=None):
    with open(c.MAPPING_INDEX) as json_file:
        mapping = json.load(json_file)
    data = prepare_json(data_row, mapping[item_type]["create"],property_ids,vocabularies_ids)
    resource_class_id = classes_ids[item_class]["id"]
    create_json = {
            "@type":["o:Item"],
            "o:resource_class": {
                "o:id": resource_class_id,
                '@id': '{}/resource_class/{}'.format(c.CONF["OMEKA_API_URL"], resource_class_id)},
            "o:item_set": [{"o:id": int(item_set_id)}],
            "o:resource_template": {
                "o:id": template_id,
                '@id': '{}/resource_templates/{}'.format(c.CONF["OMEKA_API_URL"], template_id)
                }
             }
    for k,v in data.items():
        create_json[k] = v
    return create_json

# PATCH /api/:api_resource/:id
def update_item(data_row, item_set_id=None, item_type=None):
    # TODO other stuff before
    with open(c.MAPPING_INDEX) as json_file:
        mapping = json.load(json_file)
    data = fill_json(data_row, mapping[item_type]["update"])
    update_json = 'TODO'
    return update_json

def map_to_entity(filename=None,resource_templates_ids=None):
    entity,template_id,e_class,item_set = None,None,None,None
    if filename is not None:
        if filename in c.TABLES_DICT:
            table_dict = c.TABLES_DICT[filename]
            entity, e_class, item_set = table_dict["entity"], table_dict["e_class"], table_dict["item_set"]
            if table_dict["label"] in resource_templates_ids:
                template_id = resource_templates_ids[table_dict["label"]]["id"]
    return e_class,template_id, entity, item_set

def replace_value(val,data_row):
    if '-->' in val:
        vocab = None
        column = val.split('-->',1)[1] # get column name
        if ';' in column:
            column,vocab = column.split(';',1)

        funct = val.split('-->',1)[0].replace("op:","") # call the function specified in preprocessing
        if funct == "create_name":
            value = "data_row,'"+column+"'"
        else:
            value = data_row[column]

        if vocab is not None:
            new_val = eval('p.'+funct+'("'+str(value).strip()+'","'+vocab.strip()+'")')
        else:
            if funct == "create_name":
                new_val = eval('p.'+funct+'('+value+')')
            else:
                new_val = eval('p.'+funct+'("'+str(value).strip()+'")')  # replace the final json
    if '-->' not in val:
        new_val = data_row[val]
    return new_val

def prepare_json(data_row,mapping,property_ids,vocabularies_ids):
    data = fill_json(data_row, mapping,vocabularies_ids)
    data = clean_dict(data)
    data = pop_empty(data)
    data = detect_lang(data)
    data = change_prop_id(data,property_ids)
    return data

def fill_json(data_row, item_properties,vocabularies_ids):
    item_data = {k:v for k,v in item_properties.items()}
    for prop, values_list in item_data.items():
        for value_dict in values_list:
            object = "@value" if "@value" in value_dict else "@id"
            # Note for future me: "op:" has always to be in the mapping, even if it's just for stripping
            if "op:" in value_dict[object]:
                # pre-processing operations
                if "split_values" in value_dict[object]:
                    values = replace_value(value_dict[object],data_row)
                    if isinstance(values, str):
                        value_dict[object] = replace_value(value_dict[object],data_row)
                    elif isinstance(values, list) and len(values) >= 1:
                        count_prop = 0
                        for value in values:
                            print("value",value)
                            count_prop += 1
                            new_dict = {}
                            # if "property_id" in value_dict:
                            #     new_dict["property_id"] = count_prop
                            new_dict[object] = value
                            if "type" in value_dict:
                                new_dict["type"] = value_dict["type"]
                            if value_dict["type"] == "literal":
                                if "lang" in value_dict:
                                    new_dict["lang"] = value_dict["lang"]
                            values_list.append(new_dict)
                            print("new_dict",new_dict)
                else:
                    if "customvocab" in value_dict["type"]:
                        vocab = value_dict["type"].split(":")[1]
                        value_dict["type"] = "customvocab:"+str(vocabularies_ids[vocab]["id"])
                    value_dict[object] = replace_value(value_dict[object],data_row)
    #print("item_data",item_data)
    return item_data

def clean_dict(item_data):
    new_dict = defaultdict(list)
    for prop, values_list in item_data.items():
        for value_dict in values_list:
            object = "@value" if "@value" in value_dict.keys() else "@id"
            if "op:" in value_dict[object] \
                or value_dict[object] is None \
                or len(value_dict[object].strip()) == 0 \
                or value_dict[object] == 'None' \
                or value_dict[object] == "''":
                #values_list.remove(value_dict)
                pass
            else:
                new_dict[prop].append(value_dict)
    clean_dict = dict(new_dict)
    return clean_dict

def pop_empty(item_data):
    item_data = { k : v for k,v in item_data.items() if v}
    return item_data

def detect_lang(item_data):
    for prop, values_list in item_data.items():
        for value_dict in values_list:
            if "lang" in value_dict and value_dict["lang"] == "detect":
                lang = detect(value_dict["@value"])
                lang = "ar" if lang == 'ar' else "en"
                value_dict["lang"] = lang
    return item_data

def change_prop_id(item_data,property_ids):
    for prop, values_list in item_data.items():
        for dictionary in values_list:
            dictionary["property_id"] = property_ids[prop]["id"]
        # if len(values_list) == 1 and values_list[0]["property_id"] != '1':
        #     values_list[0]["property_id"] = '1'
    return item_data

def get_ids(api_url,lookup):
    res = {}
    for api_opr in lookup:
        res[api_opr] = {}
        f_name = c.INDEX_DATA_PATH+"/"+api_opr+"_ids"+".json"
        if os.path.isfile(f_name):
            with open(f_name) as json_file:
                res[api_opr] = json.load(json_file)
        else:
            response = requests.get(api_url+"/"+api_opr)
            elems_dict = {}
            if response.status_code == 200:
                l_elems = json.loads(response.text)
                ##print(response.text)
                ##iterate over all elems
                for elem in l_elems:
                    id = elem["o:id"]
                    label = elem['o:label']
                    term = elem['o:term'] if "o:term" in elem.keys() else label
                    elems_dict[term]={'label':label,'id':id}

            #the json file is empty in case of an error with the request
            res[api_opr] = elems_dict
            d=open(f_name,'w')
            d.write(json.dumps(elems_dict))
            d.close()

    return res

# read tsv files
def read_tables(property_ids,classes_ids,resource_templates_ids,vocabularies_ids, operation="create"):
    # TODO add param for item ID if it's an update
    list_items = []
    for filename in os.listdir(c.TABLES_DATA_PATH):
        if filename.endswith(".tsv") and filename in c.TABLES_DICT:
            # TODO first upload vocabularies and map cities
            res_class,template_id,entity,item_set = map_to_entity(filename,resource_templates_ids)
            print("resource_class, template_id, entity, item_set:", res_class,template_id,entity,item_set)
            # Note for the future me: the mapping implies that for each table (tsv) corresponds _only one_ entity
            # To reuse this code in the future, the 1-to-1 relation (table-entity) must be respected

            #Check if the addressed item set is already created
            item_set_id = None
            with open(c.ITEM_SETS_INDEX) as json_file:
                item_sets_data = json.load(json_file)
                if item_set in item_sets_data:
                    item_set_id = item_sets_data[item_set]
            print("item_set_id",item_set_id)
            #if no item set or template id is provided for the examined table move to next one
            if item_set_id == None or template_id == None:
                continue
                #return "Error: the item set does not exist"

            with open(c.TABLES_DATA_PATH+'/'+filename) as tsv_file:
                next(tsv_file)
                reader = csv.DictReader(tsv_file, delimiter='\t')
                for row in reader:
                    if operation == 'create':
                        o_item = create_item(res_class,template_id,row,item_set_id,entity,property_ids,classes_ids,vocabularies_ids)
                        #print("item payload: ",o_item)
                        # The Item should be added (inserted in list_items) only if not already in Omeka
                        id_in_omeka = get_item_id(o_item,classes_ids)
                        if id_in_omeka == None:
                            list_items.append(o_item)
                    if operation == 'lookup':
                        pass
                        # add in mapping.json which fields to check, and which property
                        # CONF KEY INDEXES maybe does not make sense now
                        # return list of tuples, e.g.(Maria, class_person, prop_name)
                        # lookup in data dump if exist otherwise create and do a new backup dump (overwrite)
                        ## TODO control if uploaded classes for resources!
                    if operation == 'update':
                        o_item = update_item(row,item_set_id,entity)

    #pp.pprint(list_items)
    return list_items


# Build a key to use inside the created_items.json according to the c.KEYS_INDEX
# Format: (<resource_class>,<property_value>)
def build_key(item, resource_classes):
    rsc_class = None
    for rsc_class_k, rsc_class_k_val in resource_classes.items():
        if rsc_class_k_val["id"] == item["o:resource_class"]["o:id"]:
            rsc_class = rsc_class_k

    if (rsc_class != None) and (rsc_class in c.KEYS_INDEX):
        prop = c.KEYS_INDEX[rsc_class]
        prop_val = item[prop]
        if prop_val != None:
            ##Take only first elem of the property
            prop_val = prop_val[0]["@value"]
        return (prop,prop_val)
    return None

# Backup the created items in the created_items.json file
# Format: {<Key>:<PAYLOAD>}
def backup_items(l_omeka_items, resource_classes):
    dict_omeka_items = {}
    for omeka_item in l_omeka_items:
        #define the key#
        build_key(omeka_item, resource_classes)
        dict_omeka_items[a_key] = omeka_item
    #write
    with open(c.ITEMS_INDEX,"w") as items_index_file:
        items_index_file.write(json.dumps(dict_omeka_items))
    items_index_file.close()

# Returns the item id if is already in omeka (and in created_items.json)
# else returns None
def get_item_id(item, resource_classes):
    item_key = build_key(item, resource_classes)
    with open(c.ITEMS_INDEX) as json_file:
        created_items = json.load(json_file)
    if item_key in created_items:
        return created_items[item_key]["o:id"]
    else:
        return None


# save tables as tsv in the same folder
# fill the json file with ids of itemsets
# call read_tables to create a list of items
