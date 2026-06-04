import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder
import pickle
import os

REQUIRED_TRAIN_COLS = ["geohash", "day", "timestamp", "demand",
                       "RoadType", "NumberofLanes", "LargeVehicles",
                       "Landmarks", "Temperature", "Weather"]

REQUIRED_TEST_COLS  = ["geohash", "day", "timestamp",
                       "RoadType", "NumberofLanes", "LargeVehicles",
                       "Landmarks", "Temperature", "Weather"]

CAT_COLS = ["geohash", "geohash_prefix", "RoadType",
            "LargeVehicles", "Landmarks", "Weather"]

PEAK_MORNING_START, PEAK_MORNING_END = 7 * 60, 9 * 60
PEAK_EVENING_START, PEAK_EVENING_END = 17 * 60, 19 * 60


def validate_columns(df, required, label="dataframe"):
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"[{label}] Missing columns: {missing}")
    print(f"[{label}] Column check passed. Shape: {df.shape}")


def parse_timestamp(ts):
    h, m = ts.split(":")
    return int(h) * 60 + int(m)


def extract_time_features(df):
    df["hour"]         = df["timestamp"] // 60
    df["minute"]       = df["timestamp"] % 60
    df["is_peak_hour"] = (
        ((df["timestamp"] >= PEAK_MORNING_START) & (df["timestamp"] <= PEAK_MORNING_END)) |
        ((df["timestamp"] >= PEAK_EVENING_START) & (df["timestamp"] <= PEAK_EVENING_END))
    ).astype(int)
    df["part_of_day"]  = pd.cut(
        df["hour"],
        bins=[-1, 5, 11, 16, 20, 24],
        labels=[0, 1, 2, 3, 4]
    ).astype(int)
    return df


def extract_geohash_features(df):
    df["geohash_prefix"] = df["geohash"].str[:4]
    return df


def impute_numeric(df, col, strategy="median", fill_value=None, fit=True, cache=None):
    if cache is None:
        cache = {}
    if fit:
        if strategy == "median":
            cache[col] = df[col].median()
        elif strategy == "mean":
            cache[col] = df[col].mean()
        else:
            cache[col] = fill_value
    df[col] = df[col].fillna(cache[col])
    return df, cache


def encode_features(df, encoders=None, fit=True):
    if encoders is None:
        encoders = {}
    for col in CAT_COLS:
        if col not in df.columns:
            continue
        if fit:
            le = LabelEncoder()
            df[col] = le.fit_transform(df[col].astype(str))
            encoders[col] = le
        else:
            le = encoders[col]
            df[col] = df[col].astype(str).map(
                lambda x, le=le: le.transform([x])[0] if x in le.classes_ else -1
            )
    return df, encoders


def add_lane_interaction(df):
    df["lanes_x_peak"] = df["NumberofLanes"] * df["is_peak_hour"]
    df["lanes_x_part"]  = df["NumberofLanes"] * df["part_of_day"]
    return df


def load_and_prepare(path, encoders=None, fit=True, impute_cache=None):
    df = pd.read_csv(path)

    required = REQUIRED_TRAIN_COLS if fit else REQUIRED_TEST_COLS
    validate_columns(df, required, label=os.path.basename(path))

    df["timestamp"] = df["timestamp"].apply(parse_timestamp)
    df = extract_time_features(df)
    df = extract_geohash_features(df)

    if impute_cache is None:
        impute_cache = {}
    df, impute_cache = impute_numeric(df, "Temperature", strategy="median",
                                      fit=fit, cache=impute_cache)

    df, encoders = encode_features(df, encoders=encoders, fit=fit)
    df = add_lane_interaction(df)

    print(f"  Final shape after feature engineering: {df.shape}")
    return df, encoders, impute_cache


if __name__ == "__main__":
    print("=" * 55)
    print("Gridlock Hackathon 2.0 — Preprocessing Pipeline")
    print("Team: Paneer Package | Author: Shaurya Jain")
    print("=" * 55)

    print("\n[1/3] Loading and preparing training data...")
    train, encoders, impute_cache = load_and_prepare("dataset/train.csv", fit=True)

    print(f"\n[2/3] Saving encoders and imputation cache...")
    with open("encoders.pkl", "wb") as f:
        pickle.dump({"label_encoders": encoders, "impute_cache": impute_cache}, f)
    print("  encoders.pkl saved.")

    print(f"\n[3/3] Serialising prepared training frame...")
    train.to_parquet("train_prepared.parquet", index=False)
    print(f"  train_prepared.parquet saved.  Rows: {len(train):,}")

    print("\nPreprocessing complete.")
    print(f"Feature columns: {[c for c in train.columns if c != 'demand']}")
