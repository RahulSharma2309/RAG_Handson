# 07 — Vector Magnitude and Projections

**Source:** Math Foundation Bootcamp — Krish Naik (Udemy). Comprehensive lecture notes.

---

## 1. Vector Magnitude (Length)

**Definition:** The **magnitude** (or **length**) of a vector is the distance from the origin to the point represented by the vector.

**Formula (Pythagorean theorem in n dimensions):**

‖x‖ = √(x₁² + x₂² + … + xₙ²)

For a 2D vector [x₁, x₂]: ‖x‖ = √(x₁² + x₂²).

**Worked example:** a = [2, 3]

- ‖a‖ = √(2² + 3²) = √(4 + 9) = √13 ≈ 3.606

ASCII diagram — vector [2, 3] with right triangle from origin:

```
         y
         |
         |     • (2, 3)
         |    /|
         |   / | 3
         |  /  |
         | /   |
         |/    +---- 2 ---->
    -----+-----+------------ x
         O    |
         origin

    ‖a‖ = hypotenuse = √(2² + 3²) = √13
```

The same idea generalizes to any dimension: 3D, 500D, etc.

- 3D: ‖[x, y, z]‖ = √(x² + y² + z²)
- n-D: ‖x‖ = √(x₁² + x₂² + … + xₙ²)

**Another example (3D):** b = [1, 0, 0] → ‖b‖ = √(1 + 0 + 0) = 1 (already a unit vector).

**Example (4D):** c = [1, 1, 1, 1] → ‖c‖ = √(1+1+1+1) = √4 = 2.

---

## 2. Unit Vectors

**Definition:** A **unit vector** is a vector with magnitude exactly 1.

**Notation:** û (u-hat), or sometimes e with a subscript.

**Formula:** To turn a non-zero vector v into a unit vector in the same direction:

û = (1 / ‖v‖) × v

So each component of v is divided by ‖v‖.

**Worked example:** v = [1, 2, 0]

- ‖v‖ = √(1² + 2² + 0²) = √5
- û = (1/√5) × [1, 2, 0] = [1/√5, 2/√5, 0]

**Verify:** ‖û‖ = √((1/√5)² + (2/√5)² + 0²) = √(1/5 + 4/5 + 0) = √1 = 1 ✓

**Standard unit vectors (2D):**

- î = [1, 0] — along x-axis
- ĵ = [0, 1] — along y-axis

Any 2D vector can be expressed as a combination: e.g. [3, 3] = 3î + 3ĵ.

**Application: Normalization**

Converting vectors to unit vectors (normalization) puts them all on the same scale.

- Data features often have different magnitudes (e.g. age 18–80, weight 50–120).
- Normalizing to unit vectors (or at least same scale) improves ML optimization speed and convergence.
- Many algorithms (e.g. k-NN, gradient descent) behave better when features are on a common scale.

**3D standard unit vectors:** î = [1,0,0], ĵ = [0,1,0], k̂ = [0,0,1]. Any 3D vector [a,b,c] = aî + bĵ + ck̂.

---

## 3. Vector Projections

**Intuition:** Imagine shining a light perpendicular to a line L; the **projection** of a vector x onto L is the “shadow” of x on L.

**Key property:** The line from the tip of x down to the projection point is **perpendicular** to L. So the “error” vector (x minus its projection) is orthogonal to the line L.

**Perpendicular vectors:** Two vectors a and b are perpendicular (orthogonal) when their dot product is 0: a · b = 0.

Example: a = [1, 2], b = [-2, 1] → a·b = 1×(-2) + 2×1 = -2 + 2 = 0 → perpendicular ✓

ASCII diagram — projection of x onto line L (direction v):

```
         x
         |
         | *
         |/|
         / |
        /  | perpendicular
       /   | (shadow line)
      *----+-------------- L (direction v)
     /     |
    /  proj_L(x) = shadow of x on L
   /
  O (origin)
```

**Important:** The line L must pass through the origin for this formula. We project onto the line through the origin in the direction of v.

**Projection formula (onto line through origin with direction v):**

proj_L(x) = [(x · v) / (v · v)] × v

- x · v = dot product of x and direction vector v (gives a scalar).
- v · v = ‖v‖² (dot product of v with itself).
- Divide the scalar (x·v)/(v·v) and multiply the vector v to get the projected vector.

**Full worked example:**

- Line L defined by direction v = [2, 1]
- Vector x = [2, 3]
- x · v = 2×2 + 3×1 = 4 + 3 = 7
- v · v = 2×2 + 1×1 = 4 + 1 = 5
- proj_L(x) = (7/5) × [2, 1] = [14/5, 7/5] = [2.8, 1.4]

