import sys
import numpy as np
import pandas as pd
from sqlalchemy import create_engine

def load_data(messages_filepath, categories_filepath):
    """Loads the two input .csv as dataframes."""
    
    messages = pd.read_csv(messages_filepath)
    categories = pd.read_csv(categories_filepath)

    return messages, categories

def clean_data(messages, categories):
    """Creates the categories columns, concatenates the two dataframes
       and cleans the data.
    """
    
    # split categories into 36 individual category columns
    categories = categories['categories'].str.split(';', expand=True)
    # create appropriate column names
    categories.columns = \
        categories.loc[0,:].apply(lambda x : x.split('-')[0])
    # one-hot encode cat values (last character, convert to numeric)
    for column in categories:
        categories[column] = \
            categories[column].apply(lambda x: x.split('-')[1]) 
        categories[column] = pd.to_numeric(categories[column])

    # concatenate the two dataframes
    df = pd.concat([messages, categories], axis=1)
    
    # drop duplicates
    df.drop_duplicates(subset='id', keep='first', inplace=True)
    # remove messages with value 2 in category `related`
    df = df.loc[df['related'] != 2]
    # drop column `child_alone` (no associated messages)
    df.drop('child_alone', axis=1, inplace=True)
    
    return df
    

def save_data(df, database_filepath):
    engine = create_engine('sqlite:///' + database_filepath)
    df.to_sql('messages', engine, index=False, if_exists='replace')  


def main():
    if len(sys.argv) == 4:

        messages_filepath, categories_filepath, database_filepath = sys.argv[1:]

        print('Loading data...\n    MESSAGES: {}\n    CATEGORIES: {}'
              .format(messages_filepath, categories_filepath))
        messages, categories = load_data(messages_filepath, categories_filepath)

        print('Cleaning data...')
        df = clean_data(messages, categories)
        
        print('Saving data...\n    DATABASE: {}'.format(database_filepath))
        save_data(df, database_filepath)
        
        print('Cleaned data saved to database!')
    
    else:
        print('Please provide the filepaths of the messages and categories '\
              'datasets as the first and second argument respectively, as '\
              'well as the filepath of the database to save the cleaned data '\
              'to as the third argument. \n\nExample: python process_data.py '\
              'disaster_messages.csv disaster_categories.csv '\
              'DisasterResponse.db')


if __name__ == '__main__':
    main()
