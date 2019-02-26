# customer_lifetime_value_modelling
A repository containing code and data for a project modelling customer lifetime value (clv) in non-contracutal business. It was inspired by one of Susan Li's [blogposts](https://towardsdatascience.com/whats-a-customer-worth-8daf183f8a4f) and is based on functionality of the [lifetimes](https://github.com/CamDavidsonPilon/lifetimes) package.

### Introduction to the methodology

Goal of the project is to explore the functionalities of the aforementioned `lifetimes` package. It is based on methodology of Dr. Peter Fader of Wharton. The underlying paper ("Counting Your Customers") can be found in the `resources` section of the repository.

The package is basically built around two main models:
1. _BG/NBD model_ to predict future transactions
2. _Gamma Gamma model_ to predict the monetary value and thus the (residual) CLV of these future transactions

The BG/NBD model looks at recency / frequency in a customer's purchase history to calculate it's predictions. In theory it can also be used for the calculation of the probability for a customer to be 'alive' or 'dead'. But because of a simplyfication in it's inherent 'customer story' these values can be very misleading for one-time or infrequent buyers.

### Project and code

The **code** is split up into three notebooks:
1. 1-data_prep_and_EDA.ipynb: Data cleaning / preparation and basic EDA
2. 2-CLV_calculation.ipynb: Actual modelling with BG/NBD and Gamma-Gamma
3. 3-frequency_recency_analysis.ipynb: Analysis of Freq/Rec and P(alive) metrics
3. z_lifetimes_basic_functionality.ipynb: Basically follows the lifetimes docs through the full functionality

Main **findings** / results:
- From EDA: Data set may not be ideally suited for this test, as it spans one year only and there is seasonality.
- From modelling: CLV was underestimated, fit was not so good. May be partly due to saisonality in the set.
- From Freq/Rec: P(alive) calculation on individual level with BG/NBD model is rather misleading.

### Data

The data is the [Online Retail Dataset](http://archive.ics.uci.edu/ml/datasets/online+retail) that can be downloaded from UCI Machine Learning Repository.

This is a transnational data set which contains all the transactions occurring between 01/12/2010 and 09/12/2011 for a UK-based and registered non-store online retail.The company mainly sells unique all-occasion gifts. Many customers of the company are wholesalers.

A potential issue with this dataset is, that it spans only one year and the data shows seasonality. This makes it hard to predict actual customer behavior when you split it into calibration and holdout sets.

**Attribute Information**
- `InvoiceNo`: Invoice number. Nominal, a 6-digit integral number uniquely assigned to each transaction. If this code starts with letter 'c', it indicates a cancellation. 
- `StockCode`: Product (item) code. Nominal, a 5-digit integral number uniquely assigned to each distinct product. 
- `Description`: Product (item) name. Nominal. 
- `Quantity`: The quantities of each product (item) per transaction. Numeric. 
- `InvoiceDate`: Invoice Date and time. Numeric, the day and time when each transaction was generated. 
- `UnitPrice`: Unit price. Numeric, Product price per unit in sterling. 
- `CustomerID`: Customer number. Nominal, a 5-digit integral number uniquely assigned to each customer. 
- `Country`: Country name. Nominal, the name of the country where each customer resides. 

### Install

This project requires **Python 3.x** and the following Python libraries installed:

- [NumPy](http://www.numpy.org/)
- [Pandas](http://pandas.pydata.org)
- [matplotlib](http://matplotlib.org/)
- [seaborn](http://seaborn.org)
- [lifetimes](https://github.com/CamDavidsonPilon/lifetimes)
- [tqdm](https://pypi.org/project/tqdm/)

You will also need to have software installed to run and execute an [iPython Notebook](http://ipython.org/notebook.html)
