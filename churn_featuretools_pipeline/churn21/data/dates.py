from datetime import date, datetime, timedelta
import calendar
import logging

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
ch.setFormatter(formatter)
logger.addHandler(ch)
logger.setLevel(logging.DEBUG)

def handle_dates(
    cut_off_date: date, lookback_period_months: int, label_period_months: int
) -> dict:
    """create a dictionary containing all relevant dates

    Parameters
    ----------
    cut_off_date : date
        cut-off date; data coming in after this data cannot be used for predictions
    lookback_period_months : int
        how many months back from the cut-off date are considered for feature creation?
    label_period_months : int
        cancellations within this time period after the cut-off date are used as labels

    Returns
    -------
    dict
        [description]
    """
    # first date considered for observation period
    yrs = int(np.floor(lookback_period_months / 12))
    mths = int(np.mod(lookback_period_months, 12))
    dt_tmp = (cut_off_date - timedelta(days=(365 * yrs + mths * 30)))
    dt_obs_first_considered = date(dt_tmp.year, dt_tmp.month, 1)
    # last date considered for label
    yrs = int(np.floor(label_period_months / 12))
    mths = int(np.mod(label_period_months, 12))
    dt_tmp = (cut_off_date + timedelta(days=(365 * yrs + mths * 28)))
    last_of_month = calendar.monthrange(dt_tmp.year, dt_tmp.month)[1]
    dt_label_last_considered = date(dt_tmp.year, dt_tmp.month, last_of_month)
    dict_dates = dict(
        {
            "dt_cut_off": cut_off_date,
            "dt_obs_first_considered": dt_obs_first_considered,
            "dt_label_last_considered": dt_label_last_considered
        }
    )
    return dict_dates


def create_dateinfo(dt_params: dict) -> tuple:
    """create train and test sets for specifications in dt_params

    Parameters
    ----------
    dt_params : dict
        contains all date-relevant information
            - cut_off_date_train: last cut-off-date for the train set
            - lookback_period_months: how many months are looked back to create a single dataset?
            - label_period_months: cancellations in this period after the cut-off date represent the label
            - n_months_considered_training: for how many months should datasets be stacked to generate the full train set? 

    Returns
    -------
    tuple
        df_train: pd.DataFrame containing training data
        df_test: pd.DataFrame containing test data
    """
    l_dates_train = create_dates_training(dt_params)
    dt_params["cut_off_date_test"] = (
        l_dates_train[-1]["dt_label_last_considered"]
    )
    l_dates_test = handle_dates(
        dt_params["cut_off_date_test"], dt_params["lookback_period_months"],
        dt_params["label_period_months"]
    )
    return l_dates_train, [l_dates_test]


def create_dates_training(dt_params: dict) -> pd.DataFrame:
    """creates the necessary dates for the training set considering several cut-off dates.
    the last_cut_off_date is handed over to the function, 
    the first cut-off date is n_months_considered behind the last_cut_off_date

    Parameters
    ----------
    dt_params : dict
        dictionary containing all relevant info about training datset

    Returns
    -------
    pd.DataFrame
        training df
    """
    l_cut_off_dates = several_cut_off_dates(
        dt_params["first_cut_off_date_train"],
        dt_params["last_cut_off_date_train"]
    )
    l_dates_train = list()
    for dt_cut in l_cut_off_dates:
        l_dates_train.append(
            handle_dates(
                dt_cut, dt_params["lookback_period_months"],
                dt_params["label_period_months"]
            )
        )
    return l_dates_train


def several_cut_off_dates(dt_start_incl: date, dt_end_incl: date) -> list:
    """return all (month-end) cut-off dates between dt_start_incl and dt_end_incl

    Parameters
    ----------
    dt_start_incl : date
        first cut-off date
    dt_end_incl : date
        last cut-off date

    Returns
    -------
    list
        list containing all cut-off dates
    """
    dt_diff = (dt_end_incl - dt_start_incl)
    df_dt_range = pd.DataFrame(
        {
            "dt": [
                dt_start_incl + timedelta(days=n)
                for n in range(0, dt_diff.days + 1)
            ]
        }
    )
    df_dt_range["dt"] = pd.to_datetime(df_dt_range["dt"])
    df_dt_range["yr"] = df_dt_range["dt"].dt.year
    df_dt_range["mth"] = df_dt_range["dt"].dt.month
    l_cut_off_dates = (
        df_dt_range.groupby(["yr", "mth"])["dt"].max().reset_index(drop=True)
    )
    l_out = [dt for dt in l_cut_off_dates.dt.date]
    return l_out
