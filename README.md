# 🔍🏠 Home Market Harvester Project

## 📋 Overview

The Home Market Harvester is an all-encompassing data pipeline tailored to `gather` -> `purify` -> `analyze` -> `train model` -> `display information` on the real estate market. This system targets specific regions, juxtaposing chosen listings against the broader market context.

Culminating in an interactive dashboard, it presents an aggregate view of local market trends, a comparative table of handpicked listings against overall market conditions, and a geographical map pinpointing the locations of the collected offers.

Data is collected from the websites [`olx.pl`](https://www.olx.pl/) and [`otodom.pl`](https://www.otodom.pl/), which feature listings from the Polish property market.

The program is engineered to execute on a local machine, utilizing exclusively open-source tools, augmented by two external services for data enhancement. These services include geolocation enrichment via [`Nominatim`](https://nominatim.org/release-docs/latest/library/Getting-Started/) and travel time estimation through [`api.openrouteservice`](https://openrouteservice.org/). It's crucial to obtain and configure the necessary API keys for [`api.openrouteservice`](https://openrouteservice.org/) to ensure the seamless operation of these features. The presentation layer of the project is developed with the [`streamlit`](https://docs.streamlit.io/) framework, enabling the deployment of an interactive dashboard accessible through a local URL, effectively making the insights publicly available.

## 📊 Data Visualization

![dashboard](doc/images/dashboard_preview.png)

## 🗂️ Project Structure

The project is organized into several directories, each with a specific role:

- `data`: Contains raw data files and processed data outputs.
- `logs`: Stores log files generated by the pipeline like (`a_scraping.log`, `pipeline.log`).
- `model`: Includes the machine learning models developed and trained on the housing data.
- `notebooks`: Jupyter notebooks for exploratory data analysis, data cleaning, and model-building stages.
- `pipeline`: Core components of the data pipeline, including scraping, cleaning, model development, and visualization scripts.
- `.env`: Environment configuration file, detailing essential variables for project setup, such as API keys, file paths, and server configurations. This file is crucial for ensuring that the pipeline runs smoothly in different environments.

  - `components`: Contains utilities and helper functions that support the pipeline operations.
  - `config`: Organizes all configuration files necessary to control various aspects of the pipeline. Like: `a_scraping.py`, `d_data_visualizing.py`, and `run_pipeline.conf`.

    - `stages`: Contains the sequentially executed stages of the pipeline, each encapsulated in its directory and named alphabetically for order of execution:

      - `a_scraping`: Scripts responsible for extracting data from various sources, and websites. This stage is tasked with the initial collection of raw data.

      - `b_cleaning`: Contains scripts and notebooks dedicated to data cleaning and preprocessing, ensuring data quality for downstream processes. The contents include:
        - `a_cleaning_OLX.ipynb`: Jupyter notebook for cleaning data specific to the OLX platform.
        - `b_cleaning_otodom.ipynb`: Jupyter notebook for cleaning data related to the Otodom platform.
        - `c_combining_data.ipynb`: Jupyter notebook for merging data from various sources into a cohesive dataset.
        - `combined_df_schema.json`: JSON schema defining the structure and types of the combined dataframe, ensuring consistency in the merged data.
        - `d_creating_map_data.py`: Script for processing cleaned data to generate data suitable for mapping or geographical visualizations. It uses external services like the `Nominatim` and `api.openrouteservice`.
      - `c_model_developing`: Development and training of machine learning models. This involves selecting features, training models, and validating them.
      - `d_data_visualizing`: Creation of visual representations of the data and model outputs. It utilizes a streamlit framework.

- `tests`: Unit tests for the pipeline components to ensure code reliability.

## 📦 Requirements

Look at [Pipfile](Pipfile)

## ⚙️ Installation

To set up the project environment:

```bash
pip install pipenv
pipenv install
pipenv shell
```

## 🔨 Usage

The data pipeline can be executed by running the `run_pipeline.py` script found within the `pipeline` directory.

```bash
python pipeline/run_pipeline.py --location_query "Location Name" --area_radius <radius in kilometers> --scraped_offers_cap <maximum number of offers> --destination_coords <lattitude, longitute> --user_data_path <path to your data.csv>
```

For example, to scrape housing offers for `Warsaw` within a `25` km radius, with a maximum of `100` offers, with journey destination point `(52.203531, 21.047047)` and (Optional arg) your comparison data located at `D:\path\user_data.csv`, use the following command:

```bash
python pipeline/run_pipeline.py --location_query "Warszawa" --area_radius 25 --scraped_offers_cap 100 --destination_coords "52.203531, 21.047047" --user_data_path "D:\path\user_data.csv"
```

## 💻 Development

The `notebooks` directory contains Jupyter notebooks that serve as an interactive development environment for the data handling process. These notebooks are for development purposes and are not intended for production use.

---

The pipeline allows for the individual execution of each stage as a standalone Python script, except for the d_data_visualizing stage. This particular stage leverages the [`streamlit`](https://docs.streamlit.io/) framework to create interactive data visualizations. For detailed insights into this component, refer to the: [streamlit_README](pipeline/stages/d_data_visualizing/README.MD)

## ✅ Testing

The `tests` directory houses test scripts designed to validate the functionality and reliability of different components within the pipeline. Currently, automated testing is implemented exclusively for the scraping phase.

To execute the tests use the following command:

```bash
pipenv shell # at the root of the project
python -m unittest discover -s tests -p 'test_*.py'
```

**🚨 Note**:
It's important to remember that the pipeline relies on external data sources, which may be subject to A/B tests, frontend changes, anti-bot activity, server failures and other modifications. These factors can affect the consistency and accuracy of the data collected.

## 🔧 Configuration

Configuration management for the pipeline and its distinct stages is centralized in the `pipeline/config directory`. This setup includes `.py` files designed for straightforward invocation, eliminating the need for additional input/output logic and validation. Additionally, `.conf` files are employed to handle read/write settings.

A crucial configurational element within `run_pipeline.conf` is `MARKET_OFFERS_TIMEPLACE`. This value is dynamically generated at runtime during the `a_scraping` stage and serves as the directory name for storing the newly scraped data. The format of this value is `YYYY_MM_DD_HH_MM_SS_LOCATION`, such as `2024_02_20_16_37_54_Mierzęcice__Będziński__Śląskie`, effectively timestamping and geolocating the dataset. It plays a pivotal role in the orchestration of the pipeline workflow, particularly within the `run_pipeline.py` script and its associated stages:

- `b_cleaning` stage, where specific notebooks and scripts are used for data cleaning and preparation:
  - `a_cleaning_OLX.ipynb` for OLX data,
  - `b_cleaning_otodom.ipynb` for Otodom data,
  - `c_combining_data.ipynb` for integrating datasets,
  - `d_creating_map_data.py` for producing mappable geographic data.
- `c_model_developing` stage, which focuses on the development and training of predictive models.
- `d_data_visualizing` stage, tasked with creating visual outputs to represent data and analytical findings.

---

Additionally, a `.env` file is part of the configuration, facilitating the specification of environment variables.

## 📜 License

This project is licensed under the terms of the [LICENSE](LICENSE) file located in the project root.

---

**Note**: This README is for the root of the project. For detailed information about specific components or stages, refer to the README files located within the respective directories.
