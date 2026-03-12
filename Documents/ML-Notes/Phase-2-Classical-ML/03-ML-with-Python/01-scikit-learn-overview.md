# Machine Learning with Python — Scikit-Learn Overview

> This document covers the **scikit-learn** library — the most popular ML package for Python — including installation, the standard workflow, key methods, and how to choose the right algorithm.

---

## Table of Contents

- [What is Scikit-Learn?](#what-is-scikit-learn)
- [Installation](#installation)
- [The Scikit-Learn Workflow (Step by Step)](#the-scikit-learn-workflow-step-by-step)
- [Step 1: Import the Model](#step-1-import-the-model)
- [Step 2: Instantiate the Model](#step-2-instantiate-the-model)
- [Step 3: Split the Data](#step-3-split-the-data)
- [Step 4: Train (Fit) the Model](#step-4-train-fit-the-model)
- [Step 5: Make Predictions](#step-5-make-predictions)
- [Step 6: Evaluate the Model](#step-6-evaluate-the-model)
- [Universal Methods Across All Scikit-Learn Models](#universal-methods-across-all-scikit-learn-models)
- [Choosing the Right Algorithm](#choosing-the-right-algorithm)
- [Complete Code Example: Start to Finish](#complete-code-example-start-to-finish)

---

## What is Scikit-Learn?

**Scikit-learn** (also written as `sklearn`) is the most popular machine learning library for Python. It provides:

- Dozens of **pre-built ML algorithms** (regression, classification, clustering, etc.)
- Tools for **data preprocessing** (scaling, encoding, splitting)
- **Evaluation metrics** (accuracy, MSE, confusion matrix, etc.)
- A **consistent, uniform API** — once you learn one algorithm, the code pattern is nearly identical for all others

### Key Feature: Uniform Interface

Every algorithm in scikit-learn follows the **same pattern**:

```python
from sklearn.family import Model

model = Model(parameters)       # Create the model
model.fit(X_train, y_train)     # Train it
predictions = model.predict(X_test)  # Make predictions
score = model.score(X_test, y_test)  # Evaluate it
```

This means once you learn the workflow for one algorithm (e.g., Linear Regression), you can apply the **exact same code structure** to any other algorithm (Decision Trees, Random Forests, SVMs, etc.) — just change the import!

---

## Installation

### If you use Anaconda (recommended)

```bash
conda install scikit-learn
```

### If you use pip

```bash
pip install scikit-learn
```

> **Note:** The package is installed as `scikit-learn` but imported as `sklearn` in code.

---

## The Scikit-Learn Workflow (Step by Step)

Here's the complete ML process mapped to scikit-learn code:

```
┌──────────────────────────────────────────────────────────────────┐
│                    SCIKIT-LEARN WORKFLOW                          │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│  1. IMPORT        from sklearn.family import Model               │
│       │                                                          │
│       ▼                                                          │
│  2. INSTANTIATE   model = Model(params)                          │
│       │                                                          │
│       ▼                                                          │
│  3. SPLIT DATA    X_train, X_test, y_train, y_test               │
│       │           = train_test_split(X, y, test_size=0.3)        │
│       ▼                                                          │
│  4. TRAIN/FIT     model.fit(X_train, y_train)                    │
│       │                                                          │
│       ▼                                                          │
│  5. PREDICT       predictions = model.predict(X_test)            │
│       │                                                          │
│       ▼                                                          │
│  6. EVALUATE      Compare predictions to y_test                  │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

---

## Step 1: Import the Model

Every algorithm in scikit-learn lives inside a "family" (module). The general import pattern is:

```python
from sklearn.<family> import <Model>
```

### Common Imports

| Algorithm | Import Statement |
|-----------|-----------------|
| **Linear Regression** | `from sklearn.linear_model import LinearRegression` |
| **Logistic Regression** | `from sklearn.linear_model import LogisticRegression` |
| **Decision Tree** | `from sklearn.tree import DecisionTreeClassifier` |
| **Random Forest** | `from sklearn.ensemble import RandomForestClassifier` |
| **K-Nearest Neighbors** | `from sklearn.neighbors import KNeighborsClassifier` |
| **Support Vector Machine** | `from sklearn.svm import SVC` |
| **K-Means Clustering** | `from sklearn.cluster import KMeans` |

---

## Step 2: Instantiate the Model

Create an instance of the model. You can pass parameters to customize it, but all parameters have **sensible default values**.

```python
# With defaults (most common when starting out)
model = LinearRegression()

# With custom parameters
model = LinearRegression(fit_intercept=True, normalize=True)
```

### Exploring Available Parameters

In a Jupyter notebook, you can use `Shift + Tab` after the model name to see all available parameters and their defaults:

```python
LinearRegression()  # Press Shift+Tab here to see docs
```

Or use:

```python
print(model.get_params())
```

---

## Step 3: Split the Data

Before training, split your data into training and testing sets.

### Understanding X and y

| Symbol | Meaning | Example |
|--------|---------|---------|
| **X** | Features (input data) | Square footage, bedrooms, location |
| **y** | Labels (target variable) | House price |

### Using train_test_split

```python
from sklearn.model_selection import train_test_split

# X = features, y = labels
# test_size=0.3 means 30% for testing, 70% for training
# random_state ensures reproducibility (same split every time)

X_train, X_test, y_train, y_test = train_test_split(
    X, y,
    test_size=0.3,
    random_state=42
)
```

### What This Produces

```
Original Data (100%)
  X (features)  →  X_train (70%)  +  X_test (30%)
  y (labels)    →  y_train (70%)  +  y_test (30%)
```

| Variable | Contains | Used For |
|----------|----------|----------|
| `X_train` | Training features | Training the model |
| `y_train` | Training labels | Training the model |
| `X_test` | Test features | Getting model predictions |
| `y_test` | Test labels | Comparing predictions to evaluate performance |

### Example with Actual Data

```python
import numpy as np

# Simple example: 10 data points
X = np.array([[1], [2], [3], [4], [5], [6], [7], [8], [9], [10]])
y = np.array([2, 4, 6, 8, 10, 12, 14, 16, 18, 20])

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.3, random_state=42
)

print("X_train:", X_train.flatten())  # e.g., [1, 7, 9, 2, 3, 5, 8]
print("X_test:", X_test.flatten())    # e.g., [4, 6, 10]
print("y_train:", y_train)            # e.g., [2, 14, 18, 4, 6, 10, 16]
print("y_test:", y_test)              # e.g., [8, 12, 20]
```

---

## Step 4: Train (Fit) the Model

Pass the **training data** to the model's `.fit()` method:

```python
model.fit(X_train, y_train)
```

### What Happens Inside

- The model looks at the training features (`X_train`) and the correct labels (`y_train`)
- It learns the patterns/relationships between features and labels
- Internal parameters (weights, coefficients) are adjusted to minimize error

### Supervised vs. Unsupervised Fitting

| Type | Fit Call | Why? |
|------|----------|------|
| **Supervised** | `model.fit(X_train, y_train)` | Needs both features AND labels |
| **Unsupervised** | `model.fit(X_train)` | Only needs features (no labels exist) |

---

## Step 5: Make Predictions

Use the trained model to predict labels for the **test features**:

```python
predictions = model.predict(X_test)
```

### What Happens

- The model receives features it has **never seen before** (`X_test`)
- It applies what it learned during training to predict labels
- Returns an array of predicted values

```
X_test (features only)  ──►  Trained Model  ──►  predictions (predicted labels)
```

---

## Step 6: Evaluate the Model

Compare the predictions to the **actual test labels** (`y_test`):

### For Regression

```python
from sklearn.metrics import mean_absolute_error, mean_squared_error
import numpy as np

mae = mean_absolute_error(y_test, predictions)
mse = mean_squared_error(y_test, predictions)
rmse = np.sqrt(mse)

print(f"MAE:  {mae}")
print(f"MSE:  {mse}")
print(f"RMSE: {rmse}")
```

### For Classification

```python
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

accuracy = accuracy_score(y_test, predictions)
print(f"Accuracy: {accuracy}")
print(classification_report(y_test, predictions))
print(confusion_matrix(y_test, predictions))
```

---

## Universal Methods Across All Scikit-Learn Models

One of scikit-learn's greatest strengths is its **uniform interface**. These methods are available on virtually every estimator:

### Supervised Learning Methods

| Method | What It Does | Arguments |
|--------|-------------|-----------|
| `model.fit(X, y)` | Train the model on data | Features `X`, Labels `y` |
| `model.predict(X_new)` | Predict labels for new data | New features `X_new` |
| `model.predict_proba(X_new)` | Get probability for each class (classification only) | New features `X_new` |
| `model.score(X_test, y_test)` | Get a score (0 to 1, higher = better) | Test features and labels |

### Unsupervised Learning Methods

| Method | What It Does | Arguments |
|--------|-------------|-----------|
| `model.fit(X)` | Train on data (no labels needed) | Features `X` |
| `model.predict(X_new)` | Predict cluster labels | New features `X_new` |
| `model.transform(X_new)` | Transform data into new representation | New features `X_new` |
| `model.fit_transform(X)` | Fit and transform in one step (more efficient) | Features `X` |

### The Power of Uniform Interface

Because every model follows the same pattern, **switching algorithms is trivial**:

```python
# Want to try Linear Regression?
from sklearn.linear_model import LinearRegression
model = LinearRegression()
model.fit(X_train, y_train)
predictions = model.predict(X_test)

# Want to try a Decision Tree instead? Just change 2 lines!
from sklearn.tree import DecisionTreeRegressor
model = DecisionTreeRegressor()
model.fit(X_train, y_train)          # Same!
predictions = model.predict(X_test)  # Same!

# Want to try Random Forest? Again, just change 2 lines!
from sklearn.ensemble import RandomForestRegressor
model = RandomForestRegressor()
model.fit(X_train, y_train)          # Same!
predictions = model.predict(X_test)  # Same!
```

---

## Choosing the Right Algorithm

Scikit-learn provides an official **algorithm cheat sheet** (also called a decision flowchart) to help you choose:

```
                        START
                          │
                    More than 50 samples?
                     /            \
                   No              Yes
                   │                │
              Get more         Predicting a
                data          CATEGORY?
                              /          \
                            Yes           No
                             │             │
                      Do you have      Predicting a
                      labeled data?    QUANTITY?
                         /    \          /       \
                       Yes    No       Yes       No
                        │      │        │         │
                  Classification  │  Regression    │
                        │     Clustering   │    Dimensionality
                        │        │         │    Reduction
                        ▼        ▼         ▼        ▼
```

### Quick Decision Guide

| Question | Answer | Algorithm Type | Examples |
|----------|--------|---------------|----------|
| Is the label a **category**? | Yes | **Classification** | Logistic Regression, SVM, Decision Trees, KNN |
| Is the label a **number**? | Yes | **Regression** | Linear Regression, Random Forest Regressor, SVR |
| Do you have **no labels**? | Yes | **Clustering** | K-Means, DBSCAN, Hierarchical Clustering |
| Want to **reduce features**? | Yes | **Dimensionality Reduction** | PCA, t-SNE |

> **Tip:** Google "scikit-learn algorithm cheat sheet" to find the official interactive flowchart from the sklearn documentation.

---

## Complete Code Example: Start to Finish

Here's a complete, runnable example that ties everything together:

```python
# ============================================================
# COMPLETE SCIKIT-LEARN WORKFLOW: House Price Prediction
# ============================================================

# Step 0: Import libraries
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error

# Step 1: Create/load data
# (In real life, you'd load from a CSV or database)
np.random.seed(42)
square_feet = np.random.randint(500, 4000, 100)
bedrooms = np.random.randint(1, 6, 100)
price = square_feet * 150 + bedrooms * 20000 + np.random.randint(-10000, 10000, 100)

# Create a DataFrame
df = pd.DataFrame({
    'square_feet': square_feet,
    'bedrooms': bedrooms,
    'price': price
})

print("Sample of our data:")
print(df.head())
print(f"\nDataset shape: {df.shape}")

# Step 2: Define features (X) and label (y)
X = df[['square_feet', 'bedrooms']]  # Features
y = df['price']                       # Label (what we want to predict)

# Step 3: Split into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.3, random_state=42
)

print(f"\nTraining set size: {len(X_train)}")
print(f"Test set size: {len(X_test)}")

# Step 4: Create and train the model
model = LinearRegression()
model.fit(X_train, y_train)

print(f"\nModel coefficients: {model.coef_}")
print(f"Model intercept: {model.intercept_:.2f}")

# Step 5: Make predictions on test data
predictions = model.predict(X_test)

# Step 6: Evaluate the model
mae = mean_absolute_error(y_test, predictions)
mse = mean_squared_error(y_test, predictions)
rmse = np.sqrt(mse)

print(f"\n--- Model Performance ---")
print(f"MAE:  ${mae:,.2f}")
print(f"MSE:  {mse:,.2f}")
print(f"RMSE: ${rmse:,.2f}")
print(f"Average actual price: ${y_test.mean():,.2f}")
print(f"Relative RMSE: {(rmse / y_test.mean()) * 100:.1f}%")

# Step 7: Predict for brand new data
new_house = np.array([[2500, 3]])  # 2500 sq ft, 3 bedrooms
predicted_price = model.predict(new_house)
print(f"\nPredicted price for a 2500 sq ft, 3-bedroom house: ${predicted_price[0]:,.2f}")
```

### Expected Output (approximate)

```
Sample of our data:
   square_feet  bedrooms   price
0         2570         3  443157
1         1764         5  367340
2          509         3  139832
3         2284         1  361542
4         1584         2  280192

Dataset shape: (100, 3)

Training set size: 70
Test set size: 30

Model coefficients: [  150.03  19834.67]
Model intercept: 1023.45

--- Model Performance ---
MAE:  $5,423.18
MSE:  42,567,891.23
RMSE: $6,524.41
Average actual price: $332,156.78
Relative RMSE: 2.0%

Predicted price for a 2500 sq ft, 3-bedroom house: $434,527.46
```

---

### Quick Reference Card

```
┌────────────────────────────────────────────────────────┐
│          SCIKIT-LEARN CHEAT SHEET                       │
├────────────────────────────────────────────────────────┤
│                                                        │
│  IMPORT:   from sklearn.family import Model            │
│  CREATE:   model = Model()                             │
│  SPLIT:    train_test_split(X, y, test_size=0.3)       │
│  TRAIN:    model.fit(X_train, y_train)                 │
│  PREDICT:  model.predict(X_test)                       │
│  EVALUATE: model.score(X_test, y_test)                 │
│                                                        │
│  Package name:  scikit-learn                           │
│  Import name:   sklearn                                │
│  Install:       pip install scikit-learn                │
│                                                        │
└────────────────────────────────────────────────────────┘
```

---

> **You now have the foundation to start coding ML algorithms in Python!** The first algorithm you'll learn is **Linear Regression** — stay tuned for the next set of notes.
