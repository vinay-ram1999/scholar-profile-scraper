from bibtexparser.bibdatabase import BibDatabase
from bibtexparser import dump
from pyzotero import zotero
import pandas as pd

from dotenv import load_dotenv
import logging
import sys
import os

if __name__ == "__main__":
    logging.basicConfig(filename="zotero_api.log", level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))

    load_dotenv()

    zotero_user_id = os.getenv("zotero_user_id", "")
    zotero_api_key = os.getenv("zotero_api_key", "")
    zotero_collection_id = os.getenv("zotero_collection_id", "")

    logging.info("----- Attempting to connect to Zotero API -----")
    try:
        items = 0
        results_dir = 'api_exports'
        os.makedirs(results_dir, exist_ok=True)

        zot = zotero.Zotero(zotero_user_id, "user", zotero_api_key)
        total_items = zot.num_collectionitems(zotero_collection_id)
        logging.info(f"{total_items} items found in collection '{zotero_collection_id}'")
        
        itemTypes_df = pd.DataFrame(zot.item_types())
        for itemType in itemTypes_df['itemType'].tolist():
            collection_items: BibDatabase = zot.everything(zot.collection_items(zotero_collection_id, format = 'bibtex', itemType = itemType))
            if isinstance(collection_items, BibDatabase):
                num_items = len(collection_items.entries)
                logging.info(f"{num_items} '{itemType}' items found")
                items += num_items
                fname = f'{results_dir}/{itemType}.bib'
                with open(fname, 'w') as bibtex_file:
                    dump(collection_items, bibtex_file)
                logging.info(f"bibtex info for '{itemType}' type is exported to '{fname}'")
        assert items == total_items, "All items are not exported!"
        logging.info("----- export completed -----")
    except Exception as e:
        logging.error(e)
        raise(e)

