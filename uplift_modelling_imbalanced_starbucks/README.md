# Uplift Modelling Exercise: Starbucks
A repository containing code and data for an uplift modelling project that deals with very imbalanced target classes.

### Introduction to project and results

The dataset in this exercise was originally used as a take-home assignment provided by Starbucks for their job candidates. The data for this exercise consists of about 120,000 data points split in a 2:1 ratio among training and test files. In the experiment simulated by the data, an advertising promotion was tested to see if it would bring more customers to purchase a specific product priced at $10. Since it costs the company 0.15 to send out each promotion, it would be best to limit that promotion only to those that are most receptive to the promotion. Each data point includes one column indicating whether or not an individual was sent a promotion for the product, and one column indicating whether or not that individual eventually purchased that product. Each individual also has seven additional features associated with them, which are provided abstractly as V1-V7.

The main point in this implementation was to create a pipeline that oversamples the minority target class with SMOTENC (see [here](https://imbalanced-learn.readthedocs.io/en/stable/generated/imblearn.over_sampling.SMOTENC.html)) and selects an appropriate classifier.
Without much further tuning the benchmark metrics could be matched / beaten. 

I then also experimented with tuning the strategy based on prediction probability thresholds and recall. I could maximise one of the target KPIs but lost on the other one. A 2nd notebook contains an additional experiment / approach based on trying to lift only _incremental sales_. But this attempt unfortunately failed due to low model precision. (But at least in theory it would have been a much better strategy.)

### Install

This project requires **Python 3.x** and the following Python libraries installed:

- [NumPy](http://www.numpy.org/)
- [Pandas](http://pandas.pydata.org)
- [matplotlib](http://matplotlib.org/)
- [seaborn](http://seaborn.org)
- [scikit-learn](http://scikit-learn.org/stable/)
- [imbalanced-learn](https://imbalanced-learn.readthedocs.io/en/stable/)

You will also need the custom files `cleaning_functions`, `EDA_functions` from my codebook repository.
You will also need to have software installed to run and execute an [iPython Notebook](http://ipython.org/notebook.html)

### Code

The code is provided in the `promotion uplifting statbucks.ipynb` notebook file. 
It requires the `training.csv` and `test.csv` dataset files to run. 

### Run

In a terminal or command window, navigate to the top-level project directory (the one that contains this README) 
and run one of the following commands:

```bash
ipython notebook promotion uplifting starbucks.ipynb
```  
or
```bash
jupyter notebook promotion uplifting starbucks.ipynb
```

This will open the iPython Notebook software and project file in your browser.