# Sales Forecasting Retail Data
A repository containing code and data for a sales prediction project hosted on [kaggle Inclass](https://www.kaggle.com/c/competitive-data-science-predict-future-sales). It serves as final project for the ["How to win a data science competition"](https://www.coursera.org/learn/competitive-data-science/home/welcome) Coursera course. 

Provided with daily historical sales data, the task is to forecast the total amount of products sold in every shop for the test set. The list of shops and products slightly changes every month. So creating a robust model that can handle such situations is part of the challenge.

### Introduction to project and results

...

### Install

This project requires **Python 3.x** and the following Python libraries installed:

- [NumPy](http://www.numpy.org/)
- [Pandas](http://pandas.pydata.org)
- [matplotlib](http://matplotlib.org/)
- [seaborn](http://seaborn.org)
- [scikit-learn](http://scikit-learn.org/stable/)
- [tqdm](https://pypi.org/project/tqdm/)

You will also need to have software installed to run and execute an [iPython Notebook](http://ipython.org/notebook.html)

### Code

... 

### Data

**File descriptions** (original files are stored under `/data/raw`)
- `sales_train.csv` - the training set. Daily historical data from January 2013 to October 2015.
- `test.csv` - the test set. You need to forecast the sales for these shops and products for November 2015.
- `sample_submission.csv` - a sample submission file in the correct format.
- `items.csv` - supplemental information about the items/products.
- `item_categories.csv`  - supplemental information about the items categories.
- `shops.csv` - supplemental information about the shops.

**Data fields**
- `ID` - an Id that represents a (Shop, Item) tuple within the test set
- `shop_id` - unique identifier of a shop
- `item_id` - unique identifier of a product
- `item_category_id` - unique identifier of item category
- `item_cnt_day` - number of products sold. You are predicting a monthly amount of this measure
- `item_price` - current price of an item
- `date` - date in format dd/mm/yyyy
- `date_block_num` - a consecutive month number, used for convenience. January 2013 is 0, February 2013 is 1,..., October 2015 is 33
- `item_name` - name of item
- `shop_name` - name of shop
- `item_category_name` - name of item category
