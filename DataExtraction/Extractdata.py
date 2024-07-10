import pandas as pd
import os
import json




def return_dataFrame(folder_path):
    
 
    files = os.listdir(folder_path)
    file_name = files[0]
    file_path = folder_path + file_name


    df = pd.DataFrame()

    if file_name.endswith('.json'):
        with open(file_path, 'r') as file:
            data = json.load(file)
            df = pd.DataFrame(data)

    elif file_name.endswith('.csv'):
        data = pd.read_csv(file_path)
        df = pd.DataFrame(data)


    numeric_cols = df.select_dtypes(include=['number']).columns
    df[numeric_cols] = df[numeric_cols].fillna(0)

    string_cols = df.select_dtypes(include=['object']).columns
    df[string_cols] = df[string_cols].fillna("")

    return df





def extract_data_from_json(json_data):

    df = pd.DataFrame(json_data)
    
    numeric_cols = df.select_dtypes(include=['number']).columns
    df[numeric_cols] = df[numeric_cols].fillna(0)
    
    string_cols = df.select_dtypes(include=['object']).columns
    df[string_cols] = df[string_cols].fillna("")
    
    return df
