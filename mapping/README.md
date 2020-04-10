# PalREAD Mapping

* `import` script
  * [?] Create (5) itemsets (in omeka or via API), and save their IDs in `item_sets_id.json` (keep the same structure there is now)
  * [MARI] Upload in omeka the ontology `ontology.ttl` (to be done in omeka only via file upload)
  * [MARI] Create the templates for the itemsets (to be done in omeka, either manually or by uploading a json, we need to decide)
  * [?] Upload in omeka the controlled vocabularies (manually or via API, we need to decide): omeka has a predefined set of vocabularies, so new custom vocabularies must be treated as itemsets
  * [?] Extract vocabulary terms ID and autopopulate `vocabularies.json` (try to respect the structure)
  * [MARI] Download each [sheet](https://docs.google.com/spreadsheets/d/1fn523ktjeLyTytUuPvlOXEvb5A65SxhlKkePKtdWcSQ/edit?usp=sharing) in the folder `tables` as .tsv (do not change the name, and yes, tsv, _NOT_ csv)
  * [IVAN] Call `mapping.read_tables("tables", "item_sets_id.json", "create")`. It returns a list of dictionaries (a complete dictionary for each new entity, including the itemset, the ID of vocabulary terms and so on)
  * [IVAN] Iterate over the list and upload each dictionary in omeka as single items (bulk import?)
  * [IVAN] Export IDs of so created entities and map unique names (to decide which property/column) and IDs in `items_ids.json` (TODO: decide the structure of this json, which is likely to be similar to `item_sets_id.json`)
  * [IVAN] Call `mapping.read_tables("tables", "item_sets_id.json", "update")` to get a list of dictionaries to be uploaded in omeka (TO BE DONE, MARI)
  * [IVAN] Upload changes

Notes [MD]

 * do we need the Json api context?
 * I need to store original people names if they include dates for disambiguation
 * Upload controlled vocabularies as itemsets and get the id immediately to create the mapping in `vocabularies.json`
 * [PROBLEM] some of the controlled vocabularies are handled by omeka (geonames, RDA gender). First we need to map local vocabularies to those, e.g. RDA, geonames (and to palestine openmaps!!), then how we include this information in the import bulk? what is the object of the triple, a uri (like for items)?
