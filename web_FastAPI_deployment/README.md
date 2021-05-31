# How To Build and Deploy a Machine Learning Model with FastAPI

Learning Project, Mai 2021

Based on:
- [blogpost](https://towardsdatascience.com/how-to-build-and-deploy-a-machine-learning-model-with-fastapi-64c505213857) by Dario Radecic 
- excellent [FastAPI documentation](https://fastapi.tiangolo.com)

## Getting Started With FastAPI

Get up a FastAPI as simple as that:

```Python
import uvicorn
from fastapi import FastAPI

# 1. Create the app object
app = FastAPI()

# 2. Index route, opens automatically on http://127.0.0.1:8000
@app.get("/")
def index():
    return {"message": "Hello, stranger"}


# 3. Route with a single parameter, returns the parameter within a message
#    Located at: http://127.0.0.1:8000/AnyNameHere
@app.get("/{name}")
def async get_name(name: str):  # async optional, check if applicable
    return {"message": f"Hello, {name}"}


# 4. Run the API with uvicorn
#    Will run on http://127.0.0.1:8000
if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
```

In development mode run it like this (the reload param re-runs the API after every change in the code):

```bash
uvicorn [filename]:[app_object] --reload
```

FastAPI requires **Pyhton 3.6+** and is best installed as such:

```bash
pip install fastapi
pip install uvicorn[standard]
```

### Good to know

- I run FastAPI with a [Uvicorn ASGI server](http://www.uvicorn.org/)
- FastAPI is based on standard Python 3.6 type declarations (thanks to Pydantic - that's why in the project code IrisSpecies is based on Pydantic's BaseModel class.)

## This Mini-Project

We use the the famous [Iris dataset](https://raw.githubusercontent.com/uiuc-cse/data-fa14/gh-pages/data/iris.csv) to train a super simple Random Forest Classifier and build a REST API that exposes the prediction for the flower species for new observations.

After running the API, you can test it manually on the documentation page:

http://127.0.0.1:8000/docs

Or  programatically:

```python
import requests 

new_measurement = {
    'sepal_length': 5.7,
    'sepal_width': 3.1,
    'petal_length': 4.9,
    'petal_width': 2.2
}

response = requests.post('http://127.0.0.1:8000/predict', json=new_measurement)
print(response.content)
```

Or from a bash terminal:

```bash
curl -X 'POST' \
  'http://127.0.0.1:8000/predict' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "sepal_length": 0,
  "sepal_width": 0,
  "petal_length": 0,
  "petal_width": 0
}'
```


### Good to know

In the project we use the POST method, as it’s considered better practice to send parameters in JSON rather than in URL (as in the demo sample above).
