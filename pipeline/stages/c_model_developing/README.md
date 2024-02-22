# Home Market Harvester - Model Development

## 📋 Overview

This part of the Home Market Harvester pipeline focuses on the development of a predictive model for analyzing housing market data. The model aims to understand and forecast market trends based on current real estate data from Polish housing market platforms.

## 🗂️ Project Structure

### 📖✏️ `model_io_operations.py`

This module is responsible for input/output operations related to the model. It includes functionality to load and save datasets, as well as to manage the import and export of model parameters and metrics.

Key Functions:

- `load_data()`: Load datasets for model training and validation.
- `save_model()`: Save the trained model to a file for later use or deployment.
- `load_model()`: Load a previously saved model for inference or further training.
- `export_results()`: Save the results of model evaluations, such as accuracy metrics and error analysis.

### 🦾 `model_training.py`

This script contains the main logic for training the predictive model. It defines the model architecture, compiles the model, and manages the training process with given housing market data.

Key Components:

- Model Definition: Specifies the structure of a machine learning model.
- Training: Executes the training process using the provided dataset.
- Validating: Validates the trained model by predicting on the test set and calculating the mean error.

## 📦 Requirements

- Python 3.x
- Relevant Python [packages](pipeline/stages/c_model_developing/README.md) as required by the scripts (e.g., NumPy, pandas, scikit-learn, TensorFlow/Keras)
