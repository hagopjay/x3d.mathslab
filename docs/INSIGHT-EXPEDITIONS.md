# Insight Expeditions

[Open the laboratory](../web/) · [The Aha Atlas](Aha-Atlas.html) · [Original field guide](Mathlab-Field-Guide.html) · [Run the project](../README.md)

## Six more ways to change your mind

A mathematical picture earns its place when it helps you notice a relationship, make a risky prediction, and explain why the prediction succeeded or failed. These six expeditions connect familiar ideas to unfamiliar consequences: a matrix reveals its preferred directions; a detector can be reliable yet produce mostly false alarms; a motionless pattern can hide lost information; a hot profile becomes smooth without losing its mean.

The collection now contains eighteen lessons. This companion develops the six newest investigations, with bridges into the earlier twelve. Suggested preparation describes a useful starting point, not an age gate. A confident tenth grader can explore a conditional-probability area diagram; a third-year undergraduate should also connect its denominator to a partition of the sample space.

Each study takes about twenty minutes. Spend two minutes predicting, five changing one control, six explaining an observation, five solving the transfer problem, and two saving a lesson card with a revised explanation. A beautifully moving curve is evidence about the specified model. The equation, assumptions, and independent reference tell you what that evidence means.

## Three connected journeys

| Journey | Follow these lessons | The question that travels with you |
|---|---|---|
| Geometry finds a best answer | [Matrices](../web/#linear) → [SVD](../web/#svd) → [Least squares](../web/#least_squares) → [Lagrange multipliers](../web/#lagrange) → [Refraction](../web/#refraction) | What changes when the allowed directions of motion change? |
| Data needs a model | [Fourier circles](../web/#fourier) → [Aliasing](../web/#aliasing) → [Probability](../web/#probability) → [Bayes](../web/#bayes) | Which conclusions belong to the observations, and which require assumptions? |
| Modes carry different futures | [Complex motion](../web/#complex) → [Standing waves](../web/#waves) → [Heat flow](../web/#heat) → [Gradient descent](../web/#gradient) → [Lorenz dynamics](../web/#lorenz) | Does a mode rotate, decay, grow, or lose predictive usefulness? |

Follow one arrow at a time. Redundancy is useful here: the same dot product becomes a projection, a directional derivative, a normal condition, or a measure of compatibility. The goal is to recognize the relationship when the surrounding picture changes. For three further bridges, return to [Taylor approximation](../web/#taylor) for the meaning of an error guarantee, [integration](../web/#integral) for accumulation, and [vector fields](../web/#vector_field) for local geometry that controls global change.

## 1. SVD: find the directions that a matrix makes simple

[Open the SVD investigation](../web/#svd) · Suggested preparation: vectors, dot products, matrix multiplication, sine and cosine.

**Predict.** A matrix sends a unit circle to an ellipse, a collapsed segment, or a point. Are the ellipse's longest and shortest directions usually the matrix's columns? Are they its eigenvectors? Draw your guess before moving a control. Then ask a more precise question: which input unit vector produces the longest output vector?

**Manipulate.** Begin with unequal singular values and sweep transformation progress through its three stages: rotate into the input basis, stretch along perpendicular axes, and rotate into the output basis. Change the input rotation while holding the stretch factors fixed. Then change only the output rotation. Watch which features of the final ellipse change and which measurements remain the same. Set the singular-value ratio to zero, then to one. These two special cases reveal more than a complicated generic matrix.

**Explain.** The authored target matrix is A = R(u) Σ R(v)ᵀ, where Σ has nonnegative diagonal entries σ₁ and σ₂, with σ₁ ≥ σ₂. The columns v₁, v₂ of R(v) are input directions. The columns u₁, u₂ of R(u) are output directions. Their defining relation is A vᵢ = σᵢ uᵢ. A preferred input direction therefore need not point along its output direction; SVD is not a claim that every matrix has two real eigenvectors.

Write a unit input as x = αv₁ + βv₂ with α² + β² = 1. Orthogonality gives ||Ax||² = σ₁²α² + σ₂²β². That quantity lies between σ₂² and σ₁². The extreme output lengths are therefore the singular values, and the input directions that achieve them are visible before the final rotation. You have derived the geometry of the ellipse rather than merely recognized its outline.

The target singular values describe the final A. The intermediate display is a staged transformation with its own matrix and area scale. During the first pure rotation, for example, the displayed circle has not yet been stretched. Read a metric's label before treating target data as a measurement of the current stage.

**Transfer on paper.** Let the target stretch by factors 3 and 1, apply no input rotation, then rotate the output counterclockwise by 90°. Where do the horizontal and vertical unit vectors go? What are the condition number and area factor?

**Worked answer.** The horizontal unit vector becomes (0, 3); the vertical one becomes (−1, 0). The longest output length is 3, the shortest is 1, so the Euclidean condition number is 3. The area factor is 3. Neither the visible final directions nor these factors require the original coordinate axes to be eigenvectors.

**Catch the misconception.** If σ₂ = 0, a whole input direction disappears. Calling the inverse merely “very large” misses the structural change: no two-sided inverse exists. If σ₁ = σ₂, every unit input receives the same stretch, so the preferred perpendicular bases are not unique. An algorithm may choose a basis without nature selecting that particular one.

**Scope and bridge.** This scene constructs an orientation-preserving rotation–stretch–rotation family, including rank-one collapse. The general SVD uses orthogonal factors that can also include reflections. Connect the small singular value to the fragile coefficients in [least squares](../web/#least_squares), then compare singular values with the real eigenvalues in [the matrix lesson](../web/#linear).

**Study source.** [MIT OpenCourseWare 18.06SC: Singular Value Decomposition](https://ocw.mit.edu/courses/18-06sc-linear-algebra-fall-2011/pages/positive-definite-matrices-and-applications/singular-value-decomposition/) provides a lecture, problems, and solutions. After the visual study, derive why the input singular directions are eigenvectors of AᵀA.

## 2. Bayes: a good detector can produce mostly false alarms

[Open the Bayes investigation](../web/#bayes) · Suggested preparation: fractions, percentages, area, conditional probability.

**Predict.** Imagine tagged objects mixed into a much larger collection of untagged objects. A detector catches 99% of tagged objects and falsely flags 1% of untagged objects. If only one object in a thousand is tagged, what fraction of positive results actually come from tagged objects? Write an estimate before using the area diagram. The setting is an abstract detector, not a recommendation for interpreting a real test.

**Manipulate.** Hold sensitivity and false-positive rate fixed while changing prevalence. Inspect the whole-population partition, then the panel conditioned on a positive result. The positive panel deliberately changes scale: its whole area represents all positive outcomes, rather than all objects. Follow the same tagged-positive region through that change of denominator. Finally raise sensitivity while keeping the false-positive rate fixed. Compare its effect with lowering the false-positive rate.

**Explain.** Let H mean “tagged,” π = P(H), s = P(+|H), and q = P(+|not H). The population splits into four joint outcomes:

| Outcome | Probability |
|---|---|
| Tagged and positive | πs |
| Tagged and negative | π(1−s) |
| Untagged and positive | (1−π)q |
| Untagged and negative | (1−π)(1−q) |

The positive outcomes form a new reference population. Its mass is P(+) = πs + (1−π)q. Dividing the tagged-positive mass by that total gives P(H|+) = πs / [πs + (1−π)q]. The numerator is already part of the denominator: a true positive is still a positive. The diagram makes this inclusion visible.

For the opening example, a reference collection of 10,000 has an expected 10 tagged objects. The expected true positives are 9.9. Of 9,990 untagged objects, an expected 99.9 are falsely flagged. The posterior tagged fraction is 9.9 / 109.8, about 9.02%. Decimal expected counts describe averages across repeated collections; they are not a claim that one collection contains a fraction of an object. The exact probability areas avoid hiding small groups through integer rounding.

There is another useful form: posterior odds = prior odds × likelihood ratio. Here the positive-result likelihood ratio is s/q. Evidence can multiply the odds strongly while the posterior probability remains modest, because a rare starting hypothesis begins with small odds. A large multiplicative change and a large final probability are different statements.

**Transfer.** In a population with prevalence 1%, a detector has sensitivity 90% and false-positive rate 1%. Out of 10,000 objects, find expected true positives, false positives, and the tagged fraction among positives.

**Worked answer.** There are an expected 100 tagged and 9,900 untagged objects. True positives: 90. False positives: 99. Among the expected 189 positives, 90 are tagged, so the posterior is 90/189 = 10/21, about 47.62%. The detector's 90% sensitivity is a fraction of tagged objects, not a fraction of positive results.

**Catch the misconception.** “Accurate” is ambiguous unless its denominator is stated. Sensitivity, specificity, overall accuracy, and positive predictive value answer different questions. A nearly empty tagged region does not mean a positive detector result contains no information; compare posterior with prior, not only with 50%.

**Scope and bridge.** The scene assumes fixed probabilities for a specified reference population. It does not infer those probabilities from data or model changes in detector performance between populations. Move to [the probability lesson](../web/#probability) to distinguish a probability model from a noisy empirical frequency. A real inference problem must also justify its prior and likelihood model.

**Study source.** [3Blue1Brown: Bayes' theorem](https://www.3blue1brown.com/lessons/bayes-theorem/) develops conditioning through area. Use its visual reasoning to explain why the positive panel has a different total area before performing the division.

## 3. Lagrange multipliers: the best direction may be forbidden

[Open the constrained-extrema investigation](../web/#lagrange) · Suggested preparation: ellipses, vectors, derivatives; gradients help with the deeper explanation.

**Predict.** You want to increase f(x,y) = cₓx + cᵧy, but you must stay on an ellipse. The gradient points in the direction of fastest unconstrained increase. At the best reachable point, does that gradient have to vanish? Imagine standing at the highest point of a narrow path drawn across a hillside: you can still see higher ground that the path does not reach.

**Manipulate.** Move the probe around the constraint and watch the objective's level lines. Turn the objective direction while leaving the ellipse fixed. Then change the ellipse's semiaxes without changing the objective. Find both the maximum and minimum, not just the point that visually seems most favorable. Near an extremum, inspect the feasible tangent and the objective gradient. Ask which component of that gradient can actually move you along the curve.

**Explain.** The constraint is g(x,y) = x²/a² + y²/b² − 1 = 0, with a,b > 0. A parametrization is r(θ) = (a cos θ, b sin θ). Its tangent is r′(θ) = (−a sin θ, b cos θ). The rate of change along the allowed path is d[f(r(θ))]/dθ = ∇f · r′(θ). At a constrained stationary point this dot product vanishes even though ∇f = (cₓ,cᵧ) remains nonzero.

The constraint gradient is perpendicular to every feasible tangent. On this ellipse it never vanishes. Thus the objective gradient at a stationary point must be parallel to the constraint gradient: ∇f = λ∇g. The multiplier expresses a normal relationship; its sign does not by itself identify a maximum in every optimization problem.

For this particular linear objective, the full answer is available without numerical search. Substitute x = a cos θ, y = b sin θ. Then f = acₓ cos θ + bcᵧ sin θ, whose amplitude is D = √[(acₓ)² + (bcᵧ)²]. The maximum is D and the minimum is −D. Their positions are ±(a²cₓ, b²cᵧ)/D. Compactness guarantees that extrema exist, and the sinusoidal form identifies them globally.

**Transfer.** On x²/4 + y² = 1, maximize and minimize f = x + y. Find the locations, objective values, and the multiplier for the maximum using the g convention above.

**Worked answer.** Here a = 2, b = 1, c = (1,1), so D = √5. The maximum occurs at (4/√5, 1/√5) and equals √5; the minimum is the opposite point and equals −√5. At the maximum, ∇g = (x/2, 2y) = (2/√5, 2/√5). Therefore (1,1) = (√5/2)∇g, so λ = √5/2. The direction c need not be normalized for this paper calculation. The scene uses a unit objective direction to separate orientation from an arbitrary overall scale.

**Catch the misconception.** Parallel gradients are a necessary condition at regular constrained extrema, not a universal guarantee of a global optimum. This example has both a maximum and a minimum satisfying the condition. Other objectives and constraints can have additional stationary points, boundary issues, or singular points that require separate reasoning.

**Scope and bridge.** Compare the result with [gradient descent](../web/#gradient): an unconstrained minimum in that smooth quadratic has zero gradient. In [least squares](../web/#least_squares), the residual is normal to the reachable plane. Here a gradient is normal to the feasible curve. Both observations arise because every allowed first-order change has zero dot product with a particular normal vector.

**Study source.** [OpenStax Calculus Volume 3, §4.8: Lagrange Multipliers](https://openstax.org/books/calculus-volume-3/pages/4-8-lagrange-multipliers) develops the method and its assumptions. Use the worked exercises to practice finding every candidate, then deciding which are extrema.

## 4. Aliasing: identical samples can hide different motions

[Open the sampling investigation](../web/#aliasing) · Suggested preparation: cosine, frequency, radians, arithmetic sequences.

**Predict.** A wave oscillates seven times per second, but you observe it eight times per second. Could a slower wave produce exactly the same observations? The question concerns the sample values themselves, not whether two drawn curves look vaguely similar. Imagine photographing a rotating wheel: the spokes may appear to turn backward even though every photograph is accurate.

**Manipulate.** Compare the original continuous cosine, its displayed signed alias, and their shared sample locations. Change frequency with sample rate held fixed. Then increase the sample rate. Change phase near the Nyquist boundary rather than assuming that one convenient phase represents every signal. The continuous curves are supplied by the model; an observer holding only the sample values does not automatically know which curve generated them.

**Explain.** Samples occur at tⱼ = j/fₛ for integer j. For any integer m, the frequency fₐ = f − mfₛ satisfies 2πfₐtⱼ + φ = 2πftⱼ + φ − 2πmj. A full integer number of turns does not change cosine, so the two signals agree exactly at every sample. The scene chooses a signed representative in a Nyquist interval. Negative frequency records a direction of phase rotation; for a real cosine it can also be represented using positive frequency with a corresponding phase change.

This equality is an information limitation, not a failure of numerical precision. Connecting samples with a smooth curve introduces a choice. If a second continuous curve passes through the same dots, the dots alone cannot select between them. A longer noiseless record of this same uniformly sampled sinusoid does not remove the integer-frequency ambiguity.

The sampling theorem becomes useful after its assumptions are supplied. For a known band limit B, ideal uniform sampling at fₛ > 2B supports unique band-limited reconstruction from the full appropriate sample sequence. A finite record brings additional windowing and boundary questions. No claim that an arbitrary signal is recoverable follows merely from drawing enough points across one screen.

**Transfer.** At fₛ = 10 samples per second, find a signed alias of f = 8 Hz in the interval [−5,5). Show why it has equal samples for any fixed phase. Then consider sin(2π·5t): what happens at those same sample times?

**Worked answer.** Choose m = 1, giving fₐ = −2 Hz. At j/10 the phase difference is 2πj, so every cosine sample agrees for every fixed φ. The 5 Hz sine gives sin(πj) = 0 at every sample. This is why careless use of equality at the Nyquist boundary can lose phase information. The clean uniqueness condition uses a strict known band limit rather than assuming that a signal at the boundary is always harmless.

**Catch the misconception.** A lower apparent frequency is not necessarily the physical frequency. Nor does a negative alias prove that the source moved backward. The sign describes one compatible model of phase progression. Sampling and a prior restriction together support inference; either alone can be insufficient.

**Scope and bridge.** The demonstration uses ideal point samples of a single cosine with exact authored frequencies and no noise, jitter, exposure blur, or antialias filter. Compare the rotating-vector picture in [Fourier motion](../web/#fourier). Each Fourier mode has its own alias ambiguity after sampling; an antialias filter removes content that the chosen sample rate cannot distinguish.

**Study source.** [DSP First, Chapter 4: Sampling and Aliasing](https://dspfirst.gatech.edu/chapters/04samplin/overview.html), from the textbook authors at Georgia Tech, supplies demonstrations and practice. State the sampling times and candidate frequencies before judging a reconstruction by appearance.

## 5. Heat flow: roughness disappears before the broad shape

[Open the diffusion investigation](../web/#heat) · Suggested preparation: cosine, exponential decay, averages; second derivatives for the PDE connection.

**Predict.** A periodic temperature profile combines a broad cosine with a finer ripple. Both begin at visible amplitude. Will diffusion shrink them at the same rate? Will the whole profile sink toward zero? Sketch the profile after a short time and identify a quantity you expect to remain unchanged.

**Manipulate.** Advance time while comparing the initial profile, current profile, and the displayed evolution. Increase the ripple mode number while holding its initial amplitude fixed. Then change diffusivity. In the history sheet, depth represents time rather than a second material coordinate; vertical height represents twice the deviation from the conserved mean. Read the coordinate caption before interpreting its shape. Look for a time when the fine ripple is almost gone but the broad shape remains. Finally set the high-mode amplitude to zero to isolate one exponential decay. A mode's amplitude and the spatial average are different measurements.

**Explain.** On a periodic domain of length 2π, the lesson solves uₜ = αuₓₓ with

u(x,t) = 1 + 0.45e^(−αt) cos x + A e^(−αm²t) cos(mx).

The constant component has second derivative zero, so it remains unchanged. A cosine of mode m has second derivative −m²cos(mx); its amplitude therefore solves a′ = −αm²a. Higher spatial frequency creates larger curvature and faster decay. The broad mode has amplitude time scale 1/α; the fine mode has time scale 1/(αm²). Increasing m from 2 to 4 makes that mode's decay rate four times larger.

The integral of every nonconstant cosine over a full period is zero. The spatial mean therefore stays at 1. This is conservation of the model's total heat on the periodic domain. It does not mean every point stays warm or every local region retains its heat: diffusion redistributes the profile.

An independent quantity reveals smoothing. Let E(t) be the mean squared deviation from the conserved mean. Orthogonality gives E(t) = ½[(0.45)²e^(−2αt) + A²e^(−2αm²t)]. This decreases as time advances. Integrating the PDE against u−1 also gives E′(t) = −2α times the spatial mean of uₓ², with periodic boundary terms canceling. What disappears is variation, while the constant mode survives.

**Transfer.** Suppose a mode with m = 3 has fallen to half its initial amplitude. What fraction remains of a mode with m = 1 at the same time, for the same diffusivity? Does the mean change?

**Worked answer.** The high-mode decay factor satisfies e^(−9αt) = 1/2. Thus e^(−αt) = 2^(−1/9), about 0.926. More than 92% of the broad mode remains when half the finer mode has gone. The mean remains unchanged because it is the constant mode. This comparison does not require the two modes to have equal starting amplitudes.

**Catch the misconception.** The heat equation does not erase every component equally. It strongly suppresses fine variation. Trying to reverse time would amplify those same fine components fastest, including small measurement errors. A smooth present profile can be compatible with initial fine detail that is extremely difficult to recover reliably.

**Scope and bridge.** The lesson uses constant diffusivity, a periodic one-dimensional domain, and a small finite combination of exact modes. It does not model a rod exchanging heat with its surroundings or infer conductivity from measurements. Contrast it with [standing waves](../web/#waves), whose ideal undamped modes oscillate instead of decaying. Connect the factors e^(−αλt) with the discrete mode factors 1−αλ in [gradient descent](../web/#gradient).

**Study sources.** [Jiří Lebl: The Heat Equation](https://www.jirka.org/diffyqs/html/heateq_section.html) develops separation of variables and boundary conditions. [3Blue1Brown: Differential Equations and the Heat Equation](https://www.3blue1brown.com/lessons/pdes/) supplies a visual companion. Compare their boundary conditions with the periodic conditions declared here before transferring a formula.

## 6. Refraction: the fastest route can be longer

[Open the refraction investigation](../web/#refraction) · Suggested preparation: distances, slopes, sine, optimization; derivatives for Snell's law.

**Predict.** Travel from a point above a flat interface to a point below it. Motion is faster in one medium than the other. Is the straight geometrical path still the fastest? Before moving the crossing point, decide whether the fastest path should spend more horizontal distance in the faster or slower medium.

**Manipulate.** Compare the straight path, a trial crossing, and the optimized crossing. Set the two refractive indices equal, then make them different. Move the trial crossing slightly to each side of the optimum and compare optical travel cost. Measure angles to the interface normal, rather than to the interface itself. Hold the endpoints fixed while changing an index so the consequence belongs to speed, not to a changed destination.

**Explain.** Place the source at (0,h₁), target at (d,−h₂), and crossing at (x,0), where both heights are positive. In a medium of constant refractive index n, speed is c/n. Multiplying travel time by c gives the optical cost

J(x) = n₁√(x²+h₁²) + n₂√[(d−x)²+h₂²].

Differentiate with respect to the crossing location. At a stationary crossing, n₁x/√(x²+h₁²) = n₂(d−x)/√[(d−x)²+h₂²]. The fractions are the sines of the angles to the normal. Thus the optimal crossing satisfies n₁sin θ₁ = n₂sin θ₂: Snell's law emerges from varying a path.

The deeper check is a second derivative. Each term contributes a positive quantity: n₁h₁²/(x²+h₁²)^(3/2) and n₂h₂²/[(d−x)²+h₂²]^(3/2). Therefore J is strictly convex. Its derivative is negative at x = 0 and positive at x = d, so exactly one crossing between the endpoints minimizes this specified transmission cost. A numerical crossing can be checked against both stationarity and the Snell relation.

**Transfer.** Let h₁ = h₂ = 1 and d = 2. If n₁ = n₂, where is the fastest crossing? If the lower index is raised while the upper one stays fixed, which way does the crossing move?

**Worked answer.** Equal indices give the straight-line crossing x = 1. If n₂ becomes larger, the lower medium becomes slower. The optimum shifts to x > 1, covering more horizontal distance in the faster upper medium and making the lower segment more nearly normal. At x = 1 the new derivative is negative, so moving right initially decreases cost; strict convexity determines the unique new minimum.

**Catch the misconception.** Least distance and least time agree only when speed is appropriately uniform. Also, Fermat's principle is a stationary optical-path principle in general optics; a stationary ray is not automatically a unique global minimum in every optical system. Strict convexity is what permits the stronger conclusion in this two-medium, flat-interface example.

**Scope and bridge.** This is a fixed-endpoint transmitted-path family in two homogeneous isotropic media. It does not model reflection, total internal reflection, dispersion, wave interference, absorption, or a varying refractive-index field. Compare its scalar derivative with [the derivative lesson](../web/#derivative), then connect path variation to the allowed-direction reasoning in [Lagrange multipliers](../web/#lagrange).

**Study sources.** [OpenStax College Physics 2e, §25.3: The Law of Refraction](https://openstax.org/books/college-physics-2e/pages/25-3-the-law-of-refraction) clarifies indices and angles. [The Feynman Lectures on Physics, I–26: Optics: The Principle of Least Time](https://www.feynmanlectures.caltech.edu/I_26.html) develops the path-based viewpoint. Use the scene's strict-convexity argument to state precisely when “least” is justified here.

## Make an explanation portable

Save a lesson card after writing a prediction. Exchange it with another learner and ask them to reproduce the observation before reading your explanation. An X3D export retains static sampled geometry and parameter metadata; a Manim export generates scene source from the same sample. Neither is a complete record of slider history, camera motion, or understanding, and source generation does not itself render a film.

| Record | A useful example |
|---|---|
| Claim | The high heat mode decays faster, while the mean stays fixed. |
| Controlled change | Change the high mode from 2 to 4; keep diffusivity, time, and initial amplitude fixed. |
| Observation | The fine ripple's remaining amplitude falls much more strongly than the broad component. |
| Mathematical reason | The decay exponent contains the square of the mode number; the constant mode has eigenvalue zero. |
| Transfer question | Which components would be most unstable if I tried to recover the earlier profile? |

For research, compare explanations on unseen cases rather than treating interaction counts as learning. Can a student distinguish a target SVD invariant from an intermediate display? Can they choose the right Bayes denominator without the colors? Can they explain aliasing with a phase argument, or separate heat conservation from variance decay? These are testable questions, not measured outcomes of this prototype.

## Keep the productive redundancy

Across these expeditions, three ideas recur. **A basis can simplify a transformation:** SVD exposes independent stretches, while Fourier modes expose independent decay rates. **A constraint changes the relevant question:** an ellipse restricts motion, conditioning restricts the reference population, and a band limit restricts compatible signals. **A local condition needs a scope:** a zero derivative identifies a candidate; convexity, boundary conditions, and model assumptions determine the stronger conclusion.

Use that repetition actively. Explain one lesson using the language of another, then state where the analogy ends. Heat flow and gradient descent both damp modes, but their domains and time models differ. A projection residual and a constrained gradient are both normal to allowed changes, but they are different mathematical objects. The most valuable “aha” is a connection that survives a change of picture without losing its assumptions.
