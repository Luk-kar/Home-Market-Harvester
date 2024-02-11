#!/usr/bin/env python
# coding: utf-8

# # EDA

# ## 1. Load cleaned data

# In[1]:


# Standard imports
from pathlib import Path
import ast
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

# Suppress future warnings
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

# Third party imports
import numpy as np
import pandas as pd

# Local imports
from pipeline.src._csv_utils import DataPathCleaningManager
from pipeline.config._config_manager import ConfigManager


# In[2]:


config_file = ConfigManager("run_pipeline.conf")
TIMEPLACE = "MARKET_OFFERS_TIMEPLACE"
data_timeplace = config_file.read_value(TIMEPLACE)
if data_timeplace is None:
    raise ValueError(F"The configuration variable {TIMEPLACE} is not set.")

data_path_manager = DataPathCleaningManager(data_timeplace, project_root)

try:
    df_olx = data_path_manager.load_df(domain="olx", is_cleaned=True)
except FileNotFoundError as e:
    print(e)
    df_olx = None

try:
    df_otodom = data_path_manager.load_df(domain="otodom", is_cleaned=True)
except FileNotFoundError as e:
    print(e)
    df_otodom = None


# In[3]:


if df_olx is None and df_otodom is None:
    raise ValueError("No dataframes were loaded.")


# ### 1.1 OLX

# In[4]:


df_olx


# In[5]:


df_olx.dtypes


# In[6]:


if df_olx is not None:
    df_olx.columns


# ### 1.2 otodom

# In[7]:


if (df_otodom is not None) and (len(df_otodom) >= 5):
    df_otodom.sample(5)


# In[8]:


if df_otodom is not None and len(df_otodom) < 5:
    df_otodom.head()


# In[9]:


if df_otodom is not None:
    df_otodom.columns


# ### 1.3 Combined

# In[10]:


def safely_convert_dtypes(df, dtype_specs) -> pd.DataFrame:
    """
    Converts column data types in a DataFrame according to the specified data types,
    handling exceptions gracefully.
    
    Args:
    - df: pandas DataFrame to convert.
    - dtype_specs: Dictionary specifying the target data type for each column.
    """
    # Transform keys in dtype_specs if necessary
    transformed_dtype_specs = {
        ast.literal_eval(key) if isinstance(key, str) and key.startswith('(') else key: dtype
        for key, dtype in dtype_specs.items()
    }

    for column, target_dtype in transformed_dtype_specs.items():
        try:
            # Ensure column exists in DataFrame before attempting conversion
            if column in df.columns:
                df[column] = df[column].astype(target_dtype)
            else:
                print(f"Warning: Column {column} does not exist in the DataFrame.")
        except ValueError as e:
            print(f"Warning: Could not convert column {column} to {target_dtype}. Error: {e}")
    
    return df

def ensure_multiindex(df, combined_schema) -> pd.DataFrame:
    """
    Ensures the DataFrame's columns are in MultiIndex format according to the combined schema.
    
    Args:
    - df: DataFrame to adjust.
    - combined_schema: The schema with which to align the DataFrame's columns.
    """
    # Convert column names to MultiIndex if they are not already
    if not isinstance(df.columns, pd.MultiIndex):
        multiindex_columns = [tuple(col.split(", ")) if ", " in col else (col, '') for col in combined_schema]
        df.columns = pd.MultiIndex.from_tuples(multiindex_columns)
    return df

def align_columns_to_schema(df, combined_schema) -> pd.DataFrame:
    """
    Aligns DataFrame columns to the combined schema, preserving existing columns and adding missing ones.
    
    Args:
    - df: DataFrame to align.
    - combined_schema: Schema to align the DataFrame's columns to.
    """
    # Generate the target column order from the schema
    target_columns = list(combined_schema.keys())
    
    # Identify missing columns and fill them appropriately
    missing_columns = [col for col in target_columns if col not in df.columns]
    for col in missing_columns:
        df[col] = np.nan  # or False for boolean columns, as appropriate
    
    # Reorder the DataFrame to match the target column order, including only the columns present in the schema
    df = df.reindex(columns=[col for col in target_columns if col in df.columns or col in missing_columns])
    
    return df

