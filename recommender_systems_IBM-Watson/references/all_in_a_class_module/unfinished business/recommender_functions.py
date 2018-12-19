import numpy as np
import pandas as pd

def create_user_item_matrix(df):
    """Create user_item_matrix, with users as rows and items
    as columns.
    
    INPUT:
    df: DataFrame with (training) data.
    
    OUTPUT:
    user_item_df: DataFrame containing user_item_matrix
    user_item_np: Numpy Array containing user_item_matrix.
    """
    
    user_item = df[['user_id', 'movie_id', 'rating', 'timestamp']]
    user_item_df = user_item.groupby(
        ['user_id', 'movie_id'])['rating'].max().unstack()
    user_item_np = np.array(user_item_df)
    
    return user_item_df, user_item_np



def apply_FunkSVD(user_item_np, latent_features=12, learning_rate=0.0001, 
        iters=100):
    """ Perform matrix factorization using a basic form of FunkSVD with 
    no regularization.
    
    INPUT:
        user_item_np: np.array, matrix with users as rows, movies as columns, 
            ratings as values
        latent_features: int, number of latent features used (default = 12)
        learning_rate: float, the learning rate (defaoult = 0.0001)
        iters: int, the number of iterations (default = 100)
    
    OUTPUT:
        user_matrix: np.array, user by latent feature matrix
        movie_mat: np.array, latent feature by movie matrix
    """
    
    # Set up useful values to be used through the rest of the function
    n_users = user_item_np.shape[0]
    n_movies = user_item_np.shape[1]
    num_ratings = np.count_nonzero(~np.isnan(user_item_np))
    
    # initialize the user and movie matrices with random values
    user_mat = np.random.rand(n_users, latent_features)
    movie_mat = np.random.rand(latent_features, n_movies)
    
    # initialize sse at 0 for first iteration
    sse_accum = 0
    
    # keep track of iteration and MSE
    print("Optimization Statistics")
    print("Iterations | Mean Squared Error ")
    
    # for each iteration
    for iteration in range(iters):

        # update our sse
        old_sse = sse_accum
        sse_accum = 0
        
        # For each user-movie pair
        for i in range(n_users):
            for j in range(n_movies):
                
                # if the rating exists
                if user_item_np[i, j] > 0:
                    
                    # compute the error as the actual minus the dot product 
                    # of the user and movie latent features
                    diff = user_item_np[i, j] - \
                        np.dot(user_mat[i, :], movie_mat[:, j])
                    
                    # Keep track of the sum of squared errors for the matrix
                    sse_accum += diff**2
                    
                    # update values in each matrix in direction of the gradient
                    for k in range(latent_features):
                        user_mat[i, k] += \
                            learning_rate * (2 * diff * movie_mat[k, j])
                        movie_mat[k, j] += \
                            learning_rate * (2 * diff * user_mat[i, k])

        # print results
        print("%d \t\t %f" % (iteration+1, sse_accum / num_ratings))
        
    return user_mat, movie_mat     



def get_movie_names(movie_ids, movies):
    """ Look up and return movie titels for a given list of movie ids.

    INPUT:
        movie_ids: list of movie_ids
    OUTPUT:
        movie_list: list of movie titles associated with the movie ids
    
    """

    movie_list = [] 
    for id in movie_ids:
        title = movies.loc[movies['movie_id'] == id, 'movie'].tolist()
        movie_list.append(title[0])
        
    return movie_list



def create_ranked_movies(reviews, movies):
    '''
    Helper function. Merge the two dataframes reviews and movies and 
    ranks the movies according to the following criteria: 
            
    1. Highest average rating
    2. With ties, most ratings
    3. With ties, most recent rating
    4. minimum of 5 ratings to be considered at all

    INPUT:
        reviews: DataFrame containing review data
        movies: DataFrame containing movie data
        
    OUTPUT:
        ranked_movies: DataFrame containing ranked movies
    '''
    
    # group, aggregate and rank reviews dataframe
    grouped = reviews.groupby('movie_id')
    ratings = pd.DataFrame()
    ratings['mean_rating'] = grouped['rating'].agg(np.mean)
    ratings['rating_counts'] = grouped['movie_id'].agg(np.size)
    ratings['last_rating'] = grouped['date'].agg(np.max)
    ratings = ratings.loc[ratings['rating_counts'] >= 5]
    ratings = ratings.sort_values(['mean_rating', 'rating_counts', \
        'last_rating'], ascending=False)
    
    # merge with movies dataframe
    ranked_movies = movies.set_index('movie_id').join(ratings, how= 'right')
    
    return ranked_movies



def list_most_popular(user_id, n_top, ranked_movies):
    """Find n_top recommendations for a user according to the 
    following criteria: 
            
    1. Highest average rating
    2. With ties, most ratings
    3. With ties, most recent rating
    4. minimum of 5 ratings to be considered at all
    
    ARGUMENTS:
        user_id: int, user_id of user to get recommendations
        n_top: int, number recommendations to make
    
    RETURNS:
        top_movies: list, recommended movies in order best to worst
    """

    top_movies = list(ranked_movies['movie'][:n_top])
    
    return top_movies



def find_similar_movies(movie_id, movies):
    """Return similar movies for a given movie_id, based on content (genre
    and year).
    
    INPUT:
        movie_id: int, movie_id 
    OUTPUT:
        similar_movies: np.array containing the most similar movies by title
    """

    # movies x movies matrix to calculate dot product to get similar movies
    movie_content = np.array(movies.iloc[:,4:])
    dot_prod_movies = movie_content.dot(np.transpose(movie_content))

    # find the row of each movie id
    movie_idx = np.where(movies['movie_id'] == movie_id)[0][0]

    # find the most similar movie indices - to start they need to be the same for all content
    similar_idxs = np.where(dot_prod_movies[movie_idx] == \
        np.max(dot_prod_movies[movie_idx]))[0]

    # pull the movie titles based on the indices
    similar_movies = np.array(movies.iloc[similar_idxs, ]['movie'])

    return similar_movies
