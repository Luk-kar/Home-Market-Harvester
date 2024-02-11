#!/usr/bin/env python
# coding: utf-8

# # Data Preview

# ## 1. Set up

# In[1]:


# Standard imports
from pathlib import Path
import os
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
import numpy as np
import pandas as pd

# Local imports
from pipeline.src._csv_utils import DataPathCleaningManager
from pipeline.config._config_manager import ConfigManager

config_file = ConfigManager("run_pipeline.conf")
TIMEPLACE = "MARKET_OFFERS_TIMEPLACE"
data_timeplace = config_file.read_value(TIMEPLACE)
if data_timeplace is None:
    raise ValueError(F"The configuration variable {TIMEPLACE} is not set.")

data_path_manager = DataPathCleaningManager(data_timeplace, project_root)

df_otodom = data_path_manager.load_df(domain="otodom", is_cleaned=False)


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

# ### Otodom

# #### 2.2.1 Cleaning data

# In[7]:


def clean_otodom_data(df: pd.DataFrame):

    # 1. Split 'location' into street, city, and voivodeship
    df['location_split'] = df['location'].str.split(', ')
    df['street'] = df['location_split'].apply(lambda x: x[0] if len(x) > 2 else None)
    df['city'] = df['location_split'].apply(lambda x: x[-2] if len(x) > 1 else None)
    df['voivodeship'] = df['location_split'].apply(lambda x: x[-1] if x else None)

    # Drop the temporary 'location_split' column
    df.drop(columns=['location_split'], inplace=True)

    # 2. Convert 'price' into float
    df['price'] = df['price'].str.replace(' ', '').str.extract('(\d+)')[0]
    df['price'] = pd.to_numeric(df['price'], errors='coerce')
    df['price'] = df['price'].astype('float64')

    # Extract and convert 'square_meters' into integers
    df['square_meters'] = df['square_meters'].str.extract('(\d+)')[0].astype('float64')

    # Extract and convert 'rent' into float
    df['rent'] = df['rent'].str.extract('(\d+)')[0]
    df['rent'] = pd.to_numeric(df['rent'], errors='coerce').astype('float64')
    df['total_rent'] = df['rent'].add(df['price'], fill_value=0).astype('float64')

    # Extract and convert 'deposit' into float
    df['deposit'] = df['deposit'].str.replace(' ', '').str.extract('(\d+)')[0]
    df['deposit'] = pd.to_numeric(df['deposit'], errors='coerce').astype('float64')

    # Convert 'number_of_rooms' into an integer, special handling for "Kawalerka"
    df['number_of_rooms'] = df['number_of_rooms'].astype('Int64')

    # Extract and clean 'floor_level'
    df_split = df['floor_level'].str.split('/', expand=True)
    df_split[0] = df_split[0].replace({'parter': 0, 'suterena': -1, '> 10': 11})

    poddasze_rows = df_split[0] == 'poddasze'
    df_split.loc[poddasze_rows, 0] = (df_split.loc[poddasze_rows, 1].fillna(0).astype(int) + 1).astype(str)

    df['attic'] = df_split[0] == 'poddasze'
    df['floor'] = pd.to_numeric(df_split[0], errors='coerce')
    df['floor'] = df['floor'].astype('Int64')
    df['building_floors'] = pd.to_numeric(df_split[1], errors='coerce')
    df['building_floors'] = df['building_floors'].astype('Int64')
    
    del df['floor_level']

    # Convert 'elevator' and 'parking_space' into boolean values
    df['elevator'] = df['elevator'].map({'tak': True, 'nie': False}).astype('boolean')

    df['parking_space'] = df['parking_space'].map({'garaż/miejsce parkingowe': True, 'brak informacji': False}).astype('boolean')
    
    # Convert 'build_year' into integers
    df['build_year'] = pd.to_numeric(df['build_year'], errors='coerce').astype('Int64')

    # todo create master columns for subcolumns
    # 3. Explode 'equipment', 'media_types', 'heating', 'security', 'windows', 'building_materials', 'additional_information' into boolean categories
    def explode_and_get_dummies(column_name):
        return df[column_name].str.get_dummies(sep=', ')
    
    to_explode = ['equipment', 'media_types', 'heating', 'security', 'windows', 'balcony_garden_terrace', 'building_material', 'additional_information']

    for column in to_explode:
        df = df.join(explode_and_get_dummies(column).add_prefix(f"{column}_"))

    for column in to_explode:
        del df[column]

    return df


# In[8]:


df_otodom_cleaned = clean_otodom_data(df_otodom)
df_otodom_cleaned.head()


# In[9]:


df_otodom_cleaned.columns.to_list()


# In[10]:


