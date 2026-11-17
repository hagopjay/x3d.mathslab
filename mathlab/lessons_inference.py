"""Three inspectable bridges: singular directions, conditional evidence and constraints.

Only standard-library mathematics is used. Builders import kernel geometry
helpers lazily so catalog discovery remains independent of renderer state.
"""
from math import atan2, cos, fsum, hypot, pi, sin


def _p(key, label, lo, hi, step, default, unit=""):
    return {"id": key, "label": label, "min": lo, "max": hi, "step": step,
            "default": default, "unit": unit, "type": "number"}


LESSONS = [
    {"id": "svd", "title": "A Matrix Reveals Its Favorite Directions",
     "shortName": "SVD: turn, stretch, turn", "domain": "LINEAR ALGEBRA & GEOMETRY",
     "level": "Undergraduate 1", "view": "planar",
     "prerequisites": ["Matrix multiplication", "Rotations", "Orthogonal vectors"],
     "accent": "#a5b7ff", "tagline": "The input directions and output directions need not agree.",
     "formula": "A=UΣVᵀ    ·    Avⱼ=σⱼuⱼ    ·    σ₁≥σ₂≥0",
     "axes": "Both panels use the same Cartesian units. Left: input circle. Right: the staged image and a fixed target outline.",
     "description": "Follow an orthogonal pair from an input circle into a target ellipse: first rotate by Vᵀ, then stretch by Σ, then rotate by U. This authored family uses rotations and nonnegative singular values; it is not an arbitrary-matrix decomposition tool. The quiet violet target remains fixed while cyan geometry follows transformation progress.",
     "parameters": [_p("sigma1", "Largest singular value σ₁", .5, 2.5, .05, 2),
                    _p("ratio", "Singular-value ratio σ₂/σ₁", 0, 1, .01, .35),
                    _p("angle_u", "Output rotation angle", -pi, pi, .02, .65, "rad"),
                    _p("angle_v", "Input rotation angle", -pi, pi, .02, -.45, "rad"),
                    _p("progress", "Stages: 0 input · 1 Vᵀ · 2 Σ · 3 U", 0, 3, .01, 3)],
     "animation": {"parameter": "progress", "min": 0, "max": 3, "speed": .35, "mode": "pingpong"},
     "story": [{"title": "Choose useful inputs", "text": "The mint and pink vectors on the left are v₁ and v₂: an orthonormal input pair. The right panel shows the same two vectors after the current stage, with their colors retained."},
               {"title": "Unpack the product", "text": "Sweep progress through 1, 2 and 3. Vᵀ aligns the useful input directions with coordinate axes; Σ changes lengths; U sends the axes to the output directions. Matrix products act rightmost first."},
               {"title": "Lose information deliberately", "text": "Set σ₂/σ₁ to zero and complete all stages. One input direction disappears and the circle collapses to a segment. Equal singular values, conversely, make every orthogonal input pair equally good: the directions are not unique."}],
     "challenge": {"question": "Must a singular vector be an eigenvector of A?",
                   "answer": "No. A right singular vector vⱼ is sent to σⱼuⱼ, and the output direction uⱼ can differ from vⱼ. Right singular vectors are eigenvectors of AᵀA. Singular values are nonnegative stretch factors, unlike signed or complex eigenvalues of A."},
     "presets": [{"title": "Different directions in and out", "params": {"sigma1": 2, "ratio": .35, "angle_u": .65, "angle_v": -.45, "progress": 3}, "why": "The best input directions and the resulting ellipse axes are different objects."},
                 {"title": "Erase one direction", "params": {"sigma1": 2, "ratio": 0, "angle_u": .65, "angle_v": -.45, "progress": 3}, "why": "A zero singular value is genuine rank loss, not merely a very thin ellipse."},
                 {"title": "No favorite direction", "params": {"sigma1": 1.5, "ratio": 1, "angle_u": .8, "angle_v": -.6, "progress": 3}, "why": "Equal stretch factors preserve circular symmetry; the singular directions are not unique."}],
     "legend": [{"label": "Current image of input circle", "color": "#47d6ff"},
                {"label": "Fixed target ellipse", "color": "#a68cff"},
                {"label": "First input and its image", "color": "#5cffba"},
                {"label": "Second input and its image", "color": "#ff59a8"}],
     "resources": [{"title": "MIT 18.06SC · Singular Value Decomposition",
                    "url": "https://ocw.mit.edu/courses/18-06sc-linear-algebra-fall-2011/pages/positive-definite-matrices-and-applications/singular-value-decomposition/",
                    "note": "Connect orthogonal input/output bases, singular values, rank, and the eigenvectors of AᵀA."}],
     "connections": [{"lesson": "linear", "why": "Compare singular directions with the earlier lesson's eigenlines."},
                     {"lesson": "least_squares", "why": "A small singular value explains fragile fitting coefficients."}]},
    {"id": "bayes", "title": "A Positive Signal Changes the Denominator",
     "shortName": "Bayes: rare signals and base rates", "domain": "PROBABILITY & INFERENCE",
     "level": "Grade 10–12", "view": "planar",
     "prerequisites": ["Fractions", "Conditional probability", "Area proportions"],
     "accent": "#8affcf", "tagline": "Good detection does not remove the arithmetic of rarity.",
     "formula": "P(H|+)=P(+|H)P(H) / [P(+|H)P(H)+P(+|¬H)P(¬H)]",
     "axes": "Left rectangle: all objects, area 24. Right rectangle: positive results only, area 4.8 after conditional rescaling.",
     "description": "An abstract detector screens tagged objects. The left mosaic is the whole population, split into four exact probability areas. The narrow right panel rescales only positive results to a common area: its mint share is the posterior probability of a true tag. Expected counts refer to 10,000 objects and need not be integers.",
     "parameters": [_p("prior", "Tagged fraction P(H)", .001, .5, .001, .01),
                    _p("sensitivity", "Detection rate P(+|H)", .5, 1, .01, .99),
                    _p("false_positive", "False-alarm rate P(+|¬H)", .001, .25, .001, .01)],
     "story": [{"title": "Count both ways to be positive", "text": "Mint objects really carry the tag and trigger the detector. Amber objects have no tag but trigger it anyway. Both groups enter the denominator once the observed result is positive."},
               {"title": "Change the reference population", "text": "The right panel discards negative results and expands the positive subset to a fixed height. It is a conditional view, not a second population of the same size. Its total visual area no longer represents the original positive-result probability."},
               {"title": "Hold detector quality fixed", "text": "Compare the rare and common presets without changing the detection or false-alarm rate. The posterior changes because the sizes of the two source populations change. Bayes' theorem accounts for the base rate rather than overriding evidence."}],
     "challenge": {"question": "With a 99% detection rate and 1% false-alarm rate, must most positive results be true when only 0.1% of objects are tagged?",
                   "answer": "No. Among 10,000 objects the expected counts are 9.9 true positives and 99.9 false positives. Only 9.9/(9.9+99.9), about 9.02%, of positive results are truly tagged. The fractional counts are expectations, not a claim about a particular finite sample."},
     "presets": [{"title": "A rare tag surprises", "params": {"prior": .001, "sensitivity": .99, "false_positive": .01}, "why": "A large untagged population can generate more false positives than true positives."},
                 {"title": "Same detector, common tag", "params": {"prior": .1, "sensitivity": .99, "false_positive": .01}, "why": "Changing the base rate alone changes the meaning of a positive signal."},
                 {"title": "Reduce false alarms tenfold", "params": {"prior": .001, "sensitivity": .99, "false_positive": .001}, "why": "For a rare tag, improved specificity can matter greatly; the posterior is still just below one half here."}],
     "legend": [{"label": "Tagged and positive", "color": "#5cffba"},
                {"label": "Untagged and positive", "color": "#ffba52"},
                {"label": "Tagged and negative", "color": "#ff59a8"},
                {"label": "Untagged and negative", "color": "#1f4063"}],
     "resources": [{"title": "3Blue1Brown · Bayes theorem",
                    "url": "https://www.3blue1brown.com/lessons/bayes-theorem/",
                    "note": "Follow the area interpretation: conditioning changes the reference set used in a probability ratio."}],
     "connections": [{"lesson": "probability", "why": "Distinguish an exact probability law from random finite observations."},
                     {"lesson": "integral", "why": "The posterior is the true-positive area divided by the total positive area: a ratio of accumulated amounts."}]},
    {"id": "lagrange", "title": "The Best Move May Be Forbidden",
     "shortName": "Lagrange: optimize on a boundary", "domain": "MULTIVARIABLE CALCULUS & OPTIMIZATION",
     "level": "Undergraduate 2–3", "view": "planar",
     "prerequisites": ["Gradients", "Parametric curves", "Dot products"],
     "accent": "#ffc976", "tagline": "A nonzero gradient can coexist with a constrained maximum.",
     "formula": "maximize c·p subject to g=x²/a²+y²/b²=1    ·    ∇f=λ∇g",
     "axes": "Cartesian x,y coordinates. Cyan: feasible ellipse. Straight lines: equal objective values. Gradient arrows show unit directions.",
     "description": "Move a probe around an ellipse while a linear objective points uphill in one fixed direction. The highest reachable contour just touches the ellipse. At a constrained optimum the objective gradient need not vanish: only its component along an allowed tangent must vanish.",
     "parameters": [_p("axis_a", "Horizontal semiaxis a", .7, 2.6, .05, 2),
                    _p("axis_b", "Vertical semiaxis b", .7, 2.6, .05, 1),
                    _p("direction", "Objective direction φ", -pi, pi, .02, .7, "rad"),
                    _p("probe", "Probe parameter θ", -pi, pi, .02, 0, "rad")],
     "animation": {"parameter": "probe", "min": -pi, "max": pi, "speed": .5, "mode": "loop"},
     "story": [{"title": "Ask what moves are allowed", "text": "The probe must remain on the cyan ellipse. Its local allowed direction is tangent to that curve. The objective gradient points uphill in the plane, but stepping directly uphill usually leaves the feasible set."},
               {"title": "Find the touching contour", "text": "At the amber maximum, the objective contour and the ellipse share a tangent. Their normal directions are parallel: ∇f=λ∇g. At the pink minimum they are antiparallel. Unit direction arrows deliberately omit gradient magnitude."},
               {"title": "Use more than a stationary condition", "text": "The ellipse is compact and smooth with nonzero constraint gradient. This linear objective has exactly one maximum and one minimum, obtained analytically. In a general problem the multiplier equations only provide candidates; they do not label maxima automatically."}],
     "challenge": {"question": "Why does the objective gradient remain nonzero at the maximum?",
                   "answer": "The objective is linear with a unit gradient c everywhere. At the constrained maximum, that gradient is normal to the ellipse, so its dot product with every feasible tangent is zero. There is still an uphill direction in the plane, but it is forbidden by the constraint."},
     "presets": [{"title": "An appealing but wrong angle", "params": {"axis_a": 2, "axis_b": 1, "direction": .7, "probe": .7}, "why": "The objective direction angle is not generally the ellipse parameter at the maximum."},
                 {"title": "Touch the highest contour", "params": {"axis_a": 2, "axis_b": 1, "direction": .7, "probe": atan2(sin(.7), 2*cos(.7))}, "why": "The tangent derivative vanishes although the objective gradient has length one."},
                 {"title": "A circle makes angles agree", "params": {"axis_a": 1.6, "axis_b": 1.6, "direction": .7, "probe": .7}, "why": "Rotational symmetry makes the radial objective direction the maximizing parameter."}],
     "legend": [{"label": "Feasible ellipse / probe tangent", "color": "#47d6ff"},
                {"label": "Maximum / highest contour", "color": "#ffba52"},
                {"label": "Minimum / lowest contour", "color": "#ff59a8"},
                {"label": "Probe / objective-gradient direction", "color": "#5cffba"},
                {"label": "Constraint-normal direction", "color": "#a68cff"}],
     "resources": [{"title": "OpenStax Calculus 3 · Lagrange Multipliers",
                    "url": "https://openstax.org/books/calculus-volume-3/pages/4-8-lagrange-multipliers",
                    "note": "Study tangency, the nonzero constraint-gradient assumption, and the need to evaluate all candidate extrema."}],
     "connections": [{"lesson": "gradient", "why": "Contrast unconstrained downhill motion with a feasible tangent direction."},
                     {"lesson": "least_squares", "why": "Orthogonality again characterizes an optimum, but now along a curved feasible set."}]},
]


