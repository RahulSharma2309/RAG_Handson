# Classification Metrics

> After training a classification model, how do you know if it's any good? This document covers the four key metrics — **Accuracy, Precision, Recall, and F1-Score** — with intuitive examples that make them easy to remember.

---

## Table of Contents

- [The Fundamental Idea](#the-fundamental-idea)
- [Binary Classification Setup](#binary-classification-setup)
- [Accuracy](#accuracy)
- [The Unbalanced Class Problem](#the-unbalanced-class-problem)
- [True Positives, False Positives, True Negatives, False Negatives](#true-positives-false-positives-true-negatives-false-negatives)
- [Precision](#precision)
- [Recall (Sensitivity)](#recall-sensitivity)
- [The Precision-Recall Trade-Off](#the-precision-recall-trade-off)
- [F1-Score](#f1-score)
- [When to Use Which Metric](#when-to-use-which-metric)
- [Context Matters: The Disease Diagnosis Example](#context-matters-the-disease-diagnosis-example)

---

## The Fundamental Idea

In any classification task, your model can only achieve **two outcomes**:

| Outcome | Meaning |
|---------|---------|
| **Correct** | The model predicted the right class |
| **Incorrect** | The model predicted the wrong class |

**Every single classification metric** is built on top of this simple idea — different ways of counting and combining correct vs. incorrect predictions.

---

## Binary Classification Setup

For simplicity, we'll explain everything using **binary classification** (two classes). The concepts extend naturally to multi-class problems.

### Example: Dog vs. Cat Image Classifier

- We've **trained** a model on labeled images of dogs and cats
- Now we **test** it on 100 new images the model has never seen
- For each image, we compare the **model's prediction** to the **true label**

```
Test Image ──► Trained Model ──► Prediction: "Dog"
                                      │
                                      ▼
                              Compare to True Label: "Dog"
                                      │
                                      ▼
                                  ✅ Correct!
```

---

## Accuracy

### Definition

> **Accuracy** = Number of Correct Predictions / Total Number of Predictions

It answers the question: **"What percentage of predictions did the model get right?"**

### Formula

```
                    Correct Predictions
Accuracy = ─────────────────────────────────
                 Total Predictions
```

### Example

| | Dogs (Actual) | Cats (Actual) | Total |
|---|---|---|---|
| Predicted as Dog | 45 ✅ | 10 ❌ | 55 |
| Predicted as Cat | 5 ❌ | 40 ✅ | 45 |
| **Total** | 50 | 50 | **100** |

- Correct predictions: 45 + 40 = **85**
- Total predictions: **100**
- **Accuracy = 85 / 100 = 85%**

### When Accuracy Works Well

Accuracy is a great metric when classes are **well-balanced** — meaning you have roughly equal numbers of each class in your dataset.

In our example: 50 dog images and 50 cat images = well-balanced.

---

## The Unbalanced Class Problem

### Why Accuracy Can Be Misleading

Now imagine a **different** test set:
- **99 dog images** and only **1 cat image**

If the model simply **always predicts "Dog"** no matter what it sees:

| Prediction | Correct? |
|-----------|----------|
| 99 dogs predicted as Dog | ✅ (99 correct) |
| 1 cat predicted as Dog | ❌ (1 wrong) |

**Accuracy = 99 / 100 = 99%** 🎉

But wait — this model is **terrible!** It can't identify a single cat. It just blindly says "Dog" every time. Yet accuracy says it's 99% correct.

**This is why accuracy alone is not enough when classes are unbalanced.**

### Real-World Example: Fraud Detection

In credit card transactions:
- 99.9% of transactions are **legitimate**
- 0.1% of transactions are **fraudulent**

A model that always says "Legitimate" gets **99.9% accuracy** but catches **zero fraud**. Useless!

> **Takeaway:** When classes are unbalanced, you need **Precision** and **Recall** to understand the full picture.

---

## True Positives, False Positives, True Negatives, False Negatives

Before we define Precision and Recall, we need to understand these four building blocks. Let's use a **disease diagnosis** example — it's the most intuitive.

### Setup

- A patient takes a blood test
- Our ML model predicts: **"Disease Present"** (Positive) or **"No Disease"** (Negative)
- We compare to the **actual truth** (confirmed by further testing)

### The Four Outcomes

```
                        ACTUAL CONDITION
                 ┌──────────────┬──────────────┐
                 │  Has Disease │ No Disease   │
                 │  (Positive)  │ (Negative)   │
    ┌────────────┼──────────────┼──────────────┤
    │ Predicted  │     TRUE     │    FALSE     │
M   │ Positive   │   POSITIVE   │   POSITIVE   │
O   │ (Disease)  │     (TP)     │     (FP)     │
D   ├────────────┼──────────────┼──────────────┤
E   │ Predicted  │    FALSE     │     TRUE     │
L   │ Negative   │   NEGATIVE   │   NEGATIVE   │
    │(No Disease)│     (FN)     │     (TN)     │
    └────────────┴──────────────┴──────────────┘
```

### Detailed Explanations with Examples

---

### ✅ True Positive (TP) — Correctly identified as positive

> **The model said "YES, disease present" and the patient ACTUALLY HAS the disease.**

**Example:** 
- Rahul takes a blood test for diabetes
- The model predicts: **"Diabetes present"** ✅
- Actual result: Rahul **does have diabetes** ✅
- **This is a True Positive** — the model was RIGHT about a POSITIVE case

**Memory trick:** "True" = the prediction was correct. "Positive" = the model said positive.

---

### ✅ True Negative (TN) — Correctly identified as negative

> **The model said "NO, disease not present" and the patient ACTUALLY DOES NOT have the disease.**

**Example:**
- Priya takes a blood test for diabetes
- The model predicts: **"No diabetes"** ✅
- Actual result: Priya **does not have diabetes** ✅
- **This is a True Negative** — the model was RIGHT about a NEGATIVE case

**Memory trick:** "True" = correct prediction. "Negative" = the model said negative.

---

### ❌ False Positive (FP) — Incorrectly identified as positive (Type I Error)

> **The model said "YES, disease present" but the patient DOES NOT actually have the disease.**

**Example:**
- Amit takes a blood test for diabetes
- The model predicts: **"Diabetes present"** ❌
- Actual result: Amit **does NOT have diabetes**
- **This is a False Positive** — the model FALSELY said it was POSITIVE

**Also called:** Type I Error, "False Alarm"

**Real-world impact:** Amit now has to go through additional expensive/invasive tests unnecessarily. Causes **anxiety and wasted resources**, but at least the disease won't be missed.

**Memory trick:** "False" = the prediction was wrong. "Positive" = the model said positive (but it shouldn't have).

---

### ❌ False Negative (FN) — Incorrectly identified as negative (Type II Error)

> **The model said "NO, disease not present" but the patient ACTUALLY HAS the disease.**

**Example:**
- Sneha takes a blood test for diabetes
- The model predicts: **"No diabetes"** ❌
- Actual result: Sneha **DOES have diabetes**
- **This is a False Negative** — the model FALSELY said it was NEGATIVE

**Also called:** Type II Error, "Missed Detection"

**Real-world impact:** This is the **most dangerous** error in medical diagnosis! Sneha walks away thinking she's healthy, but she actually has a disease that goes untreated. This can have **life-threatening consequences**.

**Memory trick:** "False" = the prediction was wrong. "Negative" = the model said negative (but it shouldn't have).

---

### Summary Table with Emoji Cheat Sheet

| Outcome | Model Says | Reality | Correct? | Example (Disease) |
|---------|-----------|---------|----------|-------------------|
| **True Positive (TP)** ✅ | Positive | Positive | Yes | "Has disease" → Actually has disease |
| **True Negative (TN)** ✅ | Negative | Negative | Yes | "No disease" → Actually no disease |
| **False Positive (FP)** ❌ | Positive | Negative | No | "Has disease" → Actually healthy (false alarm) |
| **False Negative (FN)** ❌ | Negative | Positive | No | "No disease" → Actually has disease (missed!) |

### Another Example: Spam Email Detection

| Outcome | What Happens | Impact |
|---------|-------------|--------|
| **TP** | Spam email correctly sent to spam folder | Great! Spam caught |
| **TN** | Legitimate email correctly stays in inbox | Great! Important email received |
| **FP** | Legitimate email wrongly sent to spam folder | Bad! You might miss an important email |
| **FN** | Spam email wrongly stays in inbox | Annoying! Spam clutters your inbox |

---

## Precision

### Definition

> **Precision** = Of all the items the model **predicted as positive**, how many were **actually positive**?

### Formula

```
                     True Positives (TP)
Precision = ─────────────────────────────────────
              True Positives (TP) + False Positives (FP)
```

### Intuition

Precision answers: **"When the model says 'positive,' how often is it right?"**

### Example: Disease Diagnosis

Our model tested 1,000 patients and predicted 100 as having the disease:
- 80 of those 100 actually had the disease (TP = 80)
- 20 of those 100 were healthy (FP = 20)

```
Precision = 80 / (80 + 20) = 80 / 100 = 0.80 = 80%
```

**Interpretation:** When the model says "disease present," it's correct 80% of the time.

### When Precision Matters Most

Precision is critical when **false positives are costly**:

| Scenario | Why FP is Costly |
|----------|-----------------|
| **Spam filter** | Marking a legitimate email as spam means you miss important messages |
| **Criminal justice** | Wrongly convicting an innocent person |
| **Ad targeting** | Showing irrelevant ads wastes marketing budget |

---

## Recall (Sensitivity)

### Definition

> **Recall** = Of all the items that were **actually positive**, how many did the model **correctly identify**?

### Formula

```
                    True Positives (TP)
Recall = ──────────────────────────────────────
           True Positives (TP) + False Negatives (FN)
```

### Intuition

Recall answers: **"Of all the actual positive cases, how many did the model find?"**

### Example: Disease Diagnosis

In reality, 120 patients out of 1,000 actually had the disease:
- The model correctly identified 80 of them (TP = 80)
- The model missed 40 of them (FN = 40)

```
Recall = 80 / (80 + 40) = 80 / 120 = 0.667 = 66.7%
```

**Interpretation:** The model found 66.7% of all actual disease cases. It missed 33.3% of sick patients.

### When Recall Matters Most

Recall is critical when **false negatives are costly**:

| Scenario | Why FN is Costly |
|----------|-----------------|
| **Disease diagnosis** | Missing a sick patient means they don't get treatment |
| **Fraud detection** | Missing a fraudulent transaction means financial loss |
| **Airport security** | Missing a dangerous item can have catastrophic consequences |

---

## The Precision-Recall Trade-Off

In most real-world scenarios, **improving precision decreases recall** and vice versa. You can't maximize both simultaneously.

### Visualizing the Trade-Off

```
High Precision, Low Recall:
  "I only flag things I'm VERY sure about"
  → Fewer false alarms, but misses many real cases

High Recall, Low Precision:
  "I flag EVERYTHING that might be positive"
  → Catches almost every real case, but many false alarms

          Precision ◄──── Trade-Off ────► Recall
          (Be precise)                    (Find everything)
```

### Example: Airport Security Scanner

**High Precision Setting:**
- Only flags items it's 99% sure are dangerous
- Very few innocent passengers get stopped (low FP)
- But might miss some cleverly hidden weapons (high FN)

**High Recall Setting:**
- Flags anything even remotely suspicious
- Catches virtually every dangerous item (low FN)
- But many innocent passengers get flagged too (high FP)

For airport security, you'd choose **high recall** — it's better to stop 100 innocent people than to miss 1 weapon.

---

## F1-Score

### Definition

> **F1-Score** is the **harmonic mean** of Precision and Recall, combining both into a single metric.

### Formula

```
                   2 × Precision × Recall
F1-Score = ─────────────────────────────────
                 Precision + Recall
```

### Why Harmonic Mean (Not Simple Average)?

The harmonic mean **punishes extreme values**. Here's why this matters:

| Precision | Recall | Simple Average | F1-Score (Harmonic Mean) |
|-----------|--------|---------------|-------------------------|
| 1.0 | 0.0 | **0.50** | **0.00** |
| 0.9 | 0.1 | **0.50** | **0.18** |
| 0.5 | 0.5 | **0.50** | **0.50** |
| 0.8 | 0.8 | **0.80** | **0.80** |
| 1.0 | 1.0 | **1.00** | **1.00** |

Notice:
- When Precision = 1.0 and Recall = 0.0, the simple average says 0.50 (seems okay!), but F1-Score correctly says **0.00** (this model is useless — it has zero recall!)
- F1-Score only gives a high value when **both** Precision and Recall are reasonably high

### Example Calculation

Given: Precision = 0.80, Recall = 0.667

```
F1 = 2 × 0.80 × 0.667 / (0.80 + 0.667)
   = 2 × 0.5336 / 1.467
   = 1.0672 / 1.467
   = 0.727 (72.7%)
```

---

## When to Use Which Metric

| Metric | Best Used When... | Example |
|--------|------------------|---------|
| **Accuracy** | Classes are **balanced** | Dog vs Cat with equal images |
| **Precision** | **False positives** are expensive | Spam filter (don't lose important emails) |
| **Recall** | **False negatives** are expensive | Disease diagnosis (don't miss sick patients) |
| **F1-Score** | You need a **balance** between Precision and Recall | When both FP and FN matter |

---

## Context Matters: The Disease Diagnosis Example

This is a powerful example from the lecture that ties everything together.

### Scenario: Prostate Cancer Screening

A hospital wants to use an ML model as a **quick diagnostic tool** (e.g., urine test) before deciding if a patient should undergo a more invasive biopsy.

### Key Considerations

**1. Are classes balanced?**
No. Most people in the general population **do not** have prostate cancer. This is an **unbalanced class** situation.

**2. What's at stake?**
A person's life. The stakes are **extremely high**.

**3. Which errors are worse?**

| Error Type | What Happens | Severity |
|-----------|-------------|----------|
| **False Positive** | Healthy person gets told they might have cancer → goes for a biopsy → biopsy confirms no cancer | Stressful and costly, but **not fatal** |
| **False Negative** | Person WITH cancer is told they're healthy → goes home → cancer goes untreated | **Potentially fatal** |

### Decision: Minimize False Negatives (Maximize Recall)

In this context, **False Negatives are far worse than False Positives**. We'd rather:
- ✅ Send 50 healthy people for unnecessary biopsies (False Positives — stressful but survivable)
- ❌ Than miss 1 cancer patient and tell them they're fine (False Negative — potentially deadly)

```
Goal: MINIMIZE False Negatives
      ─────────────────────────
      This means we MAXIMIZE RECALL
      (catch as many true positive cases as possible)

Trade-off: This will INCREASE False Positives
           (some healthy people get flagged)
           → But they'll find out they're healthy after biopsy
```

### The Bottom Line

> **There is no universal "good" accuracy, precision, or recall.** It always depends on:
> - The **domain** (healthcare vs. advertising vs. security)
> - The **cost of errors** (false positive vs. false negative)
> - The **balance of classes** in your data
> - The **stakes** involved
> 
> Machine learning is **not performed in a vacuum** — always collaborate with domain experts (doctors, financial analysts, engineers) to decide what metrics matter most.

---

> **Next up:** [The Confusion Matrix — A Deep Dive](./02-confusion-matrix.md)
