from flask import Flask, request, jsonify, make_response
from flask_restplus import Api, Resource, fields
# from sklearn.externals import joblib
from joblib import load
import numpy as np

app = Flask(__name__)
api = Api(app=app,
          version="0.1",
          title="Titantic React App",
          description="Predict results using a trained Gradient Boosting Classifier")

name_space = api.namespace('prediction', description='Prediction APIs')

model = api.model('Prediction params',
        {'age': fields.Integer(required=True,
                               description="Age",
                               help="Must be of type integer"),
        'gender': fields.String(required=True,
                                description="Gender",
                                help="Field cannot be blank"),
        'pClass': fields.Integer(required=True,
                                 description="Passenger Class",
                                 help="Field cannot be blank"),
        'parch': fields.Integer(required=True,
                                description="Number of Parents, Children",
                                help="Must be of type integer"),
        'sibs': fields.Integer(required=True,
                               description="Number of Siblings, Spouses",
                               help="Must be of type integer")})

classifier = load('gbc_titanic.joblib')


def transform_formData(formData):
    """Function to transform and enricht the input data to a format and
    order to match the format of original X_train.

    Arguments:
    ----------
        - formData: dict, input values from UI

    Returns:
    --------
        - data: list, 9 int values as input for model prediction
    """

    mean_fares = {1: 87.74, 2: 21.15, 3: 13.27}

    data = []
    data.append(int(formData['age']))
    data.append(int(formData['sibs']))
    data.append(int(formData['parch']))
    data.append(mean_fares[int(formData['pClass'])])
    # for pclass (which has 2 cols due to encoding)
    if int(formData['pClass']) == 1:
        data.append(0)
        data.append(0)
    elif int(formData['pClass']) == 2:
        data.append(1)
        data.append(0)
    elif int(formData['pClass']) == 3:
        data.append(0)
        data.append(1)
    # for gender
    if formData['gender'] == 'male':
        data.append(1)
    else:
        data.append(0)
    # for embarked (we take a default value)
    data.append(0)
    data.append(0)

    assert len(data) == 9, 'len(data) does not match'
    return data


@name_space.route("/")
class MainClass(Resource):

    def options(self):
        response = make_response()
        response.headers.add("Access-Control-Allow-Origin", "*")
        response.headers.add('Access-Control-Allow-Headers', "*")
        response.headers.add('Access-Control-Allow-Methods', "*")
        return response

    @api.expect(model)
    def post(self):
        try:
            formData = request.json
            data = transform_formData(formData=formData)
            data_array = np.array(data).reshape(1, -1)

            prediction = classifier.predict(data_array)
            types = {0: "negative", 1: "positive"}
            probability = classifier.predict_proba(data_array)[0, 1]
            result = "Survival Prediction: {} (Survival probability: {})".format(types[prediction[0]], round(probability, 2))

            response = jsonify({
                "statusCode": 200,
                "status": "Prediction made",
                "result": result
                })
            response.headers.add('Access-Control-Allow-Origin', '*')
            return response
        except Exception as error:
            return jsonify({
                "statusCode": 500,
                "status": "Could not make prediction",
                "error": str(error)
                })


if __name__ == '__main__':
    app.run(debug=True)
