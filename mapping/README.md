# PalREAD Mapping pipeline

## `import` script

  1. [?] Create (5) itemsets (in omeka or via API), and save their IDs in `item_sets_id.json` (keep the same structure there is now)
  2. [MARI] Upload in omeka the ontology `ontology.ttl` (to be done in omeka only via file upload)
  3. [MARI] Create the templates for the itemsets (to be done in omeka, either manually or by uploading a json, we need to decide)
  4. [?] Upload in omeka the controlled vocabularies (manually or via API, we need to decide): omeka has a predefined set of vocabularies, so new custom vocabularies must be treated as itemsets
  5. [?] Extract vocabulary terms ID and autopopulate `vocabularies.json` (try to respect the structure):
  this includes both mapping to external URIs (used in valuesuggest) and local IDs of itemsets used as vocabularies
  6. [MARI] Download each [sheet](https://docs.google.com/spreadsheets/d/1fn523ktjeLyTytUuPvlOXEvb5A65SxhlKkePKtdWcSQ/edit?usp=sharing) in the folder `tables` as .tsv (do not change the name, and yes, tsv, _NOT_ csv)
  7. [IVAN] Call `mapping.read_tables("tables", "item_sets_id.json", "create")`. It returns a list of dictionaries (a complete dictionary for each new entity, including the itemset, the ID of vocabulary terms and so on)
  8. [IVAN] Iterate over the list and upload each dictionary in omeka as single items (bulk import?)
  9. [IVAN] While importing, return the IDs and labels (see below) of so created entities and store them in `items_ids.json` (TODO: decide the structure, very likely to be `"ID":{"name":"",...}`)
  10. [IVAN] Call `mapping.read_tables("tables", "item_sets_id.json", "update")` to get a list of dictionaries to be uploaded in omeka (TO BE DONE, MARI)
  11. [IVAN] Upload changes
  12. [IVAN] Delete temporary properties "pr:tmp"

## First round upload (before step 7)

 * add final vocabulary terms to `vocabularies.json`
 * reconcile LOC gender, religion -- do the mapping and substitute iri in `vocabularies.json`
 * reconcile geonames AND palestine openmaps for places (use also district and places for the reconciliation)
 * double-check dates validation

## Resource IDs and labels to be returned after the first upload (step 9)

 * People:
    * ID
    * "wdp:P2561" values (either "\@en" or "\@ar")
 * Life events:
    * ID
    * "pr:tmp-person" value (to be matched with people "wdp:P2561" values and get the ID)
    * "pr:tmp-org" value (to be matched with organisation "wdp:P2561" values and get the ID)
    * "pr:life-event-type" (to choose the relation)
 * Literary events: ID + "pr:id" value

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
       * "Mother",
       * "Father",
       * "Siblings",
       * "Spouses",
       * "Children",
       * "Friends",
       * "Influenced by person",
       * relation to rows of "Literary event"
       * relation to rows of "Life event"

## Removal of temp properties (step 12)

For every item in Omeka, remove the following properties and values

 * "pr:tmp-person"
 * "pr:tmp-org"
 * "pr:tmp-person-other"

## Notes [MD]

 * I need to store original people names if they include dates for disambiguation
