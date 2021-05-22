from datetime import date, timedelta, datetime
from typing import List, Tuple
import logging

import featuretools as ft
import numpy as np
import pandas as pd
from sqlalchemy.engine.base import Engine

from . import load as utils_ld

logger = logging.getLogger(__name__)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
ch.setFormatter(formatter)
logger.addHandler(ch)
logger.setLevel(logging.DEBUG)


def load_sales_fact(
    cut_off_date: date, first_date: date, engine: Engine
) -> pd.DataFrame:
    """load observations from the db table 'jemas_base.dbo.Sales_Fact'
    given between given start and end date. We load the entire population

    Parameters
    ----------
    cut_off_date : date
        cut-off date separating observation period from label period
    first_date :  date
        first date of observation period
    engine : Engine
        jemas connection

    Returns
    -------
    pd.DataFrame
        sales fact data in "long format" (one row per trx)
    """
    # Add one week to cut-off-date to catch time lag in kauf_datum
    cut_off_date_plus = cut_off_date + timedelta(days=3)
    logger.info(
        f"""loading sales facts between {first_date} and {cut_off_date_plus}"""
    )

    query = f"""
        SELECT
              sf.konto_lauf_id
            , sf.betrag
            , sf.kauf_datum
            , sf.transaction_type_id
            , mcc.mcg AS mcg_id
            , sf.transaktionsart_id_korr
        FROM jemas_base.dbo.Sales_Fact AS sf
        JOIN jemas_base.dbo.v_mcc AS mcc
          ON mcc.mcc_id = sf.mcc_id
       WHERE sf.erfassung_datum <= '{cut_off_date_plus}'
         AND sf.erfassung_datum >= '{first_date}'
         AND sf.ist_umsatz = 1
         AND sf.ist_trx = 1
         AND sf.betrag > 0
         ORDER BY sf.konto_lauf_id;
       """

    df_sales_fact = pd.read_sql(query, engine)
    df_sales_fact["rwn"] = np.arange(
        len(df_sales_fact)
    )     # "add primary key" for ft
    df_sales_fact = utils_ld._downcast_dtypes(df_sales_fact)

    return df_sales_fact


def load_fees_fact(
    cut_off_date: date, first_date: date, engine: Engine
) -> pd.DataFrame:
    """load observations from the db table 'jemas_base.dbo.Fees_Fact'
    given between given start and end date. We load the entire population

    Parameters
    ----------
    cut_off_date : date
        cut-off date separating observation period from label period
    first_date :  date
        first date of observation period
    engine : Engine
        jemas connection

    Returns
    -------
    pd.DataFrame
        [description]
    """
    # Add one week to cut-off-date to catch time lag in kauf_datum
    cut_off_date_plus = cut_off_date + timedelta(days=3)
    logger.info(
        f"""loading fees facts between {first_date} and {cut_off_date_plus}"""
    )

    query = f"""
        SELECT
          ff.konto_lauf_id
        , ff.betrag
        , ff.kauf_datum
       , CASE WHEN ff.bewegungstyp_id IN (41, 42, 43, 44) THEN 'mahnung'
              WHEN ff.bewegungsgrund_id IN ('FRW', 'WSZ', 'ETA') THEN 'fremdw'
              WHEN (ff.bewegungsgrund_id = 'ZIN' OR ff.bewegungstyp_id = 31) THEN 'zins'
              ELSE 'divers' END AS 'bewegungstyp'
        FROM jemas_base.dbo.Fees_Fact as ff
        WHERE erfassung_datum <= '{cut_off_date_plus}'
          AND erfassung_datum >= '{first_date}'
          AND bewegungstyp_id != 11
          AND NOT ff.bewegungsgrund_id IN ('JGT', 'JGE', 'JGR')
          AND ff.betrag > 0
        ORDER BY ff.konto_lauf_id;
       """

    df_fees_fact = pd.read_sql(query, engine)
    df_fees_fact["rwn"] = np.arange(
        len(df_fees_fact)
    )     # add "primary key" for ft
    df_fees_fact = utils_ld._downcast_dtypes(df_fees_fact)

    return df_fees_fact


def fit_fact_df_to_population(
    fact: pd.DataFrame, pop: pd.DataFrame
) -> pd.DataFrame:
    """drop all observations from fact that are for konto_lauf_ids
    which are not included in the population.

    Parameters
    ----------
    fact : pd.DataFrame
        loaded fact table
    pop : pd.DataFrame
        population used at the given cut-off date
    engine : Engine
        jemas connection

    Returns
    -------
    pd.DataFrame
        reduced copy of fact
    """
    population = set(pop["konto_lauf_id"])
    fact = fact[fact["konto_lauf_id"].isin(population)].copy()
    return fact


