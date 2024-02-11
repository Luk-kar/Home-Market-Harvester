#!/usr/bin/env python
# coding: utf-8

# # Data Preview

# ## 1. Set up

# In[1]:


# Standard imports
from pathlib import Path
import os
import re
import sys

def set_project_root():
    notebooks_dir = Path.cwd()

    # Calculate the root directory of the project (go up three levels)
    project_root = notebooks_dir.parent.parent.parent

    if str(project_root) not in sys.path:
        print(f"The root directory of the project is: {project_root}")
        sys.path.append(str(project_root))

    return project_root

project_root = set_project_root()


# ### 1.3 Importing Data

# In[2]:


# Third-party imports
import pandas as pd

# Local imports
from pipeline.src._csv_utils import DataPathCleaningManager
from pipeline.config._config_manager import ConfigManager

config_file = ConfigManager("run_pipeline.conf")
TIMEPLACE = "MARKET_OFFERS_TIMEPLACE"
data_timeplace = config_file.read_value(TIMEPLACE)
if data_timeplace is None:
    raise ValueError(F"The environment variable {TIMEPLACE} is not set.")

data_path_manager = DataPathCleaningManager(data_timeplace, project_root)

df_olx = data_path_manager.load_df(domain="olx", is_cleaned=False)


# ### 1.2 Functions

# In[3]:


def count_and_percentage(df, column_name):
    """
    Function to calculate the count and percentage of unique values in a given column of a DataFrame.

    Parameters:
    df (pandas.DataFrame): The DataFrame to analyze.
    column_name (str): The name of the column in the DataFrame.

    Returns:
    pandas.DataFrame: A DataFrame with the count and percentage of each unique value in the specified column.

    Raises:
    ValueError: If the specified column is not found in the DataFrame.
    """
    # Check if the column exists in the DataFrame
    if column_name not in df.columns:
        raise ValueError(f"Column '{column_name}' not found in DataFrame.")

    # Calculate count and normalized values
    count = df[column_name].value_counts(dropna=False)
    normalized = df[column_name].value_counts(dropna=False, normalize=True) * 100

    # Concatenate count and normalized values side by side
    result = pd.concat([count, normalized], axis=1)
    result.columns = ['Count', 'Percentage']

    return result


# In[4]:


def count_comma_separated_values(df, column_name):
    """
    Counts the occurrences of individual elements in a comma-separated string column of a DataFrame.

    Parameters:
    df (pandas.DataFrame): The DataFrame containing the column.
    column_name (str): The name of the column to analyze.

    Returns:
    pandas.DataFrame: A DataFrame with the count and percentage of each unique element found in the comma-separated values.

    Raises:
    ValueError: If the specified column is not found in the DataFrame.
    """
    # Check if the column exists in the DataFrame
    if column_name not in df.columns:
        raise ValueError(f"Column '{column_name}' not found in DataFrame.")

    # Split the column values, explode to individual elements, and count
    exploded_items = df[column_name].dropna().str.split(', ').explode()
    exploded_df = pd.DataFrame({column_name: exploded_items})
    counts_and_percent = count_and_percentage(exploded_df, column_name)

    return counts_and_percent


# In[5]:


def remove_non_numeric_characters(df, column_name):
    """
    Removes all non-numeric characters from a column of a DataFrame.

    Parameters:
    df (pandas.DataFrame): The DataFrame containing the column.
    column_name (str): The name of the column to analyze.

    Returns:
    pandas.DataFrame: A DataFrame with all non-numeric characters removed from the specified column.

    Raises:
    ValueError: If the specified column is not found in the DataFrame.
    """

    return df[column_name].str.replace('[^a-zA-Z]', '', regex=True).unique()


# In[6]:


def count_words(text):
    if pd.isna(text):
        return 0
    return len(str(text).split())


# ## 2. Data preview

# In[7]:


df_olx.head(3)


# ### OLX

# In[8]:


def clean_olx_data(df):

    split_locations = df['location'].str.split(', ')
    df['voivodeship'] = split_locations.str[0]
    df['city'] = split_locations.apply(lambda x: ', '.join(x[1:]) if len(x) > 1 else '')
    
    pattern = r'ul\s+(\w+\s+\d+/\d+)'
    df['street'] = df['summary_description'].apply(lambda x: re.search(pattern, x).group(1) if re.search(pattern, x) else None)
    
    del df['location']
    
    df['price'] = df['price'].str.extract('(\d+ \d+)')[0].str.replace(' ', '').astype(float)
    df['rent'] = df['rent'].str.extract('(\d+)')[0].astype(float)


    # Extract and convert 'square_meters' into integers
    df['square_meters'] = df['square_meters'].str.extract('(\d+)')[0].astype('Int64')

    # Convert 'number_of_rooms' into an integer, special handling for "Kawalerka"
    df['number_of_rooms'] = df['number_of_rooms'].replace('Liczba pokoi: Kawalerka', '1')
    df['number_of_rooms'] = df['number_of_rooms'].str.extract('(\d+)')
    df['number_of_rooms'] = df['number_of_rooms'].astype('Int64')

    # Extract and clean 'floor_level', 'is_furnished', 'building_type'
    df['floor_level'] = df['floor_level'].str.extract('Poziom: (\d+)')[0]
    df['is_furnished'] = df['is_furnished'].map({'Umeblowane: Tak': True, 'Umeblowane: Nie': False})
    df['building_type'] = df['building_type'].str.extract('Rodzaj zabudowy: (.+)')[0]

    return df


# In[9]:


df_olx_cleaned = clean_olx_data(df_olx)
df_olx_cleaned.head()


# In[10]:


df_olx_cleaned.dtypes


# In[11]:


df_olx_cleaned['link'] = df_olx_cleaned['link'].astype('string')
df_olx_cleaned['title'] = df_olx_cleaned['title'].astype('string')
df_olx_cleaned['summary_description'] = df_olx_cleaned['summary_description'].astype('string')
df_olx_cleaned['ownership'] = df_olx_cleaned['ownership'].astype('string')
df_olx_cleaned['floor_level'] = df_olx_cleaned['floor_level'].astype('Int64')
df_olx_cleaned['building_type'] = df_olx_cleaned['building_type'].astype('string')
df_olx_cleaned['voivodeship'] = df_olx_cleaned['voivodeship'].astype('string')
df_olx_cleaned['city'] = df_olx_cleaned['city'].astype('string')
df_olx_cleaned['street'] = df_olx_cleaned['street'].astype('string')

df = df_olx_cleaned.rename(columns={'floor_level': 'floor'})

df_olx_cleaned.dtypes


# In[12]:


df_olx_cleaned['ownership'] = df_olx_cleaned['ownership'].map({'Prywatne': 'private'})

df_olx_cleaned['building_type'] = df_olx_cleaned['building_type'].map({'Apartamentowiec': 'apartment_building'})


# In[13]:


df_olx_cleaned.head()


# ## 3. Save cleaned data

# ### 3.1. Save data

# In[14]:


data_path_manager.save_df(df_olx_cleaned, domain="olx")


# ### 3.2 Check saved data

# #### OLX

# In[15]:


df_olx_saved = data_path_manager.load_df(domain="olx", is_cleaned=True)
df_olx_saved.head()


# In[16]:


df_olx_saved.dtypes


# In[17]:


are_identical = df_olx_saved.equals(df_olx_cleaned)
if not are_identical:
    raise ValueError("The saved DataFrame is not identical to the original one.")
else:
    print("The saved DataFrame is identical to the original one.")

