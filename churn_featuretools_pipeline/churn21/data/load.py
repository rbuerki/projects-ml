import os
import sys
from datetime import date
from functools import partial, reduce
import logging

import pandas as pd
from bcag.sql_utils import execute_sql_query
from sqlalchemy.engine.base import Engine

from . import fact_features as utils_ff

sys.path.append("..")

logger = logging.getLogger(__name__)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
ch.setFormatter(formatter)
logger.addHandler(ch)
logger.setLevel(logging.DEBUG)


def create_dataset(
    l_dates_train: list, l_dates_test: list, update_sql_scripts: bool,
    engine: Engine
) -> list:
    """create train and test set using l_dates_train and l_dates_test 
    for train and test periods, respectively

    Parameters
    ----------
    l_dates_train : list
        date parameters for train period
    l_dates_test : list
        date parameters for test period
    update_sql_scripts : bool
        should the .sql scripts in $ROOT\sql\ be run?
    engine : Engine
        jemas connection. can be dev, test, or prod

    Returns
    -------
    list
        containing df_train and df_test
    """
    if update_sql_scripts:
        run_sql_scripts(engine)
    pop = load_population(engine)
    label = load_label(engine)
    af_history = load_annual_fee_history(engine)
    af_date = load_annual_fee_date(engine)
    gi = load_jamo_based_info(engine, "churn21_general_information")
    fd = load_jamo_based_info(engine, "churn21_fakturadaten")
    segs = load_jamo_based_info(engine, "churn21_segments")
    l_jamo_based = [gi, fd, segs]
    dict_dfs = dict(
        {
            "pop": pop,
            "label": label,
            "af_history": af_history,
            "af_date": af_date,
            "l_jamo_based": l_jamo_based
        }
    )

    # l_df_train = [None] * len(l_dates_train)
    # for i, dict_dates in enumerate(l_dates_train):
    #     l_df_train[i] = process_cut_off_date(dict_dfs, dict_dates)
    # df_train = reduce(lambda x, y: pd.concat, l_df_train) # ignore index?
    df_train = pd.DataFrame()

    for dict_dates in l_dates_test:
        df_test = process_cut_off_date(
            dict_dfs, dict_dates, engine, is_test=False
        )

    return [df_train, df_test]


def process_cut_off_date(
    dict_dfs: dict, dict_dates: dict, engine: Engine, is_test: bool
) -> pd.DataFrame:

    pop = filter_population(dict_dfs["pop"], dict_dates["dt_cut_off"])
    if is_test:
        pop = pop.sample(1000)
    label = filter_label(
        dict_dfs["label"], dict_dates["dt_cut_off"],
        dict_dates["dt_label_last_considered"]
    )
    # most recent info of jamo-based
    most_recent_partial = partial(
        _most_recent_information, cut_off_date=dict_dates["dt_cut_off"]
    )
    iterable = map(most_recent_partial, dict_dfs["l_jamo_based"])
    l_out = list(iterable)

    # annual fee infos
    af_date = time_to_next_fee(dict_dfs["af_date"], dict_dates["dt_cut_off"])
    af_history = aggregate_af_history(
        dict_dfs["af_history"], dict_dates["dt_cut_off"]
    )

    # featuretools part for this given cut-off date
    df_ft = utils_ff.load_fact_feature_set(
        pop,
        dict_dates["dt_cut_off"],
        dict_dates["dt_obs_first_considered"],
        engine,
        n_jobs=1,
        do_check=True
    )

    # merge all data frames
    l_chunk = [pop, af_date, af_history] + l_out + [df_ft, label]
    df_chunk = reduce(
        lambda x, y: pd.merge(x, y, how="left", on="konto_lauf_id"), l_chunk
    )

    return df_chunk


def run_sql_scripts(engine: Engine) -> None:
    """runs all .sql scripts stored under $ROOT\sql\

    Parameters
    ----------
    engine : Engine
        jemas connection
    """
    for file in os.listdir("..\sql"):
        if file.endswith(".sql"):
            with open(f"""..\sql\{file}""", "r") as f:
                query = f.read()
                logger.info(f"""executing .sql {file}""")
                execute_sql_query(query, engine)


