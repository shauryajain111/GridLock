# Gridlock Hackathon 2.0 — Traffic Demand Prediction

**Team:** Paneer Package  
**Author:** Shaurya Jain  
**Leaderboard R²:** 0.9979

---

This repository contains our submission for the [Flipkart Gridlock Hackathon 2.0](https://www.hackerearth.com/challenges/competitive/gridlock-hackathon-20/) hosted on HackerEarth.

## The Problem Statement

With urbanization rapidly increasing, traffic congestion has become a major challenge for logistics and delivery networks. Flipkart, one of India's leading e-commerce giants, relies on efficient routing to ensure timely deliveries. However, unpredictable traffic patterns can cause significant delays, impacting customer satisfaction and increasing operational costs.

The objective of the **Gridlock Hackathon 2.0** is to accurately predict traffic demand across various road segments and intersections. By forecasting traffic patterns, delivery networks can dynamically adjust routes, optimize dispatch times, and ultimately reduce the time spent in gridlocks.

Participants were provided with extensive spatiotemporal data, including:
- Geographical location identifiers (Geohashes)
- Timestamps and specific days
- Road features such as type, number of lanes, and large vehicle permissions
- Environmental conditions like temperature and weather

The goal is to predict the **traffic demand** (a normalized value between 0 and 1) for over 41,000 distinct locations and time slots. The accuracy of the predictions is evaluated using the Coefficient of Determination (R² score), meaning precise, robust forecasting is essential to rank highly on the leaderboard.

## Approach

We used an **XGBoost regression model** with careful feature engineering. Key steps:
- Geohash and categorical features label-encoded
- Timestamps converted to minutes-since-midnight
- Missing temperature values imputed with the training median
- 5-fold cross-validation for model selection (OOF R² ≈ 0.9979)
- Final model trained on the complete dataset

See [`approach.txt`](approach.txt) for the full write-up.

## Repository Structure

```
├── dataset/
│   ├── train.csv              — training data with demand labels
│   └── test.csv               — test data for submission
├── preprocess.py              — feature engineering and encoding
├── train.py                   — XGBoost model training (5-fold CV)
├── predict_xgb.py             — inference and submission generation
├── requirements.txt           — dependencies
├── approach.txt               — detailed approach and methodology
├── preprocess_log.txt         — output from preprocess run
├── training_log.txt           — output from training run with fold scores
├── model.pkl                  — trained model
└── submission.csv             — final predictions
```

## How to Run

```bash
pip install -r requirements.txt
python preprocess.py
python train.py
python predict_xgb.py --test dataset/test.csv --out submission.csv
```
