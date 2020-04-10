import os , json , csv ,re , itertools , pprint
import preprocessing as p
from langdetect import detect

pp = pprint.PrettyPrinter(indent=4)

# POST /api/:api_resource
def create_item(data_row, item_set_id=None, item_type=None):
    with open("mapping.json") as json_file:
        mapping = json.load(json_file)
    data = prepare_json(data_row, mapping[item_type]["create"])
    create_json = {
            "@type":"o:Item",
            "o:item_set": [{"o:id": int(item_set_id)}],
             }
    for k,v in data.items():
        create_json[k] = v
    return create_json

# PATCH /api/:api_resource/:id
def update_item(data_row, item_set_id=None, item_type=None):
    # TODO other stuff before
    with open("mapping.json") as json_file:
        mapping = json.load(json_file)
    data = fill_json(data_row, mapping[item_type]["update"])
    update_json = 'TODO'
    return update_json

def map_to_entity(filename=None):
    entity = None
    if filename is not None:
        if filename == 'PalREAD_authorities - People.tsv':
            entity = 'person'
        if filename == 'PalREAD_authorities - Life events.tsv':
            entity = 'life_event'
        if filename == 'PalREAD_authorities - Organisations.tsv':
            entity = 'organisation'
        if filename == 'PalREAD_authorities - Publishers.tsv':
            entity = 'publisher'
        if filename == 'PalREAD_authorities - Literary events.tsv':
            entity = 'lit_event'
    return entity

def replace_value(val,data_row):
    if '-->' in val:
        column = val.split('-->',1)[1] # get column name
        funct = val.split('-->',1)[0].replace("op:","") # call the function specified in preprocessing
        value = data_row[column]
        new_val = eval('p.'+funct+'("'+str(value)+'")')  # replace the final json
    if '-->' not in val:
        new_val = data_row[val]
    return new_val

def prepare_json(data_row,mapping):
    data = fill_json(data_row, mapping)
    data = clean_dict(data)
    data = pop_empty(data)
    data = detect_lang(data)
    data = change_prop_id(data)
    return data

def fill_json(data_row, item_properties):
    item_data = {k:v for k,v in item_properties.items()}
    for prop, values_list in item_data.items():
        for value_dict in values_list:
            # Note for future me: "op:" has always to be in the mapping, even if it's just for stripping
            if "op:" in value_dict["@value"]:
                # pre-processing operations
                if "split_values" in value_dict["@value"]:
                    values = replace_value(value_dict["@value"],data_row)
                    if len(values) != 0:
                        count_prop = 0
                        for value in values:
                            count_prop += 1
                            new_dict = {}
                            new_dict["property_id"] = count_prop
                            new_dict["property_label"] = value_dict["property_label"]
                            new_dict["@value"] = value
                            new_dict["type"] = value_dict["type"]
                            if value_dict["type"] == "literal":
                                new_dict["lang"] = value_dict["lang"]
                            values_list.append(new_dict)
                else:
                    value_dict["@value"] = replace_value(value_dict["@value"],data_row)
    return item_data

def clean_dict(item_data):
    for prop, values_list in item_data.items():
        for value_dict in values_list:
            if "op:" in value_dict["@value"] or value_dict["@value"] == '':
                values_list.remove(value_dict)
            # change property id
    return item_data

def pop_empty(item_data):
    item_data = { k : v for k,v in item_data.items() if v}
    return item_data

def detect_lang(item_data):
    for prop, values_list in item_data.items():
        for value_dict in values_list:
            if "lang" in value_dict and value_dict["lang"] == "detect":
                lang = detect(value_dict["@value"])
                print("val",value_dict["@value"] ,"lang",lang)
                lang = "ar" if lang == 'ar' else "en"
                value_dict["lang"] = lang
    return item_data

def change_prop_id(item_data):
    for prop, values_list in item_data.items():
        if len(values_list) == 1 and values_list[0]["property_id"] != '1':
            values_list[0]["property_id"] = '1'
    return item_data

# read tsv files
def read_tables(tables_folder, item_sets_ids, operation="create"):
    # TODO add param for item ID if it's an update
    for filename in os.listdir(tables_folder):
        if filename.endswith(".tsv") and filename != "PalREAD_authorities - Vocabularies.tsv":
            # TODO first upload vocabularies and map cities
            entity = map_to_entity(filename)
            # Note for the future me: the mapping implies that for each table (tsv) corresponds _only one_ entity
            # To reuse this code in the future, the 1-to-1 relation (table-entity) must be respected

            with open(item_sets_ids) as json_file:
                data = json.load(json_file)
                item_set_id = data[entity]
            with open(tables_folder+'/'+filename) as tsv_file:
                next(tsv_file)
                reader = csv.DictReader(tsv_file, delimiter='\t')
                list_items = []
                for row in reader:
                    if operation == 'create':
                        o_item = create_item(row,item_set_id,entity)
                        list_items.append(o_item)
                    if operation == 'update':
                        o_item = update_item(row,item_set_id,entity)
    print("\n\n\nlist_items")
    pp.pprint(list_items)
    return list_items

read_tables('tables', "item_sets_ids.json", operation="create")
# save tables as tsv in the same folder
# fill the json file with ids of itemsets
# call read_tables to create a list of items
