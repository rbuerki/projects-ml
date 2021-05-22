# Feature Tools Pipeline

May 2021

## Project

This documents only part of a project I was working on. The end goal was to predict churn for customers of a credit card provider. The full project cannot be disclosed here, but I would like to document the usage of the featuretools pipeline for feature generation. The

While a lot of features were loaded directly from the databases, the transactional data (coming in two types: sales and fees) had to be brought from long to wide format. For this we used  featuretools.

### Relevant code for documentation

- **Notebook 1_featuretools_exploration:** Documents some basic experimentation with featuretools leading to some important insights.
- **Notebook 2_fact_features_generation:** Was used to develop and test the actual data flow that would later be implemented in the project ...
- **fact_features.py:** ... is the (pre-)final clean code from notebook 2. It's functionality is called within them main load pipeline (load.py)