def _matmul(a, b):
    return [[fsum(a[i][k]*b[k][j] for k in range(2)) for j in range(2)] for i in range(2)]


def _rotation(theta):
    c, s = cos(theta), sin(theta)
    return [[c, -s], [s, c]]


def _apply(matrix, vector):
    return [fsum(row[j]*vector[j] for j in range(2)) for row in matrix]


def _svd(p):
    from .kernel import AMBER, CYAN, MINT, PINK, QUIET, VIOLET, _line, _metric, _sphere

    first, ratio, u, v, progress = (p[k] for k in ("sigma1", "ratio", "angle_u", "angle_v", "progress"))
    second = first*ratio
    U, V, Vt = _rotation(u), _rotation(v), _rotation(-v)
    target = _matmul(_matmul(U, [[first, 0.], [0., second]]), Vt)
    right = min(progress, 1.)
    stretch = max(0., min(progress-1, 1.))
    left = max(0., min(progress-2, 1.))
    displayed_scales = [1+stretch*(first-1), 1+stretch*(second-1)]
    current = _matmul(_matmul(_rotation(left*u), [[displayed_scales[0], 0.], [0., displayed_scales[1]]]), _rotation(-right*v))
    inputs = [[V[0][j], V[1][j]] for j in range(2)]
    outputs = [[U[0][j], U[1][j]] for j in range(2)]
    # Rebuild A as a sum of rank-one outer products, independently of matmul.
    rebuilt = [[fsum(s*outputs[k][i]*inputs[k][j] for k, s in enumerate((first, second)))
                for j in range(2)] for i in range(2)]
    reconstruction = max(abs(target[i][j]-rebuilt[i][j]) for i in range(2) for j in range(2))
    direction_residual = max(hypot(*[a-s*b for a, b in zip(_apply(target, inputs[k]), outputs[k])])
                             for k, s in enumerate((first, second)))
    orthogonality = max(abs(fsum(matrix[k][i]*matrix[k][j] for k in range(2))-(i == j))
                        for matrix in (U, V) for i in range(2) for j in range(2))
    determinant = current[0][0]*current[1][1]-current[0][1]*current[1][0]
    target_det = target[0][0]*target[1][1]-target[0][1]*target[1][0]
    primitives = []
    input_center, image_center = -3., 2.3
    circle = [[cos(2*pi*i/192), sin(2*pi*i/192)] for i in range(193)]
    for prefix, cx, extent in (("input", input_center, 1.25), ("image", image_center, 2.8)):
        _line(primitives, prefix+"_axis_x", [[cx-extent, 0, -.08], [cx+extent, 0, -.08]], QUIET)
        _line(primitives, prefix+"_axis_y", [[cx, -extent, -.08], [cx, extent, -.08]], QUIET)
    _line(primitives, "input_circle", [[x+input_center, y, 0] for x, y in circle], CYAN)
    _line(primitives, "target_ellipse", [[x+image_center, y, -.025] for x, y in map(lambda q: _apply(target, q), circle)], VIOLET)
    primitives[-1]["transparency"] = .5
    _line(primitives, "displayed_ellipse", [[x+image_center, y, .03] for x, y in map(lambda q: _apply(current, q), circle)], CYAN)
    for j, color in enumerate((MINT, PINK)):
        a = inputs[j]
        b = _apply(current, a)
        _line(primitives, f"input_direction_{j}", [[input_center, 0, .06], [input_center+a[0], a[1], .06]], color)
        _line(primitives, f"displayed_direction_{j}", [[image_center, 0, .07], [image_center+b[0], b[1], .07]], color)
        _sphere(primitives, f"input_tip_{j}", [input_center+a[0], a[1], .09], .065, color)
        _sphere(primitives, f"image_tip_{j}", [image_center+b[0], b[1], .09], .075, color)
    _line(primitives, "mapping_arrow", [[-1.45, 0, .08], [-.75, 0, .08], [-.9, .1, .08], [-.75, 0, .08], [-.9, -.1, .08]], AMBER)
    stage = "Vᵀ rotation" if progress < 1 else "Σ stretching" if progress < 2 else "U rotation" if progress < 3 else "complete target A"
    return primitives, [
        _metric("stage", "Currently displayed stage", stage),
        _metric("display_area", "Displayed signed-area factor", determinant, "×", "Determinant of the current staged matrix, not automatically that of target A."),
        _metric("sigma1", "Target σ₁", first), _metric("sigma2", "Target σ₂", second),
        _metric("condition", "Target condition number κ₂(A)", first/second if second else "rank deficient", "", "Singular values describe the target; only progress=3 shows that complete target."),
        _metric("direction_residual", "Target max ||Avⱼ−σⱼuⱼ||", direction_residual)
    ], {}, {"U": U, "V": V, "Vt": Vt, "singular_values": [first, second],
            "target_matrix": target, "displayed_matrix": current, "reconstructed_matrix": rebuilt,
            "input_directions": inputs, "output_directions": outputs,
            "reconstruction_residual": reconstruction, "singular_direction_residual": direction_residual,
            "orthogonality_residual": orthogonality, "target_determinant": target_det,
            "displayed_determinant": determinant, "displayed_scales": displayed_scales,
            "target_area_residual": abs(target_det-first*second),
            "target_rank": 1 if second == 0 else 2,
            "target_condition": first/second if second else None,
            "progress": progress, "stage": stage,
            "panel_centers": {"input": [input_center, 0], "image": [image_center, 0]}}, [
        "Left and right panels use equal Cartesian scale, with x translations −3 and +2.3. Subtract the appropriate panel center before comparing vector coordinates.",
        "Only progress=3 displays the target A. The target singular values and violet outline stay fixed during the instructional path; the displayed determinant belongs to the current staged map.",
        "This family chooses rotations U,V and sorted nonnegative stretches. General real matrices may require orthogonal reflections as well; an arbitrary determinant-negative matrix is not covered by these controls.",
        "At σ₂=0 the target is rank one and cannot be inverted; no finite condition number is reported. If σ₁=σ₂, the choice of singular directions is not unique.",
        "The checks compare matrix multiplication, rank-one reconstruction and Avⱼ=σⱼuⱼ. Small floating-point residuals check implementation consistency rather than prove the general SVD theorem."]