def transform_olx(df_olx: pd.DataFrame, combined_df_schema_json: dict) -> pd.DataFrame:
    """
    Transforms the df_olx DataFrame to align with the combined DataFrame schema,
    including converting column names to a MultiIndex format, filling missing columns,
    adding calculated columns, and ensuring data types match the combined schema.

    Args:
    - df_olx (pd.DataFrame): DataFrame containing data from OLX.
    - combined_df_schema_json (dict): Schema definition for the combined DataFrame,
                                      including data types and column structure.

    Returns:
    - pd.DataFrame: Transformed df_olx aligned with the combined DataFrame schema.
    """

    # Step 1: Create a mapping
    column_mapping = {
        'link': ('listing', 'link'),
        'title': ('listing', 'title'),
        'price': ('pricing', 'price'),
        'rent': ('pricing', 'rent'),
        'summary_description': ('listing', 'summary_description'),
        'ownership': ('legal_and_availability', 'ownership'),
        'floor_level': ('size', 'floor'),
        'is_furnished': ('equipment', 'furniture'),
        'building_type': ('type_and_year', 'building_type'),
        'square_meters': ('size', 'square_meters'),
        'number_of_rooms': ('size', 'number_of_rooms'),
        'voivodeship': ('location', 'voivodeship'),
        'city': ('location', 'city'),
        'street': ('location', 'street')
    }


    # Step 2: Modify df_olx to have a MultiIndex
    df_olx.columns = pd.MultiIndex.from_tuples([column_mapping.get(col, (col, '')) for col in df_olx.columns])

    # Step 3: Identify and fill missing columns 
    # in df_olx based on the combined schema
    combined_df_columns_names = [ast.literal_eval(key) if isinstance(key, str) and key.startswith('(') else key for key in combined_df_schema_json["dtypes"].keys()]
    missing_columns = set(combined_df_columns_names) - set(df_olx.columns)

    for col in missing_columns:
        if col in [('equipment', 'furniture'),]:  # Add other boolean columns if any
            df_olx[col] = False
        else:
            df_olx[col] = np.nan

    # Step 5: Reorder df_olx columns to match the combined DataFrame schema
    df_olx = df_olx.reindex(columns=combined_df_columns_names)

    # Step 6: Add calculated columns
    df_olx[('pricing', 'total_rent')] = df_olx[('pricing', 'price')].add(df_olx[('pricing', 'rent')], fill_value=0).round(2)

    df_olx[('location', 'complete_address')] = df_olx.apply(
        lambda row: ', '.join(
            value for value in [row[('location', 'street')], row[('location', 'city')], row[('location', 'voivodeship')]]
            if not pd.isna(value)
        ),
        axis=1
    )

    # Step 7: Fill NaNs for specified columns and replace NaNs with appropriate values
    columns_to_fill_false = [
        ('size', 'attic'),
        ('amenities', 'elevator'),
        ('amenities', 'parking_space'),
        ('equipment', 'no_information'),
        ('equipment', 'stove'),
        ('equipment', 'fridge'),
        ('equipment', 'oven'),
        ('equipment', 'washing_machine'),
        ('equipment', 'TV'),
        ('equipment', 'dishwasher'),
        ('media_types', 'internet'),
        ('media_types', 'telephone'),
        ('media_types', 'cable_TV'),
        ('heating', 'electric'),
        ('heating', 'gas'),
        ('heating', 'other'),
        ('heating', 'boiler_room'),
        ('heating', 'district'),
        ('heating', 'tile_stove'),
        ('security', 'intercom_or_video_intercom'),
        ('security', 'anti_burglary_doors_or_windows'),
        ('security', 'monitoring_or_security'),
        ('security', 'anti_burglary_roller_blinds'),
        ('security', 'alarm_system'),
        ('security', 'enclosed_area'),
        ('windows', 'aluminum'),
        ('windows', 'wooden'),
        ('windows', 'plastic'),
        ('building_material', 'concrete'),
        ('building_material', 'aerated_concrete'),
        ('building_material', 'brick'),
        ('building_material', 'wood'),
        ('building_material', 'other'),
        ('building_material', 'lightweight_aggregate'),
        ('building_material', 'hollow_brick'),
        ('building_material', 'silicate'),
        ('building_material', 'large_panel'),
        ('building_material', 'reinforced_concrete'),
        ('additional_information', 'duplex'),
        ('additional_information', 'air_conditioning'),
        ('additional_information', 'separate_kitchen'),
        ('additional_information', 'basement'),
        ('additional_information', 'utility_room'),
        ('additional_information', 'non_smokers_only'),
    ] 
    for col in columns_to_fill_false:
        df_olx[col] = df_olx[col].fillna(False)

    columns_to_fill_true = [
        ('media_types', 'no_information'),
        ('heating', 'no_information'),
        ('security', 'no_information'),
        ('windows', 'no_information'),
        ('building_material', 'no_information'),
        ('additional_information', 'no_information'),
    ]

    for col in columns_to_fill_true:
        df_olx[col] = df_olx[col].fillna(True)

    # Step 8: Safely convert data types according to the combined schema
    df_olx = safely_convert_dtypes(df_olx, combined_df_schema_json["dtypes"])

    return df_olx

