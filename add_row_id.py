import pandas as pd

df = pd.read_csv("congressional_to_go_withrows.csv")

df.insert(1, "row_id", [f"row_{i}" for i in range(len(df))])

df.to_csv("congressional_to_go_withrows.csv", index=False)
