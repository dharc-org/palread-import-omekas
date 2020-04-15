# PalREAD Mapping

Pipeline

* `import` script
  * [?] Create (5) itemsets (in omeka or via API), and save their IDs in `item_sets_id.json` (keep the same structure there is now)
  * [MARI] Upload in omeka the ontology `ontology.ttl` (to be done in omeka only via file upload)
  * [MARI] Create the templates for the itemsets (to be done in omeka, either manually or by uploading a json, we need to decide)
  * [?] Upload in omeka the controlled vocabularies (manually or via API, we need to decide): omeka has a predefined set of vocabularies, so new custom vocabularies must be treated as itemsets
  * [?] Extract vocabulary terms ID and autopopulate `vocabularies.json` (try to respect the structure):
  this includes both mapping to external URIs (used in valuesuggest) and local IDs of itemsets used as vocabularies
  * [MARI] Download each [sheet](https://docs.google.com/spreadsheets/d/1fn523ktjeLyTytUuPvlOXEvb5A65SxhlKkePKtdWcSQ/edit?usp=sharing) in the folder `tables` as .tsv (do not change the name, and yes, tsv, _NOT_ csv)
  * [IVAN] Call `mapping.read_tables("tables", "item_sets_id.json", "create")`. It returns a list of dictionaries (a complete dictionary for each new entity, including the itemset, the ID of vocabulary terms and so on)
  * [IVAN] Iterate over the list and upload each dictionary in omeka as single items (bulk import?)
  * [IVAN] While importing, return the IDs and labels (see below) of so created entities and store them in `items_ids.json` (TODO: decide the structure, very likely to be `"ID":"name"`)
  * [IVAN] Call `mapping.read_tables("tables", "item_sets_id.json", "update")` to get a list of dictionaries to be uploaded in omeka (TO BE DONE, MARI)
  * [IVAN] Upload changes

Resource IDs and labels to be returned after the first upload
 * People: ID + "wdp:P2561" values (either "\@en" or "\@ar")
 * Life events: ID + "pr:id" value
 * Literary events: ID + "pr:id" value

Notes [MD]

 * I need to store original people names if they include dates for disambiguation


TODO

first round upload

 * add final vocabulary terms to `vocabularies.json`
 * reconcile LOC gender, religion -- do the mapping and substitute iri in `vocabularies.json`
 * reconcile geonames AND palestine openmaps for places (use also district and places for the reconciliation)
 * double-check dates validation

update

preliminary work
 * look into a list of fields and check if a record has already been created for that label otherwise create it (e.g. mother, father, etc) and return Id and name
    * Table People: "Mother","Father","Siblings","Spouses","Children","Friends","Influenced by person"
    * Table Life events: "Student of"

actual update
 * then for every row of the tables update relations
    * Table People: "Mother","Father","Siblings","Spouses","Children","Friends","Influenced by person","Literary event"
