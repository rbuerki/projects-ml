import sys
import numpy as np
import pandas as pd
from sqlalchemy import create_engine

from sklearn.model_selection import StratifiedShuffleSplit, GridSearchCV, \
    train_test_split, StratifiedKFold, cross_validate
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
from sklearn.pipeline import Pipeline, FeatureUnion
from sklearn.metrics import make_scorer, classification_report, f1_score
from sklearn.externals import joblib
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.preprocessing import OneHotEncoder

from sklearn.multioutput import MultiOutputClassifier
from sklearn.linear_model import SGDClassifier

import re
import nltk
nltk.download(['punkt', 'wordnet', 'stopwords', 'averaged_perceptron_tagger', \
    'maxent_ne_chunker', 'words'])
from nltk.corpus import stopwords
from nltk import pos_tag, ne_chunk
from nltk.tokenize import word_tokenize
from nltk.stem.wordnet import WordNetLemmatizer

# pipeline caching
from tempfile import mkdtemp
from shutil import rmtree
from sklearn.utils import Memory

# define two custom transformers for the pipeline
class MessageSelector(BaseEstimator, TransformerMixin):
    """Custom transformer to select the text column."""

    def __init__(self, column):
        self.column = column
        
    def fit(self, X_train, y_train=None):
        return self
    
    def transform(self, X_train):
        return X_train[self.column].values

class CategoricalsSelector(BaseEstimator, TransformerMixin):
    """Custom transformer to select the categorical columns."""

    def __init__(self, column):
        self.column = column
    
    def fit(self, X_train, y_train=None):
        return self
    
    def transform(self, X_train):
        return X_train[[self.column]]


def load_split_data(database_filepath):
    """Load 'messages' table into dataframe and splits into train and 
    test sets with stratified sampling.
    
    ARGUMENTS:
        database_filepath: string
    RETURNS:
        df: dataframe
    """
    
    engine = create_engine('sqlite:///' + database_filepath)
    df = pd.read_sql_table('messages', engine)

    # create col with total number of active categories per message
    df['total'] = df.iloc[:,4:40].sum(axis=1)
    df['total'] = np.where((df['total'] >10), 11, df['total'])

    # perform stratified split
    split = StratifiedShuffleSplit(n_splits = 1, 
        test_size = 0.2, random_state = 111)
    for train_index, test_index in split.split(df, df['total']):
        train = df.loc[train_index]
        test = df.loc[test_index]
        
    # remove 'total' column from train and test sets
    for set_ in (train, test):
        set_.drop('total', axis=1, inplace=True)
    
    # split into features and labels
    X_train = train[['message', 'genre']]
    Y_train = train.iloc[:, 4:39].values
    X_test = test[['message', 'genre']]
    Y_test = test.iloc[:, 4:39].values  
    
    # create list of strings with target label names
    label_names = train.iloc[:, (-1 * Y_test.shape[1]):].columns 
    
    return X_train, Y_train, X_test, Y_test, label_names


def tokenize_text(text):
    """Process text data.
    
    ARGUMENTS:
        text: str to be processed
    RETURNS:
        tokens: processed text
    """
    lemmatizer = WordNetLemmatizer()
    stop_words = stopwords.words('english')
    
    # normalize case and remove punctuation
    message = re.sub(r"[^a-zA-Z0-9]", " ", text.lower())
    # tokenize text
    tokens = word_tokenize(message)
    # lemmatize, stip and remove stop words
    tokens = [lemmatizer.lemmatize(word.strip()) \
        for word in tokens if word not in stop_words]
    # add part-of-speech tags
    tokens = pos_tag(tokens)
    
    return tokens


def build_model(cv=StratifiedKFold(3)):
    """Build a full nlp classification pipeline with GridSearchCV
       for best parameters.
    
    ARGUMENTS:
        X_train: training features (df or array)
        y_train: training labels (df or array)
        cv: type of CV, default is StratifiedKFold(3)
        
    RETURNS:
        cv: grid search object that can be fitted to the data to 
        transform it and find the best parameters.
    """
    
    
   # define classifier and scoring function  
    clf = SGDClassifier(loss='log', fit_intercept=False, 
        class_weight='balanced', max_iter=5, tol=None, 
        random_state=1, n_jobs=-1)
    scorer = make_scorer(f1_score, average='weighted')
    
    # create temporary folder to store pipeline transformers (cache)
    cachedir = mkdtemp()
    memory = Memory(location=cachedir, verbose=1)
    
    full_pipe = Pipeline([
    ('features', FeatureUnion([

        ('text', Pipeline([
            ('text_select', MessageSelector('message')),
            ('vect', CountVectorizer(tokenizer=tokenize_text)),
            ('tfidf', TfidfTransformer()),
        ])),

        ('genre', Pipeline([
            ('cat_select', CategoricalsSelector('genre')),
            ('ohe', OneHotEncoder()),
        ])),
    ])),

        ('clf', MultiOutputClassifier(clf))],
        
    memory=memory)
    
    
    parameters = {
        'features__text__vect__max_df': [0.8, 0.9],
        }
    
    # create grid search object
    cv = GridSearchCV(full_pipe, param_grid=parameters, 
            scoring=scorer, cv=cv, error_score='raise', 
            n_jobs=1, verbose=1)
            
    return cv

    # delete the temporary cache before exiting
    rmtree(cachedir)
    

def evaluate_model(model, X_test, Y_test, label_names):
    """Calculate and display evaluation metrics (classification report) 
       for every category and cumulated / averaged.
    
    ARGUMENTS:
    model: name of sclearn model / pipeline object
    X_test: Array containing features in test set.
    Y_test: Array containing actual labels in test set.
       
    RETURNS:
    metrics_df: Dataframe containing the entire multilabel
    classification report.
    """
    
    Y_pred = model.predict(X_test)
    
    # Calculate classification report
    metrics = classification_report(
                Y_test, Y_pred,
                target_names=label_names,
                output_dict=True,
                )

    # Create dataframe, tanspose it
    metrics_df = pd.DataFrame(
                    data = metrics, 
                    ).T
      
    print(metrics_df)


def save_model(model, model_filepath):
    """Save fitted model.
    
    ARGUMENTS:
        model: variable name for model
        model_filepath: sring
    """
    
    joblib.dump(model, model_filepath)


def main():
    if len(sys.argv) == 3:
        database_filepath, model_filepath = sys.argv[1:]
        print('Loading data...\n    DATABASE: {}'.format(database_filepath))
        X_train, Y_train, X_test, Y_test, label_names = \
            load_split_data(database_filepath)

        print('Building model...')
        model = build_model(cv=3)
        
        print('Training model...')
        model.fit(X_train, Y_train)
        
        print('Evaluating model...')
        evaluate_model(model, X_test, Y_test, label_names)

        print('Saving model...\n    MODEL: {}'.format(model_filepath))
        save_model(model, model_filepath)

        print('Trained model saved!')

    else:
        print('Please provide filepath of disaster messages database '\
              'as 1st argument and filepath of pickle file to '\
              'save the model to as 2nd argument. \n\nExample: python '\
              'train_classifier.py ../data/DisasterResponse.db '\
              'classifier.pkl')


if __name__ == '__main__':
    main()
