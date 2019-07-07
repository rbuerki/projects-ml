# Association Rules Mining 
A repository containing code and experimental data for implemenation of association rules mining (ARM, also called frequent itemset mining or market basket analysis) with the apriori algorithm.


### Introduction to project and code

WIP

We write an implementation that is leveraging the apriori algorithm to generate simple {A} -> {B} association rules. Since (for simplicity) we only care about understanding relationships between any given pair of items, using apriori to get to item sets of size 2 is sufficient. The code and idea is based on this [blogpost](https://www.datatheque.com/posts/association-analysis/). 


### Data

“The Instacart Online Grocery Shopping Dataset 2017”, accessed from [here](https://www.instacart.com/datasets/grocery-shopping-2017) on July, 4th 2019. For information about the contents of the files, see this [data dictionary](https://gist.github.com/jeremystan/c3b39d947d9b88b3ccff3147dbcf6c6b).

(The second notebook is based on another private data source that can not be disclosed.)


### Additional Resources

- Good and profound introduction to ARM with Apriori in this [blogpost](https://medium.com/cracking-the-data-science-interview/an-introduction-to-big-data-itemset-mining-a97a17e0665a) (no code)


### Install

This project requires **Python 3.x** and the following Python libraries installed:

- [NumPy](http://www.numpy.org/)
- [Pandas](http://pandas.pydata.org)
- [matplotlib](http://matplotlib.org/)
- [seaborn](http://seaborn.org)
- [tqdm](https://pypi.org/project/tqdm/)
- [MLxtnd](http://rasbt.github.io/mlxtend/)

You will also need to have software installed to run and execute an [iPython Notebook](http://ipython.org/notebook.html)



 