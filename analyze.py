import pandas as pd

# Read the JSON file
df = pd.read_json("google_scholar_profile.json", orient="records", lines=True)
print(df)