columns_order = [
    'link', 'title', 'summary_description', 'remote service', 
    'price', 'rent', 'total_rent', 'deposit', 
    'location', 'street', 'city', 'voivodeship', 
    'square_meters', 'number_of_rooms', 'floor', 'attic', 'building_floors', 
    'available_from', 'completion', 'ownership', 'rent_to_students', 
    'building_type', 'build_year', 
    'elevator', 'parking_space', 
    'equipment_brak informacji', 'equipment_kuchenka', 'equipment_lodówka', 'equipment_meble', 'equipment_piekarnik', 'equipment_pralka', 'equipment_telewizor', 'equipment_zmywarka', 
    'media_types_brak informacji', 'media_types_internet', 'media_types_telefon', 'media_types_telewizja kablowa', 
    'heating_brak informacji', 'heating_elektryczne', 'heating_gazowe', 'heating_inne', 'heating_kotłownia', 'heating_miejskie', 'heating_piece kaflowe', 
    'security_brak informacji', 'security_domofon / wideofon', 'security_drzwi / okna antywłamaniowe', 'security_monitoring / ochrona', 'security_rolety antywłamaniowe', 'security_system alarmowy', 'security_teren zamknięty', 
    'windows_aluminiowe', 'windows_brak informacji', 'windows_drewniane', 'windows_plastikowe', 
    'building_material_beton', 'building_material_beton komórkowy', 'building_material_brak informacji', 'building_material_cegła', 'building_material_drewno', 'building_material_inne', 'building_material_keramzyt', 'building_material_pustak', 'building_material_silikat', 'building_material_wielka płyta', 'building_material_żelbet', 
    'additional_information_brak informacji', 'additional_information_dwupoziomowe', 'additional_information_klimatyzacja', 'additional_information_oddzielna kuchnia', 'additional_information_piwnica', 'additional_information_pom. użytkowe', 'additional_information_tylko dla niepalących'
]

# Add missing columns from columns_order with NaN values
for column in columns_order:
    if column not in df_otodom_cleaned.columns:
        df_otodom_cleaned[column] = np.nan
        
df_otodom_cleaned = df_otodom_cleaned[columns_order]


# In[11]:


columns_multiindex = [
    ('listing', 'link'),
    ('listing', 'title'),
    ('listing', 'summary_description'),
    ('listing', 'remote_service'),
    ('pricing', 'price'),
    ('pricing', 'rent'),
    ('pricing', 'total_rent'),
    ('pricing', 'deposit'),
    ('location', 'complete_address'),
    ('location', 'street'),
    ('location', 'city'),
    ('location', 'voivodeship'),
    ('size', 'square_meters'),
    ('size', 'number_of_rooms'),
    ('size', 'floor'),
    ('size', 'attic'),
    ('size', 'building_floors'),
    ('legal_and_availability', 'available_from'),
    ('legal_and_availability', 'completion'),
    ('legal_and_availability', 'ownership'),
    ('legal_and_availability', 'rent_to_students'),
    ('type_and_year', 'building_type'),
    ('type_and_year', 'build_year'),
    ('amenities', 'elevator'),
    ('amenities', 'parking_space'),
    ('equipment', 'no_information'),
    ('equipment', 'stove'),
    ('equipment', 'fridge'),
    ('equipment', 'furniture'),
    ('equipment', 'oven'),
    ('equipment', 'washing_machine'),
    ('equipment', 'TV'),
    ('equipment', 'dishwasher'),
    ('media_types', 'no_information'),
    ('media_types', 'internet'),
    ('media_types', 'telephone'),
    ('media_types', 'cable_TV'),
    ('heating', 'no_information'),
    ('heating', 'electric'),
    ('heating', 'gas'),
    ('heating', 'other'),
    ('heating', 'boiler_room'),
    ('heating', 'district'),
    ('heating', 'tile_stove'),
    ('security', 'no_information'),
    ('security', 'intercom_or_video_intercom'),
    ('security', 'anti_burglary_doors_or_windows'),
    ('security', 'monitoring_or_security'),
    ('security', 'anti_burglary_roller_blinds'),
    ('security', 'alarm_system'),
    ('security', 'enclosed_area'),
    ('windows', 'aluminum'),
    ('windows', 'no_information'),
    ('windows', 'wooden'),
    ('windows', 'plastic'),
    ('building_material', 'concrete'),
    ('building_material', 'aerated_concrete'),
    ('building_material', 'no_information'),
    ('building_material', 'brick'),
    ('building_material', 'wood'),
    ('building_material', 'other'),
    ('building_material', 'lightweight_aggregate'),
    ('building_material', 'hollow_brick'),
    ('building_material', 'silicate'),
    ('building_material', 'large_panel'),
    ('building_material', 'reinforced_concrete'),
    ('additional_information', 'no_information'),
    ('additional_information', 'duplex'),
    ('additional_information', 'air_conditioning'),
    ('additional_information', 'separate_kitchen'),
    ('additional_information', 'basement'),
    ('additional_information', 'utility_room'),
    ('additional_information', 'non_smokers_only')
]

