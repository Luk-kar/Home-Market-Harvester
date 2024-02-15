# Notebooks Directory

## Overview

The **notebooks** directory is an integral part of the development environment for our data pipeline. It contains Jupyter notebooks that are used for exploratory data analysis, data cleaning, and model-building stages of the pipeline.

## Purpose

The notebooks within this directory are designed strictly for **development purposes** and are not intended for use in production. They serve as a platform for interactive development and debugging, which is particularly crucial given the fragile nature of dealing with second-party data sources.

The interactivity of Jupyter notebooks provides a more flexible environment for handling the intricacies and potential unpredictability of external data sources. The ability to iteratively run and modify small sections of code makes it easier to identify and address issues that arise during the data handling process.

## Directory Contents

    `001_data_preview.ipynb`: For initial exploration and previewing of the data.
    `002_data_cleaning.ipynb`: Contains routines for cleaning the dataset.
    `003_EDA_local.ipynb`: Used for exploratory data analysis, focusing on local aspects of the dataset for the selected point.
    `003_EDA_narrowed.ipynb`: A more focused exploratory data analysis on specific aspects of the selected building types.
    `003_EDA.ipynb`: General exploratory data analysis of the entire dataset.
    `004_model_building.ipynb`: Notebook for building and tuning the predictive models.

## Usage in Production

Please note that while these notebooks are valuable for development, the production pipeline relies on scripts that are tested, version-controlled, and optimized for performance and stability. The production environment ensures the seamless operation of the data pipeline, adherence to production standards, and integration with our CI/CD processes.

## Contribution

Developers are welcome to use these notebooks as a playground for experimenting with new ideas and debugging existing processes. It is important to note that enhancements or experimental code within these notebooks are not expected to be integrated into the production pipeline. The primary purpose of this space is to provide a flexible environment for exploration and testing, without the obligation of advancing the notebook content to production stages.
