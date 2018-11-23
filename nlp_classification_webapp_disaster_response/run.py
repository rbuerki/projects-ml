import json
import plotly
import pandas as pd

from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize

from train_classifier import tokenize_text
from train_classifier import MessageSelector, CategoricalsSelector

from flask import Flask
from flask import render_template, request, jsonify
from plotly.graph_objs import Bar
from sklearn.externals import joblib
from sqlalchemy import create_engine


app = Flask(__name__)

# load data
engine = create_engine('sqlite:///DisasterResponse.db')
df = pd.read_sql_table('messages', engine)

# load model
model = joblib.load("models/app_classifier.pkl")


# index webpage displays cool visuals and receives user input text for model
@app.route('/')
@app.route('/index')
def index():
    
    # extract data needed for visuals
    # TODO: Below is an example - modify to extract data for your own visuals
    cat_proportions = df.iloc[:,4:39].sum()/len(df)
    cat_per_message = df['total'] = df.iloc[:,4:39].sum(axis=1)
    cat_per_message_values = df['total'] = df.iloc[:,4:39].sum(axis=1).value_counts()
    cat_labels = df.iloc[:,4:39].columns
    
    # create visuals
    # TODO: Below is an example - modify to create your own visuals
    graphs = [
        {
            'data': [
                Bar(
                    x=cat_labels,
                    y=cat_proportions
                )
            ],

            'layout': {
                'title': 'Distribution of Target Categories for ' \
                         'Disaster Related Messages'
                },
                'yaxis': {
                    'title': "Count"
                },
                'xaxis': {
                    'title': "Target Category"
                }
        },
        
        {
            'data': [
                Bar(
                    x=cat_per_message,
                    y=cat_per_message_values
                )
            ],

            'layout': {
                'title': 'Distribution of Number of Active ' \
                         'Target Categories per Message'
                },
                'yaxis': {
                    'title': "Count"
                },
                'xaxis': {
                    'title': "Target Categories / Message"
                }
        }
    ]
    
    # encode plotly graphs in JSON
    ids = ["graph-{}".format(i) for i, _ in enumerate(graphs)]
    graphJSON = json.dumps(graphs, cls=plotly.utils.PlotlyJSONEncoder)
    
    # render web page with plotly graphs
    return render_template('master.html', ids=ids, graphJSON=graphJSON)


# web page that handles user query and displays model results
@app.route('/go')
def go():
    # save user input in query
    query = request.args.get('query', '') 

    # use model to predict classification for query
    classification_labels = model.predict([query])[0]
    classification_results = dict(zip(df.columns[4:], classification_labels))

    # This will render the go.html  
    return render_template(
        'go.html',
        query=query,
        classification_result=classification_results
    )


def main():
    app.run(host='0.0.0.0', port=3001, debug=True)


if __name__ == '__main__':
    main()