multiindex = pd.MultiIndex.from_tuples(columns_multiindex, names=['Category', 'Subcategory'])
df_otodom_cleaned.columns = multiindex


# In[12]:


df_otodom_cleaned.head()


# In[13]:


df_otodom_cleaned.dtypes.to_dict()


# #### 2.2.2 Checking data

# ##### Prices

# In[14]:


assert df_otodom_cleaned[[('pricing', 'price'), ('pricing', 'rent'), ('pricing', 'deposit')]].min().min() >= 0, "Price, rent, or deposit contains negative values"


# In[15]:


df_otodom_cleaned[[('pricing', 'price'), ('pricing', 'rent'), ('pricing', 'deposit')]].max()


# In[16]:


def last_and_first_percentile(column_name, df):
    """
    Returns the first and last percentile of a column in a DataFrame.

    Parameters:
    column_name (str): The name of the column to analyze.
    df (pandas.DataFrame): The DataFrame containing the column.

    Returns:
    tuple: A tuple containing the first and last percentile of the column.
    """
    return df[column_name].quantile([0.01, 0.99])


# In[17]:


last_and_first_percentile(('pricing', 'price'), df_otodom_cleaned)


# Quick look

# In[18]:


pd.set_option('display.max_colwidth', None)
df_otodom_cleaned.sort_values(by=[('pricing', 'price')], ascending=False).head()[[('listing', 'link'), ('listing', 'title'), ('listing', 'summary_description'), ('pricing', 'total_rent'), ('location', 'city')]]


# In[19]:


pd.set_option('display.max_colwidth', 50)


# ##### locations

# In[20]:


set(df_otodom_cleaned[('location', 'city')])


# In[21]:


set(df_otodom_cleaned[('location', 'voivodeship')])


# Textual Data Analysis

# In[22]:


df_otodom_cleaned[('listing', 'summary_description')].str.len().max()


# In[23]:


df_otodom_cleaned[('listing', 'summary_description')].apply(count_words).max()


# Max values of the selected columns

# In[24]:


df_otodom_cleaned[('size', 'square_meters')].max()


# In[25]:


df_otodom_cleaned[('size', 'square_meters')].min()


# In[26]:


df_otodom_cleaned[('size', 'number_of_rooms')].max()


# In[27]:


df_otodom_cleaned[('size', 'number_of_rooms')].min()


# In[28]:


df_otodom_cleaned[('size', 'floor')].value_counts().index.to_list()


# In[29]:


df_otodom_cleaned[('size', 'building_floors')].value_counts()


# Check if date column is the date format

# In[30]:


date_format_regex = r'^\d{4}-\d{2}-\d{2}$'

# Check if each date in the column matches the format
# Perform the assertion directly
assert (df_otodom_cleaned[('legal_and_availability', 'available_from')].dropna().str.match(date_format_regex)).all(), "Not all dates match the required format"


# #####  2.2.3 Translate Polish to English
# `Listing | title`, `Listing | summary_description` are not translated due to losing context by using a translation

# listing

# In[31]:


df_otodom_cleaned[('listing', 'remote_service')] = df_otodom_cleaned[('listing', 'remote_service')].map(
    {'Obsługa zdalnaZapytaj': np.NaN, 
     'Obsługa zdalnatak': 'unspecified', 
     'Obsługa zdalnaFilm': 'video',
     'Obsługa zdalnaWirtualny spacer': 'virtual_tour',
     'Obsługa zdalnaFilmWirtualny spacer': 'video_virtual_tour',
     }
    )
df_otodom_cleaned[('listing', 'remote_service')].value_counts(dropna=False)


# legal_and_availability

# In[32]:


df_otodom_cleaned[('legal_and_availability', 'completion')] = df_otodom_cleaned[('legal_and_availability', 'completion')].map(
    {'do zamieszkania': 'ready_to_move_in', 
     'do remontu': 'in_need_of_renovation', 
     'do wykończenia': 'unfinished'}
    )
df_otodom_cleaned[('legal_and_availability', 'completion')].value_counts()


# In[33]:


df_otodom_cleaned[('legal_and_availability', 'ownership')]= df_otodom_cleaned[('legal_and_availability', 'ownership')].map(
    {'biuro nieruchomości': 'real_estate_agency', 
     'prywatny': 'private', 
     'deweloper': 'developer'}
     )
df_otodom_cleaned[('legal_and_availability', 'ownership')].value_counts()


