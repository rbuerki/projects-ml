import numpy as np
import pandas as pd
import recommender_functions as rf
import sys # can use sys to take command line arguments

class Recommender():
    """This Recommender uses FunkSVD to make predictions of exact ratings. 
    And uses either FunkSVD or a Knowledge Based recommendation (highest 
    ranked) to make recommendations for users.  Finally, if given a movie, 
    the recommender will provide movies that are most similar as a 
    Content Based Recommender."""

    def __init__(self, ):
       """No attributes required here."""



    def fit(self, reviews_pth, movies_pth, latent_features=12, learning_rate=0.0001, iters=100):
        """ Perform matrix factorization using a basic form of FunkSVD with 
    no regularization.
    
    INPUT:
        reviews_pth: path to csv with at least the four columns: 
            'user_id', 'movie_id', 'rating', 'timestamp'
        movies_pth: path to csv with each movie / movie information in each row
        latent_features: int, number of latent features used (default = 12)
        learning_rate: float, the learning rate (defaoult = 0.0001)
        iters: int, the number of iterations (default = 100)
    
    OUTPUT:
        user_matrix: np.array, user by latent feature matrix
        movie_mat: np.array, latent feature by movie matrix
    """
        
        # store inputs as attributes
        self.reviews = pd.read_csv(reviews_pth)
        self.movies = pd.read_csv(movies_pth)

        # create user-item-matrix
        self.user_item_df, self.user_item_np = rf.create_user_item_matrix(self.reviews)

        # fit FunkSVD to training set
        self.user_mat, self.movie_mat = rf.apply_FunkSVD(user_item_np, 
            latent_features=latent_features, learning_rate=learning_rate, 
            iters=iters)

    def predict_rating(self, user_id, movie_id):
        """ Predict rating for a user_id and movie_id pair. 
        
        INPUT:
            user_id: int, user_id according to input data
            movie_id: int, movie_id according to input data

        OUTPUT:
            pred: float, predicted rating according to FunkSVD
        """
        
        try: # identify user and movie indices in U and V
            user_row = np.where(self.user_ids_series == user_id)[0][0]
            movie_col = np.where(self.movie_ids_series == movie_id)[0][0]

            # take dot product 
            pred = np.dot(self.user_mat[user_row, :], self.movie_mat[:, movie_col])

            # get movie name
            movie_name = \
                str(self.movies[self.movies['movie_id'] == movie_id]['movie'])[5:]
            movie_name = \
                movie_name.replace('\nName: movie, dtype: object', '')
            
            print("For user {} we predict a {} rating for the movie {}." \
                .format(user_id, round(pred, 2), str(movie_name)))

            return pred

        except:
            print("Prediction cannot be made for this user-movie pair. It " \
                "looks like one of these items does not exist in the database.")

            return None
            


    def make_recommendations(self, _id, _id_type='movie', rec_num=5):
        """ Make recommendations for a user_id or a movie_id. 
        - For users in data base FunkSVD-based collaborative filtering is 
            applied. For new users we return just the top rated movies.
        - For movies content based filtering depending on 
            year and genre is applied.

        INPUT:
            _id: int, either a user or movie id
            _id_type: str, "movie" or "user" (default = "movie")
            rec_num: int, number of recommendations to return

        OUTPUT:
        recs: list or numpy array of recommended movies like the
                       given movie, or for a given user_id
        """
       
        rec_ids, rec_names = None, None
        
        if _id_type == 'user':

            # if we have the user
            if _id in self.user_ids_series:
                # Get index of which row the user is in for use in U matrix
                idx = np.where(self.user_ids_series == _id)[0][0]

                # take the dot product of that row and the V matrix
                preds = np.dot(self.user_mat[idx,:],self.movie_mat)

                # pull the top movies according to the prediction
                indices = preds.argsort()[-rec_num:][::-1] #indices
                rec_ids = self.movie_ids_series[indices]
                rec_names = rf.get_movie_names(rec_ids, self.movies)

            else:
                # if we don't have the users
                rec_names = rf.list_most_popular(_id, rec_num, 
                    self.ranked_movies)
                print("Because user isn't in database, we are giving " \
                    "back the top movie recommendations for all users.")

        # Find similar movies if it is a movie that is passed
        else:
            if _id in self.movie_ids_series:
                rec_names = \
                    list(rf.find_similar_movies(_id, self.movies))[:rec_num]
            else:
                print("That movie doesn't exist in our database. " \
                    "Sorry, we don't have any recommendations for you.")

        return rec_ids, rec_names




# test different parts to make sure it works

if __name__ == '__main__':
    import recommender as r

    #instantiate recommender
    rec = r.Recommender()

    # fit recommender
    rec.fit(reviews_pth='../data/train_data.csv', \
        movies_pth= '../data/movies_clean.csv', learning_rate=.01, iters=3)

    # predict
    rec.predict_rating(user_id=8, movie_id=2844)

    # make recommendations
    print(rec.make_recommendations(8,'user')) # user in the dataset
    print(rec.make_recommendations(1,'user')) # user not in dataset
    print(rec.make_recommendations(1853728)) # movie in the dataset
    print(rec.make_recommendations(1)) # movie not in dataset
    print(rec.n_users)
    print(rec.n_movies)
    print(rec.num_ratings)



