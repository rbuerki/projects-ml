# Disaster Response Classification and Web App
A repository containing code and data for NLP Classification with Multi-Label Target. The goal is to classify disaster related messages.

### Introduction to the project and methodology

This project has two major parts:

1. Data / ML Pipelines: Two pipelines for ETL of the input data and for model training (incl. GridsearchCV) with new data. 

2. A web app for use during a disaster event, to classify a disaster message into several categories, in order that the message can be directed to the appropriate aid agencies.

Note: For the two parts of the project two different models / ML pipelines have been created. For the main pipeline there is a model that takes the message and the corresponding genre category as input (saved as `classifier`), for the app there is a simpler model that takes only the message string as input (saved as `app_classifier`).


This project was completed as part of the [Udacity Data Scientist Nanodegree](https://eu.udacity.com/course/data-scientist-nanodegree--nd025). Code templates and data were provided by Udacity. The data was originally sourced by Udacity from Figure Eight.

### Install

This project requires **Python 3.x** and the following Python libraries installed:

- [NumPy](http://www.numpy.org/)
- [Pandas](http://pandas.pydata.org)
- [sklearn](scikit-learn.org/)
- [nltk](http://www.nltk.org/)
- [sqlalchemy](https://www.sqlalchemy.org/)
- [plotly](https://plot.ly/)
- [flask](https://pypi.org/project/Flask/)
- [joblib](https://pypi.org/project/joblib/)
- [sys](https://docs.python.org/3/library/sys.html)
- [re](https://docs.python.org/3/library/re.html)


### Code / Files

- `process_data.py`: ETL pipeline. Takes csv files containing message data and message categories (labels) as input, stores a merged and cleaned version of this data in a SQLite database.
- `train_classifier.py`: Takes the SQLite database as input and uses the data to train and tune a ML model for categorizing messages. The fitted model is stored as pickle file test evaluation metrics are printed as part of the training process.
- `run.py`: Launches the web app. 
- `ETL Pipeline Preparation.ipynb`: Some code in this Jupyter notebook was used in the development of process_data.py. It contains basic exploration concerning cleaning and the decision on how to perform a stratified split into train / test sets.
- `EDA on training set.ipynb`: Some deeper exploration of the input data performed on the training set.
- `ML Model Evaluation.ipynb`: Code for testing of different baselines models (algorithms) and development of the pipeline that is used in train_classifier.py
- models: Folder containing saved models and aslo an alternative ML training pipeline for training the simpler app classifier and the Model Evaluation notebook.
- data: Folder containing messages and categories datasets in csv format. And also the EDA and ETL preparation notebooks.
- templates: Folder containing the files necessary to run and render the web app.

### Run

In a terminal or command window, navigate to the top-level project directory (the one that contains this README) 
and run one the following commands:

Launch ETL Pipeline
```bash
python process_data.py data/messages.csv data/categories.csv DisasterResponse.db
```  
Launch ML Pipeline
```bash
python train_classifier.py DisasterResponse.db models/classifier.pkl
```
Launch Web App
```bash
python run.py
```
(Then go to http://0.0.0.0:3001)


### Data (Warning)

The data used for this project is very unbalanced. Some of the target categories have very few positive examples. In such cases the classifier recall (i.e. proportion of positive examples that are correctly labelled) is very low. 