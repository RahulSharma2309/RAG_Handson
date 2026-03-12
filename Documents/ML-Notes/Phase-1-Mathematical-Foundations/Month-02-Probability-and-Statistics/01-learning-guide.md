# Month 2 — Probability & Statistics for Machine Learning

**Duration:** 4 weeks  
**Phase:** Mathematical Foundations

---

## Table of Contents

1. [Primary & Supplementary Resources](#primary--supplementary-resources)
2. [Learning Objectives for the Month](#learning-objectives-for-the-month)
3. [Topic Breakdown with ML Relevance](#topic-breakdown-with-ml-relevance)
4. [Weekly Plan (Week 1–4)](#weekly-plan-week-14)
5. [Key Formulas Reference](#key-formulas-reference)
6. [Practice Exercises (Python-based)](#practice-exercises-python-based)
7. [Mini-Project: Customer Churn Probability Estimator](#mini-project-customer-churn-probability-estimator)
8. [Self-Check Questions](#self-check-questions)
9. [My Notes (Placeholder)](#my-notes-placeholder)

---

## Primary & Supplementary Resources

| Resource | Type | Link / Location | When to Use |
|----------|------|-----------------|-------------|
| **Mathematics for Machine Learning: Probability & Statistics** | Course | [Coursera — Imperial College London](https://www.coursera.org/learn/probability-statistics-machine-learning) | Primary: follow module-by-module; complete quizzes and assignments |
| **StatQuest with Josh Starmer** | YouTube | Search "StatQuest" | Intuition for MLE, distributions, hypothesis testing |
| **Khan Academy — Probability & Statistics** | Video + exercises | Khan Academy website | Fill gaps: probability rules, random variables, basic inference |

**Suggested flow:** Watch StatQuest for intuition on a topic (e.g., MLE, Bayes), then do the corresponding Imperial module, then implement the Python exercises.

---

## Learning Objectives for the Month

By the end of Month 2, you should be able to:

- Use **probability axioms** and **conditional probability** to reason about uncertain events (e.g., model confidence).
- Apply **Bayes’ theorem** and explain its role in Naive Bayes, spam filters, and Bayesian inference.
- Define **random variables** (discrete and continuous) and **probability distributions** (Bernoulli, Binomial, Gaussian, Poisson) and say how they model data and noise.
- Compute **expectation**, **variance**, and **standard deviation** and interpret them for model predictions.
- Use **covariance** and **correlation** to describe feature relationships and multicollinearity.
- Derive and implement **Maximum Likelihood Estimation (MLE)** for simple models and state how it relates to “how models learn parameters.”
- Interpret **hypothesis tests** and **confidence intervals** in the context of A/B testing and model comparison.
- Explain the **bias–variance tradeoff** and connect it to underfitting vs overfitting.

---

## Topic Breakdown with ML Relevance

### 1. Probability basics (sample space, events, axioms)

| Concept | Definition / Intuition | ML Relevance |
|---------|------------------------|---------------|
| **Sample space** | Set of all possible outcomes | **Data space:** all possible inputs/outputs; defining what we’re modeling. |
| **Event** | Subset of sample space | “Model predicts class 1,” “error &gt; 0.5,” “user churns.” |
| **Axioms** | `P(Ω) = 1`, `P(A) ≥ 0`, `P(A ∪ B) = P(A) + P(B)` for disjoint A, B | Foundation for all probabilistic reasoning; model outputs as probabilities (e.g., softmax). |

**Why it matters for ML:** Models often output probabilities (e.g., P(spam|email)). You need a clear notion of events and probability to interpret and evaluate these outputs.

---

### 2. Conditional Probability & Independence

| Concept | Definition / Intuition | ML Relevance |
|---------|------------------------|---------------|
| **Conditional probability** | `P(A|B) = P(A ∩ B) / P(B)` | Probability of label given features: P(Y|X). |
| **Independence** | `P(A ∩ B) = P(A)P(B)` or `P(A|B) = P(A)` | **Naive Bayes:** assumes features are independent given the class; simplifies P(X|Y). |

**Why it matters for ML:** Classification is often P(class|features). Naive Bayes relies on conditional probability and (conditional) independence assumptions.

---

### 3. Bayes’ Theorem

| Concept | Definition / Intuition | ML Relevance |
|---------|------------------------|---------------|
| **Bayes’ theorem** | `P(A|B) = P(B|A)·P(A) / P(B)` | **Spam filters:** P(spam|words). **Medical diagnosis:** P(disease|test). **Bayesian inference:** update prior P(θ) with likelihood P(D|θ). |

**Why it matters for ML:** Naive Bayes classifiers, Bayesian networks, and Bayesian optimization all use Bayes’ theorem. It’s the backbone of “update belief given evidence.”

---

### 4. Random Variables (discrete & continuous)

| Concept | Definition / Intuition | ML Relevance |
|---------|------------------------|---------------|
| **Discrete RV** | Takes countable values; PMF p(x) | Labels, counts (e.g., number of clicks). |
| **Continuous RV** | Takes values in an interval; PDF f(x), `P(a ≤ X ≤ b) = ∫ₐᵇ f(x) dx` | Real-valued targets, errors, weights; Gaussian noise. |

**Why it matters for ML:** Inputs and outputs are modeled as random variables; loss functions and likelihoods depend on whether we assume discrete or continuous distributions.

---

### 5. Probability Distributions (Bernoulli, Binomial, Gaussian, Poisson)

| Distribution | Use case | ML Relevance |
|--------------|----------|---------------|
| **Bernoulli** | Single binary trial; `P(X=1) = p` | Binary classification; one data point. |
| **Binomial** | Number of successes in n trials | Counts of successes (e.g., clicks in n impressions). |
| **Gaussian (Normal)** | Bell curve; mean μ, variance σ² | **Noise in regression;** many ML algorithms assume Gaussian errors; central limit theorem. |
| **Poisson** | Counts in fixed interval; rate λ | Event counts (e.g., number of visits per day). |

**Why it matters for ML:** Choosing a distribution (e.g., Bernoulli for binary, Gaussian for regression noise) defines the likelihood and thus the loss (e.g., cross-entropy, MSE).

---

### 6. Expectation, Variance, Standard Deviation

| Concept | Definition / Intuition | ML Relevance |
|---------|------------------------|---------------|
| **Expectation** | `E[X] = Σ x·p(x)` or `∫ x·f(x) dx`; “average” outcome | **Model prediction:** often E[Y|X]; mean of a distribution. |
| **Variance** | `Var(X) = E[(X - E[X])²]`; spread | **Uncertainty of predictions;** regularization. |
| **Standard deviation** | `σ = √Var(X)` | Same units as X; reporting error bars. |

**Why it matters for ML:** We optimize losses that are often expectations (e.g., mean squared error). Variance is key to overfitting and to Bayesian uncertainty.

---

### 7. Covariance & Correlation

| Concept | Definition / Intuition | ML Relevance |
|---------|------------------------|---------------|
| **Covariance** | `Cov(X,Y) = E[(X - E[X])(Y - E[Y])]` | **Feature relationships;** redundant features. |
| **Correlation** | `ρ = Cov(X,Y) / (σ_X σ_Y)`; −1 ≤ ρ ≤ 1 | **Multicollinearity:** high correlation between features can make some models unstable. |

**Why it matters for ML:** Feature selection and interpretation; understanding why some models prefer uncorrelated or regularized features.

---

### 8. Maximum Likelihood Estimation (MLE)

| Concept | Definition / Intuition | ML Relevance |
|---------|------------------------|---------------|
| **Likelihood** | `L(θ) = P(data|θ)`; function of parameters | How well do parameters θ explain the data? |
| **MLE** | `θ̂ = argmax_θ L(θ)` (often maximize log L) | **How models learn parameters:** many estimators (linear regression, logistic regression) are MLE under a chosen distribution. |

**Why it matters for ML:** Training is often “find parameters that maximize likelihood (or minimize negative log-likelihood).” Cross-entropy and MSE can be derived from MLE.

---

### 9. Hypothesis Testing & Confidence Intervals

| Concept | Definition / Intuition | ML Relevance |
|---------|------------------------|---------------|
| **Hypothesis test** | Decide between H₀ and H₁ using p-value or critical region | **A/B testing:** is the new model/UI better? **Model comparison:** is difference in accuracy significant? |
| **Confidence interval** | Interval that contains true parameter with a given probability (e.g., 95%) | Reporting uncertainty of metrics (e.g., accuracy, AUC). |

**Why it matters for ML:** You need to know whether an improvement is real or due to chance, and how to report metrics with uncertainty.

---

### 10. Bias–Variance Tradeoff

| Concept | Definition / Intuition | ML Relevance |
|---------|------------------------|---------------|
| **Bias** | Error due to model being too simple (systematic error) | **Underfitting:** high bias. |
| **Variance** | Error due to model being too sensitive to the training set | **Overfitting:** high variance. |
| **Tradeoff** | More complex model ⇒ lower bias, higher variance (and vice versa) | Choosing model complexity; regularization. |

**Why it matters for ML:** Explains underfitting vs overfitting and guides choice of model complexity and regularization.

---

## Weekly Plan (Week 1–4)

### Week 1: Probability basics, conditional probability, Bayes

| Day | Topic | Activities |
|-----|------|------------|
| 1–2 | Sample space, events, axioms; basic rules (addition, complement) | Coursera Week 1; Khan Academy probability |
| 3 | Conditional probability; independence | Coursera; tree diagrams; “given B, what’s P(A)?” |
| 4 | Bayes’ theorem; prior, likelihood, posterior | StatQuest “Bayes”; medical/test example |
| 5 | Naive Bayes idea: P(class|features) with independence | Coursera quiz; small Bayes calculation by hand |

---

### Week 2: Random variables, distributions, expectation, variance

| Day | Topic | Activities |
|-----|------|------------|
| 1–2 | Random variables (discrete and continuous); PMF, PDF, CDF | Coursera; define RV for “number of clicks” |
| 3 | Bernoulli, Binomial, Gaussian, Poisson (when to use each) | StatQuest “Probability distributions”; plot in Python |
| 4 | Expectation, variance, standard deviation; rules (e.g., `Var(aX+b) = a² Var(X)`) | Coursera; compute for Bernoulli and Gaussian |
| 5 | Covariance and correlation; interpret in a small dataset | NumPy: `np.cov`, correlation matrix; link to multicollinearity |

---

### Week 3: MLE, hypothesis testing, confidence intervals

| Day | Topic | Activities |
|-----|------|------------|
| 1–2 | Likelihood; log-likelihood; MLE for Bernoulli and Gaussian | Coursera; StatQuest “Maximum Likelihood”; derive p̂ for Bernoulli |
| 3 | MLE and loss: cross-entropy ↔ Bernoulli MLE; MSE ↔ Gaussian MLE | Derive; implement MLE for mean of Gaussian in Python |
| 4 | Hypothesis testing: H₀, p-value, type I/II error | Coursera; StatQuest “Hypothesis testing” |
| 5 | Confidence intervals; A/B test interpretation | Build 95% CI for a proportion; interpret “difference significant or not” |

---

### Week 4: Bias–variance tradeoff and mini-project

| Day | Topic | Activities |
|-----|------|------------|
| 1 | Bias–variance decomposition; underfitting vs overfitting | Coursera; diagram: complexity vs error |
| 2 | Regularization as variance reduction; model selection | Link to Ridge/Lasso; train/validation split |
| 3–5 | **Mini-project:** Customer Churn Probability Estimator (logistic regression from scratch) | See below; implement sigmoid, gradient, MLE view |

---

## Key Formulas Reference

| Concept | Formula |
|---------|---------|
| **Conditional probability** | `P(A|B) = P(A ∩ B) / P(B)` |
| **Bayes’ theorem** | `P(A|B) = P(B|A)·P(A) / P(B)` |
| **Independence** | `P(A ∩ B) = P(A)·P(B)` |
| **Expectation** | `E[X] = Σ x·p(x)` or `∫ x·f(x) dx` |
| **Variance** | `Var(X) = E[X²] - (E[X])²` |
| **Gaussian** | `f(x) = (1 / (σ√(2π))) × e^(-(x-μ)²/(2σ²))` |
| **Covariance** | `Cov(X,Y) = E[XY] - E[X]E[Y]` |
| **Correlation** | `ρ_{X,Y} = Cov(X,Y) / (σ_X σ_Y)` |
| **MLE (Bernoulli)** | `p̂ = (number of successes) / n` |
| **MLE (Gaussian mean)** | `μ̂ = x̄ = (1/n) Σᵢ xᵢ` |
| **Logistic (sigmoid)** | `σ(z) = 1 / (1 + e⁻ᶻ)`; `P(Y=1|X) = σ(wᵀx)` |

---

## Practice Exercises (Python-based)

### Exercise 1: Bayes’ theorem — spam filter

```python
# P(Spam) = 0.3, P(Word|Spam) = 0.6, P(Word|Not Spam) = 0.1
# Find P(Spam|Word)
P_Spam = 0.3
P_Word_given_Spam = 0.6
P_Word_given_NotSpam = 0.1
P_NotSpam = 0.7

P_Word = P_Word_given_Spam * P_Spam + P_Word_given_NotSpam * P_NotSpam
P_Spam_given_Word = (P_Word_given_Spam * P_Spam) / P_Word
print("P(Spam|Word) =", round(P_Spam_given_Word, 3))
```

### Exercise 2: Distributions and expectation/variance

```python
import numpy as np
from scipy import stats

# Bernoulli p=0.4
p = 0.4
print("Bernoulli: E[X] =", p, ", Var(X) =", p * (1 - p))

# Sample from Gaussian, compute sample mean and variance
X = np.random.normal(2, 3, size=1000)
print("Gaussian sample: mean =", np.mean(X), ", std =", np.std(X))
```

### Exercise 3: Correlation and covariance

```python
import numpy as np

# Two features with high correlation
x1 = np.random.randn(100)
x2 = 0.9 * x1 + 0.1 * np.random.randn(100)  # x2 ≈ 0.9*x1 + noise

corr = np.corrcoef(x1, x2)[0, 1]
print("Correlation(x1, x2) =", round(corr, 3))
```

### Exercise 4: MLE for Bernoulli

```python
# Simulate n flips with true p=0.6
np.random.seed(42)
n = 100
data = np.random.binomial(1, 0.6, size=n)

# MLE for p is sample mean
p_hat = np.mean(data)
print("MLE p_hat =", round(p_hat, 3))
```

---

## Mini-Project: Customer Churn Probability Estimator

**Goal:** Implement a simple **logistic regression from scratch** (no sklearn) to estimate P(churn|features) and interpret it as a probability model (MLE view).

**Steps:**

1. **Data:** Use a small churn dataset (e.g., 2–4 features: tenure, monthly charges, contract type encoded). Or create synthetic: `X` (features), `y` (0/1 churn).
2. **Model:** `P(Y=1|X) = σ(wᵀx + b)` where `σ(z) = 1 / (1 + e⁻ᶻ)`.
3. **Loss:** Binary cross-entropy (negative log-likelihood under Bernoulli):  
   `−Σᵢ [ yᵢ log pᵢ + (1−yᵢ) log(1−pᵢ) ]`.
4. **Optimization:** Gradient descent on the loss with respect to **w** and b. Derive `∂L/∂wⱼ` (chain rule: loss → p → z).
5. **Training:** Loop: compute probabilities, loss, gradients; update **w** and b.
6. **Output:** For a few test customers, output P(churn) and classify (e.g., threshold 0.5).

**Success criteria:** You implement sigmoid, loss, and gradient by hand; you can state that this is MLE for Bernoulli with linear model for log(p/(1−p)).

**Optional:** Plot loss vs iteration; plot decision boundary in 2D if you have 2 features.

---

## Self-Check Questions

1. Write Bayes’ theorem and name each term (prior, likelihood, posterior, evidence).
2. When is Naive Bayes “naive”? What independence assumption does it make?
3. Which distribution would you use to model (a) binary click, (b) count of visits per day, (c) continuous prediction error?
4. What is the relationship between MLE for Bernoulli and binary cross-entropy loss?
5. How does the bias–variance tradeoff relate to underfitting and overfitting?
6. Why might high correlation between two features be a problem for some models?

---

## My Notes (Placeholder)

*Use the sections below to add your own notes as you learn. Delete this line when you start.*

### Probability and Bayes
<!-- Your notes here -->


### Random variables and distributions
<!-- Your notes here -->


### MLE and hypothesis testing
<!-- Your notes here -->


### Bias–variance and mini-project
<!-- Your notes here -->