def transform_otodom(df_otodom: pd.DataFrame, combined_df_schema_json: dict) -> pd.DataFrame:
    """
    Transforms the df_otodom DataFrame to align with the combined DataFrame schema,
    including filling missing columns and ensuring data types match the combined schema.

    Args:
    - df_otodom (pd.DataFrame): DataFrame containing data from Otodom.
    - combined_df_schema_json (dict): Schema definition for the combined DataFrame,
                                      including data types and column structure.

    Returns:
    - pd.DataFrame: Transformed df_otodom aligned with the combined DataFrame schema.
    """

    # Step 1: Identify and fill missing columns in df_otodom based on the combined schema
    combined_df_columns_names = [
        ast.literal_eval(key) if isinstance(key, str) and key.startswith('(') else key for key in combined_df_schema_json["dtypes"].keys()
        ]

    # Step 2: Reorder otodom_pl columns to match the combined DataFrame schema
    df_otodom = df_otodom.reindex(columns=combined_df_columns_names)

    # Step 3: Safely convert data types according to the combined schema
    df_otodom = safely_convert_dtypes(df_otodom, combined_df_schema_json["dtypes"])

    return df_otodom

def transform_combined_df(combined_df: pd.DataFrame) -> pd.DataFrame:
    """
    Adds calculated columns to the combined DataFrame and reorders the columns.
    
    Args:
    - combined_df: DataFrame to transform.
    
    Returns:
    - pd.DataFrame: The transformed combined DataFrame.
    """

    # Step 1: Add deposit_ratio column
    combined_df.loc[:, ("pricing", "deposit_ratio")] = np.where(
        combined_df["pricing"]["total_rent"] != 0,
        (combined_df["pricing"]["deposit"] / combined_df["pricing"]["total_rent"]).round(2),
        np.nan  # or 0, depending on your preference for default value
    )

    # Step 2: Add total price per square meter column
    combined_df.loc[:, ("pricing", "total_rent_sqm")] = (
        combined_df['pricing']['total_rent'] / combined_df['size']['square_meters']).replace([np.inf, -np.inf], np.nan
                                                                                             ).round(2)

    # round to 2 decimals if non Nan value else leave as is
    combined_df.loc[:, ("pricing", "deposit")] = combined_df[("pricing", "deposit")].apply(lambda x: round(x, 2) if pd.notna(x) else x)


    # Step 3: Reorder columns
    columns = combined_df.columns.tolist()

    combined_df = combined_df[columns]

    return combined_df

def combine_olx_otodom(df_olx: pd.DataFrame, df_otodom: pd.DataFrame) -> pd.DataFrame:
    """
    Combines the OLX and Otodom DataFrames into a single DataFrame.
    """

    combined_df = pd.concat([df_otodom, df_olx], ignore_index=True)

    return combined_df