# In[34]:


df_otodom_cleaned[('legal_and_availability', 'rent_to_students')] = df_otodom_cleaned[('legal_and_availability', 'rent_to_students')].map({'brak informacji': np.NaN, 'tak': True, 'nie': False})
df_otodom_cleaned[('legal_and_availability', 'rent_to_students')].value_counts(dropna=False)


# type_and_year

# In[35]:


df_otodom_cleaned['type_and_year'].head()


# In[36]:


df_otodom_cleaned[('type_and_year', 'building_type')].value_counts()


# In[37]:


df_otodom_cleaned[('type_and_year', 'building_type')] = df_otodom_cleaned[('type_and_year', 'building_type')].map({
    'blok': 'block_of_flats', 
    'apartamentowiec': 'apartment_building', 
    'kamienica': 'historic_apartment_building',
    'dom wolnostojący': 'detached_house',
    'szeregowiec': 'terraced_house',
    })
df_otodom_cleaned[('type_and_year', 'building_type')].value_counts(dropna=False)


# ##### Change data types

# bool

# In[38]:


df_otodom_cleaned[('legal_and_availability', 'rent_to_students')] = df_otodom_cleaned[('legal_and_availability', 'rent_to_students')].fillna(False).astype('boolean')
df_otodom_cleaned[('legal_and_availability', 'rent_to_students')].head()


# In[39]:


df_otodom_cleaned[('legal_and_availability', 'rent_to_students')].value_counts(dropna=False)


# In[40]:


df_otodom_cleaned['equipment'].head()


# In[41]:


for col in df_otodom_cleaned['equipment'].columns:
    df_otodom_cleaned[('equipment', col)] = df_otodom_cleaned[('equipment', col)].fillna(0).astype(bool)
df_otodom_cleaned['equipment'].head()


# In[42]:


for col in df_otodom_cleaned['media_types'].columns:
    df_otodom_cleaned[('media_types', col)] = df_otodom_cleaned[('media_types', col)].fillna(0).astype(bool)
df_otodom_cleaned['media_types'].head()


# In[43]:


for col in df_otodom_cleaned['heating'].columns:
    df_otodom_cleaned[('heating', col)] = df_otodom_cleaned[('heating', col)].fillna(0).astype(bool)
df_otodom_cleaned['heating'].head()


# In[44]:


for col in df_otodom_cleaned['security'].columns:
    df_otodom_cleaned[('security', col)] = df_otodom_cleaned[('security', col)].fillna(0).astype(bool)
df_otodom_cleaned['security'].head()


# In[45]:


for col in df_otodom_cleaned['windows'].columns:
    df_otodom_cleaned[('windows', col)] = df_otodom_cleaned[('windows', col)].fillna(0).astype(bool)
df_otodom_cleaned['windows'].head()


# In[46]:


for col in df_otodom_cleaned['building_material'].columns:
    df_otodom_cleaned[('building_material', col)] = df_otodom_cleaned[('building_material', col)].fillna(0).astype(bool)
df_otodom_cleaned['building_material'].head()


# In[47]:


for col in df_otodom_cleaned['additional_information'].columns:
    df_otodom_cleaned[('additional_information', col)] = df_otodom_cleaned[('additional_information', col)].fillna(0).astype(bool)
df_otodom_cleaned['additional_information'].head()


# Converting selected columns to the strings<br>
# *We do not care about backward compatibly, and a `string` is much more readable than a `object`*

# In[48]:


columns_to_convert = [
    ('listing', 'link'),
    ('listing', 'title'),
    ('listing', 'summary_description'),
    ('listing', 'remote_service'),
    ('location', 'complete_address'),
    ('location', 'street'),
    ('location', 'city'),
    ('location', 'voivodeship'),
    ('legal_and_availability', 'available_from'),
    ('legal_and_availability', 'completion'),
    ('legal_and_availability', 'ownership'),
    ('type_and_year', 'building_type'),
]

# Convert each column to the pandas string type
for col in columns_to_convert:
    df_otodom_cleaned[col] = df_otodom_cleaned[col].astype('string')


# In[49]:


df_otodom_cleaned.dtypes.to_dict()


# ## 3. Save cleaned data

# ### 3.1. Save data

# In[50]:


data_path_manager.save_df(df_otodom_cleaned, domain="otodom")


# ### 3.2 Check saved data

# ### Otodom

# In[51]:


df_otodom_saved = data_path_manager.load_df(domain="otodom", is_cleaned=True)
df_otodom_saved.head()


# In[52]:


are_identical = df_otodom_saved.equals(df_otodom_cleaned)
if not are_identical:
    raise ValueError("The saved DataFrame is not identical to the original one.")
else:
    print("The saved DataFrame is identical to the original one.")

