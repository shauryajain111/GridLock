import pandas as pd
import numpy as np
import pickle
import argparse
from preprocess import load_and_prepare

FEATURES = [
    "geohash", "day", "timestamp", "hour", "minute",
    "is_peak_hour", "part_of_day", "geohash_prefix",
    "RoadType", "NumberofLanes", "LargeVehicles",
    "Landmarks", "Temperature", "Weather",
    "lanes_x_peak", "lanes_x_part",
]

def predict(test_path, model_path, encoders_path, out_path):
    with open(model_path, "rb") as f:
        model = pickle.load(f)
    with open(encoders_path, "rb") as f:
        bundle = pickle.load(f)

    encoders     = bundle["label_encoders"]
    impute_cache = bundle["impute_cache"]

    test, _, _ = load_and_prepare(test_path, encoders=encoders,
                                   fit=False, impute_cache=impute_cache)

    preds = model.predict(test[FEATURES])
    preds = np.clip(preds, 0, 1)

    submission = test[["Index"]].copy()
    submission["demand"] = preds
    submission = submission.sort_values("Index")
    submission.to_csv(out_path, index=False)
    print(f"Saved {len(submission)} predictions to {out_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate submission for Gridlock Hackathon")
    parser.add_argument("--test",     default="dataset/test.csv")
    parser.add_argument("--model",    default="model.pkl")
    parser.add_argument("--encoders", default="encoders.pkl")
    parser.add_argument("--out",      default="submission.csv")
    args = parser.parse_args()

    predict(args.test, args.model, args.encoders, args.out)