def _rectangle(primitives, name, x, y, width, height, color):
    if width > 0 and height > 0:
        primitives.append({"kind": "box", "id": name,
                           "position": [x+width/2, y+height/2, 0],
                           "size": [width, height, .035], "color": color[:], "transparency": .1})


def _bayes(p):
    from .kernel import AMBER, MINT, PINK, QUIET, WHITE, _line, _metric

    prior, sensitivity, false_positive = (p[k] for k in ("prior", "sensitivity", "false_positive"))
    masses = {"true_positive": prior*sensitivity,
              "false_negative": prior*(1-sensitivity),
              "false_positive": (1-prior)*false_positive,
              "true_negative": (1-prior)*(1-false_positive)}
    positive = masses["true_positive"]+masses["false_positive"]
    posterior = masses["true_positive"]/positive
    prior_odds = prior/(1-prior)
    likelihood_ratio = sensitivity/false_positive
    posterior_odds = masses["true_positive"]/masses["false_positive"]
    expected = {key: 10_000*mass for key, mass in masses.items()}
    primitives = []
    width, height, origin_x, origin_y = 6., 4., -5., -2.
    tagged_width = width*prior
    untagged_width = width*(1-prior)
    _rectangle(primitives, "population_true_positive", origin_x, height*(1-sensitivity)+origin_y, tagged_width, height*sensitivity, MINT)
    _rectangle(primitives, "population_false_negative", origin_x, origin_y, tagged_width, height*(1-sensitivity), PINK)
    _rectangle(primitives, "population_false_positive", origin_x+tagged_width, height*(1-false_positive)+origin_y, untagged_width, height*false_positive, AMBER)
    _rectangle(primitives, "population_true_negative", origin_x+tagged_width, origin_y, untagged_width, height*(1-false_positive), QUIET)
    # Both complete panels have fixed height but deliberately different sample
    # spaces. The second is P(H|+), not another joint-probability rectangle.
    conditional_x, conditional_width = 2.3, 1.2
    _rectangle(primitives, "positive_true_share", conditional_x, origin_y+height*(1-posterior), conditional_width, height*posterior, MINT)
    _rectangle(primitives, "positive_false_share", conditional_x, origin_y, conditional_width, height*(1-posterior), AMBER)
    for name, x, w in (("population", origin_x, width), ("conditioned", conditional_x, conditional_width)):
        _line(primitives, name+"_frame", [[x, origin_y, .05], [x+w, origin_y, .05],
              [x+w, origin_y+height, .05], [x, origin_y+height, .05], [x, origin_y, .05]], WHITE)
    _line(primitives, "conditioning_arrow", [[1.3, 0, .08], [2.05, 0, .08], [1.88, .11, .08], [2.05, 0, .08], [1.88, -.11, .08]], WHITE)
    return primitives, [
        _metric("posterior", "Tagged among positive results", 100*posterior, "%", "This conditional probability is the mint share of the right panel."),
        _metric("expected_tp", "Expected true positives", expected["true_positive"], "per 10,000", "Expected counts may be fractional; no random population was simulated."),
        _metric("expected_fp", "Expected false positives", expected["false_positive"], "per 10,000"),
        _metric("positive", "All positive results", 100*positive, "% of all objects"),
        _metric("likelihood_ratio", "Positive likelihood ratio", likelihood_ratio, "× prior odds"),
        _metric("threshold", "Prior threshold for posterior >50%", 100*false_positive/(sensitivity+false_positive), "%", "The posterior exceeds one half precisely when the prior exceeds this threshold.")
    ], {}, {"masses": masses, "expected_counts": expected, "reference_population": 10_000,
            "prior": prior, "positive_marginal": positive, "posterior": posterior,
            "prior_odds": prior_odds, "posterior_odds": posterior_odds,
            "positive_likelihood_ratio": likelihood_ratio,
            "odds_update_residual": abs(posterior_odds-prior_odds*likelihood_ratio),
            "total_mass": fsum(masses.values()), "population_display_area": width*height,
            "conditional_display_area": conditional_width*height,
            "posterior_majority_prior_threshold": false_positive/(sensitivity+false_positive)}, [
        "Every left-panel cell area divided by 24 is its exact joint probability, including very thin rare-tag cells. The right panel has fixed area 4.8 and is separately normalized to positive results only.",
        "Mint and amber together form the positive-result denominator. Detection probability P(+|H) and posterior P(H|+) answer different questions.",
        "Expected counts for 10,000 objects are probability times 10,000. They are not rounded tiles, observed integer counts, or a Monte Carlo result.",
        "The detector rates are assumed fixed for this population. The model makes no claim that a real detector has constant sensitivity or false-alarm rate across changing populations.",
        "A likelihood ratio multiplies prior odds, not prior probability. The resulting posterior is a consequence of the stated joint model, not a measure of certainty independent of its assumptions."]


