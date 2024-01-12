import pandas as pd
import numpy as np
import datetime
import re

"""
Take generated input data (customer, contact and staff) from raw_input_data folder. Data generated from https://generatedata.com/
Transform the data into required format based on data model

Mock up the fact tables (customer_contact, lead and interaction)
Save all transformed data into mocked_input_date

Create and load into Sqlite3 database
"""

def add_date_columns(df):
    # Helper columns to track update time and effective date (from_date and to_date)
    min_date, max_date = datetime.date(2000, 1, 1), datetime.date(9999, 1, 1)
    current_timestamp = datetime.datetime(2000, 1, 1)

    df["version"] = 1
    df["from_date"] = min_date
    df["to_date"] = max_date
    df["insert_datetime"] = current_timestamp

def mock_version(df,col_prefix,version):
    # For each row 40% chance to inserts an updated row (or version)
    probability_threshold = 0.4

    for index, row in df[df['version']==version].iterrows():
        if np.random.random() < probability_threshold:
         
            # Determine when changes are effective and when update timestamp is required
            start_date = row['from_date']
            end_date = datetime.date(2024, 1, 1)
            max_delta = (end_date-start_date).days
            
            updated_effective_date = start_date + datetime.timedelta(np.random.randint(max_delta))
            current_timestamp = pd.to_datetime(updated_effective_date - datetime.timedelta(1))
            
            # Update new row
            updated_row = row.copy()
            updated_version = version + 1

            updated_row['version'] = updated_version
            updated_row['insert_datetime'] = current_timestamp
            updated_row['from_date'] = updated_effective_date

            if version == 1:
                updated_row[f'{col_prefix}_name'] = f'{updated_row[f'{col_prefix}_name']} (V{updated_version})'
            else:
                pattern = r"\d+(?=\)$)"
                updated_row[f'{col_prefix}_name'] = re.sub(pattern,str(updated_version),updated_row[f'{col_prefix}_name'])

            df = pd.concat ([df, updated_row.to_frame().T], ignore_index=True)

            # Amend old row    
            df.loc[index,'to_date'] = updated_effective_date
    return df
    
def mock_df(df, col_prefix):
    # Iterate through all the rows and 40% chance to insert an updated row
    # Then iterate through all these new rows and repeat, until no more updates are inserted

    version_count = 1
    while df['version'].max() == version_count:
        df = mock_version(df,col_prefix,df['version'].max())
        version_count += 1
    return df
    
def mock_dimension(csv_file, col_prefix, status, columns):
    # Transforms the generated data into the required format
    df = pd.read_csv(f"raw_input_data/{csv_file}.csv")
    df.reset_index(inplace=True)
    df.columns = [f"{col_prefix}_{col}" for col in columns]
    df[f"{col_prefix}_status"] = df.apply(
        lambda x: np.random.choice(status, p=(0.8, 0.2)), axis=1
    )
    add_date_columns(df)
    df = mock_df(df,col_prefix)
    df.to_csv(f'mocked_input_data/mocked_{csv_file}.csv',index=False)
    return df  

if __name__ == '__main__':
    cust_df = mock_dimension('customer','cust',["active","closed"],["id","name","address"])
    cont_df = mock_dimension('contact','cont',["active","no longer with business"],["id","name","phone","email"])
    staff_df = mock_dimension('staff','staff',["active","no longer with business"],["id","name","phone","email"])

    
