# Home Market Harvester - Data Cleaning and Visualization

This repository contains a series of Jupyter notebooks and scripts that form part of the Home Market Harvester pipeline, focused on cleaning and visualizing housing market data from Polish real estate websites.

## a_cleaning_OLX.ipynb

This Jupyter notebook contains the data cleaning process for the housing offers scraped from olx.pl. It includes steps for removing duplicates, handling missing values, and standardizing data formats to ensure quality for further analysis and modeling.

## b_cleaning_otodom.ipynb

Similar to `a_cleaning_OLX.ipynb`, this notebook is dedicated to processing data from otodom.pl. It follows a similar cleaning regimen to ensure the data is consistent with the dataset from olx.pl and ready for combination and comparison.

## c_combining_data.ipynb

The purpose of this notebook is to combine the cleaned datasets from both sources into a unified dataframe. It may include additional processing such as aligning columns, merging datasets, and creating new features for comparative analysis.

## combined_df_schema.json

This JSON file defines the schema for the combined dataframe that results from `c_combining_data.ipynb`. It outlines the structure, expected data types, and any constraints on the data fields within the combined dataset.

## d_creating_map_data.py

This Python script takes the cleaned and combined data to generate geographical visualizations. The script includes functionality to create map-based visualizations that can be integrated into the dashboard for an interactive user experience.

---

To run the cleaning and visualization stages, ensure that the raw data is placed in the `data` directory, and then execute each Jupyter notebook in sequence. The final script `d_creating_map_data.py` can be run as a standalone Python script or imported and used in other components of the pipeline.

## a_cleaning_OLX.py, b_cleaning_otodom.py, c_combining_data.py

For operational efficiency, these notebooks are converted into Python scripts (`a_cleaning_OLX.py`, `b_cleaning_otodom.py`, `c_combining_data.py`) during runtime using the `nbconvert` tool. This conversion takes place within the same folder in the runtime, ensuring that the transition from development to production is streamlined without the need for manual script creation. The `run_ipynb` function facilitates this process, allowing the data pipeline to execute the steps defined in the notebooks automatically and reproducibly in a script-based environment.
