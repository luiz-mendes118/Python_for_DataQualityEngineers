"""
Script Name: ecommerce_pipeline.py
Purpose: Modular Data Auditing Pipeline using Pandas DataFrames. Performs multi-format ingestion,
         vertical concatenation, vectorized data cleaning, relational full outer joins,
         index-aligned joins, and analytical group-by aggregations.
"""

import pandas as pd


def ingest_and_concat_sales(us_csv_path: str, eu_json_path: str) -> pd.DataFrame:
    """
    Ingests US sales CSV and EU sales JSON, adds 'channel' column ('US' and 'EU'),
    and vertically stacks them into a single DataFrame with unique sequential indexes.
    """
    df_us = pd.read_csv(us_csv_path)
    df_eu = pd.read_json(eu_json_path)

    # Add channel identifiers
    df_us["channel"] = "US"
    df_eu["channel"] = "EU"

    # Vertically stack DataFrames with ignore_index=True
    df_sales = pd.concat([df_us, df_eu], ignore_index=True)

    return df_sales


def clean_and_calculate_sales(df_sales: pd.DataFrame) -> pd.DataFrame:
    """
    Cleans sales data vectorially: converts date, drops rows with missing transaction_id or quantity,
    fills missing discounts with 0.0, and calculates net revenue.
    """
    # Create a copy to avoid SettingWithCopyWarning
    df_cleaned = df_sales.copy()

    # Convert date column to datetime64[ns]
    if "date" in df_cleaned.columns:
        df_cleaned["date"] = pd.to_datetime(df_cleaned["date"])

    # Drop rows where either 'transaction_id' OR 'quantity' is missing
    subset_cols = [col for col in ["transaction_id", "quantity"] if col in df_cleaned.columns]
    if subset_cols:
        df_cleaned = df_cleaned.dropna(subset=subset_cols)

    # Fill missing values in 'discount' column with 0.0
    if "discount" in df_cleaned.columns:
        df_cleaned["discount"] = df_cleaned["discount"].fillna(0.0)

    # Calculate net revenue using vectorized arithmetic: quantity * unit_price * (1 - discount)
    if all(col in df_cleaned.columns for col in ["quantity", "unit_price", "discount"]):
        df_cleaned["net_revenue"] = (
                df_cleaned["quantity"] * df_cleaned["unit_price"] * (1 - df_cleaned["discount"])
        )

    return df_cleaned


def merge_product_catalog(df_sales: pd.DataFrame, catalog_csv_path: str) -> pd.DataFrame:
    """
    Ingests product catalog CSV, merges with df_sales (left_on='product_id', right_on='sku_code'),
    performs a full outer join with audit indicator, and retains only matched records (_merge == 'both').
    """
    df_catalog = pd.read_csv(catalog_csv_path)

    # Perform full outer join with merge audit indicator
    merged_df = pd.merge(
        df_sales,
        df_catalog,
        left_on="product_id",
        right_on="sku_code",
        how="outer",
        indicator=True
    )

    # Filter to retain only matched transactions (_merge == 'both') and drop the _merge column
    df_matched = merged_df[merged_df["_merge"] == "both"].drop(columns=["_merge"])

    return df_matched


def join_store_targets(df_sales: pd.DataFrame, targets_csv_path: str) -> pd.DataFrame:
    """
    Ingests targets CSV, sets 'store_id' as index on both DataFrames, joins target data
    using .join() with suffix collision handling on 'discount', and resets the index.
    """
    df_targets = pd.read_csv(targets_csv_path)

    # Set 'store_id' as index for both DataFrames
    df_sales_indexed = df_sales.set_index("store_id")
    df_targets_indexed = df_targets.set_index("store_id")

    # Join target data into df_sales using .join() with suffix collision handling
    joined_df = df_sales_indexed.join(
        df_targets_indexed,
        lsuffix="_sale",
        rsuffix="_target"
    )

    # Reset index back to standard integer positioning
    df_result = joined_df.reset_index()

    return df_result


def audit_ecommerce_pipeline(
        us_csv_path: str,
        eu_json_path: str,
        catalog_csv_path: str,
        targets_csv_path: str
) -> dict:
    """
    Master pipeline orchestrator: executes functions 1-4 sequentially,
    calculates summary metrics, and returns the final audit dictionary.
    """
    # Step 1: Ingest and concatenate sales
    df_raw = ingest_and_concat_sales(us_csv_path, eu_json_path)
    total_raw_records = len(df_raw)

    # Step 2: Clean and calculate sales metrics
    df_clean = clean_and_calculate_sales(df_raw)
    clean_sales_records = len(df_clean)

    # Step 3: Merge product catalog
    df_catalog_merged = merge_product_catalog(df_clean, catalog_csv_path)

    # Step 4: Join store targets
    df_final = join_store_targets(df_catalog_merged, targets_csv_path)

    # Step 5: Summary metrics & Aggregations (Vectorized Groupby)
    # Revenue by category
    revenue_by_category = df_final.groupby("category")["net_revenue"].sum()

    # Regional performance
    # Group by region to calculate net_revenue sum and sales_target mean
    regional_grouped = df_final.groupby("region").agg(
        net_revenue=("net_revenue", "sum"),
        sales_target=("sales_target", "mean")
    )

    # Vectorized calculation for target achieved percentage
    regional_grouped["target_achieved_pct"] = (
                                                      regional_grouped["net_revenue"] / regional_grouped["sales_target"]
                                              ) * 100

    regional_performance = regional_grouped[
        ["net_revenue", "sales_target", "target_achieved_pct"]
    ]

    # Construct final summary dictionary
    pipeline_summary = {
        "total_raw_records": total_raw_records,
        "clean_sales_records": clean_sales_records,
        "revenue_by_category": revenue_by_category,
        "regional_performance": regional_performance
    }

    return pipeline_summary


# -------------------------------------------------------------------------
# Execution Test Block
# -------------------------------------------------------------------------
if __name__ == "__main__":
    #Test your pipeline by passing your file paths
    summary = audit_ecommerce_pipeline(
        "sales_us.csv",
        "sales_eu.json",
        "product_catalog.csv",
        "store_targets.csv"
    )
    print(summary)
    #pass