def split_fact_df_into_3_periods(
    fact: pd.DataFrame, cut_off_date: date, first_date: date
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """split fact observations into 3 periods: 1st month of observation
    period, 12 months back from cut_off_date and 1 month back from
    cut_off_date (last two periods overlapp)

    Parameters
    ----------
    fact : pd.DataFrame
        loaded fact table
    cut_off_date : date
        cut-off date separating observation period from label period
    first_date : date
        first date of observation period

    Returns
    -------
    pd.DataFrame, pd.DataFrame, pd.DataFrame
        df_first_month, df_12_months, df_last_month
    """
    start_first_month = first_date
    next_month = start_first_month.replace(day=28) + timedelta(
        days=4
    )     # never fails
    end_first_month = next_month - timedelta(days=next_month.day)
    start_12_months = end_first_month + timedelta(days=1)
    end_12_months = cut_off_date
    start_last_month = end_12_months.replace(day=1)
    end_last_month = end_12_months

    df_first_month = fact[
        (fact["kauf_datum"] >= pd.to_datetime(start_first_month))
        & (fact["kauf_datum"] <= pd.to_datetime(end_first_month))].copy()

    df_12_months = fact[
        (fact["kauf_datum"] >= pd.to_datetime(start_12_months))
        & (fact["kauf_datum"] <= pd.to_datetime(end_12_months))].copy()

    df_last_month = fact[
        (fact["kauf_datum"] >= pd.to_datetime(start_last_month))
        & (fact["kauf_datum"] <= pd.to_datetime(end_last_month))].copy()

    return df_first_month, df_12_months, df_last_month


# FEATURE-TOOLS-RELATED


def create_entity_set_ft(
    pop: pd.DataFrame,
    sales: pd.DataFrame,
    fees: pd.DataFrame,
) -> ft.EntitySet:
    """Create the featuretools entity set, with the 3 related entities
    population, sales and fees. Define interesting values

    Parameters
    ----------
    pop : pd.DataFrame
        population used at the given cut-off date
    sales : pd.DataFrame
        slice of loaded sales_fact table, for given population and period
    fees : date
        slice of loaded fees_fact table, for given population and period
    cut_off_date : date
        cut-off date separating observation period from label period

    Returns
    -------
    ft.EntitySet
        featuretools entity set for the fiven cut-off date
    """
    es = ft.EntitySet()

    # Add entities
    es = es.entity_from_dataframe(
        entity_id="population",
        dataframe=pop,
        index="konto_lauf_id",
    )
    es = es.entity_from_dataframe(
        entity_id="sales_fact",
        dataframe=sales,
        index="rwn",
        time_index="kauf_datum",
        variable_types={
            "transaction_type_id": ft.variable_types.Categorical,
            "mcg_id": ft.variable_types.Categorical,
            "transaktionsart_id_korr": ft.variable_types.Categorical,
        }
    )
    es = es.entity_from_dataframe(
        entity_id="fees_fact",
        dataframe=fees,
        index="rwn",
        time_index="kauf_datum",
        variable_types={
            "bewegungstyp": ft.variable_types.Categorical,
        }
    )

    # Add relationships
    rs_population_sales_fact = ft.Relationship(
        es["population"]["konto_lauf_id"], es["sales_fact"]["konto_lauf_id"]
    )
    rs_population_fees_fact = ft.Relationship(
        es["population"]["konto_lauf_id"], es["fees_fact"]["konto_lauf_id"]
    )

    es = es.add_relationship(rs_population_sales_fact)
    es = es.add_relationship(rs_population_fees_fact)

    # Add interesting values (-> where_primitives)
    es["fees_fact"]["bewegungstyp"].interesting_values = [
        "mahnung", "fremdw", "zins"
    ]
    es["sales_fact"]["transaktionsart_id_korr"].interesting_values = [
        0
    ]     # BC closed loop

    return es


def create_ft_matrix_and_defs_full(
    es: ft.EntitySet, cut_off_date: date, n_jobs: int
) -> Tuple[pd.DataFrame, List[ft.FeatureBase]]:
    """Calculate feature matrix for the input entity set, with the 3 related entities
    population, sales and fees. Define interesting values. This is the full set
    for the 12-month period.

    Parameters
    ----------
    es : ft.EntitySet
        featuretools entity set for the fiven cut-off date
    cut_off_date : date
        cut-off date separating observation period from label period
    n_jobs: int
        number of workers to use

    Returns
    -------
    pd.DataFrame, List[ft.FeatureBase]
        featuretools feature matrix and feature list
    """

    ft_to_drop = [
        "MODE(sales_fact.MONTH(kauf_datum))",
        "MODE(fees_fact.MONTH(kauf_datum))",
        "MODE(sales_fact.mcg_id)",
    ]

    feature_matrix, feature_defs = ft.dfs(
        entityset=es,
        target_entity="population",
        verbose=True,
        drop_exact=ft_to_drop,
        cutoff_time=pd.to_datetime(cut_off_date),
        agg_primitives=[
            "sum",
            "std",
            "max",
            "skew",
            "min",
            "mean",
            "count",
            "num_unique",
            "mode",
            "avg_time_between",
            "trend",
            "time_since_last",
        ],
        trans_primitives=[
            "month",
        ],
        where_primitives=["sum", "count", "mean", "trend"],
        n_jobs=n_jobs,
    )

    return feature_matrix, feature_defs


def create_ft_matrix_and_defs_reduced(
    es: ft.EntitySet, cut_off_date: date, n_jobs: int
) -> Tuple[pd.DataFrame, List[ft.FeatureBase]]:
    """Calculate feature matrix for the input entity set, with the 3 related entities
    population, sales and fees. Define interesting values. This is the reduced set
    for the first and last month.

    Parameters
    ----------
    es : ft.EntitySet
        featuretools entity set for the fiven cut-off date
    cut_off_date : date
        cut-off date separating observation period from label period
    n_jobs: int
        number of workers to use

    Returns
    -------
    pd.DataFrame, List[ft.FeatureBase]
        featuretools feature matrix and feature list
    """

    ft_to_drop = [
        "NUM_UNIQUE(sales_fact.transaktionsart_id_korr)",
        "AVG_TIME_BETWEEN(fees_fact.kauf_datum)",
        "NUM_UNIQUE(sales_fact.MONTH(kauf_datum))",
        "NUM_UNIQUE(fees_fact.MONTH(kauf_datum))",
        "SUM(sales_fact.betrag WHERE transaktionsart_id_korr = 0)",
        "COUNT(fees_fact WHERE bewegungstyp = mahnung)",
        "COUNT(fees_fact WHERE bewegungstyp = fremdw)",
        "COUNT(fees_fact WHERE bewegungstyp = zins)",
        "NUM_UNIQUE(fees_fact.MONTH(kauf_datum))",
    ]

    feature_matrix, feature_defs = ft.dfs(
        entityset=es,
        target_entity="population",
        verbose=True,
        drop_exact=ft_to_drop,
        cutoff_time=pd.to_datetime(cut_off_date),
        agg_primitives=[
            "sum",
            "count",
            "num_unique",
            "avg_time_between",
        ],
        trans_primitives=[],
        where_primitives=["sum", "count"],
        n_jobs=n_jobs
    )

    return feature_matrix, feature_defs


def impute_missing_values_full(
    feature_matrix_reduced: pd.DataFrame
) -> pd.DataFrame:
    """Impute missing values in some of the created features. This
    function is meant for reduced feature matrixes with data
    for periods of one months!

    Parameters
    ----------
    feature_matrix_reduced : pd.DataFrame
        feature matrix for period of one month

    Returns
    -------
    pd.DataFrame
        copy of input feature matrix with imputed NaN
    """
    max_year_diff_secs = 367 * 24 * 60 * 60     # > max
    fm = feature_matrix_reduced.copy()

    cols_fill_secs = [
        col for col in fm.columns
        if col.startswith("TIME_SINCE") or col.startswith("AVG_TIME")
    ]
    cols_fill_0 = [
        col for col in fm.columns
        if col.startswith("NUM_UNIQUE") or col.startswith("MEAN")
        or col.startswith("MIN") or col.startswith("MAX")
    ]

    for col in cols_fill_secs:
        assert max_year_diff_secs >= fm[col].max()
        fm[col] = fm[col].fillna(max_year_diff_secs)

    for col in cols_fill_0:
        fm[col] = fm[col].fillna(0)

    return fm


def impute_missing_values_reduced(
    feature_matrix_reduced: pd.DataFrame
) -> pd.DataFrame:
    """Impute missing values in some of the created features. This
    function is meant for reduced feature matrixes with data
    for periods of one months!

    Parameters
    ----------
    feature_matrix_reduced : pd.DataFrame
        feature matrix for period of one month

    Returns
    -------
    pd.DataFrame
        copy of input feature matrix with imputed NaN
    """
    max_month_diff_secs = 32 * 24 * 60 * 60     # > max
    fm = feature_matrix_reduced.copy()

    cols_fill_secs = [
        col for col in fm.columns
        if col.startswith("TIME_SINCE") or col.startswith("AVG_TIME")
    ]
    cols_fill_0 = [col for col in fm.columns if col.startswith("NUM_UNIQUE")]

    for col in cols_fill_secs:
        assert max_month_diff_secs >= fm[col].max()
        fm[col] = fm[col].fillna(max_month_diff_secs)

    for col in cols_fill_0:
        fm[col] = fm[col].fillna(0)

    return fm


def calculate_trend_last_minus_first(feature_matrix_first, feature_matrix_last):
    """Subtract the values for the first month from those for the last month
    for a set of relevant features, to have a trend indication.

    Parameters
    ----------
    feature_matrix_first : pd.DataFrame
        feature matrix for period first month
    feature_matrix_last : pd.DataFrame
        feature matrix for period last month

    Returns
    -------
    pd.DataFrame
        trend feature dataset
    """
    assert (feature_matrix_first.index == feature_matrix_last.index).all()

    trend_features = feature_matrix_last.to_numpy(
    ) - feature_matrix_first.to_numpy()
    trend_columns = [f"trend_{col}" for col in feature_matrix_first.columns]
    trend_features = pd.DataFrame(
        trend_features, columns=trend_columns, index=feature_matrix_first.index
    )

    return trend_features


def concat_fm_12m_and_trend_features(
    feature_matrix: pd.DataFrame, trend_features: pd.DataFrame
) -> pd.DataFrame:
    """Append the trend features to the main feature matrix
    containing the values for the 12 month period

    Parameters
    ----------
    feature_matrix : pd.DataFrame
        feature matrix (for period 12 months)
    trend_features : pd.DataFrame
        trend feature dataset (from period last month - period first month)

    Returns
    -------
    pd.DataFrame, List[ft.FeatureBase]
        full feature set
    """
    return pd.concat([feature_matrix, trend_features], axis=1)


# TODO add asserts
def load_fact_feature_set(
    pop: pd.DataFrame,
    cut_off_date: date,
    first_date: date,
    engine: Engine,
    n_jobs: int,
    do_check: bool = False
) -> pd.DataFrame:
    """main function for loading the complete fact feature set,
    applying featuretools during the process. This brings together
    all the other function in the module `fact_features`.

    Parameters
    ----------
    pop : pd.DataFrame
        population used at the given cut-off date
    cut_off_date : date
        cut-off date separating observation period from label period
    first_date :  date
        first date of observation period
    engine : Engine
        jemas connection
    n_jobs: int
        number of workers to use for feature_set calculation (featuretools)

    Returns
    -------
    pd.DataFrame
        reduced copy of fact
    """
    # Load, fit and split fact data
    sales = load_sales_fact(cut_off_date, first_date, engine)
    sales_red = fit_fact_df_to_population(sales, pop)
    sales_first, sales_12m, sales_last = split_fact_df_into_3_periods(
        sales_red, cut_off_date, first_date
    )

    fees = load_fees_fact(cut_off_date, first_date, engine)
    fees_red = fit_fact_df_to_population(fees, pop)
    fees_first, fees_12m, fees_last = split_fact_df_into_3_periods(
        fees_red, cut_off_date, first_date
    )

    # Create entity sets and featuretools matrices
    es_first = create_entity_set_ft(pop, sales_first, fees_first)
    es_last = create_entity_set_ft(pop, sales_last, fees_last)
    es_12m = create_entity_set_ft(pop, sales_12m, fees_12m)

    t_start = datetime.now()
    fm_first, _ = create_ft_matrix_and_defs_reduced(
        es_first, cut_off_date, n_jobs
    )
    t_diff = (datetime.now() - t_start).seconds
    logger.info(
        f"""creating features -13 months took {round(t_diff/60, 1)} minutes"""
    )
    t_start = datetime.now()
    fm_last, _ = create_ft_matrix_and_defs_reduced(
        es_last, cut_off_date, n_jobs
    )
    logger.info(
        f"""creating features -1 months took {round(t_diff/60, 1)} minutes"""
    )
    t_start = datetime.now()
    fm_12m, _ = create_ft_matrix_and_defs_full(es_12m, cut_off_date, n_jobs)
    logger.info(
        f"""creating features for 12 months months took {round(t_diff/60, 1)} minutes"""
    )
    logger.info(
        f"""imputing (logically) missing values for featuretools data"""
    )
    if do_check:
        assert fm_first.shape == fm_last.shape
        assert fm_first.index.all() == fm_last.index.all() == fm_12m.index.all()

    fm_first = impute_missing_values_reduced(fm_first)
    fm_last = impute_missing_values_reduced(fm_last)
    fm_12m = impute_missing_values_full(fm_12m)

    if do_check:
        assert pd.concat([fm_first, fm_last], axis=1).isna().sum().sum() == 0

    # Calculate trend_features and append to full set
    logger.info("calculating trends for months -1 vs. -13")
    trend_features = calculate_trend_last_minus_first(fm_first, fm_last)
    df_ft = concat_fm_12m_and_trend_features(fm_12m, trend_features)

    if do_check:
        assert df_ft.shape[1] == (fm_12m.shape[1] + trend_features.shape[1])
        assert (df_ft.index == fm_first.index).all()

    return df_ft
