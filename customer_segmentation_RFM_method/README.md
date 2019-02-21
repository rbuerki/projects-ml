# Customer Segmenation with RFM
A repository containing code and data for customer segmentation with the RFM method (Recency, Frequency, Monetary Value). Two approaches have been tested, one with k-means clustering and one with the 'classic' quantile method. The results have been compared, but without deeper analysis - this project is focused on code implementation.

### Introduction to the methodology

RFM is an acronym of recency, frequency and monetary value.These three values are commonly used quantifiable factors in cohort analysis. Because of their simple and intuitive concept, they are popular among other customer segmentation methods. (And they are also ready available most of the time.)

I have referenced 2 good blogposts in the notebooks that adress RFM segmentation. Some more conceptual rescources can be found here:
- https://clevertap.com/blog/rfm-analysis/
- https://www.optimove.com/learning-center/rfm-segmentation
- https://www.blastam.com/blog/rfm-analysis-boosts-sales

### Project and code

The **code** is split up into three notebooks:
1. `1-data_prep.ipynb`: Data cleaning / preparation (calculation RFM-metrics)
2. `2-CLV_calculation.ipynb`: k-means based clustering with help of RFM-metrics
3. `3-frequency_recency_analysis.ipynb`: quantile scoring with help of RFM-metrics, comparison of results with k-means

### Data

The data is the [Online Retail Dataset](http://archive.ics.uci.edu/ml/datasets/online+retail) that can be downloaded from UCI Machine Learning Repository. It is the same data as in the clv calculation project.

This is a transnational data set which contains all the transactions occurring between 01/12/2010 and 09/12/2011 for a UK-based and registered non-store online retail.The company mainly sells unique all-occasion gifts. Many customers of the company are wholesalers.

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
- [sklearn](https://scikit-learn.org/)
- [tqdm](https://pypi.org/project/tqdm/)

You will also need to have software installed to run and execute an [iPython Notebook](http://ipython.org/notebook.html)