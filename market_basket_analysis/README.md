# Association Rules Mining 
A repository containing code and experimental data for implemenation of association rules mining (ARM, also called frequent itemset mining) with the apriori algorithm. In this case we use it for Market Basket Analysis


### Introduction to project and code

There is three noteboks:

1. Write an implementation from scratch that is leveraging the apriori algorithm to generate simple {A} -> {B} association rules. Since (for simplicity) we only care about understanding relationships between any given pair of items, using apriori to get to item sets of size 2 is sufficient. The code and idea is based on this [blogpost](https://www.datatheque.com/posts/association-analysis/). 
2. Perform ARM with help of the MLextnd library. First generate frequent itemsets with the apriori algorithm, then calculate the association rules und visualize the results. Description of the MLextnd functionalities can be found [here](http://rasbt.github.io/mlxtend/user_guide/frequent_patterns/association_rules/).


### Data

For notebook 1:
“The Instacart Online Grocery Shopping Dataset 2017”, accessed from [here](https://www.instacart.com/datasets/grocery-shopping-2017) on July, 4th 2019. For information about the contents of the files, see this [data dictionary](https://gist.github.com/jeremystan/c3b39d947d9b88b3ccff3147dbcf6c6b).

For notebook 2:
Private data set of a B2B retailer that can not be disclosed.


### Additional Resources

Blogposts

- Good and profound introduction to ARM with Apriori in this [blogpost](https://medium.com/cracking-the-data-science-interview/an-introduction-to-big-data-itemset-mining-a97a17e0665a) (no code)
- [Blogpost](https://select-statistics.co.uk/blog/market-basket-analysis-understanding-customer-behaviour/) with implementation with arviz package in R, nice for the plots (of which I 'copied' two).

Papers

- Tan, Steinbach, Kumar. Introduction to Data Mining. Pearson New International Edition. Harlow: Pearson Education Ltd., 2014. (pp. 327-414).
- R. Agrawal, T. Imielinski, and A. Swami. Mining associations between sets of items in large databases. In Proc. of the ACM SIGMOD Int'l Conference on Management of Data, pages 207-216, Washington D.C., May 1993


### Install

This project requires **Python 3.x** and the following Python libraries installed:

- [NumPy](http://www.numpy.org/)
- [Pandas](http://pandas.pydata.org)
- [matplotlib](http://matplotlib.org/)
- [seaborn](http://seaborn.org)
- [tqdm](https://pypi.org/project/tqdm/)
- [MLxtend](http://rasbt.github.io/mlxtend/)

You will also need to have software installed to run and execute an [iPython Notebook](http://ipython.org/notebook.html)



 