import pandas as pd


def load_raw():
    '''Loads the raw data and renames columns and sets data types.'''
    # load csv
    df = pd.read_csv('../data/train.csv', index_col='observation_id')
    
    # convert timestamps
    df['Date'] = pd.to_datetime(df['Date'])
    
    # convert categoricals
    categoricals = ['Type', 'Gender', 'Age range', 'Self-defined ethnicity', 'Officer-defined ethnicity', 'Legislation', 'Object of search', 'Outcome', 'station', 'Part of a policing operation']
    df[categoricals] = df[categoricals].astype('category')
    
    # convert booleans
    bools = ['Outcome linked to object of search', 'Removal of more than just outer clothing']
    #df[bools] = df[bools].astype('boolean')
    
    # rename columns
    df = df.rename(columns={'Type': 'type',
                            'Date': 'date',
                            'Part of a policing operation': 'operation',
                            'Latitude': 'lat',
                            'Longitude': 'long',
                            'Gender': 'sex',
                            'Age range': 'age',
                            'Self-defined ethnicity': 'ethnicity_self',
                            'Officer-defined ethnicity': 'ethnicity_officer',
                            'Legislation': 'legislation',
                            'Object of search': 'search_target',
                            'Outcome': 'outcome',
                            'Outcome linked to object of search': 'found_target',
                            'Removal of more than just outer clothing': 'stripped',
                            'station': 'station'})
    
    # sort
    df = df.sort_values('date')
    
    return df

def load_heroku_csv(columns, dtypes):
    '''Loads the data from Heroku PostgresSQL database
    downloaded csv file in appropriate foramtting.
    '''
    # load
    df_heroku = pd.read_csv('../data/heroku_data.csv')
    df = pd.DataFrame.from_dict([eval(string) for string in df_heroku.request])\
            .set_index('observation_id')
    df.columns = columns
    df = df.astype(dtypes)
    
    # add new columns
    df['predicted_outcome'] = df_heroku['predicted_outcome'].astype('boolean').values
    df['success'] = df_heroku['true_outcome'].astype('boolean').values
    
    return df

def load_second_heroku_csv(columns, dtypes):
    '''Loads the data from Heroku PostgresSQL database
    downloaded csv file in appropriate foramtting.
    '''
    # load
    df_heroku = pd.read_csv('../data/heroku_data_2.csv')
    df = pd.DataFrame.from_dict([eval(string) for string in df_heroku.request])\
            .set_index('observation_id')
    df.columns = columns
    df = df.astype(dtypes)
    
    # add new columns
    df['predicted_outcome'] = df_heroku['predicted_outcome'].astype('boolean').values
    df['success'] = df_heroku['true_outcome'].astype('boolean').values
    
    return df