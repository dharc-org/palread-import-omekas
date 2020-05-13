import os , json , csv ,re , itertools , pprint , requests
import mapping.preprocessing as p
import conf as c
from langdetect import detect
from collections import defaultdict

pp = pprint.PrettyPrinter(indent=4)

# prepare the item-set payload
def prepare_item_set(a_value, property_ids):
    return {
        "dcterms:title": [{
            "type": "literal",
            "property_id": int(property_ids["dcterms:title"]["id"]),
            "@value": a_value
        }]
    }

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

def map_to_entity(entity_index,resource_templates_ids=None):
    entity_obj = c.ENTITIES[entity_index]
    entity_obj["id"] = c.ENTITIES[entity_index]
    template_id,e_class,item_set = None,None,None
    e_class, item_set = entity_obj["e_class"], entity_obj["item_set"]
    if entity_obj["label"] in resource_templates_ids:
        template_id = resource_templates_ids[entity_obj["label"]]["id"]
    return e_class,template_id, entity_index, item_set

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

        elems_dict = {}
        l_elems = get_from_omeka(api_url,api_opr)

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


# checks if any item in <items> with resouce_template = <template_id> has a property <prop_k> == <prop_v>
def get_item_id(prop_k, val, items, template_id):
    for i_item in range(0,len(items)):
        item = items[i_item]
        if "o:resource_template" in item:
            if "o:id" in item["o:resource_template"]:
                if item["o:resource_template"]["o:id"] == template_id:
                    if prop_k in item:
                        #check if one of the property values == <val>
                        for a_prop in item[prop_k]:
                            if a_prop["@value"] == val:
                                return i_item
    return None


def lookup_item(list_lookup_items,item,item_type,resource_templates_ids, property_ids, classes_ids, vocabularies_ids):
    with open(c.MAPPING_INDEX) as mapping_file:
        mapping = json.load(mapping_file)
    with open(c.ITEMS_INDEX) as items_file:
        items = json.load(items_file)

    new_items = []
    for k,v in mapping[item_type]["lookup"].items():
        if k in item:
            lookup_prop_v = item[k]
            ## Take only first elem of the property
            ## NOTE: Maybe we must check all valeues
            lookup_prop_v = lookup_prop_v[0]["@value"]
            dest_prop = v["dest_prop"]
            res_class, template_id, entity, item_set = map_to_entity(v["entity"],resource_templates_ids)
            item_set_id = get_item_set_id(item_set)

            if item_set_id != None and template_id != None:
                #Check the lookup mapping rule
                item_id_index = get_item_id(dest_prop, lookup_prop_v, items, template_id)
                #Check if item has been already added during the process
                item_id_lookup = get_item_id(dest_prop, lookup_prop_v, list_lookup_items, template_id)
                #print(k,lookup_prop_v,dest_prop,item_id_index,item_id_lookup)

                #add it in case item does not exist in <items> and <list_lookup_items>
                if item_id_index == None and item_id_lookup == None:
                    ## CREATE a ROW and change the property value
                    row = gen_table_row(v["entity"])
                    row[v["column"]] = lookup_prop_v
                    o_item = create_item(res_class, template_id, row, item_set_id, entity, property_ids, classes_ids, vocabularies_ids)
                    new_items.append(o_item)

    return new_items

# read tsv files
def read_tables(property_ids,classes_ids,resource_templates_ids,vocabularies_ids, operation="create"):
    # TODO add param for item ID if it's an update
    list_items = []
    for filename in os.listdir(c.TABLES_DATA_PATH):
        if filename.endswith(".tsv") and filename in c.TABLES_DICT:
            # TODO first upload vocabularies and map cities

            entity_index = c.TABLES_DICT[filename]
            res_class,template_id,entity,item_set = map_to_entity(entity_index,resource_templates_ids)
            #print("resource_class, template_id, entity, item_set:", res_class,template_id,entity,item_set)
            # Note for the future me: the mapping implies that for each table (tsv) corresponds _only one_ entity
            # To reuse this code in the future, the 1-to-1 relation (table-entity) must be respected

            #Get the item set ID
            item_set_id = get_item_set_id(item_set)

            #if no item set or template id is provided for the examined table move to next one
            if item_set_id == None or template_id == None:
                continue
                #return "Error: the item set does not exist"

            with open(c.TABLES_DATA_PATH+'/'+filename) as tsv_file:
                next(tsv_file)
                reader = csv.DictReader(tsv_file, delimiter='\t')
                for row in reader:
                    o_item = create_item(res_class,template_id,row,item_set_id,entity,property_ids,classes_ids,vocabularies_ids)
                    if operation == 'create':
                        list_items.append(o_item)
                    if operation == 'lookup':
                        list_lookup_items = lookup_item(list_items,o_item,entity,resource_templates_ids, property_ids, classes_ids, vocabularies_ids)
                        for item in list_lookup_items:
                            list_items.append(item)
                    if operation == 'update':
                        o_item = update_item(row,item_set_id,entity)

    #pp.pprint(list_items)
    return list_items


#Backup only the items included in <ITEM_SETS> (congiguration file)
def backup_items(d):
    with open(c.ITEM_SETS_INDEX) as json_file:
        item_sets_ids = json.load(json_file)

    ready_for_file = []
    for item in d:
        if "o:item_set" in item:
            for item_set in item["o:item_set"]:
                if item_set["o:id"] in item_sets_ids.values():
                    ready_for_file.append(item)
                    break

    with open(c.ITEMS_INDEX,"w") as items_index_file:
        items_index_file.write(json.dumps(ready_for_file))
    items_index_file.close()


def get_from_omeka(api_url, api_opr, curr_page=1, curr_data=[]):
    response = requests.get(api_url+"/"+api_opr+"?page="+str(curr_page))
    if response.status_code == 200:
        l_elems = json.loads(response.text)
        if len(l_elems) == 0:
            return curr_data
        else:
            return get_from_omeka(api_url, api_opr, curr_page+1, curr_data + l_elems)
    else:
        return curr_data

def get_item_set_id(item_set_name):
    item_set_id = None
    with open(c.ITEM_SETS_INDEX) as json_file:
        item_sets_data = json.load(json_file)
        if item_set_name in item_sets_data:
            item_set_id = item_sets_data[item_set_name]
    return item_set_id

def gen_table_row(res_class):
    a_table = None
    for k,v in c.TABLES_DICT.items():
        if v == res_class:
            a_table = k

    if a_table == None:
        return None

    with open(c.TABLES_DATA_PATH+'/'+a_table) as tsv_file:
        next(tsv_file)
        reader = csv.DictReader(tsv_file, delimiter='\t')
        for row in reader:
            header = row
            break
    return dict.fromkeys(header, None)