def _contour_segment(level, c, extent):
    """Clip c·x=level to a square, preserving true Cartesian geometry."""
    cx, cy = c
    points = []
    if abs(cy) > 1e-12:
        for x in (-extent, extent):
            y = (level-cx*x)/cy
            if -extent-1e-10 <= y <= extent+1e-10:
                points.append([x, max(-extent, min(extent, y)), -.04])
    if abs(cx) > 1e-12:
        for y in (-extent, extent):
            x = (level-cy*y)/cx
            if -extent-1e-10 <= x <= extent+1e-10:
                point = [max(-extent, min(extent, x)), y, -.04]
                if not any(hypot(point[0]-q[0], point[1]-q[1]) < 1e-8 for q in points):
                    points.append(point)
    return points[:2]


def _direction_arrow(primitives, name, point, direction, color, z):
    from .kernel import _line

    x, y = point
    dx, dy = direction
    tip = [x+.85*dx, y+.85*dy, z]
    _line(primitives, name, [[x, y, z], tip], color)
    _line(primitives, name+"_head", [[tip[0]-.14*dx-.07*dy, tip[1]-.14*dy+.07*dx, z],
                                     tip,
                                     [tip[0]-.14*dx+.07*dy, tip[1]-.14*dy-.07*dx, z]], color)


