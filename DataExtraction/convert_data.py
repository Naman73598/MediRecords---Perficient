import pandas as pd

def convert_into_Dataframe(data,cur):
    return pd.DataFrame(data, columns=[desc[0] for desc in cur.description])