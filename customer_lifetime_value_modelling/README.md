# customer_lifetime_value_modelling
A repository containing code and data for a project modelling customer lifetime value (clv) in non-contracutal business.

This project is based on an excellent [blogpost](https://towardsdatascience.com/whats-a-customer-worth-8daf183f8a4f) by Susan Li published on Medium. 

### Introduction to the project and methodology

In e-Commerce or the stationary retail business, the relationships between businesses and customers are non-contractual. In the non-contractual world, customers go away silently This makes CLV calculation tricky. We have to look at a customer’s purchase history and the time since his last transaction and ask a question: is the customer alive but dormant, or is the customer “dead” (“alive” means customers interact with us, “die” means they become inactive as customers)?

The methodology is based on paper by Dr. Peter Fader of Wharton. The paper ("Counting Your Customers") can be found in the repository. The complex underlying mathematics is handled by the lifetimes package (see below, and thanks for that!)

### Install

This project requires **Python 3.x** and the following Python libraries installed:

- [NumPy](http://www.numpy.org/)
- [Pandas](http://pandas.pydata.org)
- [matplotlib](http://matplotlib.org/)
- [seaborn](http://seaborn.org)
- [lifetimes](https://github.com/CamDavidsonPilon/lifetimes)
- [tqdm](https://pypi.org/project/tqdm/)

You will also need to have software installed to run and execute an [iPython Notebook](http://ipython.org/notebook.html)

### Code

The code is provided in the `blog_automotiveChurn.ipynb` notebook file. 
It requires the `churnData.csv` dataset file to run. 

### Run

In a terminal or command window, navigate to the top-level project directory (the one that contains this README) 
and run one of the following commands:

```bash
ipython notebook code_churnBlog.ipynb
```  
or
```bash
jupyter notebook code_churnBlog.ipynb
```

This will open the iPython Notebook software and project file in your browser.

### Data

The data is the [Online Retail Dataset](http://archive.ics.uci.edu/ml/datasets/online+retail) that can be downloaded from UCI Machine Learning Repository.

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
