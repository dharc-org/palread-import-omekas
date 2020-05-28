# PalREAD Mapping pipeline

## `import` script

  1. [?] Create (5) itemsets (in omeka or via API), and save their IDs in `item_sets_id.json` (keep the same structure there is now)
  2. [MARI] Upload in omeka the ontology `ontology.ttl` (to be done in omeka only via file upload)
  3. [MARI] Create the templates for the itemsets (to be done in omeka, either manually or by uploading a json, we need to decide) - include valuesuggest
  4. [?] Upload in omeka the controlled custom vocabularies (manually or via API, we need to decide)
  5. [?] Extract vocabulary terms ID and autopopulate `vocabularies.json` (try to respect the structure):
  this includes both mapping to external URIs (used in valuesuggest) and local IDs of itemsets used as vocabularies, include Palestine Maps custom vocabulary

    * 5.1 Extract properties and classes ids in two json files by calling ``mapping.get_ids(api_url)``
    * 5.2 Replace properties id in `mapping.json`
    * 5.3 distinguish in payload when the vocabulary is an external term or an item (change key:value!!)
  6. [MARI] Download each [sheet](https://docs.google.com/spreadsheets/d/1fn523ktjeLyTytUuPvlOXEvb5A65SxhlKkePKtdWcSQ/edit?usp=sharing) in the folder `tables` as .tsv (do not change the name, and yes, tsv, _NOT_ csv)
  7. [IVAN] Call `mapping.read_tables("tables", "item_sets_id.json", "create")`. It returns a list of dictionaries (a complete dictionary for each new entity, including the itemset, the ID of vocabulary terms and so on)
  8. [IVAN] Iterate over the list and upload each dictionary in omeka as single items (bulk import?)
  9. [IVAN] While importing, return the IDs and labels (see below) of so created entities and store them in `items_ids.json` (TODO: decide the structure, very likely to be `"ID":{"name":"",...}`)
  10. [IVAN] Call `mapping.read_tables("tables", "item_sets_id.json", "update")` to get a list of dictionaries to be uploaded in omeka (TO BE DONE, MARI)
  11. [IVAN] Upload changes
  12. [IVAN] Delete temporary properties "pr:tmp"

## First round upload (before step 7)

 * upload vocabulary terms from spreadsheets and save their IDs in `vocabularies_ids.json`
 * reconcile geonames for places (use also district and places for the reconciliation) in `vocabularies.json`
 * double-check dates validation
 * change all properties IDs in `mapping.json` by querying the `api/properties`
 * distinguish two fields for cities and palestine cities? or two vocabularies?
 * literary events: look at how they create events, first create the general event in the first upload and then in the update create the relation
 * finish the mapping for the relations of the update
 * extract all the links in "Sources public"????
 * New field "Notes private"????
 * add classes to mapping json

## Resource IDs and labels to be returned after the first upload (step 9)

 * People:
    * ID
    * "wdp:P2561" values (either "\@en" or "\@ar")
 * Life events:
    * ID
    * "wdp:P2561" value
    * "pr:tmp-person" value (to be matched with people "wdp:P2561" values and get the ID)
    * "pr:tmp-org" value (to be matched with organisation "wdp:P2561" values and get the ID)
    * "pr:life-event-type" (to choose the relation)
    * "pr:tmp-person-other"
 * Organisations:
   * ID
   * "wdp:P2561" value
 * Publishers:
   * ID
   * "wdp:P2561" value
 * Literary events:
    * ID
    * "pr:id" value
    * "wdp:P2561" value

## Preliminary work before update (between step 9 and step 10)

* In certain tables (see below) look into a list of fields and check if a record has already been created for that value otherwise create a new item (e.g. mother, father, etc) and return ID and info in the `items_ids.json` as specified before

   * Table People:
       * "Mother"
         * ID
         * "wdp:P2561" values (either "\@en" or "\@ar")
       * "Father"
         * ID
         * "wdp:P2561" values (either "\@en" or "\@ar")
       * "Siblings"
         * ID
         * "wdp:P2561" values (either "\@en" or "\@ar")
       * "Spouses"
         * ID
         * "wdp:P2561" values (either "\@en" or "\@ar")
       * "Children"
         * ID
         * "wdp:P2561" values (either "\@en" or "\@ar")
       * "Friends"
         * ID
         * "wdp:P2561" values (either "\@en" or "\@ar")
       * "Influenced by person"
         * ID
         * "wdp:P2561" values (either "\@en" or "\@ar")

   * Table Life events:
       * "Student of"
         * ID
         * "wdp:P2561" values (either "\@en" or "\@ar")


## Actual update (step 10)

There are few specific operations that must be done in this step, so it's very likely that this will not be a generic script as the one for the first upload

For every row of the tables update relations

   * Table People:

       * relation to People "Mother",
       * relation to People "Father",
       * relation to People "Siblings",
       * relation to People "Spouses",
       * relation to People "Children",
       * relation to People "Friends",
       * relation to People "Influenced by person",
       * relation to Literary events "Literary event" + "Relation to event"
       * relation to Life events "Life event"

   * Table Life events:

       * relation to Organisations "Organisation or POI"
       * relation to People "Student of"

   * Table Organisations:

       * relation to Literary events "Literary event" + "Relation to event"

   * Table Publishers:

       * relation to Organisations "Political affiliation"
       * relation to Organisations "Union affiliation"
       * relation to Literary events "Literary event" + "Relation to event"
       * relation to People "Founder name \@en"
       * relation to People "Founder name \@ar"
       * relation to People "Founder name 2 \@ar"

   * Table Literary events:

       * relation to Literary events "Event name" and "Related event"
       * "Event name" (if more than one has the same name create the parent event)


## Removal of temp properties (step 12)

For every item in Omeka, remove the following properties and values

 * "pr:tmp-person"
 * "pr:tmp-org"
 * "pr:tmp-person-other"
 * "pr:tmp-event"

## Notes [MD]

 * I need to store original people names if they include dates for disambiguation
 * private fields for people - sex religion: not queryable!
 * [ASK Tommy] everything has to be closed!
    * public API, item private, via authentication to access private is possible?
    * api in vpn
    * IP privato sul cloud
    * white list of IP addresses: scholars, giorgio and matteo for the API
    SOLUTION
    * ip Public
    * default setting private items
    * API with key and credential to access everything + `pages=*`
 * how to add new vocabulary terms -- SOLUTION itemset themes can we automatise the import of updates? can be done in the interface?
 * automatic lookup for VIAF and works
 * export from omeka to endnote