def create_combined_df(df_olx: pd.DataFrame, df_otodom: pd.DataFrame, combined_df_schema_json: dict) -> pd.DataFrame:
    """
    Creates the combined DataFrame by transforming the OLX and Otodom DataFrames and combining them.
    
    Args:
    - df_olx: DataFrame containing OLX data.
    - df_otodom: DataFrame containing Otodom data.
    
    Returns:
    - pd.DataFrame: The combined DataFrame.
    
    Raises:
    - ValueError: If both input DataFrames are None.
    """

    if df_olx is None and df_otodom is None:
        raise ValueError("Both dataframes are None.")

    if df_olx is not None:
        df_olx = transform_olx(df_olx, combined_df_schema_json)
    if df_otodom is not None:
        df_otodom = transform_otodom(df_otodom, combined_df_schema_json)

    combined_df = None
    if df_olx is not None and df_otodom is not None:
        combined_df = combine_olx_otodom(df_olx, df_otodom)
    elif df_olx is not None:
        combined_df = df_olx
    else:
        combined_df = df_otodom

    combined_df = transform_combined_df(combined_df)

    return combined_df

combined_df_schema_json = data_path_manager.load_schema("combined")

combined_df = create_combined_df(df_olx, df_otodom, combined_df_schema_json)

combined_df.tail()


# In[11]:


pd.reset_option('display.max_rows')


# In[12]:


combined_df.dtypes.to_dict()


# Saving and checking combined df

# In[13]:


data_path_manager.save_df(combined_df, domain="combined")


# In[14]:


def find_discrepancies(combined_df: pd.DataFrame, combined_df_loaded: pd.DataFrame) -> dict:
    """
    Finds discrepancies between the DataFrame and the combined schema.
    
    Args:
    - combined_df: DataFrame to check for discrepancies.
    - combined_df_loaded: The schema to compare the DataFrame to.
    
    Returns:
    - dict: A dictionary containing the discrepancies found in the DataFrame.
    """
    # With different shapes, the DataFrames the comparison is not meaningful
    if combined_df_loaded.shape != combined_df.shape:
        raise ValueError(f"DataFrames have different shapes: {combined_df_loaded.shape} vs {combined_df.shape}")
    
    # Check for data type discrepancies
    dtype_discrepancies = combined_df.dtypes != combined_df_loaded.dtypes
    if dtype_discrepancies.any():
        print("Data type discrepancies found:")
        for col, is_different in dtype_discrepancies.items():
            if is_different:
                print(f"Column '{col}': Original dtype = {combined_df[col].dtype}, Loaded dtype = {combined_df_loaded[col].dtype}")

    # Find rows and columns where the two DataFrames differ
    diff_mask = combined_df_loaded.ne(combined_df)

    # Any columns with differences?
    columns_with_difference = diff_mask.any()

    # Any rows with differences?
    rows_with_difference = diff_mask.any(axis=1)

    # Extract indices of rows with differences
    rows_diff_indices = rows_with_difference[rows_with_difference].index

    # Report on differences
    if rows_diff_indices.size > 0:
        print(f"Differences found in {rows_diff_indices.size} rows.")
        for col in combined_df.columns[columns_with_difference]:
            for idx in rows_diff_indices:
                val_original = combined_df.loc[idx, col]
                val_loaded = combined_df_loaded.loc[idx, col]
                if pd.notna(val_original) or pd.notna(val_loaded):  # Report only non-NaN differences
                    print(f"Row {idx}, Column '{col}': original = {val_original}, loaded = {val_loaded}")
    else:
        print("The saved DataFrame is identical to the original one.")


# In[15]:


combined_df_loaded = data_path_manager.load_df(domain="combined", is_cleaned=True)

are_identical = combined_df_loaded.equals(combined_df)
if not are_identical:
    find_discrepancies(combined_df, combined_df_loaded)
    raise ValueError("The saved DataFrame is not identical to the original one.")
else:
    print("The saved DataFrame is identical to the original one.")


# In[16]:


combined_df_loaded['type_and_year'].dtypes


# In[17]:


if len(combined_df_loaded) < 5:
    print(f"The DataFrame has {len(combined_df_loaded)} rows.")
    combined_df_loaded.head()


# In[18]:


if len(combined_df_loaded) >= 5:
    combined_df_loaded.sample(5)


# In[19]:


combined_df_loaded[('listing', 'link')].duplicated().sum()


# In[20]:


len(combined_df_loaded)

