import os , json , csv ,re , itertools , pprint
import preprocessing as p
from langdetect import detect
from collections import defaultdict

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
        # TODO make the external mapping
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
                            if "property_id" in value_dict:
                                new_dict["property_id"] = count_prop
                            new_dict[object] = value
                            if "type" in value_dict:
                                new_dict["type"] = value_dict["type"]
                            if value_dict["type"] == "literal":
                                if "lang" in value_dict:
                                    new_dict["lang"] = value_dict["lang"]
                            values_list.append(new_dict)
                            print("new_dict",new_dict)
                else:
                    value_dict[object] = replace_value(value_dict[object],data_row)
    print("item_data",item_data)
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
                print("\nTO BE REMOVED",value_dict)
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

def change_prop_id(item_data):
    for prop, values_list in item_data.items():
        if len(values_list) == 1 and values_list[0]["property_id"] != '1':
            values_list[0]["property_id"] = '1'
    return item_data

def get_ids(api_url):
	lookup=['resource_classes','properties']
	for l in lookup:
		id=1
		id_dict = {}
		while id <500:
			this_url = api_url+'%s/%s' %(l,str(id))
			response = requests.get(this_url)
			print(id,response)
			results = json.loads(response.text)
			code = response.status_code
			if code == 200:
				label = results['o:label']
				term = results['o:term']
				id_dict[term]={'label':label,'id':id}
				print(term)
			id +=1

		d=open('%s_ids.json'%l,'w')
		d.write(json.dumps(id_dict))
		d.close()

# read tsv files
def read_tables(tables_folder, item_sets_ids, operation="create"):
    # TODO add param for item ID if it's an update
    list_items = []
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
