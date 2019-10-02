# Titanic Survival Predictor
A web app that predicts survival probabilities for new instances based on the famous Titanic Data Set.

- The front-end is developed in **React** and includes a single page with a form to submit the input values
- The back-end is developed in **Flask / Flask-RESTful** which exposes prediction endpoints to predict using a trained classifier and send the result back to the front-end for easy consumption.

### Install
Prepare a Pyhton 3.x environment according to requirements.txt in the `service` folder. Make sure to match the exact versions of numpy and scikit-learn for sucsessful loading of the pickled model.

### Run
1) open console for running the APP
- activate environment (see **Install**, in my case for example: `conda activate react_app`)
- move to `service` folder
- run `python app.py`

2) open 2. console for running the UI
- move to `ui` folder
- [build with `npm run build` (if you want to change some ui elements)
- serve to `serve -s build`

### Creation
The complete guide to create a similar web app from a template can be found in this [blogpost](https://towardsdatascience.com/create-a-complete-machine-learning-web-application-using-react-and-flask-859340bddb33).
Just make sure you have node.js and yarn installed and follow the instructions. Thanks to Karan Bhanot!
