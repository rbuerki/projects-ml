# Movie Tweetings Recommender Class

All code of the different notebooks put together in one `Recommender` class.

This Recommender uses FunkSVD to make predictions of exact ratings. And uses 
either FunkSVD or a Knowledge Based recommendation (highest ranked) to make 
recommendations for users. Finally, if given a movie, the recommender will 
provide movies that are most similar as a Content Based Recommender.

### Install

This project requires **Python 3.x** and the following Python libraries installed:

- [NumPy](http://www.numpy.org/)
- [Pandas](http://pandas.pydata.org)

### Code / Files

- `recommender.py`: Recommender Class with the functions
    - init()
    - fit()
    - predict_ratings()
    - make_recommendations()

- `recommender_functions.py`: Several helper functions that are called to make recommendations.

(In the folder `unfinished business` is a second attempt, that has better docstrings / formatting, but I didn't make it work fully. Too lazy to track the bug down at the moment.)

### Run

In a terminal or command window, navigate to the top-level project directory (the one that contains this README) 
and run one the following commands:

Active python
```bash
ipython
``` 
Pull recommender file
```bash
from recommender import Recommender
```  
Instantiate Recommender
```bash
rec = Recommender()
```
fit with default parameters
```bash
rec.fit('../data/training_data.csv', '../data/movies_clean.csv')
```
and so on (rec.predict_ratings(), rec.make_recommendations(), ...)


### Data

Pre-cleaned MovieTweetings data. Data source: [MovieTweetings Data](https://github.com/sidooms/MovieTweetings/tree/master/recsyschallenge2014) 