def load_label(engine: Engine) -> pd.DataFrame:
    """load label for the whole population

    Parameters
    ----------
    cut_off_date : date
        cut-off date separating observation period from label period
    engine : Engine
        jemas connection

    Returns
    -------
    pd.DataFrame
        df with all accounts cancelling in the label period
        after the cut-off date
    """
    logger.info(f"""loading label""")
    query = (
        f"select konto_lauf_id \
                     , kuendigung_an_datum \
                     , cancellation_type \
            from     jemas_temp.thm.churn21_label"
    )
    df_label = pd.read_sql(query, engine)
    df_label["kuendigung_an_datum"] = pd.to_datetime(
        df_label["kuendigung_an_datum"]
    )
    df_label = _downcast_dtypes(df_label)
    # checks: konto_lauf_id unique, konto_lauf_id in population

    return df_label


def load_population(engine: Engine) -> pd.DataFrame:
    """load the population for a given cut-off date

    Parameters
    ----------
    engine : Engine
        jemas connection

    Returns
    -------
    pd.DataFrame
        df with all accounts for the given cut-off date
    """
    logger.info(f"""loading population""")
    query = (
        """select  konto_lauf_id
                   , konto_id
                   , jamo
           from    jemas_temp.thm.churn21_population"""
    )
    df_pop = pd.read_sql(query, engine)
    df_pop = _downcast_dtypes(df_pop)
    # checks: konto_lauf_id unique

    return df_pop


def load_jamo_based_info(engine: Engine, tbl_name: str) -> pd.DataFrame:
    """load whole table, which is jamo based

    Parameters
    ----------
    engine : Engine
        jemas connection

    Returns
    -------
    pd.DataFrame
        fakturadaten
    """
    logger.info(f"""loading from {tbl_name}""")
    query = (f"""select * from jemas_temp.thm.{tbl_name}""")
    df = pd.read_sql(query, engine)
    df["letzter_tag"] = pd.to_datetime(df["letzter_tag"])
    df = _downcast_dtypes(df)
    # checks: konto_lauf_id and jamo unique

    return df


def load_annual_fee_history(engine: Engine) -> pd.DataFrame:
    """load history of all paid annual fees

    Parameters
    ----------
    engine : Engine
        jemas connection. dev, test, or prod

    Returns
    -------
    pd.DataFrame
        annual fee history data
    """
    logger.info(f"""loading annual fee history""")
    query = (f"""select * from jemas_temp.thm.churn21_annual_fee_history""")
    df = pd.read_sql(query, engine)
    df["kauf_datum"] = pd.to_datetime(df["kauf_datum"])
    df = _downcast_dtypes(df)
    # checks:

    return df


def load_annual_fee_date(engine: Engine) -> pd.DataFrame:
    """load annual fee dates

    Parameters
    ----------
    engine : Engine
        jemas connection. dev, test, or prod

    Returns
    -------
    pd.DataFrame
        all annual fee dates
    """
    logger.info(f"""loading next annual fee date""")
    query = (f"""select * from jemas_temp.thm.churn21_annual_fee_date""")
    df = pd.read_sql(query, engine)
    df["jahresgebuehr_datum"] = pd.to_datetime(df["jahresgebuehr_datum"])
    df["load_lauf_end_datum"] = pd.to_datetime(df["load_lauf_end_datum"])
    df = _downcast_dtypes(df)
    # checks:

    return df


def _most_recent_information(
    df: pd.DataFrame, cut_off_date: date
) -> pd.DataFrame:
    """select most recent information from table having konto_lauf_id 

    and jamo as columns

    Parameters
    ----------
    df : pd.DataFrame
        data frame with konto_lauf_id and jamo in columns
    cut_off_date : date
        cut-off date separating observation period from label period

    Returns
    -------
    pd.DataFrame
        most recent row for every konto_lauf_id
    """
    df = df.loc[df["letzter_tag"] <= pd.to_datetime(cut_off_date)]
    df.sort_values(["konto_lauf_id", "jamo"], inplace=True)
    df.reset_index(drop=True, inplace=True)
    df["rwn"] = df.groupby(["konto_lauf_id"]).cumcount(ascending=False)
    df = df.query("rwn == 0")

    return df


