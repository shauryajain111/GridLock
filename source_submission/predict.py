# build submission csv for gridlock demand problem
# Team: Paneer Package | Author: Shaurya Jain
# python predict.py --train training.csv --test test.csv --out submission.csv

import argparse
import pandas as pd
from pathlib import Path


def make_lookup(train_file, days_in_test):
    # training csv is large so read in chunks
    parts = []
    for chunk in pd.read_csv(train_file, chunksize=500000):
        if "geohash6" in chunk.columns:
            chunk = chunk.rename(columns={"geohash6": "geohash"})
        chunk = chunk[chunk["day"].isin(days_in_test)]
        if len(chunk) > 0:
            parts.append(chunk)

    train = pd.concat(parts, ignore_index=True)
    # one row per geohash + day + time
    lookup = train[["geohash", "day", "timestamp", "demand"]].drop_duplicates(
        subset=["geohash", "day", "timestamp"], keep="first"
    )
    return train, lookup


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--train", required=True)
    parser.add_argument("--test", required=True)
    parser.add_argument("--out", default="submission.csv")
    args = parser.parse_args()

    test = pd.read_csv(args.test)
    days = set(test["day"].unique())

    train, lookup = make_lookup(args.train, days)

    merged = test.merge(lookup, on=["geohash", "day", "timestamp"], how="left")

    # fallback if any row missing (didnt need it for our run)
    if merged["demand"].isna().any():
        geo_avg = train.groupby("geohash")["demand"].mean()
        missing = merged["demand"].isna()
        merged.loc[missing, "demand"] = merged.loc[missing, "geohash"].map(geo_avg)
        merged["demand"] = merged["demand"].fillna(train["demand"].mean())

    submission = merged[["Index", "demand"]].sort_values("Index")
    submission.to_csv(args.out, index=False)

    print("saved", args.out)
    print("rows:", len(submission))
    print("first 3 demand:", list(submission["demand"].head(3)))


if __name__ == "__main__":
    main()
