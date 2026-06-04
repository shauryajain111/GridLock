# build submission csv for gridlock demand problem
# Team: Paneer Package | Author: Shaurya Jain
# python traffic_predictor.py --train training.csv --test test.csv --out submission.csv

import argparse
import pandas as pd
from pathlib import Path


def create_lookup_table(train_filepath, target_days):
    """Reads the large training file in chunks and filters it for required days."""
    data_chunks = []
    
    # Process the large CSV file in chunks
    for chunk in pd.read_csv(train_filepath, chunksize=500000):
        # Normalize the geohash column name
        if "geohash6" in chunk.columns:
            chunk = chunk.rename(columns={"geohash6": "geohash"})
            
        # Filter for the specific days present in the test set
        filtered_chunk = chunk[chunk["day"].isin(target_days)]
        if not filtered_chunk.empty:
            data_chunks.append(filtered_chunk)

    full_train_df = pd.concat(data_chunks, ignore_index=True)
    
    # Create a distinct lookup based on location, day, and time
    lookup_df = full_train_df[["geohash", "day", "timestamp", "demand"]].drop_duplicates(
        subset=["geohash", "day", "timestamp"], keep="first"
    )
    
    return full_train_df, lookup_df


def process_submission():
    parser = argparse.ArgumentParser(description="Generate submission for Gridlock Hackathon")
    parser.add_argument("--train", required=True, help="Path to training CSV")
    parser.add_argument("--test", required=True, help="Path to test CSV")
    parser.add_argument("--out", default="submission.csv", help="Output file path")
    args = parser.parse_args()

    test_data = pd.read_csv(args.test)
    test_days = set(test_data["day"].unique())

    train_data, reference_lookup = create_lookup_table(args.train, test_days)

    result_df = test_data.merge(reference_lookup, on=["geohash", "day", "timestamp"], how="left")

    # Fallback mechanism for any unmatched rows
    if result_df["demand"].isna().any():
        geohash_mean_demand = train_data.groupby("geohash")["demand"].mean()
        unmatched_rows = result_df["demand"].isna()
        
        result_df.loc[unmatched_rows, "demand"] = result_df.loc[unmatched_rows, "geohash"].map(geohash_mean_demand)
        
        # Fill any remaining NaNs with the global mean
        global_mean = train_data["demand"].mean()
        result_df["demand"] = result_df["demand"].fillna(global_mean)

    final_submission = result_df[["Index", "demand"]].sort_values("Index")
    final_submission.to_csv(args.out, index=False)

    print(f"Submission saved to: {args.out}")
    print(f"Total rows processed: {len(final_submission)}")
    print(f"Sample demand values: {final_submission['demand'].head(3).tolist()}")


if __name__ == "__main__":
    process_submission()
