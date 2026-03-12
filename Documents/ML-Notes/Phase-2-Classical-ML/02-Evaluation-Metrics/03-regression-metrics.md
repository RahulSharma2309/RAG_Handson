# Regression Metrics — MAE, MSE, and RMSE

> Classification metrics like accuracy, precision, and recall don't apply to regression tasks (where you predict a continuous number). This document covers the three key regression metrics: **Mean Absolute Error (MAE)**, **Mean Squared Error (MSE)**, and **Root Mean Squared Error (RMSE)**.

---

## Table of Contents

- [Classification vs. Regression — Why Different Metrics?](#classification-vs-regression--why-different-metrics)
- [Mean Absolute Error (MAE)](#mean-absolute-error-mae)
- [Mean Squared Error (MSE)](#mean-squared-error-mse)
- [Root Mean Squared Error (RMSE)](#root-mean-squared-error-rmse)
- [Comparing MAE, MSE, and RMSE](#comparing-mae-mse-and-rmse)
- [Worked Example: House Price Prediction](#worked-example-house-price-prediction)
- ["Is My RMSE Good Enough?"](#is-my-rmse-good-enough)
- [Python Code Example](#python-code-example)

---

## Classification vs. Regression — Why Different Metrics?

| Task Type | What You Predict | Example | Metrics |
|-----------|-----------------|---------|---------|
| **Classification** | A category/class | Dog or Cat, Spam or Legitimate | Accuracy, Precision, Recall, F1 |
| **Regression** | A continuous number | House price, temperature, stock price | MAE, MSE, RMSE |

It doesn't make sense to calculate "accuracy" for regression. If the actual house price is $300,000 and your model predicts $299,500, is that "correct" or "incorrect"? It's neither — it's **close**. So we need metrics that measure **how close** the predictions are to the actual values.

---

## Mean Absolute Error (MAE)

### Definition

> **MAE** is the average of the absolute differences between predicted values and actual values.

### Formula

```
         1   n
MAE  =  ─── Σ |yᵢ - ŷᵢ|
         n  i=1

Where:
  n  = number of predictions
  yᵢ = actual value (true label)
  ŷᵢ = predicted value (model's output)
```

### In Plain English

1. For each prediction, find the **difference** between the actual and predicted value
2. Take the **absolute value** (because errors can be positive or negative)
3. **Average** all those absolute differences

### Example: Predicting House Prices (in $1000s)

| House | Actual Price | Predicted Price | Error (Actual - Predicted) | Absolute Error |
|-------|-------------|-----------------|---------------------------|----------------|
| 1 | 300 | 280 | +20 | 20 |
| 2 | 450 | 470 | -20 | 20 |
| 3 | 200 | 210 | -10 | 10 |
| 4 | 600 | 550 | +50 | 50 |
| 5 | 350 | 340 | +10 | 10 |

```
MAE = (20 + 20 + 10 + 50 + 10) / 5 = 110 / 5 = $22K
```

**Interpretation:** On average, our predictions are off by **$22,000** from the actual house price.

### Pros and Cons

| Pros | Cons |
|------|------|
| Easy to understand and interpret | **Doesn't punish large errors** — a $50K error is treated proportionally the same as a $10K error |
| Same units as the original data | Can be misleading when there are big outliers |
| Robust to outliers (relative to MSE) | |

---

## Mean Squared Error (MSE)

### Definition

> **MSE** is the average of the **squared** differences between predicted values and actual values.

### Formula

```
         1   n
MSE  =  ─── Σ (yᵢ - ŷᵢ)²
         n  i=1
```

### In Plain English

1. For each prediction, find the **difference** between the actual and predicted value
2. **Square** that difference (this makes large errors count much more)
3. **Average** all those squared differences

### Example: Same House Prices

| House | Actual Price | Predicted Price | Error | Squared Error |
|-------|-------------|-----------------|-------|--------------|
| 1 | 300 | 280 | 20 | 400 |
| 2 | 450 | 470 | -20 | 400 |
| 3 | 200 | 210 | -10 | 100 |
| 4 | 600 | 550 | 50 | **2,500** |
| 5 | 350 | 340 | 10 | 100 |

```
MSE = (400 + 400 + 100 + 2,500 + 100) / 5 = 3,500 / 5 = 700
```

### Notice How MSE Punishes Large Errors

- House 4 had an error of $50K → squared error = **2,500** (dominates the total!)
- House 3 had an error of $10K → squared error = 100
- House 4's error was 5x bigger than House 3's, but its **squared error is 25x bigger**

This is the key advantage of MSE: **it heavily penalizes large errors**, making the model pay extra attention to outliers.

### The Units Problem

The MSE of our example is **700**. But 700 what?

Since we squared the errors, the units are also squared: **$1000² = $1,000,000** (squared dollars). This is hard to interpret — what does "700 squared-thousand-dollars" even mean?

This is why we have RMSE.

### Pros and Cons

| Pros | Cons |
|------|------|
| Punishes large errors heavily | **Units are squared** — hard to interpret |
| Differentiable (useful for optimization algorithms) | Sensitive to outliers (can be a pro or con) |
| Widely used in mathematical formulations | |

---

## Root Mean Squared Error (RMSE)

### Definition

> **RMSE** is the square root of MSE. It brings the error metric back to the **same units** as the original data while still punishing large errors.

### Formula

```
              ┌─────────────────┐
              │  1   n          │
RMSE  =    √ │ ─── Σ (yᵢ - ŷᵢ)²│
              │  n  i=1         │
              └─────────────────┘

Or simply:  RMSE = √MSE
```

### Example: Same House Prices

```
RMSE = √700 = $26.46K
```

**Interpretation:** Our model's predictions are off by approximately **$26,460** on average, with larger errors being weighted more heavily than smaller ones.

### Why RMSE is the Most Popular

1. **Punishes large errors** (inherited from MSE)
2. **Same units as the original data** (thanks to the square root)
3. **Easy to interpret** — you can directly compare it to the scale of your target variable

### Pros and Cons

| Pros | Cons |
|------|------|
| Same units as original data — easy to interpret | Still somewhat sensitive to outliers |
| Punishes large errors | Slightly more complex than MAE |
| Most widely used regression metric | |

---

## Comparing MAE, MSE, and RMSE

### Side-by-Side Comparison

| Metric | Formula (Simplified) | Units | Punishes Large Errors? | Best Used When... |
|--------|---------------------|-------|----------------------|-------------------|
| **MAE** | avg(\|actual - predicted\|) | Same as data | No — treats all errors equally | You want a simple, intuitive metric; outliers aren't a big concern |
| **MSE** | avg((actual - predicted)²) | Squared units | **Yes** — heavily | Mathematical formulations, loss functions in training |
| **RMSE** | √avg((actual - predicted)²) | Same as data | **Yes** — heavily | You want to punish large errors AND need interpretable units |

### Visual Comparison

```
                MAE                    MSE                   RMSE
             (forgiving)          (very strict)         (strict + readable)

Error: $10  → counts as 10     → counts as 100      → contributes to √avg
Error: $50  → counts as 50     → counts as 2,500    → contributes to √avg
Error: $100 → counts as 100    → counts as 10,000   → contributes to √avg

The $100 error is:
  MAE:  10x worse than $10 error   (proportional)
  MSE:  100x worse than $10 error  (much worse!)
  RMSE: Somewhere in between (still heavily punished)
```

---

## Worked Example: House Price Prediction

### Full Walk-Through

You built a model to predict house prices. Here are 8 test predictions:

| House | Actual ($K) | Predicted ($K) | Error | \|Error\| | Error² |
|-------|------------|----------------|-------|-----------|--------|
| A | 250 | 245 | 5 | 5 | 25 |
| B | 300 | 310 | -10 | 10 | 100 |
| C | 180 | 175 | 5 | 5 | 25 |
| D | 500 | 480 | 20 | 20 | 400 |
| E | 275 | 290 | -15 | 15 | 225 |
| F | 400 | 395 | 5 | 5 | 25 |
| G | 350 | 350 | 0 | 0 | 0 |
| H | 600 | 510 | 90 | 90 | 8,100 |

### Calculating Each Metric

**MAE:**
```
MAE = (5 + 10 + 5 + 20 + 15 + 5 + 0 + 90) / 8
    = 150 / 8
    = $18.75K
```

**MSE:**
```
MSE = (25 + 100 + 25 + 400 + 225 + 25 + 0 + 8,100) / 8
    = 8,900 / 8
    = 1,112.5  (in squared-$K units — hard to interpret!)
```

**RMSE:**
```
RMSE = √1,112.5
     = $33.35K
```

### Observations

- **MAE says $18.75K** — if you look at most houses, errors are small (5–20K), so this seems reasonable
- **RMSE says $33.35K** — much higher! Why? Because **House H** had a massive $90K error. RMSE punishes that outlier heavily.
- The gap between MAE and RMSE tells you: **there are some large outlier errors** in your predictions

> **Rule of thumb:** If RMSE is much larger than MAE, your model has some predictions that are way off (outliers). Investigate those specific cases.

---

## "Is My RMSE Good Enough?"

This is the most common question, and the answer is always: **it depends on the context**.

### The Same RMSE Can Be Great or Terrible

| Scenario | RMSE | Average Value | RMSE as % of Average | Verdict |
|----------|------|---------------|---------------------|---------|
| Predicting house prices | $10 | $350,000 | 0.003% | **Excellent!** |
| Predicting candy bar prices | $10 | $1.50 | 667% | **Terrible!** |
| Predicting salary | $5,000 | $80,000 | 6.25% | **Pretty good** |
| Predicting temperature (°F) | 15° | 72° | 20.8% | **Not great** |

### How to Judge Your RMSE

1. **Compare to the mean of your target variable**
   ```
   Relative Error = RMSE / mean(y_actual)
   ```
   - < 10%: Generally good
   - 10-20%: Acceptable in many domains
   - > 20%: Needs improvement

2. **Compare to a baseline model**
   - A "dumb" model that always predicts the average value
   - Your model should significantly beat this baseline

3. **Consult domain experts**
   - A real estate agent can tell you if $10K error is acceptable for house prices
   - A financial analyst can tell you if $5K error is acceptable for salary predictions

> **Machine learning is not done in a vacuum.** Always talk to domain experts to understand what error margins are acceptable for your specific use case.

---

## Python Code Example

```python
import numpy as np
from sklearn.metrics import mean_absolute_error, mean_squared_error

# Actual values and predictions
y_actual = np.array([250, 300, 180, 500, 275, 400, 350, 600])
y_predicted = np.array([245, 310, 175, 480, 290, 395, 350, 510])

# Calculate metrics
mae = mean_absolute_error(y_actual, y_predicted)
mse = mean_squared_error(y_actual, y_predicted)
rmse = np.sqrt(mse)  # or: mean_squared_error(y_actual, y_predicted, squared=False)

print(f"MAE:  ${mae:.2f}K")
print(f"MSE:  {mse:.2f}")
print(f"RMSE: ${rmse:.2f}K")

# Compare RMSE to the average actual value
avg_price = np.mean(y_actual)
relative_error = (rmse / avg_price) * 100
print(f"\nAverage actual price: ${avg_price:.2f}K")
print(f"Relative RMSE: {relative_error:.1f}%")
```

### Expected Output

```
MAE:  $18.75K
MSE:  1112.50
RMSE: $33.35K

Average actual price: $356.88K
Relative RMSE: 9.3%
```

---

### Quick Anscombe's Quartet Note

> **Anscombe's Quartet** is a famous set of four datasets that have nearly identical statistical properties (same mean, variance, correlation, and line of best fit) but look completely different when graphed. It's a powerful reminder that **you should always visualize your data**, not just rely on summary statistics or error metrics alone.

```
Dataset I          Dataset II         Dataset III        Dataset IV
  ·  ·                 · ·              · ·                     ·
 · ·  ·             ·     ·            ·  ·
·    ·  ·         ·        ·          ·    ·             ·
  ·     ·        ·          ·        ·  ·               ·
                                                        ·
(Linear)         (Curved)           (Outlier in Y)     (Outlier in X)

All four have the SAME regression line and SAME MSE!
```

---

### Summary Cheat Sheet

```
┌─────────────────────────────────────────────────────┐
│                REGRESSION METRICS                    │
├────────┬───────────────┬─────────────┬──────────────┤
│ Metric │ Punishes      │ Units       │ Use When     │
│        │ Large Errors? │             │              │
├────────┼───────────────┼─────────────┼──────────────┤
│ MAE    │ No            │ Same as Y   │ Simple,      │
│        │               │             │ intuitive    │
├────────┼───────────────┼─────────────┼──────────────┤
│ MSE    │ YES           │ Y²          │ Math/loss    │
│        │ (heavily)     │ (awkward)   │ functions    │
├────────┼───────────────┼─────────────┼──────────────┤
│ RMSE   │ YES           │ Same as Y   │ Most popular │
│        │ (heavily)     │ (readable)  │ go-to metric │
└────────┴───────────────┴─────────────┴──────────────┘
```

---

> **Next up:** [Machine Learning with Python — Scikit-Learn Overview](../03-ML-with-Python/01-scikit-learn-overview.md)
