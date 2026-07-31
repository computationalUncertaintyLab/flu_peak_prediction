# mcandrew

import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


def assign_season(row):
    """
    Define an influenza season as week 35 through week 20.

    Examples
    --------
    2023 week 40 -> 2023/2024
    2024 week 10 -> 2023/2024

    Weeks 21 through 34 are assigned to the upcoming season.
    Change this rule if you want to exclude off-season weeks.
    """
    year = int(row["ISO_YEAR"])
    week = int(row["ISO_WEEK"])

    if week >= 35:
        return f"{year}/{year + 1}"
    else:
        return f"{year - 1}/{year}"


if __name__ == "__main__":

    d = pd.read_csv(
        "./data/who_viw_fid_epi.csv",
        low_memory=False,
    )

    numeric_columns = [
        "ISO_YEAR",
        "ISO_WEEK",
        "ILI_CASE",
        "ILI_OUTPATIENTS",
        "ILI_POP_COV",

    ]

    for column in numeric_columns:
        d[column] = pd.to_numeric(
            d[column],
            errors="coerce",
        )

    d["AGEGROUP_NORMALIZED"] = (
        d["AGEGROUP_CODE"]
        .astype("string")
        .str.strip()
        .str.upper()
    )

    d["IS_ALL_AGES"] = d["AGEGROUP_NORMALIZED"].eq("ALL")

    keys = [
        "COUNTRY_CODE",
        "COUNTRY_AREA_TERRITORY",
        "ISO_YEAR",
        "ISO_WEEK",
        "ISOYW",
        "HEMISPHERE"
    ]

    # Keep one explicit all-ages record per country-week.
    all_age = (
        d.loc[d["IS_ALL_AGES"]]
        .sort_values(keys)
        .drop_duplicates(keys, keep="first")
        .copy()
    )

    # Remove rows without a valid year or week.
    all_age = all_age.loc[
        all_age["ISO_YEAR"].notna()
        & all_age["ISO_WEEK"].between(1, 53)
    ].copy()

    all_age["season"] = all_age.apply(
        assign_season,
        axis=1,
    )

    # ---------------------------------------------------------
    # Outpatient-based ILI proportion
    #
    # Only count ILI cases from weeks having a valid outpatient
    # denominator. This keeps numerator and denominator aligned.
    # ---------------------------------------------------------

    all_age["valid_outpatient_week"] = (
        all_age["ILI_CASE"].notna()
        & (all_age["ILI_CASE"] >= 0)
        & all_age["ILI_OUTPATIENTS"].notna()
        & (all_age["ILI_OUTPATIENTS"] > 0)
    )

    all_age["ili_cases_with_outpatient_data"] = (
        all_age["ILI_CASE"]
        .where(all_age["valid_outpatient_week"])
    )

    all_age["outpatient_visits_valid"] = (
        all_age["ILI_OUTPATIENTS"]
        .where(all_age["valid_outpatient_week"])
    )

    # ---------------------------------------------------------
    # Population-coverage rate
    #
    # Summing weekly population coverage produces a person-week
    # denominator. Therefore, this is a rate per 100,000 covered
    # person-weeks, not cumulative seasonal incidence.
    # ---------------------------------------------------------

    all_age["valid_population_week"] = (
        all_age["ILI_CASE"].notna()
        & (all_age["ILI_CASE"] >= 0)
        & all_age["ILI_POP_COV"].notna()
        & (all_age["ILI_POP_COV"] > 0)
    )

    all_age["ili_cases_with_population_data"] = (
        all_age["ILI_CASE"]
        .where(all_age["valid_population_week"])
    )

    all_age["population_covered_valid"] = (
        all_age["ILI_POP_COV"]
        .where(all_age["valid_population_week"])
    )

    group_columns = [
        "COUNTRY_CODE",
        "COUNTRY_AREA_TERRITORY",
        "season",
        "HEMISPHERE"
    ]

    seasonal = (
        all_age
        .groupby(group_columns, as_index=False)
        .agg(
            seasonal_ili_cases_outpatient=(
                "ili_cases_with_outpatient_data",
                lambda x: x.sum(min_count=1),
            ),
            seasonal_outpatient_visits=(
                "outpatient_visits_valid",
                lambda x: x.sum(min_count=1),
            ),
            weeks_with_outpatient_data=(
                "valid_outpatient_week",
                "sum",
            ),
            seasonal_ili_cases_population=(
                "ili_cases_with_population_data",
                lambda x: x.sum(min_count=1),
            ),
            seasonal_population_person_weeks=(
                "population_covered_valid",
                lambda x: x.sum(min_count=1),
            ),
            weeks_with_population_data=(
                "valid_population_week",
                "sum",
            ),
            total_weeks_reported=(
                "ISOYW",
                "nunique",
            ),
        )
    )

    seasonal["ili_proportion"] = np.where(
        seasonal["seasonal_outpatient_visits"] > 0,
        (
            seasonal["seasonal_ili_cases_outpatient"]
            / seasonal["seasonal_outpatient_visits"]
        ),
        np.nan,
    )

    seasonal["ili_percent"] = (
        100 * seasonal["ili_proportion"]
    )

    seasonal["ili_rate_per_100k_person_weeks"] = np.where(
        seasonal["seasonal_population_person_weeks"] > 0,
        (
            100_000
            * seasonal["seasonal_ili_cases_population"]
            / seasonal["seasonal_population_person_weeks"]
        ),
        np.nan,
    )

    seasonal.to_csv(
        "./analysis_data/ILI_signal_by_season.csv",
        index=False,
    )
