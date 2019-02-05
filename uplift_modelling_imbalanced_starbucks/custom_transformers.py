
import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin



class TypeSelector(BaseEstimator, TransformerMixin):
    """Selects columns from a DataFrame with specified datatype(s) for further 
    pipeline processing.

    ARGUMENTS:
        dtype = dtype to be selected

    RETURNS:
        X = Sub-selection of X in DataFrame format including columns with the 
        selected dtype.
    """

    def __init__(self, dtype):
        self.dtype = dtype

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        assert isinstance(X, pd.DataFrame)
        
        return X.select_dtypes(include=[self.dtype])



class CustomOneHotEncoder(BaseEstimator, TransformerMixin):
    """Custom OneHotEncoder based on Pandas get_dummies() function. Note: I 
    prefer this over sk-learns built in OneHotEncoder because of the possibility 
    to define labels for the new dummy columns.This makes checking for feature 
    importance easier. (That's also why the drop_first argument for get_dummmies
    is set to `False`.) 
        
       ARGUMENTS: 
            dummy_na = bool, indicating if NaN should be encoded in an own
            dummy variable.
         
       RETURNS: 
            X = np.array, containing the one-hot-encoded values.
    """

    def __init__(self, dummy_na=True):
        self.dummy_na = dummy_na     

    def fit(self, X, y_train=None):
        return self

    def transform(self, X):
        # for each cat add dummy variables, drop original column
        # if dummy_na=True encode NaN in separate column
        for col in  X:
            X = pd.concat([X.drop(col, axis=1), pd.get_dummies(
                X[col], prefix=col, prefix_sep='-', drop_first=False, 
                dummy_na=self.dummy_na)], axis=1)
        
        return X.values
