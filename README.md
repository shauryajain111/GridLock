# Gridlock Hackathon 2.0 — Traffic Demand Prediction

**Team:** Paneer Package  
**Author:** Shaurya Jain  
**Score:** 100 (R² = 1.0) — Perfect leaderboard score

---

This repository contains our submission for the [Flipkart Gridlock Hackathon 2.0](https://www.hackerearth.com/challenges/competitive/gridlock-hackathon-20/) hosted on HackerEarth.

## The Problem Statement

With urbanization rapidly increasing, traffic congestion has become a major challenge for logistics and delivery networks. Flipkart, one of India's leading e-commerce giants, relies on efficient routing to ensure timely deliveries. However, unpredictable traffic patterns can cause significant delays, impacting customer satisfaction and increasing operational costs.

The objective of the **Gridlock Hackathon 2.0** is to accurately predict traffic demand across various road segments and intersections. By forecasting traffic patterns, delivery networks can dynamically adjust routes, optimize dispatch times, and ultimately reduce the time spent in gridlocks.

Participants were provided with extensive spatiotemporal data, including:
- Geographical location identifiers (Geohashes)
- Timestamps and specific days
- Road features and weather conditions

The goal is to predict the **traffic demand** (a normalized value between 0 and 1) for over 41,000 distinct locations and time slots. The accuracy of the predictions is evaluated using the Coefficient of Determination (R² score), meaning precise, robust forecasting is essential to rank highly on the leaderboard.

## Quick Start

To generate the predictions:

```bash
pip install -r source_submission/requirements.txt
python source_submission/predict.py --train dataset/train.csv --test dataset/test.csv --out submission.csv
```
