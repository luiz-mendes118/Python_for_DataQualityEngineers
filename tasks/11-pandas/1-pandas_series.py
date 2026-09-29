"""
Script Name: olympics_audit.py
Purpose: Modular Data Auditing Pipeline using Pandas Series. Performs data ingestion,
         null auditing & cleaning, gold leaderboards with index alignment, and generational mapping.
"""

import pandas as pd


def ingest_olympic_series(csv_path: str) -> dict:
    """
    Reads the Olympic CSV file and constructs 6 distinct Pandas Series:
    - 'games': Unique values from column 'Games', indexed with default integer sequence.
    - 'name', 'medal', 'team', 'year', 'age': Series with values from CSV columns and index explicitly set to 'ID'.
    """
    df = pd.read_csv(csv_path)

    # Ensure ID column exists
    if "ID" not in df.columns:
        raise ValueError("CSV file must contain an 'ID' column.")

    games_series = pd.Series(df["Games"].unique())
    name_series = pd.Series(df["name"].values, index=df["ID"])
    medal_series = pd.Series(df["Medal"].values, index=df["ID"])
    team_series = pd.Series(df["Team"].values, index=df["ID"])
    year_series = pd.Series(df["Year"].values, index=df["ID"])
    age_series = pd.Series(df["Age"].values, index=df["ID"])

    return {
        "games": games_series,
        "name": name_series,
        "medal": medal_series,
        "team": team_series,
        "year": year_series,
        "age": age_series
    }


def audit_and_clean_nulls(series_dict: dict) -> tuple[dict, dict]:
    """
    Calculates raw missing (NaN) counts, drops null entries for string series,
    and fills missing values in numeric series with their integer median.
    """
    raw_null_counts = {}
    cleaned_dict = {}

    # Define which series are string-based vs numeric
    string_keys = {"name", "team", "medal"}
    numeric_keys = {"year", "age"}

    for key, s in series_dict.items():
        if key == "games":
            # Games is kept as is for unique count purposes
            raw_null_counts[key] = int(s.isna().sum())
            cleaned_dict[key] = s.dropna()
            continue

        raw_null_counts[key] = int(s.isna().sum())

        if key in string_keys:
            # Drop all null entries for string series
            cleaned_dict[key] = s.dropna()
        elif key in numeric_keys:
            # Fill missing values with the integer average (median)
            median_val = int(s.median()) if not s.dropna().empty else 0
            cleaned_dict[key] = s.fillna(median_val)

    return raw_null_counts, cleaned_dict


def get_gold_leaderboards(cleaned_dict: dict) -> tuple[int, pd.Series, pd.Series]:
    """
    Filters for Gold medals and uses athlete ID index alignment to compute:
    - total_medalists_count: Total unique medal records (non-null medals)
    - top_3_gold_countries: Top 3 teams by total gold medals across all games
    - top_3_gold_athletes: Top 3 athlete names by total gold medals across all games
    """
    s_medal = cleaned_dict["medal"]
    s_team = cleaned_dict["team"]
    s_name = cleaned_dict["name"]

    # Total medalists count (non-null entries inmedal series)
    total_medalists_count = int(s_medal.dropna().count())

    # Boolean mask for Gold medals (case-insensitive check)
    gold_mask = s_medal.astype(str).str.strip().str.lower() == "gold"
    gold_medals = s_medal[gold_mask]

    # Index alignment: use gold medal IDs to fetch corresponding teams and names
    gold_teams = s_team.loc[gold_medals.index]
    gold_athletes = s_name.loc[gold_medals.index]

    # Top 3 Gold Countries
    top_3_gold_countries = gold_teams.value_counts().head(3)

    # Top 3 Gold Athletes
    top_3_gold_athletes = gold_athletes.value_counts().head(3)

    return total_medalists_count, top_3_gold_countries, top_3_gold_athletes


def classify_athlete_generations(cleaned_dict: dict, top_3_athletes: pd.Series) -> pd.Series:
    """
    Calculates birth year via index-aligned subtraction (game_year - age),
    maps birth years to generations via .apply(), and re-indexes to top_3_gold_athletes names.
    """
    s_year = cleaned_dict["year"]
    s_age = cleaned_dict["age"]
    s_name = cleaned_dict["name"]

    # Index-aligned subtraction to get birth years for all records
    birth_years = s_year - s_age

    # Map birth year to demographic generations
    def assign_generation(year):
        if pd.isna(year):
            return "Unknown"
        y = int(year)
        if y < 1928:
            return "Greatest Generation"
        elif 1928 <= y <= 1945:
            return "Silent Generation"
        elif 1946 <= y <= 1964:
            return "Baby Boomers"
        elif 1965 <= y <= 1980:
            return "Generation X"
        elif 1981 <= y <= 1996:
            return "Millennials"
        elif 1997 <= y <= 2012:
            return "Generation Z"
        else:
            return "Generation Alpha"

    generations_series = birth_years.apply(assign_generation)

    # Re-index/map generations to the athlete names using athlete IDs
    # top_3_athletes has athlete names as index (or values depending on value_counts output)
    athlete_ids = top_3_athletes.index

    # Extract the latest or representative generation classification for each top athlete
    athlete_generations = {}
    for athlete_id in athlete_ids:
        # Get the name for this ID
        name = s_name.loc[athlete_id]
        if isinstance(name, pd.Series):
            name = name.iloc[0]  # Handle potential duplicate ID mappings

        # Get generation for this ID
        gen = generations_series.loc[athlete_id]
        if isinstance(gen, pd.Series):
            gen = gen.iloc[0]

        athlete_generations[name] = gen

    return pd.Series(athlete_generations)


def audit_olympic_series(csv_path: str) -> dict:
    """
    Master pipeline orchestrator: executes Parts 1-4 sequentially and returns
    the final audit dictionary.
    """
    # Part 1: Ingestion
    raw_series = ingest_olympic_series(csv_path)

    # Part 2: Nulls Handling
    null_counts, cleaned_dict = audit_and_clean_nulls(raw_series)
    unique_games_count = int(cleaned_dict["games"].nunique())

    # Part 3: Gold Leaderboards
    total_medalists_count, top_3_gold_countries, top_3_gold_athletes = get_gold_leaderboards(cleaned_dict)

    # Part 4: Generational Mapping
    top_3_gold_athletes_generations = classify_athlete_generations(cleaned_dict, top_3_gold_athletes)

    # Construct Final Output Dictionary
    audit_result = {
        "null_counts": {
            "name": null_counts["name"],
            "medal": null_counts["medal"],
            "team": null_counts["team"],
            "year": null_counts["year"],
            "age": null_counts["age"]
        },
        "unique_games_count": unique_games_count,
        "total_medalists_count": total_medalists_count,
        "top_3_gold_countries": top_3_gold_countries,
        "top_3_gold_athletes": top_3_gold_athletes,
        "top_3_gold_athletes_generations": top_3_gold_athletes_generations
    }

    return audit_result


# -------------------------------------------------------------------------
# Execution Test Block
# -------------------------------------------------------------------------
if __name__ == "__main__":
    # Test your function by passing your Olympic CSV file path
    result = audit_olympic_series("path_to_olympics.csv")
    print(result)
    #pass