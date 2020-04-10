# PalREAD Mapping

* Create in omeka 5 itemsets, and specify their IDs in `item_sets_id.json`
* Upload in omeka the ontology (manually?)
* Upload in omeka the vocabularies (manually?)
* Extract vocabulary terms ID and copy them in `vocabularies.json` (TODO: decide the structure)
* Download each [sheet](https://docs.google.com/spreadsheets/d/1fn523ktjeLyTytUuPvlOXEvb5A65SxhlKkePKtdWcSQ/edit?usp=sharing) in the folder `tables` as .tsv (do not change the name, and yes, tsv, _NOT_ csv)
* Create an `import` script (Ivan)
  * Call `mapping.read_tables("tables", "item_sets_id.json", "create")`. It returns a list of dictionaries (a complete dictionary for each new entity)
  * Iterate over the list and upload each dictionary in omeka as single entities
  * Export IDs of so created entities and map names (to decide which property) and IDs in `items_ids.json` (TODO: decide the structure)
  * Call `mapping.read_tables("tables", "item_sets_id.json", "update")` to get a list of dictionaries to be uploaded in omeka

Notes

 * do we need the Json api context?
 * I need to store original people names if they include dates for disambiguation
