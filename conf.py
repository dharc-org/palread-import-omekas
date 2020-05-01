# OMEKA Configurations
CONF = {
    "CONTENT_TYPE": "application/json",
    "KEY_IDENTITY": "R5gHxiJaUyrNDDPP86IrlTWzldmtjaH4",
    "KEY_CREDENTIALS": "HpqKENp75D8gfdgZFdoDfMVSbEge3I6L",
    "OMEKA_API_URL": "http://137.204.168.20/api"
    #"OMEKA_API_URL": "https://dl.ficlit.unibo.it/api"
}


# Script Configurations
ITEM_SETS = ["palread"]
TABLES_DICT = {
    "PalREAD_authorities - People.tsv": {"entity": "person", "e_class": "wd:Q215627", "label": "Person", "item_set":"palread"},
    "PalREAD_authorities - Life events.tsv": {"entity": "life_event", "e_class":"pr:LifeEvent", "label": "Life event", "item_set":"palread"},
    "PalREAD_authorities - Organisations.tsv": {"entity": "organisation", "e_class": "wd:Q43229", "label": "Organisation", "item_set":"palread"},
    "PalREAD_authorities - Publishers.tsv": {"entity": "publisher","e_class":"wd:Q2085381", "label":"Publisher", "item_set":"palread"},
    "PalREAD_authorities - Literary events.tsv": {"entity": "lit_event", "e_class":"pr:LiteraryEvent", "label": "Literary event", "item_set":"palread"}
}
# An index of keys. Each item will have a key defined as a tuple of its resource_class and a particular property
# the defined key is used also in the ITEMS_INDEX file.
KEYS_INDEX = {
    "wd:Q215627":"wd:P2561",
    "pr:LifeEvent":"wd:P2561",
    "wd:Q43229":"wd:P2561",
    "wd:Q2085381":"wd:P2561",
    "pr:LiteraryEvent":"wd:P2561",
}


#PATHS
DATA_PATH = "data"
TABLES_DATA_PATH = DATA_PATH+"/tables"
TEMPLATES_DATA_PATH = DATA_PATH+"/templates"
#--
INDEX_DATA_PATH = "data/index"
ITEM_SETS_INDEX = INDEX_DATA_PATH+"/item_sets_ids.json"
MAPPING_INDEX = INDEX_DATA_PATH+"/mapping.json"
VOCABULARIES_INDEX = INDEX_DATA_PATH+"/vocabularies.json"
ITEMS_INDEX = INDEX_DATA_PATH+"/created_items.json"
