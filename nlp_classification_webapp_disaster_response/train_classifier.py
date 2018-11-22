import sys


def load_data(database_filepath):
    """Load 'messages' table into dataframe.
    
    ARGUMENTS:
        database_filepath: string
    RETURNS:
        df: dataframe
    """
    
    engine = create_engine(database_filepath)
    df = pd.read_sql_table('messages', engine)

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
    message = re.sub(r"[^a-zA-Z0-9]", " ", message.lower())
    # tokenize text
    tokens = word_tokenize(message)
    # lemmatize, stip and remove stop words
    tokens = [lemmatizer.lemmatize(word.strip()) \
        for word in tokens if word not in stop_words]
    # add part-of-speech tags
    tokens = pos_tag(tokens)
    
    return tokens


def build_model():
    pass


def evaluate_model(model, X_test, Y_test, category_names):
    pass


def save_model(model, model_filepath):
    pass


def main():
    if len(sys.argv) == 3:
        database_filepath, model_filepath = sys.argv[1:]
        print('Loading data...\n    DATABASE: {}'.format(database_filepath))
        X, Y, category_names = load_data(database_filepath)
        X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size=0.2)
        
        print('Building model...')
        model = build_model()
        
        print('Training model...')
        model.fit(X_train, Y_train)
        
        print('Evaluating model...')
        evaluate_model(model, X_test, Y_test, category_names)

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
