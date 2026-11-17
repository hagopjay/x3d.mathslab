# The Aha Atlas

[Open the lab](../web/) · [Original Mathlab Field Guide](Mathlab-Field-Guide.html) · [Run locally and inspect the project](../README.md)

## Twelve doors into the same mathematical world

Mathematics becomes more useful when you can move between a picture, an equation, a prediction, and a check. This atlas gives you short investigations in that spirit: the visual storytelling of a mathematical animation, with the controls and inspectable calculations of a notebook.

Begin with a question you can answer incorrectly. Write your prediction before moving a control. Change one thing, compare the measured result, then explain the difference. A surprising picture is the beginning of an argument; the equation and its assumptions do the rest.

The suggested levels describe useful preparation, not an age limit. A confident tenth grader can explore a vector field visually; an undergraduate should also derive its flux. Conversely, an advanced student can learn a great deal by explaining a simple secant carefully.

## Choose a route

| Route | Suggested sequence | Preparation | Connecting idea |
|---|---|---|---|
| Rotation becomes sound | [Complex numbers](../web/#complex) → [Fourier circles](../web/#fourier) → [Standing waves](../web/#waves) | Algebra, radians, sine and cosine | Rotations generate oscillations; boundary conditions select their combinations. |
| Local clues become global behavior | [Derivative](../web/#derivative) → [Taylor approximation](../web/#taylor) → [Integration](../web/#integral) → [Vector fields](../web/#vector_field) | Functions and slopes; add calculus as you go | Local measurements can assemble a global prediction, with conditions and error estimates. |
| Geometry becomes inference | [Matrices](../web/#linear) → [Least squares](../web/#least_squares) → [Gradient descent](../web/#gradient) → [Probability](../web/#probability) → [Lorenz dynamics](../web/#lorenz) | Vectors, basic probability; calculus helps later | Fitting, uncertainty, optimization, and numerical reliability ask different questions. |

Spend one session on each arrow rather than racing to the final lesson. The routes overlap deliberately: complex multiplication is a matrix, a standing wave is a Fourier mode, and least squares is both geometry and an optimization problem.

## A useful twenty-minute rhythm

1. **Predict, 2 minutes.** Draw a rough result and name the quantity you expect to stay fixed.
2. **Manipulate, 5 minutes.** Change one control. Try a revealing preset, then make your own nearby example.
3. **Explain, 6 minutes.** Translate one visible feature into an equation. Say why that equation applies.
4. **Transfer, 5 minutes.** Solve a related case before checking the answer below.
5. **Keep, 2 minutes.** Save a lesson card with your prediction. Record what changed your mind.

Use the on-screen legend for colors and the measurements for quantities. Orbit a genuinely spatial scene before deciding that two vectors intersect. A flattened projection can hide perpendicularity or make a plane look like a line.

## 1. Complex multiplication: arithmetic that moves a plane

[Open this investigation](../web/#complex) · Suggested entry: grade 10–12 · Preparation: the complex plane, radians, right triangles.

**The question.** Multiply a point repeatedly by the same nonzero complex number. When will its powers close into a polygon rather than form a spiral? Predict whether completing a full turn is enough.

**Manipulate.** Set the multiplier modulus r to one. Sweep the angle and follow the successive powers, beginning at 1. Change r while holding the angle fixed, then vary the multiplication progress and the roots/steps count. Compare the amber powers with the violet roots of unity. The amber points form a sequence, not one rigid object transformed once: its jth point turns through j times the multiplier’s displayed angle. The scene displays roots of unity, rather than roots of an arbitrary target.

**Explain.** If z = r(cos θ + i sin θ) and w = s(cos φ + i sin φ), their product has modulus rs and argument θ + φ, modulo a full turn. The same multiplier rotates every vector through the same angle and scales every length by the same positive factor. Multiplication by a + bi is also a real linear map. Its output coefficients are:

| Output coordinate | Coefficient of x | Coefficient of y |
|---|---|---|
| Real part | a | −b |
| Imaginary part | b | a |

The length factor is √(a²+b²); the area factor is a²+b².

This connects the lesson to [The Shape of a Matrix](../web/#linear). A nonzero complex multiplier can rotate and scale, but it cannot shear or reverse orientation. Outside the displayed positive-modulus range, the zero multiplier collapses the plane; angle information then disappears.

**Transfer.** On paper, extend the roots-of-unity idea: find every cube root of −8, and check one root by cubing it.

**Worked answer.** Write −8 = 8 cis(π). The root modulus is 2. The angles are π/3, π, and 5π/3, giving 1 + i√3, −2, and 1 − i√3. For the first root, cubing multiplies the modulus to 8 and triples the angle to π, so the result is −8. The three roots are equally spaced because adding 2π to the target angle before dividing by three produces a distinct root.

**Misconception to catch.** A calculator's principal root is one chosen root, not every solution of a power equation. Angles that differ by 2π describe the same nonzero point, but dividing those angles before taking a root can produce different points.

**Boundary and deeper invitation.** The lesson uses a finite set of samples. The rotation-and-scale statement follows from the product identity for every complex input. Prove that the two columns of the real matrix have equal length and zero dot product, then compare with a shear matrix.

**Study source.** [OpenStax, Precalculus 2e, §8.5: Polar Form of Complex Numbers](https://openstax.org/books/precalculus-2e/pages/8-5-polar-form-of-complex-numbers). Use its product and root exercises after making a geometric prediction.

## 2. Taylor approximation: how far does a local promise reach?

[Open this investigation](../web/#taylor) · Suggested entry: upper secondary to undergraduate year 1 · Preparation: derivatives, factorials, polynomials.

**The question.** If a polynomial agrees with a function and several derivatives at one point, must it stay close everywhere? Predict where a low-order approximation to sine will first look unconvincing.

**Manipulate.** Hold the expansion center fixed and increase the polynomial degree. Inspect a probe near the center and then farther away. Move the center toward the probe without changing the degree. Compare the actual error with the reported bound. At a center of zero, watch what happens when an even degree is added: some coefficients vanish.

**Explain.** A Taylor polynomial stores local derivative data. For sine, the derivatives cycle through sin, cos, −sin, and −cos. At center a, the coefficient of (x − a)ʲ is the jth derivative at a divided by j!. Because every derivative of sine has magnitude at most one, Taylor's theorem supplies this bound in real arithmetic.

```text
|sin(x) − Tₙ(x)| ≤ |x − a|ⁿ⁺¹ / (n+1)!
```

The bound is a guarantee from a theorem, often a loose one. The displayed difference is a floating-point calculation of one particular error. They answer related but different questions. For any fixed real x, the bound tends to zero as n increases, establishing convergence for this sine example. That conclusion requires its derivative control; it does not follow merely from matching derivatives.

**Transfer.** Use the degree-three Maclaurin polynomial to estimate sin(0.5). Give a guaranteed error bound without knowing the exact sine value.

**Worked answer.** T₃(x) = x − x³/6, so T₃(0.5) = 0.4791666667. The bound above gives 0.5⁴/4! = 1/384, approximately 0.00260417. A sharper sine-specific argument is possible, but this bound already follows from the stated theorem. Raising the degree to four at zero leaves the polynomial unchanged because the fourth coefficient is zero; its valid general remainder bound is nevertheless smaller at this point.

**Misconception to catch.** A smaller error bound does not mean the actual error changed. Nor must the absolute pointwise error fall at every degree and every point.

**Boundary and deeper invitation.** A rendered ribbon or pair of curves samples a finite interval. Use the formula to reason between the samples. Later investigate a smooth function whose derivatives all vanish at a point but whose nearby values do not; smoothness alone does not imply equality with its Taylor series.

**Study source.** [OpenStax, Calculus Volume 2, §6.3: Taylor and Maclaurin Series](https://openstax.org/books/calculus-volume-2/pages/6-3-taylor-and-maclaurin-series). Focus on Taylor's theorem with remainder before treating a fitted-looking curve as reliable.

## 3. Standing waves: motion with a stationary pattern

[Open this investigation](../web/#waves) · Suggested entry: grade 10–12 to undergraduate year 1 · Preparation: trigonometric graphs and superposition.

**The question.** Can two moving patterns add to a pattern whose special points stay put? Predict what a marked material point does when a standing wave passes through its equilibrium position.

**Manipulate.** Advance time through one oscillation. Follow each traveling component, then follow the sum at a fixed horizontal location. Change the integer mode and count the stationary nodes, including the endpoints. Compare two amplitudes while keeping the mode and speed unchanged. Separate display lanes or depths identify the components; they are visual offsets, not an extra term in the wave equation.

**Explain.** Equal-amplitude waves traveling in opposite directions satisfy a trigonometric identity.

```text
y₊ = A sin(kx − ωt),   y₋ = A sin(kx + ωt)
y₊ + y₋ = 2A sin(kx) cos(ωt),   ω = ck
```

The factor sin(kx) fixes the node positions; cos(ωt) changes every material point's displacement through time. For fixed ends at x = 0 and x = L, a nonzero mode must have kL = mπ. Thus wavelength is 2L/m and frequency is mc/(2L). An individual traveling component need not satisfy the fixed-end condition; their sum does. The time control uses a fraction of one period: changing speed changes the physical period, while a snapshot at the same phase has the same shape.

**Transfer.** An ideal string has length 1 m and wave speed 2 m/s. Find the third mode's wavelength, frequency, and node positions.

**Worked answer.** With m = 3, wavelength is 2/3 m and frequency is 3 Hz. Nodes lie at x = jL/m for j = 0, 1, 2, 3: 0, 1/3, 2/3, and 1 m. There are two internal nodes and four nodes including the ends. An antinode moves up and down; it does not travel along the string.

**Misconception to catch.** A stationary envelope does not mean the string is stationary. At some instants the whole ideal mode passes through zero displacement while most points have nonzero velocity.

**Boundary and deeper invitation.** This is an ideal linear, nondispersive, undamped wave model. It illustrates displacement and superposition; it does not calculate energy flow or model a real instrument's losses. Connect to [Fourier circles](../web/#fourier): a mode expansion can combine allowed standing modes to describe more complicated initial shapes.

**Study source.** [MIT OpenCourseWare, 8.03SC, Lecture 9: Wave Equation, Standing Waves, Fourier Series](https://ocw.mit.edu/courses/8-03sc-physics-iii-vibrations-and-waves-fall-2016/pages/part-i-mechanical-vibrations-and-waves/lecture-9/), Prof. Yen-Jie Lee. Pair the lecture's notes with your node-count prediction.

## 4. The central limit theorem: changing a distribution, not polishing a histogram

[Open this investigation](../web/#probability) · Suggested entry: grade 10–12 to undergraduate year 2 · Preparation: probability, mean, variance, standard deviation.

**The question.** Why can a sum of very non-bell-shaped random variables look approximately normal? Predict whether doubling the number of trials makes the standardized distribution twice as wide.

**Manipulate.** Begin with a small number of fair Bernoulli trials. Increase the number of trials while comparing the discrete distribution with the normal curve. Then make success rare and repeat. Inspect the reported mean and variance of the standardized distribution. These are calculations from the finite probability law, not estimates from random runs.

**Explain.** Let independent, identically distributed trials take values zero and one with success probability p. Their sum K is binomial. Its mean is np and its variance is np(1 − p). Standardization subtracts the mean and divides by the standard deviation.

```text
Z = (K − np) / √(np(1 − p))
Δz = 1 / √(np(1 − p))
mathematical density height = P(K = k) / Δz
displayed height = 6 P(K = k) / Δz
```

The density scaling is essential: before the common vertical display scaling, each bar’s area, rather than its height, equals probability mass. A continuous normal density also gives probabilities through area. The scene multiplies both density heights by six for legibility, so divide a displayed bar’s area by six to recover its probability. Very distant bars may be omitted from the view; the reported undrawn mass accounts for them. At finite trial count the binomial law remains discrete, even when its outline resembles the normal curve. Under the Bernoulli assumptions with fixed 0 < p < 1, its standardized sum converges in distribution to the standard normal as the trial count grows.

**Transfer.** For 25 independent trials with p = 0.2, find the mean and standard deviation of K. What Z value corresponds to eight successes? How would 10,000 repeated experiments change the exact law?

**Worked answer.** The mean is 5 and variance is 4, so the standard deviation is 2. Eight successes corresponds to Z = (8 − 5)/2 = 1.5. Repeating the whole 25-trial experiment 10,000 times would give an empirical histogram that more clearly estimates the same binomial law. It would not change that law or turn its 25 trials into 250,000 trials per observation.

**Misconception to catch.** There is no universal trial count at which normality suddenly becomes valid. A strongly asymmetric case can remain visibly skewed at a count that works well for a balanced case. Standardization preserves asymmetry; it does not remove it by definition.

**Boundary and deeper invitation.** The finite distribution is evaluated in floating point from the exact binomial formula. The lesson does not demonstrate the theorem for dependent trials or arbitrary heavy-tailed variables. Compare mass in a bin with the normal integral over that bin; evaluating the normal density at one point is not itself a probability.

**Study source.** [OpenStax, Introductory Statistics 2e, §7.1: The Central Limit Theorem for Sample Means](https://openstax.org/books/introductory-statistics-2e/pages/7-1-the-central-limit-theorem-for-sample-means-averages). Translate between sums and means: the Bernoulli sample mean is K/n, and both lead to the same standardized variable.

## 5. Least squares: the best answer is a shadow

[Open this investigation](../web/#least_squares) · Suggested entry: undergraduate years 1–2 · Preparation: vectors, dot products, matrix columns.

**The question.** If a vector b lies outside a matrix's column plane, what should the equation Ax = b mean? Predict the direction in which the remaining error points at the best fit.

**Manipulate.** Orbit the scene to identify the column plane, b, its projection, and the residual connecting the projection to b. Move b within and away from the plane. Then make the two matrix columns nearly parallel. Compare the fitted vector with the coefficients needed to construct it. Near-parallel columns can make those coefficients large even when the fitted point stays moderate.

**Explain.** Least squares minimizes ‖b − Ax‖². When A has independent columns, there is one coefficient vector x̂ whose fitted vector p = Ax̂ is the orthogonal projection of b onto the column space. The residual r = b − p is perpendicular to every column.

```text
Aᵀr = 0,   AᵀA x̂ = Aᵀb
‖b − (p + Av)‖² = ‖r‖² + ‖Av‖²
```

The second identity explains optimality: every allowed movement Av lies in the plane and is perpendicular to r, so its squared length only adds to the error. The normal equations express this geometry; explicitly forming an inverse is not a recommended general numerical algorithm. QR or SVD methods are usual tools for harder numerical work.

**Transfer.** Take columns a₁ = (1, 0, 0), a₂ = (0, 1, 0), and b = (2, −1, 3). Find x̂, p, r, and the minimum squared error. Then replace a₂ by (1, ε, 0), with ε nonzero.

**Worked answer.** Initially x̂ = (2, −1), p = (2, −1, 0), r = (0, 0, 3), and squared error is 9. With the replacement column, the same plane and projection remain, but εx̂₂ = −1 and x̂₁ + x̂₂ = 2. Thus x̂₂ = −1/ε and x̂₁ = 2 + 1/ε. Small ε demands large cancelling coefficients. At ε = 0 the rank changes and this argument no longer applies: the column space becomes a line.

**Misconception to catch.** A small residual does not guarantee stable coefficients. Likewise, the best fit minimizes squared Euclidean residual, not absolute residual or every individual coordinate's error independently.

**Boundary and deeper invitation.** The displayed lesson keeps its columns independent and its parameter range bounded. Its near-collinear examples illustrate conditioning without pretending to solve every rank-deficient case. Revisit [gradient descent](../web/#gradient): for the objective ½‖Ax − b‖², the Hessian is AᵀA. Nearly dependent columns create a narrow optimization valley.

**Study source.** [MIT OpenCourseWare, 18.06SC: Projection Matrices and Least Squares](https://ocw.mit.edu/courses/18-06sc-linear-algebra-fall-2011/pages/least-squares-determinants-and-eigenvalues/projection-matrices-and-least-squares/), Prof. Gilbert Strang. Work a projection problem before watching its solution.

## 6. Divergence and curl: expansion is not rotation

[Open this investigation](../web/#vector_field) · Suggested entry: undergraduate years 2–3; visual entry earlier · Preparation: vectors and partial derivatives; line integrals for the full derivation.

**The question.** Does a swirling field have to produce outward flux? Predict what happens to the area of a small particle ring in a pure rotation.

**Manipulate.** Start with rotation alone. Advance time and follow the marked particles. Then switch to expansion alone; finally combine them. Compare the field arrows, the particle ring, the reported divergence and curl, and the two boundary integrals. The fixed integration circle and the evolving particle ring serve different purposes; do not identify them just because they coincide at time zero.

**Explain.** The field separates into a radial part and a rotational part.

```text
F(x,y) = (ax − by, bx + ay)
div F = 2a,    curl_z F = 2b
```

For a circle of radius R with outward normal and counterclockwise traversal, direct parametrization gives outward flux 2πaR² and circulation 2πbR². Dividing each integral by the disk's area gives 2a and 2b. For this special linear field the quantities are constant across the disk; in a general field these are area averages, approaching local divergence or curl in a shrinking-loop limit under appropriate smoothness.

Particle positions satisfy q(t) = exp(at) Rot(bt) q(0). Their ring radius grows by exp(at), and the enclosed area grows by exp(2at). Rotation changes orientation, not area. The angular speed here is b, while scalar curl is 2b; the factor two has geometric meaning.

**Transfer.** Let a = 0 and b = 2. For a circle of radius 3, find divergence, curl, outward flux, counterclockwise circulation, and the material ring's area after one time unit.

**Worked answer.** Divergence is 0, curl is 4, outward flux is 0, and circulation is 2π·2·9 = 36π. The ring's area stays 9π because exp(2at) = 1. It rotates through 2 radians, not 4. Zero divergence here says no local area expansion; it does not say no motion.

**Misconception to catch.** An arrow pointing to the right does not by itself indicate positive divergence or curl. Both describe spatial change across nearby arrows, not the absolute direction of one arrow.

**Boundary and deeper invitation.** A finite arrow grid cannot establish a field identity. Derive the derivatives and boundary integrals, then use the numerical diagnostics as a check. A compressing material ring is an illustration of the specified mathematical flow, not a complete fluid simulation with pressure, viscosity, or conservation laws supplied independently.

**Study source.** [OpenStax, Calculus Volume 3, §6.5: Divergence and Curl](https://openstax.org/books/calculus-volume-3/pages/6-5-divergence-and-curl). Follow with Green's theorem to connect local derivatives and boundary measurements.

## Revisit the original six with a sharper question

| Experiment | A productive test | What to carry forward |
|---|---|---|
| [Linear transformations](../web/#linear) | Compare a reflection, a shear, and multiplication by i. | Equal area magnitude does not imply equal shape or orientation. Complex multiplication occupies a special subset of real 2×2 matrices. |
| [The derivative](../web/#derivative) | Halve h repeatedly and compare central and forward errors. | Different approximation methods have different error orders. A finite secant and a derivative are not identical objects. |
| [Integration](../web/#integral) | Hold the interval fixed and compare sample choices at the same rectangle count. | A method's guarantee depends on its assumptions. A right-endpoint rule is not automatically an overestimate. |
| [Fourier circles](../web/#fourier) | Increase harmonics while inspecting both the average error and the neighborhood of a jump. | Average accuracy can improve while a conspicuous local feature persists. |
| [Lorenz dynamics](../web/#lorenz) | Separate a nearby-start comparison from a same-start step refinement. | Sensitivity to initial data and numerical discretization error need separate experiments. |
| [Gradient descent](../web/#gradient) | Predict whether the stiffest mode contracts or flips before increasing the rate. | Curvature controls useful step sizes. For the lesson's positive-definite quadratic, each mode multiplies by 1 − αλ. |

## Keep evidence that another learner can inspect

**A lesson card** keeps the lesson and its parameters, plus a saved prediction when provided. Reopening it recomputes the model. It does not preserve a camera pose, every intermediate action, or an assessment of understanding.

**An X3D export** keeps a static sampled world with its parameter metadata. It is useful for inspection in another X3D tool and for discussing how geometry encodes a mathematical claim. Sampling, floating-point coordinates, and camera projection still have limits.

**A Manim export** is generated scene source built from the same sampled model. It offers a starting point for a locally rendered explanation. Generating that source is distinct from rendering a video; the optional Manim toolchain must be installed separately.

Use a small observation record rather than relying on memory:

| Question | Prediction before interaction | One controlled change | Measurement or visible evidence | Revised explanation | Remaining uncertainty |
|---|---|---|---|---|---|
| Example: Does pure rotation expand area? | I expect the ring to grow because particles move. | Hold expansion at zero; advance time. | Radius and area stay fixed while angle changes. | Motion can preserve area; divergence and curl measure different local behavior. | Does every zero-divergence field preserve a circle's shape? |
| Your investigation | | | | | |

The example's final question is deliberately useful. Area preservation does not imply shape preservation: other zero-divergence fields can stretch one direction while compressing another. This lesson's circular behavior is a feature of its chosen field, not a universal property of zero divergence.

## A small research agenda

The atlas is a teaching prototype, not a measured learning-outcome claim. The following hypotheses are testable questions for an educator or researcher.

| Hypothesis | Comparison worth studying | Evidence to collect | What would weaken the claim? |
|---|---|---|---|
| Prediction before manipulation improves explanations. | Prediction-first activity versus the same scene explored freely. | Explanations before, immediately after, and on a delayed transfer problem. | Better recall of colors or controls without improved mathematical reasoning. |
| Linked cases help students distinguish concepts. | Pure rotation and pure expansion before their mixture, versus mixture alone. | Whether students independently separate flux, circulation, and particle motion. | Correct answers only for the exact presets already seen. |
| Exposing error meanings improves numerical judgment. | Actual error plus bound versus a curve comparison alone. | Decisions about acceptable tolerance on unseen Taylor or integration cases. | Treating every displayed diagnostic as a rigorous bound. |
| Reproducible cards improve peer critique. | Exchanging parameter cards with predictions versus screenshots alone. | Whether a peer can reproduce, challenge, and repair an explanation. | More reproducible pictures without clearer claims or assumptions. |

Predefine a rubric: identify the relevant quantity, state its assumptions, connect the picture to an equation, and transfer to an unseen case. Collect consent and protect learner data in any real study. Avoid equating time-on-page, repeated slider movement, or a pleasing image with understanding.

## Build your own next investigation

Choose one bridge and make it precise: represent a complex multiplier as a matrix; build a wave from Fourier modes; derive a least-squares valley; integrate a vector field around a loop; or compare an exact finite probability law with an approximation.

Before adding visual complexity, write four sentences: **What can the learner change? What should stay invariant? What would refute their first intuition? What calculation checks the picture?** A strong new lesson can answer all four.
