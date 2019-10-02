from joblib import load
import numpy as np


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
    data.append(formData['age'])
    data.append(formData['sibs'])
    data.append(formData['parch'])
    data.append(mean_fares[formData['pClass']])
    # for pclass (which has 2 cols due to encoding)
    if formData['pClass'] == 1:
        data.append(0)
        data.append(0)
    elif formData['pClass'] == 2:
        data.append(1)
        data.append(0)
    elif formData['pClass'] == 3:
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


formData = {'age': 41, 'gender': 'male', 'pClass': 1,
            'parch': 2, 'sibs': 1}

data = transform_formData(formData=formData)
data_array = np.array(data).reshape(1, -1)
print(data_array)

classifier = load('gbc_titanic.joblib')

prediction = classifier.predict(data_array)
types = {0: "negative", 1: "positive"}
probability = classifier.predict_proba(data_array)[0, 1]

result = "Survival Prediction: {} (Survival probability: {})".format(types[prediction[0]],round(probability, 2))

# result = "Survival Prediction: " + types[prediction[0]] +\
# " (Survival probability: " + str(round(probability, 2)) + ")"

print(result)

# test only
print(transform_formData(formData={'age': 41, 'gender': 'male', 'pClass': 1,
                                   'parch': 2, 'sibs': 1}))
print(transform_formData(formData={'age': 41, 'gender': 'male', 'pClass': 3,
                                   'parch': 2, 'sibs': 1}))
