import pandas as pd
import numpy as np
import pickle
import time
from xgboost import XGBRegressor
from sklearn.model_selection import KFold, cross_val_score
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error

FEATURES = [
    "geohash", "day", "timestamp", "hour", "minute",
    "is_peak_hour", "part_of_day", "geohash_prefix",
    "RoadType", "NumberofLanes", "LargeVehicles",
    "Landmarks", "Temperature", "Weather",
    "lanes_x_peak", "lanes_x_part",
]
TARGET = "demand"

N_FOLDS    = 5
SEED       = 42
MODEL_OUT  = "model.pkl"

PARAMS = {
    "n_estimators"    : 800,
    "learning_rate"   : 0.05,
    "max_depth"       : 7,
    "subsample"       : 0.8,
    "colsample_bytree": 0.8,
    "min_child_weight": 3,
    "reg_alpha"       : 0.1,
    "reg_lambda"      : 1.0,
    "objective"       : "reg:squarederror",
    "tree_method"     : "hist",
    "random_state"    : SEED,
    "n_jobs"          : -1,
}


def print_fold_metrics(fold, y_true, y_pred):
    r2  = r2_score(y_true, y_pred)
    mse = mean_squared_error(y_true, y_pred)
    mae = mean_absolute_error(y_true, y_pred)
    rmse = np.sqrt(mse)
    print(f"  Fold {fold}  |  R²={r2:.6f}  RMSE={rmse:.6f}  MAE={mae:.6f}")
    return r2


def print_overall_metrics(y_true, oof_preds):
    r2   = r2_score(y_true, oof_preds)
    rmse = np.sqrt(mean_squared_error(y_true, oof_preds))
    mae  = mean_absolute_error(y_true, oof_preds)
    print(f"\n  OOF R²  : {r2:.6f}")
    print(f"  OOF RMSE: {rmse:.6f}")
    print(f"  OOF MAE : {mae:.6f}")
    return r2


def print_feature_importance(model, top_n=15):
    importance = model.feature_importances_
    feat_imp = sorted(zip(FEATURES, importance), key=lambda x: x[1], reverse=True)
    print(f"\n  Top {top_n} feature importances:")
    for i, (feat, score) in enumerate(feat_imp[:top_n], 1):
        bar = "█" * int(score * 300)
        print(f"    {i:>2}. {feat:<22} {score:.5f}  {bar}")


def run_cross_validation(X, y):
    kf = KFold(n_splits=N_FOLDS, shuffle=True, random_state=SEED)
    oof_preds = np.zeros(len(y))
    fold_r2s  = []

    print(f"\n  Running {N_FOLDS}-fold cross-validation...")
    for fold, (tr_idx, val_idx) in enumerate(kf.split(X), 1):
        t0 = time.time()
        X_tr,  X_val = X.iloc[tr_idx],  X.iloc[val_idx]
        y_tr,  y_val = y.iloc[tr_idx],  y.iloc[val_idx]

        model = XGBRegressor(**PARAMS)
        model.fit(
            X_tr, y_tr,
            eval_set=[(X_val, y_val)],
            verbose=False,
        )

        oof_preds[val_idx] = model.predict(X_val)
        elapsed = time.time() - t0
        r2 = print_fold_metrics(fold, y_val, oof_preds[val_idx])
        fold_r2s.append(r2)
        print(f"         elapsed: {elapsed:.1f}s")

    return oof_preds, fold_r2s


def summarise_cv(fold_r2s):
    arr = np.array(fold_r2s)
    print(f"\n  CV R² summary:  mean={arr.mean():.6f}  "
          f"std={arr.std():.6f}  "
          f"min={arr.min():.6f}  "
          f"max={arr.max():.6f}")


def train_final_model(X, y):
    print("\n  Training final model on full dataset...")
    t0 = time.time()
    model = XGBRegressor(**PARAMS)
    model.fit(X, y, verbose=False)
    elapsed = time.time() - t0
    print(f"  Done in {elapsed:.1f}s")
    return model


def save_model(model, path):
    with open(path, "wb") as f:
        pickle.dump(model, f)
    size_mb = round(pickle.dumps(model).__len__() / 1e6, 2)
    print(f"\n  Saved {path}  (~{size_mb} MB in memory)")


if __name__ == "__main__":
    print("=" * 55)
    print("Gridlock Hackathon 2.0 — Training Pipeline")
    print("Team: Paneer Package | Author: Shaurya Jain")
    print("=" * 55)

    print("\n[1/4] Loading prepared training data...")
    train = pd.read_parquet("train_prepared.parquet")
    print(f"  Shape: {train.shape}")

    missing = [f for f in FEATURES if f not in train.columns]
    if missing:
        raise ValueError(f"Features missing from parquet: {missing}")

    X = train[FEATURES]
    y = train[TARGET]
    print(f"  X shape: {X.shape}  |  y range: [{y.min():.4f}, {y.max():.4f}]")

    print("\n[2/4] Cross-validation...")
    oof_preds, fold_r2s = run_cross_validation(X, y)
    overall_r2 = print_overall_metrics(y, oof_preds)
    summarise_cv(fold_r2s)

    print("\n[3/4] Final model training...")
    final_model = train_final_model(X, y)
    print_feature_importance(final_model, top_n=15)

    print("\n[4/4] Saving model...")
    save_model(final_model, MODEL_OUT)

    print(f"\nDone. Final leaderboard R² target: {overall_r2:.4f}")
