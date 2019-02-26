# blogPost-Churn
A repository containing code and data for a project based on functionality of Cameron Davidson's [lifelines](https://github.com/CamDavidsonPilon/lifelines) package. Goal is to construct survival functions / survival curves for customers (as a whole, in cohorts and individual). 

This is an alternative approach to churn analysis, based on the durations of customer relationship.

### Project and code

Goal of the project is to explore part of the functionalities of the aforementioned `lifelines` package. 

The **code** is split up into two notebooks:
1. 1-cohort_survival_curves_KaplanMeier.ipynb: The Kaplan-Meier estimator is a powerful non-parametric method to estimate Survival Curves for a Population / Cohort in general.
2. 2-individual_survival_regression_CoxPropHazard.ipynb: The Cox (proportional hazard) model is one of the most popular models combining the covariates (features) and the general survival function (as calculated in nb 1) to estimate survival functions on the individual level.

Some background and links to additional information can be found at the start of both notebooks.


### Data

The data is a set on Customer Churn in Telecomunications from IBM Watson Analytics. It can be downloaded [here](https://www.ibm.com/communities/analytics/watson-analytics-blog/Telco-Customer-Churn/).

For general Survival Functions with Kaplan-Meier only a minimal feature set is needed: the time at which event occurred (death or censorship) and the lifetime duration between birth and event. For the individual curves it is necessary to have some meaningful covariates (features). 

### Install

This project requires **Python 3.x** and the following Python libraries installed:

- [NumPy](http://www.numpy.org/)
- [Pandas](http://pandas.pydata.org)
- [matplotlib](http://matplotlib.org/)
- [seaborn](http://seaborn.org)
- [lifelines](https://github.com/CamDavidsonPilon/lifelines)
- [tqdm](https://pypi.org/project/tqdm/)

You will also need to have software installed to run and execute an [iPython Notebook](http://ipython.org/notebook.html)