def _lagrange(p):
    from .kernel import AMBER, CYAN, MINT, PINK, QUIET, VIOLET, _axes, _line, _metric, _sphere

    a, b, phi, theta = (p[k] for k in ("axis_a", "axis_b", "direction", "probe"))
    c = [cos(phi), sin(phi)]
    support = hypot(a*c[0], b*c[1])
    maximum = [a*a*c[0]/support, b*b*c[1]/support]
    minimum = [-v for v in maximum]
    point = [a*cos(theta), b*sin(theta)]
    tangent = [-a*sin(theta), b*cos(theta)]
    tangent_length = hypot(*tangent)
    normal = [2*point[0]/(a*a), 2*point[1]/(b*b)]
    normal_length = hypot(*normal)
    derivative = fsum(x*y for x, y in zip(c, tangent))
    value = fsum(x*y for x, y in zip(c, point))
    maximum_normal = [2*maximum[0]/(a*a), 2*maximum[1]/(b*b)]
    residual = hypot(*[x-support*y/2 for x, y in zip(c, maximum_normal)])
    primitives = []
    _axes(primitives, -3.25, 3.25, -3.25, 3.25, -.09)
    for i, fraction in enumerate((-1., -.5, 0., .5, 1.)):
        segment = _contour_segment(fraction*support, c, 3.25)
        if len(segment) == 2:
            _line(primitives, f"objective_contour_{i}", segment,
                  PINK if fraction == -1 else AMBER if fraction == 1 else QUIET)
    _line(primitives, "feasible_ellipse", [[a*cos(2*pi*i/256), b*sin(2*pi*i/256), .02]
                                            for i in range(257)], CYAN)
    _sphere(primitives, "constrained_maximum", maximum+[.07], .105, AMBER)
    _sphere(primitives, "constrained_minimum", minimum+[.07], .105, PINK)
    _sphere(primitives, "probe_point", point+[.13], .08, MINT)
    unit_tangent = [v/tangent_length for v in tangent]
    _line(primitives, "probe_tangent", [[point[i]+sign*.55*unit_tangent[i] for i in range(2)]+[.065]
                                         for sign in (-1, 1)], CYAN)
    _direction_arrow(primitives, "objective_gradient_direction", point, c, MINT, .09)
    _direction_arrow(primitives, "constraint_gradient_direction", point,
                     [v/normal_length for v in normal], VIOLET, .11)
    return primitives, [
        _metric("value", "Objective at probe c·p", value),
        _metric("maximum", "Analytic constrained maximum", support),
        _metric("gap", "Maximum − current value", max(0., support-value)),
        _metric("tangent_derivative", "Feasible derivative df/dθ", derivative, "", "Zero at both extrema. θ parametrizes the ellipse, so this is not the derivative per unit arc length."),
        _metric("gradient", "Unconstrained ||∇f||", hypot(*c), "", "The objective gradient is a nonzero constant even at constrained extrema."),
        _metric("residual", "Maximum multiplier residual", residual, "", "||∇f−λ∇g|| with λ=maximum/2.")
    ], {}, {"objective_direction": c, "probe_point": point, "probe_theta": theta,
            "probe_objective": value, "probe_tangent": tangent,
            "probe_constraint_gradient": normal, "probe_tangent_derivative": derivative,
            "probe_arclength_derivative": derivative/tangent_length,
            "maximum_point": maximum, "minimum_point": minimum,
            "maximum_objective": support, "minimum_objective": -support,
            "maximizing_theta": atan2(b*c[1], a*c[0]),
            "maximum_multiplier": support/2, "minimum_multiplier": -support/2,
            "multiplier_residual": residual,
            "probe_constraint_value": point[0]**2/a**2+point[1]**2/b**2,
            "maximum_constraint_value": maximum[0]**2/a**2+maximum[1]**2/b**2,
            "gradient_direction_display_length": .85}, [
        "The objective is linear, f=cₓx+cᵧy, with ||c||=1. It has no unconstrained maximum on the whole plane. Restricting to a compact ellipse creates finite extrema.",
        "The probe's allowed tangent is (−a sin θ,b cos θ). Its objective derivative is ∇f·p′(θ); vanishing means no first-order improvement along the curve, not a zero ambient gradient.",
        "Arrow lengths are fixed to show unit gradient directions. Their alignment is meaningful; their displayed lengths do not represent the different gradient magnitudes.",
        "For this ellipse g=x²/a²+y²/b², ∇g never vanishes on g=1. The maximum equals √((acₓ)²+(bcᵧ)²), and λ=maximum/2. The opposite point is the minimum, with negative λ.",
        "The analytic extrema follow from Cauchy–Schwarz after mapping the ellipse to a unit circle. Lagrange multiplier equations alone do not classify stationary points in arbitrary constrained problems."]


MODELS = {"svd": _svd, "bayes": _bayes, "lagrange": _lagrange}
