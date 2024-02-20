# Home Market Harvester Project

## Overview

The Home Market Harvester is an all-encompassing data pipeline tailored to gather, purify, analyze, and display information on the real estate market. This system targets specific regions, juxtaposing chosen listings against the broader market context.

Culminating in an interactive dashboard, it presents an aggregate view of local market trends, a comparative table of handpicked listings against overall market conditions, and a geographical map pinpointing the locations of the collected offers.

Data is collected from the websites [olx.pl](https://www.olx.pl/) and [otodom.pl](https://www.otodom.pl/), which feature listings from the Polish property market.

## Project Structure

The project is organized into several directories, each with a specific role:

- `data`: Contains raw data files and processed data outputs.
- `logs`: Stores log files generated by the pipeline.
- `model`: Includes the machine learning models developed and trained on the housing data.
- `notebooks`: Jupyter notebooks for exploratory data analysis, data cleaning, and model-building stages.
- `pipeline`: Core components of the data pipeline, including scraping, cleaning, model development, and visualization scripts.

  - `components`: Contains utilities and helper functions that support the pipeline operations.
  - `config`: Organizes all configuration files necessary to control various aspects of the pipeline. Like: `a_scraping.py`, `d_data_visualizing.py`, and `run_pipeline.conf`.

    - `stages`: Contains the sequentially executed stages of the pipeline, each encapsulated in its directory and named alphabetically for order of execution:

      - `a_scraping`: Scripts responsible for extracting data from various sources, and websites. This stage is tasked with the initial collection of raw data.

      - `b_cleaning`: Contains scripts and notebooks dedicated to data cleaning and preprocessing, ensuring data quality for downstream processes. The contents include:
        - `a_cleaning_OLX.ipynb`: Jupyter notebook for cleaning data specific to the OLX platform.
        - `b_cleaning_otodom.ipynb`: Jupyter notebook for cleaning data related to the Otodom platform.
        - `c_combining_data.ipynb`: Jupyter notebook for merging data from various sources into a cohesive dataset.
        - `combined_df_schema.json`: JSON schema defining the structure and types of the combined dataframe, ensuring consistency in the merged data.
        - `d_creating_map_data.py`: Script for processing cleaned data to generate data suitable for mapping or geographical visualizations.
      - `c_model_developing`: Development and training of machine learning models. This involves selecting features and training models.
      - `d_data_visualizing`: Creation of visual representations of the data and model outputs. It utilizes a streamlit framework.

- `tests`: Unit tests for the pipeline components to ensure code reliability.

## Requirements

Look at [Pipfile](Pipfile)

## Installation

To set up the project environment:

```bash
pip install pipenv
pipenv install
pipenv shell
```

## Usage

The data pipeline can be executed by running the `run_pipeline.py` script found within the `pipeline` directory.

```bash
python pipeline/run_pipeline.py --location_query "Polish city" --area_radius int --scraped_offers_cap int
```

```bash
python pipeline/run_pipeline.py --location_query "Warszawa" --area_radius 25 --scraped_offers_cap 100
```

## Development

The `notebooks` directory contains Jupyter notebooks that serve as an interactive development environment for the data handling process. These notebooks are for development purposes and are not intended for production use.

## Testing

Tests are located in the tests directory and can be run to verify the integrity of the pipeline components. Coverage reports are generated to assess test completeness.

```bash
python -m unittest discover -s tests
```

## License

This project is licensed under the terms of the [LICENSE](LICENSE) file located in the project root.

---

**Note**: This README is for the root of the project. For detailed information about specific components or stages, refer to the README files located within the respective directories.
