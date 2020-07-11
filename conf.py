# OMEKA Configurations
CONF = {
    "CONTENT_TYPE": "application/json",

    # ## DL test version
    # ## ---------------
    # "KEY_IDENTITY": "R5gHxiJaUyrNDDPP86IrlTWzldmtjaH4",
    # "KEY_CREDENTIALS": "HpqKENp75D8gfdgZFdoDfMVSbEge3I6L",
    # "OMEKA_API_URL": "http://137.204.168.20/api",

    ## DL production version
    ## ---------------
    # "KEY_IDENTITY": "GXcCjZm5RAPi1THZgrW3BBMIWFMJkb97",
    # "KEY_CREDENTIALS": "zDPuS0Q04wMusERac70ssovZHhd3iJ0f",
    # "OMEKA_API_URL": "https://dl.ficlit.unibo.it/api",

    # ## Palread test
    # ## ---------------
    "KEY_IDENTITY": "umPgHIUxAn5tc9ueMNu10wgnuII9tq2v",
    "KEY_CREDENTIALS": "cYeGaXJM1CMQ0ZpDXdFhARnmN8KXpC7n",
    "OMEKA_API_URL": "http://137.204.168.11/palread/api"
}


# Script Configurations
ITEM_SETS = ["palread"]
ENTITIES = {
    "person": {"e_class": "wd:Q215627", "label": "Person", "item_set":"palread"},
    "work": {"e_class": "wd:Q1002697", "label": "Periodical", "item_set":"palread"},
    "life_event": {"e_class":"pr:LifeEvent", "label": "Life event", "item_set":"palread"},
    "organisation": {"e_class": "wd:Q43229", "label": "Organisation", "item_set":"palread"},
    "publisher": {"e_class":"wd:Q2085381", "label":"Publisher", "item_set":"palread"},
    "lit_event": {"e_class":"pr:LiteraryEvent", "label": "Literary event", "item_set":"palread"}
}
TABLES_DICT = {
    "PalREAD_authorities - Works.tsv": "work",
    "PalREAD_authorities - People.tsv": "person",
    "PalREAD_authorities - Life events.tsv": "life_event",
    "PalREAD_authorities - Organisations.tsv": "organisation",
    "PalREAD_authorities - Publishers.tsv": "publisher",
    "PalREAD_authorities - Literary events.tsv": "lit_event"
}

# the fields in tables including the identifying label of resources (i.e. subjects of statements)
# and the property used to associate that value to the resource
TABLES_KEYS = {
    "work": {"Work title":"wd:P1476"},
    "person": {"Name @ar":"wd:P2561","Name @en":"wd:P2561"},
    "life_event": {"Event type": "pr:life-event-type", "Person  name @ar":"pr:tmp-person","Person name @en":"pr:tmp-person", "Student of":"pr:tmp-person-other", "Organisation or POI": "pr:tmp-org"},
    "organisation": {"Organisation or POI":"wd:P2561"},
    "publisher":{"Name @ar":"wd:P2561","Name @en":"wd:P2561"},
    "lit_event": {"Event  ID":"pr:identifier"}
}

# some properties may be deduced from a controlled vocabulary
VOCABULARY_PROPERTIES = {
    "boycotted":"pr:boycotted",
    "has participant":"wd:P1344",
    "was participant":"wd:P1344",
    "participated in":"wd:P1344",
    "banned from attending":"pr:banned-from",
    "frequented by":"wd:P1344",
    "hosted by":"pr:hosted",
    "was venue for":"pr:hosted",
    "took place at":"pr:hosted",
    "organised by":"pr:organised",
    "read poetry":"pr:read-poetry-at",
    "wrote about":"pr:has-topic",
    "spoke about":"pr:has-topic",
    "works of publisher were read at":"pr:reading-event"
}

#PATHS
DATA_PATH = "data"
#TABLES_DATA_PATH = DATA_PATH+"/tables/data_8_7_2020"
TABLES_DATA_PATH = "_local/data_8_7_2020/sample" #local sample

TEMPLATES_DATA_PATH = DATA_PATH+"/templates"
#--
INDEX_DATA_PATH = "data/index"
ITEM_SETS_INDEX = INDEX_DATA_PATH+"/item_sets_ids.json"
MAPPING_INDEX = INDEX_DATA_PATH+"/mapping.json"
VOCABULARIES_INDEX = INDEX_DATA_PATH+"/vocabularies.json"
ITEMS_INDEX = INDEX_DATA_PATH+"/created_items.json"
RESOURCE_TEMPLATES_INDEX = INDEX_DATA_PATH+"/resource_templates_ids.json"
