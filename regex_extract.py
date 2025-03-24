import pandas as pd

import logging
import sys

if __name__ == "__main__":
    logging.basicConfig(filename="regex_extract.log", level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))

    df = pd.read_csv("gs_export.csv")
    
    df = df[df["Volume"].isnull()]
    df = df[~df["Publication"].str.contains(r'\b(?:conference|journal|proceedings|ieee|springer)\b', case=False, na=True)]
    df = df[~df["Publisher"].str.contains(r'\b(?:conference|ieee|springer|association|igi|publications)\b', case=False, na=False)]
    df = df[df["Pages"].isnull()]
    df = df[df["Number"].isnull()]
    print(df)

    fpath = "regex_exports/filtered_articles.csv"
    logging.info(f'{df.shape} results are exported to {fpath}')
    df.to_csv(fpath, index=False)