def filter_population(pop: pd.DataFrame, cut_off_date: date) -> pd.DataFrame:
    """filter the population for the given cut-off date

    Parameters
    ----------
    pop : pd.DataFrame
        population df
    cut_off_date : date
        cut-off date separating observation period from label period

    Returns
    -------
    pd.DataFrame
        population
    """
    logger.info(f"""filtering population""")
    jamo_required = cut_off_date.year * 100 + cut_off_date.month
    pop.query(f"jamo <= {jamo_required}", inplace=True)
    pop.sort_values(["konto_lauf_id", "jamo"], inplace=True)
    pop.reset_index(drop=True, inplace=True)
    pop["rwn"] = pop.groupby(["konto_lauf_id"]).cumcount(ascending=False)
    pop = pop.query("rwn == 0 & ~konto_id.isna()")
    pop = pop.filter(["konto_lauf_id"])

    return pop


def filter_label(
    label: pd.DataFrame, dt_cut_off: date, dt_label_last: date
) -> pd.DataFrame:
    """filter all labels for the given 

    Parameters
    ----------
    label : pd.DataFrame
        unfiltered labels
    dt_cut_off : date
        cut-off date separating observation from label period
    dt_label_last : date
        last considered date in label period

    Returns
    -------
    pd.DataFrame
        filtered label df
    """
    logger.info(f"""filtering label""")
    filt = (
        (label["kuendigung_an_datum"] > pd.to_datetime(dt_cut_off))
        & (label["kuendigung_an_datum"] <= pd.to_datetime(dt_label_last))
    )

    return label.loc[filt]


def time_to_next_fee(af_date: pd.DataFrame, dt_cut_off: date) -> pd.DataFrame:
    """calculate remaining days to next annual fee due date

    Parameters
    ----------
    af_date : pd.DataFrame
        all paid annual fees
    dt_cut_off : date
        cut-off date separating observation period from label period

    Returns
    -------
    pd.DataFrame
        df with column stating remaining days to next annual fee
    """
    logger.info(f"""calculating time to next annual fee date""")
    filt = (af_date["jahresgebuehr_datum"] > pd.to_datetime(dt_cut_off))
    af_date = af_date.loc[filt]
    df_next = pd.DataFrame(
        af_date.groupby(["konto_lauf_id"])["jahresgebuehr_datum"].min()
    )
    df_next["dd_next_annual_fee"
            ] = df_next["jahresgebuehr_datum"] - pd.to_datetime(dt_cut_off)
    df_next["dd_next_annual_fee"] = df_next["dd_next_annual_fee"].dt.days

    return df_next


def aggregate_af_history(
    af_history: pd.DataFrame, dt_cut_off: date
) -> pd.DataFrame:
    """summarize history of annual fee up to cut-off date

    Parameters
    ----------
    af_history : pd.DataFrame
        df with all paid annual fees
    dt_cut_off : date
        cut-off date separating observation period from label period

    Returns
    -------
    pd.DataFrame
        aggregated df
    """
    logger.info(f"""aggregating annual fee history data""")
    filt = (af_history["kauf_datum"] <= pd.to_datetime(dt_cut_off))
    af_history = af_history.loc[filt]
    af_history = af_history.groupby(
        ["konto_lauf_id"]
    ).agg(n_annual_fee=("betrag", "count"),
          sum_annual_fee=("betrag", "sum")).reset_index()

    return af_history


# HELPER FUNCTION(S)


def _downcast_dtypes(df: pd.DataFrame, verbose=False) -> pd.DataFrame:
    """Return a copy of a input dataframe with reduced memory usage.
    Numeric dtypes will be downcast to the smallest possible format,
    object dtypes with less distinct values than rowcount will be
    transformed to dtype 'category'. Limitations: Only 'object' cols
     are considered for conversion to dtype 'category'.

    Parameters
    ----------
    df : pd.DataFrame
        data to transform
    verbose : bool
        wether or not to print the size before and after the transformation
        (defaults to False)

    Returns
    -------
    pd.DataFrame
        copy of the original dataframe with downcast dtypes

    """
    if verbose:
        print(
            f" Original size "
            f"{df.memory_usage(deep=True).sum() / (1024**2):,.2f} MB"
        )

    df = df.copy()

    for col in df.columns:
        col_type = str(df[col].dtype)
        col_items = df[col].count()
        col_unique_itmes = df[col].nunique()

        if col_type == 'object' and col_unique_itmes < col_items:
            df[col] = df[col].astype('category')
        if col_type.startswith("int"):
            df[col] = pd.to_numeric(df[col], downcast='integer')
        if col_type.startswith("float"):
            df[col] = pd.to_numeric(df[col], downcast='float')

    if verbose:
        print(
            f" New size "
            f"{df.memory_usage(deep=True).sum() / (1024**2):,.2f} MB"
        )

    return df
