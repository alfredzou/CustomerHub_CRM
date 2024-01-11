import pandas as pd
import numpy as np
import datetime
import math

"""
Take generated input data (customer, contact and staff) from raw_input_data folder. Data generated from https://generatedata.com/
Transform the data into required format based on data model

Mock up the fact tables (customer_contact, lead and interaction)
Save all transformed data into mocked_input_date

Create and load into Sqlite3 database
"""

def add_date_columns(df):
    # Helper columns to track update time and effective date (from_date and to_date)
    min_date, max_date = datetime.date(1, 1, 1), datetime.date(9999, 1, 1)
    current_timestamp = datetime.datetime.now()

    df["from_date"] = min_date
    df["to_date"] = max_date
    df["insert_datetime"] = current_timestamp

def mock_changes(df, col_prefix):
    # Mocks last 20% of the rows in dimension tables to simulate changing details 
    rows = df.shape[0]
    initial_pool = list(range(math.ceil(rows*0.8)))
    change_pool = list(range(initial_pool[-1]+1,rows))
    
    current_timestamp = datetime.datetime.now()
    start_date = datetime.date(2020, 1, 1)
    end_date = datetime.date(2024, 1, 1)
    max_delta = (end_date-start_date).days

    for row in change_pool:
        # Pick random initial id to simulate changing dimensions
        updated_id = np.random.choice(initial_pool)
        initial_pool.remove(updated_id)

        # Find initial id row and update 'to_date'
        new_effective_date = start_date + datetime.timedelta(np.random.randint(max_delta))
        df.loc[updated_id,'to_date'] = new_effective_date

        # Find changed id row and update
        df.loc[row,'insert_datetime'] = current_timestamp
        df.loc[row,'from_date'] = new_effective_date
        df.loc[row,f'{col_prefix}_id'] = updated_id

def mock_dimension(csv_file, col_prefix, status, columns):
    # Transforms the generated data into the required format
    df = pd.read_csv(f"raw_input_data/{csv_file}.csv")
    df.reset_index(inplace=True)
    df.columns = [f"{col_prefix}_{col}" for col in columns]
    df[f"{col_prefix}_status"] = df.apply(
        lambda x: np.random.choice(status, p=(0.8, 0.2)), axis=1
    )
    add_date_columns(df)
    mock_changes(df,col_prefix)
    df.to_csv(f'mocked_input_data/mocked_{csv_file}.csv',index=False)
    return df  

if __name__ == '__main__':
    mock_dimension('customer','cust',["active","closed"],["id","name","address"])
    mock_dimension('contact','cont',["active","no longer with business"],["id","name","phone","email"])
    mock_dimension('staff','staff',["active","no longer with business"],["id","name","phone","email"])
    

    