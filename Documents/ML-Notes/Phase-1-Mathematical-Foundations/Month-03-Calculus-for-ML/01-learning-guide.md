# Month 3 — Calculus & Optimization for Machine Learning

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
7. [Mini-Project: Gradient Descent Visualizer](#mini-project-gradient-descent-visualizer)
8. [Self-Check Questions](#self-check-questions)
9. [My Notes (Placeholder)](#my-notes-placeholder)

---

## Primary & Supplementary Resources

| Resource | Type | Link / Location | When to Use |
|----------|------|-----------------|-------------|
| **Essence of Calculus** | Video playlist | 3Blue1Brown (YouTube) | First pass: derivatives, chain rule, intuition for rate of change |
| **Mathematics for Machine Learning: Multivariate Calculus** | Course | [Coursera — Imperial College London](https://www.coursera.org/learn/multivariate-calculus-machine-learning) | Primary: gradients, chain rule, Jacobian; formalize and practice |
| **3Blue1Brown — Gradient descent** | YouTube | In Calculus or Neural nets playlists | Intuition for “walking downhill” and learning rate |

**Suggested flow:** Watch 3Blue1Brown for a topic (e.g., “Derivative,” “Chain rule”), then complete the corresponding Imperial module, then implement the NumPy examples and mini-project.

---

## Learning Objectives for the Month

By the end of Month 3, you should be able to:

- Interpret the **derivative** as rate of change and relate it to the **rate of change of the loss** with respect to a parameter.
- Compute **partial derivatives** and explain **how each parameter affects the loss**.
- Define the **gradient** and use it as the **direction of steepest ascent**; descent = -∇L.
- Implement **gradient descent** from scratch and explain the role of the **learning rate** (step size).
- Apply the **chain rule** (single and multivariable) and recognize it as the **backbone of backpropagation**.
- Describe **computational graphs** and how frameworks compute gradients (forward pass, backward pass).
- Reason about **multivariate optimization**: stationary points, **convexity**, and **local minima** in the context of loss landscapes.
- Compare **variants**: SGD, mini-batch, momentum, Adam, and when to use them in practice.

---

## Topic Breakdown with ML Relevance

### 1. Derivatives (intuition, rules)

| Concept | Definition / Intuition | ML Relevance |
|---------|------------------------|---------------|
| **Derivative** | `f'(x) = lim[h→0] (f(x+h) - f(x)) / h`; slope of tangent; rate of change | **Loss as function of one weight:** `L(w)`; `dL/dw` tells you how much L changes when you nudge w. |
| **Rules** | Power, product, quotient, chain; `(xⁿ)' = n·xⁿ⁻¹`, `(eˣ)' = eˣ`, `(ln x)' = 1/x` | Used everywhere when deriving gradients (e.g., MSE, cross-entropy). |

**Why it matters for ML:** Training = adjusting parameters to reduce loss. Derivatives tell you *in which direction* and *how strongly* to change each parameter.

---

### 2. Partial Derivatives

| Concept | Definition / Intuition | ML Relevance |
|---------|------------------------|---------------|
| **Partial derivative** | `∂f/∂x`: differentiate w.r.t. x while holding other variables constant | **How each parameter affects loss:** `∂L/∂wⱼ` = contribution of wⱼ to the loss. |
| **Notation** | `∂/∂x` vs `d/dx` when other variables exist | In ML we almost always have many parameters → partials. |

**Why it matters for ML:** A model has many weights. You need the partial derivative of the loss with respect to each weight to update them independently.

---

### 3. The Gradient

| Concept | Definition / Intuition | ML Relevance |
|---------|------------------------|---------------|
| **Gradient** | `∇f = (∂f/∂x₁, ..., ∂f/∂xₙ)ᵀ`; vector of all partials | **Direction of steepest ascent**; magnitude = rate of increase in that direction. |
| **Descent** | `-∇f` is direction of **steepest descent** | We minimize loss → take steps in -∇L. |

**Why it matters for ML:** The gradient ∇L(θ) is the single most important object in optimization: it tells you how to move all parameters at once to decrease the loss fastest.

---

### 4. Gradient Descent Algorithm

| Concept | Definition / Intuition | ML Relevance |
|---------|------------------------|---------------|
| **Update rule** | `θ(t+1) = θ(t) - η · ∇L(θ(t))`; repeat until convergence | **THE core optimization algorithm** for training neural networks and most ML models. |
| **Intuition** | At each step, move a little in the direction that decreases the loss | Same idea in SGD, mini-batch, and advanced optimizers (Adam, etc.). |

**Why it matters for ML:** Almost all model training (linear regression, logistic regression, deep learning) uses some form of gradient-based descent on the loss.

---

### 5. Learning Rate

| Concept | Definition / Intuition | ML Relevance |
|---------|------------------------|---------------|
| **Learning rate η** | Step size: `θ_new = θ - η·∇L` | **Too large:** divergence or oscillation. **Too small:** very slow convergence. |
| **Scheduling** | Decrease η over time (e.g., decay, step decay) | Often used in practice to stabilize and then refine. |

**Why it matters for ML:** Choice of η (and schedule) directly affects training stability and speed. It is one of the most important hyperparameters.

---

### 6. Chain Rule

| Concept | Definition / Intuition | ML Relevance |
|---------|------------------------|---------------|
| **Single variable** | `(f∘g)'(x) = f'(g(x)) · g'(x)` | Composing small derivatives along a path. |
| **Multivariable** | `∂f/∂x = Σₖ (∂f/∂zₖ)(∂zₖ/∂x)` | **Backbone of backpropagation:** loss depends on output, output on hidden layer, hidden on weights → chain rule gives ∂L/∂w. |

**Why it matters for ML:** Neural networks are compositions of many functions. Backpropagation is the efficient application of the chain rule from output back to each parameter.

---

### 7. Computational Graphs

| Concept | Definition / Intuition | ML Relevance |
|---------|------------------------|---------------|
| **Graph** | Nodes = inputs, operations, outputs; edges = data flow | **How frameworks compute gradients:** build graph in forward pass; traverse backward applying chain rule. |
| **Forward / backward** | Forward: compute output and store intermediates. Backward: compute ∂L/∂ for each node | PyTorch and TensorFlow “autograd” do exactly this. |

**Why it matters for ML:** Understanding computational graphs makes autograd and custom gradients less mysterious; you see that it’s “just” chain rule on a graph.

---

### 8. Multivariate Optimization

| Concept | Definition / Intuition | ML Relevance |
|---------|------------------------|---------------|
| **Stationary point** | `∇f = 0` | Candidates for minima (and maxima, saddle points). |
| **Second-order info** | Hessian (matrix of second partials) distinguishes min/max/saddle | Explains curvature of the loss surface; used in some advanced optimizers. |

**Why it matters for ML:** We optimize loss L(θ) over many parameters. Stationary points and curvature determine whether we get a good minimum or get stuck.

---

### 9. Convexity & Local Minima

| Concept | Definition / Intuition | ML Relevance |
|---------|------------------------|---------------|
| **Convex function** | Bowl-shaped; one global minimum; no saddle points | Linear regression (MSE) is convex in w; gradient descent finds global min. |
| **Non-convex** | Many local minima and saddle points | Neural networks: loss is non-convex; we aim for “good” local minima. |

**Why it matters for ML:** Convex problems are “easy” (global convergence); non-convex ones require care with initialization and optimization (hence importance of initialization and optimizers like Adam).

---

### 10. Variants: SGD, Mini-batch, Momentum, Adam

| Variant | Idea | ML Relevance |
|---------|------|---------------|
| **SGD** | One sample per update; ∇L approximated by one example | **Practical optimization:** fast per step; noisy but often generalizes well. |
| **Mini-batch** | Average gradient over a small batch | Balance between speed and stability; default in deep learning. |
| **Momentum** | Accumulate past gradients; smooth updates | Faster convergence; helps escape shallow local minima. |
| **Adam** | Adaptive learning rate per parameter + momentum | **Widely used:** good default for many models. |

**Why it matters for ML:** In practice you rarely use “vanilla” full-batch gradient descent. Understanding these variants helps you choose and tune optimizers.

---

## Weekly Plan (Week 1–4)

### Week 1: Derivatives, partials, gradient, and descent

| Day | Topic | Activities |
|-----|------|------------|
| 1–2 | Derivative as rate of change; rules (power, product, chain for 1D) | 3B1B “Derivative”; differentiate `x²`, `eˣ`, `ln x` by hand |
| 3 | Partial derivatives; gradient vector | Imperial Week 1; compute `∂/∂x`, `∂/∂y` for `f(x,y)=x²y` |
| 4 | Gradient = steepest ascent; -∇L = descent | 3B1B “Partial derivatives”; gradient of a 2D function |
| 5 | Gradient descent: `θ(t+1) = θ(t) - η·∇L`; implement in 1D/2D | Implement GD for a simple `L(w)`; plot trajectory |

---

### Week 2: Chain rule and computational graphs

| Day | Topic | Activities |
|-----|------|------------|
| 1–2 | Chain rule (single and multivariable) | 3B1B “Chain rule”; Imperial Week 2 |
| 3 | Computation graph: forward pass (output), backward pass (gradients) | Draw graph: input → linear → loss; write `∂L/∂w` via chain rule |
| 4 | Jacobian; chain rule as matrix multiplication | Imperial; Jacobian of a small vector function |
| 5 | Backpropagation at a high level | Relate backprop to “chain rule on the graph”; optional: read autograd docs |

---

### Week 3: Learning rate, convexity, variants

| Day | Topic | Activities |
|-----|------|------------|
| 1–2 | Learning rate: too big vs too small; optional scheduling | Try `η = 0.01, 0.1, 1.0` on same problem; plot loss curves |
| 3 | Stationary points; convex vs non-convex; local minima | Plot 2D loss surface; mark GD path; discuss convex (MSE) vs non-convex (NN) |
| 4 | SGD, mini-batch, momentum, Adam (conceptual) | Implement mini-batch GD; compare with full-batch; optional: add momentum |
| 5 | Review and practice | Derive gradient of MSE and cross-entropy; implement one optimizer from scratch |

---

### Week 4: Mini-project and review

| Day | Topic | Activities |
|-----|------|------------|
| 1–2 | **Mini-project:** Gradient Descent Visualizer (see below) | Implement from scratch; animate convergence on 2D loss surface |
| 3 | Tune visualizer: learning rate slider; different surfaces (paraboloid, saddle) | Add at least two loss functions; compare convergence |
| 4 | Phase 1 wrap-up: link calculus to linear algebra (Month 1) and MLE (Month 2) | Summarize: loss from MLE; gradients via chain rule; parameters in ℝⁿ |
| 5 | Self-check and cheat sheet | Redo self-check questions; write one-page “derivatives + GD” summary |

---

## Key Formulas Reference

| Concept | Formula |
|---------|---------|
| **Derivative (limit)** | `f'(x) = lim[h→0] (f(x+h) - f(x)) / h` |
| **Gradient** | `∇f = (∂f/∂x₁, ..., ∂f/∂xₙ)ᵀ` |
| **Gradient descent** | `θ(t+1) = θ(t) - η · ∇L(θ(t))` |
| **Chain rule (1D)** | `(f∘g)'(x) = f'(g(x)) · g'(x)` |
| **Chain rule (multivariable)** | `∂f/∂x = Σₖ (∂f/∂zₖ)(∂zₖ/∂x)` |
| **MSE gradient (one weight)** | `∂/∂w · ½(wx - y)² = (wx - y)x` |
| **Sigmoid derivative** | `σ'(z) = σ(z) · (1 - σ(z))` |
| **Stationary point** | `∇f(θ) = 0` |

---

## Practice Exercises (Python-based)

### Exercise 1: Gradient of a scalar function

```python
import numpy as np

def f(x, y):
    return x**2 + 2*x*y + y**2

# Partial derivatives: df/dx = 2x + 2y, df/dy = 2x + 2y
def gradient_f(x, y):
    df_dx = 2*x + 2*y
    df_dy = 2*x + 2*y
    return np.array([df_dx, df_dy])

# At (1, 1): gradient = (4, 4)
print("∇f(1,1) =", gradient_f(1, 1))
```

### Exercise 2: Gradient descent in 2D

```python
import numpy as np

# Minimize f(x,y) = x^2 + y^2 (min at (0,0))
def f(xy):
    return xy[0]**2 + xy[1]**2
def grad_f(xy):
    return np.array([2*xy[0], 2*xy[1]])

theta = np.array([3.0, 4.0])
eta = 0.1
for step in range(20):
    theta = theta - eta * grad_f(theta)
    if step % 5 == 0:
        print(f"Step {step}: theta = {theta}, f = {f(theta):.4f}")
```

### Exercise 3: MSE gradient and descent for linear regression

```python
import numpy as np

# Data: y ≈ w*x, find w
x = np.array([1.0, 2.0, 3.0])
y = np.array([2.1, 3.9, 6.2])

w = 0.0
eta = 0.01
for epoch in range(100):
    pred = w * x
    loss = np.mean((pred - y)**2) / 2
    grad = np.mean((pred - y) * x)  # d/dw of (1/2)*mean((w*x - y)^2)
    w = w - eta * grad
    if epoch % 20 == 0:
        print(f"Epoch {epoch}: w = {w:.4f}, loss = {loss:.4f}")
```

---

## Mini-Project: Gradient Descent Visualizer

**Goal:** Implement **gradient descent from scratch** and build a **visualizer** that shows the **loss surface** and the **optimization path**, with optional **animation** of convergence.

**Steps:**

1. **Loss surface:** Choose a 2D function (e.g., paraboloid L(w₁,w₂) = w₁² + w₂², or a saddle). Create a grid of (w₁, w₂) and compute L. Plot as a **contour plot** or **surface plot** (e.g., `matplotlib`: `contour`, `contourf`, or `plot_surface`).
2. **Gradient descent:** Implement the update θ(t+1) = θ(t) - η·∇L(θ(t)). Store the sequence of θ (e.g., list of points).
3. **Plot path:** Overlay the sequence of (θ₁, θ₂) on the contour plot (e.g., scatter or line). Mark start and end.
4. **Animate (optional):** Use `matplotlib.animation` or a loop with `plt.pause()` to show the path being drawn step by step (convergence animation).
5. **Learning rate:** Try different η (e.g., 0.01, 0.1, 0.5) and show how too large η causes oscillation or divergence, and too small causes slow convergence.
6. **Optional:** Add a second loss function (e.g., non-convex with two minima) and compare behavior from different initializations.

**Success criteria:** You implement the gradient and the update loop yourself (no high-level optimizer). The visualizer clearly shows the descent path on the loss surface and the effect of learning rate.

**Deliverable:** A script or Jupyter notebook that runs the visualizer and, if possible, saves a short animation (e.g., GIF or MP4) of one run.

---

## Self-Check Questions

1. What is the geometric interpretation of the gradient? Why do we use -∇L for minimization?
2. Write the gradient descent update rule in one line. What is the role of η?
3. Why is the chain rule essential for training neural networks?
4. What is the difference between a convex and a non-convex loss surface? Give one example of each.
5. What is the main advantage of mini-batch GD over full-batch? Over pure SGD?
6. In one sentence, what does a “computational graph” represent, and how does it relate to backpropagation?

---

## My Notes (Placeholder)

*Use the sections below to add your own notes as you learn. Delete this line when you start.*

### Derivatives and gradient
<!-- Your notes here -->


### Chain rule and backprop
<!-- Your notes here -->


### Gradient descent and learning rate
<!-- Your notes here -->


### Convexity and optimizer variants
<!-- Your notes here -->


### Mini-project and takeaways
<!-- Your notes here -->
