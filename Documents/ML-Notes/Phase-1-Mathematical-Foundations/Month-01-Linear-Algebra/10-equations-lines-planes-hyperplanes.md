# 10 — Equations of Lines, Planes, and Hyperplanes

---

## 1. Equation of a Straight Line (2D)

**Standard forms:**
- **Slope-intercept:** y = mx + c
- **General form:** ax + by + c = 0
- **Weights form:** w₁x₁ + w₂x₂ + b = 0

**Equivalence:** From y = mx + c, rewrite as mx - y + c = 0, so a = m, b = -1, c = c. So ax + by + c = 0. Setting w₁ = a, w₂ = b, b (bias) = c gives w₁x₁ + w₂x₂ + b = 0.

**Meaning:**
- **m** = slope (unit change in x → how much y changes).
- **c** = intercept (where the line crosses the y-axis).

**Matrix notation:** wᵀx + b = 0, where w = [w₁, w₂], x = [x₁, x₂].

**ASCII diagram — line with slope and intercept:**

```
    y
    |
    |        /  line: y = mx + c
    |       /   slope = m
    |      /
    |     /
    |    /
    |___/___________  x
    c (intercept)
```

**Special case — line through origin:** b = 0, so **wᵀx = 0**. The line passes through (0, 0).

**Numerical example:** y = 2x + 1 → 2x - y + 1 = 0. So w₁ = 2, w₂ = -1, b = 1. In vector form: w = [2, -1], and the line is the set of points x = [x₁, x₂] such that 2x₁ - x₂ + 1 = 0.

---

## 2. Equation of a 3D Plane

**Equation:** w₁x₁ + w₂x₂ + w₃x₃ + b = 0.

**Matrix notation:** Same idea: **wᵀx + b = 0** with w = [w₁, w₂, w₃], x = [x₁, x₂, x₃].

**ASCII diagram — 3D plane:**

```
         x₃
         |
         |    ____ plane
         |   /
         |  /
         | /
         +-------- x₂
        /
       /
         x₁
```

Any point [x₁, x₂, x₃] satisfying w₁x₁ + w₂x₂ + w₃x₃ + b = 0 lies on the plane. Changing b shifts the plane parallel to itself; w still gives the normal direction.

---

## 3. Hyperplane (n dimensions)

**Equation:** w₁x₁ + w₂x₂ + … + wₙxₙ + b = 0.

**Matrix notation:** **wᵀx + b = 0** — same formula for any number of dimensions.

**What is a hyperplane?**
- In **2D:** a hyperplane is a **line** (1-dimensional).
- In **3D:** a hyperplane is a **plane** (2-dimensional).
- In **nD:** a hyperplane is an **(n-1)-dimensional** surface that splits the space into two half-spaces.

**Half-spaces:** The inequality wᵀx + b > 0 defines one side of the hyperplane; wᵀx + b < 0 defines the other. This is exactly how classifiers assign “positive” vs “negative” class.

---

## 4. The Weight Vector w is Perpendicular to the Hyperplane

**Proof using dot product:** For points x on the hyperplane, wᵀx + b = 0, so wᵀx = -b. For two points x₁, x₂ on the hyperplane, wᵀ(x₁ - x₂) = wᵀx₁ - wᵀx₂ = (-b) - (-b) = 0. So the vector (x₁ - x₂) lying in the hyperplane is orthogonal to w. Thus **w** is perpendicular to every direction in the hyperplane, i.e. **w ⊥ hyperplane**.

Alternatively: wᵀx = ‖w‖ ‖x‖ cos(θ). When we consider the direction of w and a direction in the plane, that dot product is 0, so cos(θ) = 0, so θ = 90° → w is perpendicular to the hyperplane.

**ASCII diagram — w perpendicular to line/plane:**

```
    2D:                          w (weight vector)
    --------> w                    |
         |                        |  perpendicular
         |  line                  |
    -----+-----  hyperplane       +========  hyperplane (line in 2D)
         |                        |
```

This is **critical** for understanding SVM, logistic regression, and linear classifiers: the decision boundary is a hyperplane, and w points in the “positive” direction (direction of the positive class or higher score).

**Distance from a point to the hyperplane:** The signed distance from a point x to the hyperplane wᵀx + b = 0 is proportional to (wᵀx + b) / ‖w‖. SVM maximizes the margin by making this distance as large as possible for the support vectors.

---

## 5. Why This Matters for Machine Learning

- **Linear regression:** Finds the best line (2D) or plane/hyperplane (higher D) that fits the data: **y = wᵀx + b**. Predictions lie on or near this surface.

- **Logistic regression:** Finds a **decision boundary** (hyperplane) that separates classes. Points on one side are predicted class 0, on the other class 1. Equation of the boundary: wᵀx + b = 0.

- **SVM:** Finds the hyperplane with **maximum margin** between the two classes. The same wᵀx + b = 0; the margin is determined by the distance from the boundary to the nearest points.

- **Neural networks:** Each neuron computes **wᵀx + b**, then applies an activation function. So every layer is built from affine (linear + bias) maps and non-linearities.

**ASCII — classification with a decision boundary:**

```
    Class A (○)          |          Class B (●)
         ○               |               ●
      ○    ○             |            ●     ●
         ○    ○    ----- wᵀx + b = 0 -----    ●
              ○          |                  ●
                         |  decision
                         |  boundary (line in 2D)
```

**Summary table — where wᵀx + b appears:**

```
    Model              Role of wᵀx + b
    -----              -----------------
    Linear regression  Prediction (output = wᵀx + b)
    Logistic reg.     Log-odds; boundary where wᵀx + b = 0
    SVM               Decision function; margin from boundary
    Neural net        Pre-activation in each neuron
```

---

## 6. Key Takeaways

- **2D line:** y = mx + c or w₁x₁ + w₂x₂ + b = 0 or wᵀx + b = 0.
- **3D plane / nD hyperplane:** Same form wᵀx + b = 0 with more coordinates.
- **Hyperplane in ℝⁿ** is (n-1)-dimensional; in 2D it’s a line, in 3D it’s a plane.
- **w** is perpendicular to the hyperplane (w ⊥ hyperplane); essential for SVMs and linear classifiers.
- **ML:** Linear regression (fit w,b), logistic regression and SVM (decision boundary wᵀx + b = 0), neural nets (neurons compute wᵀx + b).

---

## 7. Quick Reference

| Object    | Dimension | Equation       | Matrix form   |
|----------|-----------|----------------|----------------|
| Line     | 2D        | ax + by + c = 0| wᵀx + b = 0   |
| Plane    | 3D        | w₁x₁+w₂x₂+w₃x₃+b=0 | wᵀx + b = 0 |
| Hyperplane | nD      | w₁x₁+…+wₙxₙ+b=0   | wᵀx + b = 0   |

- **w** = weight vector (normal to hyperplane).
- **b** = bias (shift; related to distance of hyperplane from origin).
- **w ⊥ hyperplane** → used in margin and distance formulas in SVM and elsewhere.

**Converting between forms (2D):** Given y = mx + c, we have x₂ = mx₁ + c, so -mx₁ + x₂ - c = 0. So in wᵀx + b = 0 we can take w = [-m, 1] and b = -c. Conversely, from w₁x₁ + w₂x₂ + b = 0, if w₂ ≠ 0 we get x₂ = (-w₁/w₂)x₁ - b/w₂, so slope m = -w₁/w₂ and intercept c = -b/w₂.

---

**Navigation:** Previous → [09](09-eigenvalues-and-eigenvectors.md)