ASCII coordinate diagram:

```
    y
    |
    |     • x = [2, 3]
    |    /
    |   /
    |  /  proj = [2.8, 1.4]
    | /  *
    |/  /
    *--+---------------- L (v = [2,1])
    | /
    |/
    +------------------------ x
    O
```

**Where projections are used:**

- **PCA:** Project data onto principal component directions to reduce dimension.
- **Linear regression:** The least-squares solution projects the target vector onto the column space of the design matrix.
- **Orthogonalization:** The Gram–Schmidt process builds orthogonal bases using repeated projections.

**Optional: length of the projection (scalar).** The scalar (x·v)/(v·v) tells you how far along v the projection goes (in “v-units”). If v is a unit vector, then the length of the projection is just |x·v|.

**Second example (quick check):** x = [1, 0], v = [1, 1]. Then x·v = 1, v·v = 2, so proj = (1/2)[1,1] = [0.5, 0.5]. The projection of the x-axis unit vector onto the 45° line is halfway along that line, as expected.

---

## 4. Key Takeaways

| Topic | Takeaway |
|-------|----------|
| Magnitude ‖x‖ | ‖x‖ = √(x₁² + x₂² + … + xₙ²); distance from origin. |
| Unit vector | Vector with ‖û‖ = 1; û = (1/‖v‖)×v. |
| Normalization | Scale vector to unit length; same direction, length 1. |
| Standard unit vectors | î = [1,0], ĵ = [0,1] in 2D; any vector = combination of these. |
| Projection onto line L | proj_L(x) = [(x·v)/(v·v)]×v, with v as direction of L. |
| Perpendicular | a · b = 0 means a and b are orthogonal. |
| Applications | PCA (project onto PCs), linear regression (project onto column space), Gram–Schmidt. |

| Magnitude properties | ‖cx‖ = |c|·‖x‖; ‖x + y‖ ≤ ‖x‖ + ‖y‖ (triangle inequality). |
| Projection formula | proj_L(x) = [(x·v)/(v·v)]×v; requires v ≠ 0. |

| Dot product and norm | ‖x‖² = x·x; so v·v = ‖v‖² in the projection formula. |

**Reminder:** When you normalize a vector, you keep its direction and set length to 1. When you project, you get a vector along the line L that is the “shadow” of x; its length can be less than or equal to ‖x‖ (equal only when x is already along L).

---

## 5. Python Quick Check

You can verify magnitude, unit vectors, and projection in Python as follows.

**Magnitude and unit vector:**

```python
import numpy as np
v = np.array([1, 2, 0])
mag = np.linalg.norm(v)       # sqrt(1+4+0) = sqrt(5)
u_hat = v / mag               # unit vector
print(np.linalg.norm(u_hat)) # should be 1.0
```

**Projection of x onto v:**

```python
x = np.array([2, 3])
v = np.array([2, 1])
scalar = np.dot(x, v) / np.dot(v, v)   # (x·v)/(v·v)
proj = scalar * v                      # [(x·v)/(v·v)] * v
print(proj)                            # [2.8, 1.4]
```

**Dot product and perpendicular check:**

```python
a = np.array([1, 2])
b = np.array([-2, 1])
print(np.dot(a, b))  # 0 → perpendicular
```

**Magnitude and unit vector (2D):**

```python
a = np.array([2, 3])
mag_a = np.linalg.norm(a)   # sqrt(13)
u = a / mag_a
print(u)                    # [2/√13, 3/√13]
print(np.linalg.norm(u))   # 1.0
```

**Projection (reusable pattern):**

```python
def project_onto(x, v):
    return (np.dot(x, v) / np.dot(v, v)) * v
x = np.array([2, 3])
v = np.array([2, 1])
print(project_onto(x, v))   # [2.8, 1.4]
```

**Check projection length (when v is unit vector):**

```python
v_unit = v / np.linalg.norm(v)
proj_len = np.dot(x, v_unit)   # length of projection when v is unit
print(proj_len)                # scalar
```

**Summary:** Magnitude is length (Pythagoras in n-D). Unit vectors have length 1 (divide by ‖v‖). Projection onto line with direction v: [(x·v)/(v·v)]×v — used in PCA and linear regression. In Python: `np.linalg.norm(v)` for magnitude, `v/norm(v)` for unit vector, `(np.dot(x,v)/np.dot(v,v))*v` for projection.

---

**Navigation:** [Previous → 06](06-functions-and-transformations.md) | [Next → 08](08-matrix-basics.md)
