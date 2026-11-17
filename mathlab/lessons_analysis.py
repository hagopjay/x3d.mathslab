"""Bounded lessons on complex motion, local approximation and superposition.

The catalog is data only. Renderer-neutral builders import shared geometry
helpers lazily so catalog discovery never creates a kernel import cycle.
"""
from math import cos, factorial, hypot, pi, sin


def _p(key, label, lo, hi, step, default, unit="", integer=False):
    return {"id": key, "label": label, "min": lo, "max": hi, "step": step,
            "default": default, "unit": unit,
            "type": "integer" if integer else "number"}


LESSONS = [
    {
        "id": "complex", "title": "Multiplication Becomes Motion",
        "shortName": "Complex rotations and roots", "domain": "COMPLEX NUMBERS",
        "tagline": "Multiply lengths. Add angles. Close a polygon.",
        "accent": "#ffc976", "level": "Grade 10–12",
        "prerequisites": ["Trigonometry", "Complex numbers a + bi"],
        "formula": "zₜ=rᵗ cis(tθ)    ·    zₜʲ=rᵗʲ cis(jtθ)    ·    ζⱼ=cis(2πj/n)",
        "description": "Repeated complex multiplication traces an orbit in the complex plane. Compare it with the n roots of unity, then discover when a spiral closes into a regular polygon.",
        "parameters": [
            _p("radius", "Multiplier modulus r", .7, 1.15, .01, 1),
            _p("angle", "Multiplier angle θ", -pi, pi, .02, 2*pi/5, "rad"),
            _p("progress", "Multiplication progress t", 0, 1, .01, 1),
            _p("roots", "Roots / multiplication steps n", 3, 12, 1, 5, integer=True),
        ],
        "animation": {"parameter": "progress", "min": 0, "max": 1,
                      "speed": .16, "mode": "pingpong"},
        "story": [
            {"title": "Predict a product", "text": "The cyan arrow is zₜ. Each amber point applies exactly the same multiplication again: multiply its distance by rᵗ and add tθ to its angle."},
            {"title": "Find closure", "text": "Use the pentagon preset. At full progress, amber powers coincide with violet roots. Set r below one: the angles still turn, but the orbit spirals inward."},
            {"title": "Explain the constraint", "text": "A nonzero orbit returns to 1 after n multiplications precisely when r=1 and nθ is an integer multiple of 2π. Some angles visit only a subset of the n roots before repeating."},
        ],
        "challenge": {"question": "For n=6, must a sixth root visit all six vertices before returning to 1?",
                      "answer": "No. θ=2π/3 visits only three vertices and repeats twice. A root cis(2πk/n) visits n/gcd(k,n) distinct points. The primitive roots have gcd(k,n)=1."},
        "presets": [
            {"title": "A closed pentagon", "params": {"radius": 1, "angle": 2*pi/5, "progress": 1, "roots": 5}, "why": "Five equal angle additions complete exactly one revolution."},
            {"title": "A spiral, same angles", "params": {"radius": .84, "angle": 2*pi/5, "progress": 1, "roots": 5}, "why": "Angle closure alone cannot restore a shrinking modulus."},
            {"title": "Six steps, three vertices", "params": {"radius": 1, "angle": 2*pi/3, "progress": 1, "roots": 6}, "why": "A sixth root need not be a primitive sixth root."},
        ],
        "legend": [{"label": "First multiplier zₜ", "color": "#47d6ff"},
                   {"label": "Repeated powers", "color": "#ffba52"},
                   {"label": "n roots of unity", "color": "#a68cff"}],
        "resources": [{"title": "OpenStax · Polar Form of Complex Numbers",
                       "url": "https://openstax.org/books/precalculus-2e/pages/8-5-polar-form-of-complex-numbers",
                       "note": "Read the product rule, De Moivre's theorem and the formula for nth roots; explain the polygon before calculating its coordinates."}],
    },
    {
        "id": "taylor", "title": "How Far Can a Local Idea Reach?",
        "shortName": "Taylor's local lens", "domain": "SERIES AND APPROXIMATION",
        "tagline": "Match derivatives, then measure where the match lasts.",
        "accent": "#ff93b9", "level": "Undergraduate 1",
        "prerequisites": ["Derivatives", "Factorials", "Trigonometric functions"],
        "formula": "Tₙ(x)=Σₖ₌₀ⁿ sin⁽ᵏ⁾(a)(x−a)ᵏ/k!    ·    |sin x−Tₙ(x)|≤|x−a|ⁿ⁺¹/(n+1)!",
        "description": "A polynomial remembers the sine curve's derivatives at one center. Widen the window, move the center and compare the actual error with a rigorous remainder bound.",
        "parameters": [
            _p("center", "Expansion center a", -2, 2, .05, 0),
            _p("degree", "Polynomial degree n", 0, 10, 1, 3, integer=True),
            _p("radius", "Window radius R", .4, 3.5, .05, 2.5),
            _p("probe", "Probe offset as fraction of R", -1, 1, .01, .8),
        ],
        "story": [
            {"title": "Match a neighborhood", "text": "At x=a, cyan sine and amber polynomial share derivatives through degree n. Degree one is the familiar tangent; higher terms match bending and changes of bending."},
            {"title": "Move the evidence", "text": "The pink ribbon is actual signed separation, not an uncertainty interval. Move the probe; its violet bracket is the pointwise Taylor bound. The bracket can be much larger than the observed error."},
            {"title": "Justify the reach", "text": "Every derivative of sine has magnitude at most one. Taylor's theorem therefore bounds the remainder by |x−a|^(n+1)/(n+1)!. This bound tends to zero for every fixed real x as n grows; smoothness alone would not justify that conclusion for another function."},
        ],
        "challenge": {"question": "Why does changing the Maclaurin degree from 3 to 4 leave the amber curve unchanged?",
                      "answer": "The fourth derivative of sine at zero is zero, so the x⁴ coefficient vanishes. The theorem's general remainder bound still changes. Moving the center away from zero usually makes that coefficient nonzero."},
        "presets": [
            {"title": "The tangent is local", "params": {"center": 0, "degree": 1, "radius": 3, "probe": .9}, "why": "The correct slope at zero does not guarantee accuracy three units away."},
            {"title": "A missing fourth term", "params": {"center": 0, "degree": 4, "radius": 2.5, "probe": .8}, "why": "Compare degree three: symmetry makes the fourth coefficient vanish."},
            {"title": "Move the local lens", "params": {"center": 1.5, "degree": 5, "radius": 2, "probe": -.9}, "why": "A Taylor polynomial is tied to its center, not to the origin."},
        ],
        "legend": [{"label": "True sin x", "color": "#47d6ff"},
                   {"label": "Taylor polynomial", "color": "#ffba52"},
                   {"label": "Actual error ribbon", "color": "#ff59a8"},
                   {"label": "Pointwise error bound", "color": "#a68cff"}],
        "resources": [{"title": "OpenStax · Taylor and Maclaurin Series",
                       "url": "https://openstax.org/books/calculus-volume-2/pages/6-3-taylor-and-maclaurin-series",
                       "note": "Use Taylor's theorem with remainder to distinguish a matching polynomial, a convergent series and a justified error guarantee."}],
    },
    {
        "id": "waves", "title": "Two Moving Waves Make Still Nodes",
        "shortName": "Waves, nodes and hidden motion", "domain": "WAVES AND DIFFERENTIAL EQUATIONS",
        "tagline": "A stationary pattern can hide two travelling waves.",
        "accent": "#8affcf", "level": "Undergraduate 1",
        "prerequisites": ["Sine addition identities", "Frequency and wavelength"],
        "formula": "A sin(kx−ωt)+A sin(kx+ωt)=2A sin(kx)cos(ωt)    ·    k=nπ/L, ω=ck",
        "description": "Compare two counterpropagating waves with their sum on a fixed string. Watch the permanent nodes, then discover why a momentarily flat string can still carry energy.",
        "parameters": [
            _p("mode", "Fixed-end mode n", 1, 6, 1, 3, integer=True),
            _p("amplitude", "Each travelling amplitude A", .2, .8, .02, .65),
            _p("time", "Time as fraction of period t/T", 0, 1, .01, .12, "cycles"),
            _p("speed", "Wave speed c", .5, 3, .05, 1, "units/s"),
            _p("probe", "Probe position x/L", 0, 1, .01, .37),
        ],
        "animation": {"parameter": "time", "min": 0, "max": 1,
                      "speed": .2, "mode": "loop"},
        "story": [
            {"title": "Read the three lanes", "text": "Cyan above is right-travelling displacement; pink below is left-travelling displacement. Amber in the middle is their pointwise sum. Vertical and depth offsets separate the displays; subtract those offsets before adding coordinates."},
            {"title": "Keep a node still", "text": "Mint beads mark x=jL/n. Those locations stay at zero for all times, even though both component waves move. The components individually do not obey the fixed-end constraint; their sum does."},
            {"title": "Look beyond shape", "text": "At t/T=1/4 the entire string is instantaneously flat but most points move fastest. The ideal small-slope string's energy is entirely kinetic then. At maximum deflection it is entirely elastic. The energy shares come from integrating the whole ideal string, not from one probe."},
        ],
        "challenge": {"question": "When the whole amber string crosses zero at once, has its energy vanished?",
                      "answer": "No. In this ideal undamped standing mode, normalized kinetic energy is sin²(ωt) and elastic energy is cos²(ωt). At t/T=1/4 the sum is flat and kinetic energy is maximal. Permanent nodes are the locations that stay zero at every time."},
        "presets": [
            {"title": "The fundamental", "params": {"mode": 1, "amplitude": .65, "time": 0, "speed": 1, "probe": .5}, "why": "One antinode fits between two fixed endpoints."},
            {"title": "Flat, still moving", "params": {"mode": 3, "amplitude": .65, "time": .25, "speed": 1, "probe": .5}, "why": "Instantaneous zero displacement is different from a permanent node."},
            {"title": "A permanent node", "params": {"mode": 4, "amplitude": .65, "time": .125, "speed": 2, "probe": .5}, "why": "The middle point remains zero throughout the cycle in every even mode."},
        ],
        "legend": [{"label": "Upper: right-going wave", "color": "#47d6ff"},
                   {"label": "Lower: left-going wave", "color": "#ff59a8"},
                   {"label": "Middle: sum", "color": "#ffba52"},
                   {"label": "Permanent nodes", "color": "#5cffba"}],
        "resources": [{"title": "OpenStax · Standing Waves and Resonance",
                       "url": "https://openstax.org/books/university-physics-volume-1/pages/16-6-standing-waves-and-resonance",
                       "note": "Derive the sum identity and fixed-end mode condition; distinguish travelling components from the resultant standing pattern."},
                      {"title": "MIT OCW 8.03SC · Lecture 9",
                       "url": "https://ocw.mit.edu/courses/8-03sc-physics-iii-vibrations-and-waves-fall-2016/pages/part-i-mechanical-vibrations-and-waves/lecture-9/",
                       "note": "Extend the visual experiment into normal modes and the wave equation."}],
    },
]


def _complex(p):
    from .kernel import _axes, _line, _metric, _sphere, AMBER, CYAN, MINT, QUIET, VIOLET

    radius, theta, progress, n = (p[k] for k in ("radius", "angle", "progress", "roots"))
    rho, phi = radius**progress, theta*progress
    multiplier = [rho*cos(phi), rho*sin(phi)]
    powers = [[1., 0.]]
    for _ in range(n):
        x, y = powers[-1]
        a, b = multiplier
        powers.append([a*x-b*y, b*x+a*y])
    polar = [rho**n*cos(n*phi), rho**n*sin(n*phi)]
    roots = [[cos(2*pi*j/n), sin(2*pi*j/n)] for j in range(n)]
    primitives = []
    extent = max(1.5, rho**n*1.1)
    _axes(primitives, -extent, extent, -extent, extent, -.05)
    _line(primitives, "unit_circle", [[cos(2*pi*j/180), sin(2*pi*j/180), -.04]
                                     for j in range(181)], QUIET)
    _line(primitives, "root_polygon", [[x, y, -.02] for x, y in roots+[roots[0]]], VIOLET)
    for j, (x, y) in enumerate(roots):
        _sphere(primitives, f"root_{j}", [x, y, -.02], .045, VIOLET)
    spiral = [[rho**u*cos(u*phi), rho**u*sin(u*phi), .02]
              for u in (n*j/240 for j in range(241))]
    _line(primitives, "continuous_power_interpolation", spiral, AMBER)
    _line(primitives, "discrete_multiplication_steps", [[x, y, .035] for x, y in powers], QUIET)
    for j, (x, y) in enumerate(powers):
        _sphere(primitives, f"power_{j}", [x, y, .06], .06 if j else .085,
                AMBER if j else MINT)
    _line(primitives, "multiplier", [[0, 0, .12], multiplier+[.12]], CYAN)
    _sphere(primitives, "multiplier_tip", multiplier+[.12], .075, CYAN)
    endpoint = powers[-1]
    residual = hypot(endpoint[0]-polar[0], endpoint[1]-polar[1])
    closure = hypot(endpoint[0]-1, endpoint[1])
    return primitives, [
        _metric("modulus", "Displayed multiplier modulus", rho, "× per step"),
        _metric("angle", "Displayed angle added", phi, "rad per step"),
        _metric("endpoint_modulus", "Modulus after n steps", hypot(*endpoint), "", "Compare with r^(tn)."),
        _metric("closure", "Distance of zₜⁿ from 1", closure, "", "Zero indicates closure after n steps, not necessarily n distinct vertices."),
        _metric("polar_residual", "Cartesian / polar endpoint difference", residual, "", "Repeated Cartesian products compared with the closed polar formula."),
    ], {}, {"multiplier": multiplier, "powers": powers, "roots": roots,
            "displayed_modulus": rho, "displayed_angle": phi,
            "polar_endpoint": polar, "cartesian_polar_residual": residual,
            "closure_distance": closure, "endpoint_modulus": hypot(*endpoint)}, [
        "Violet points solve ζⁿ=1. Amber points are successive powers of the displayed multiplier; only particular modulus/angle choices make the two sets coincide.",
        "The thin amber curve chooses the unwrapped angle tθ to interpolate between integer powers. It is one chosen continuous interpolation, not a claim about a unique complex logarithm.",
        "Progress interpolates the multiplier multiplicatively: rᵗ cis(tθ). At t=0 the multiplier is 1; at t=1 it is the chosen target. Angles are in radians.",
    ]


def _taylor(p):
    from .kernel import _axes, _line, _metric, _sphere, AMBER, CYAN, MINT, PINK, QUIET, VIOLET

    a, degree, radius, probe = (p[k] for k in ("center", "degree", "radius", "probe"))
    derivative_cycle = (sin(a), cos(a), -sin(a), -cos(a))
    coefficients = [derivative_cycle[k % 4]/factorial(k) for k in range(degree+1)]

    def polynomial(x):
        value = 0.
        for c in reversed(coefficients):
            value = value*(x-a)+c
        return value

    xs = [a-radius+2*radius*j/160 for j in range(161)]
    true = [sin(x) for x in xs]
    approximate = [polynomial(x) for x in xs]
    point_x = a+radius*probe
    reference, estimate = sin(point_x), polynomial(point_x)
    error = estimate-reference
    bound = abs(point_x-a)**(degree+1)/factorial(degree+1)
    window_bound = radius**(degree+1)/factorial(degree+1)
    primitives = []
    low = min(-1.3, min(approximate)-.2, estimate-bound)
    high = max(1.3, max(approximate)+.2, estimate+bound)
    _axes(primitives, xs[0]-.2, xs[-1]+.2, low, high, -.05)
    _line(primitives, "center_guide", [[a, low, -.04], [a, high, -.04]], QUIET)
    ribbon = []
    indices = []
    for x, actual, approx in zip(xs, true, approximate):
        ribbon.extend([[x, actual, -.015], [x, approx, -.015]])
    for j in range(160):
        indices.extend([2*j, 2*j+1, 2*j+3, 2*j+2, -1])
    primitives.append({"kind": "mesh", "id": "actual_error_ribbon", "points": ribbon,
                       "indices": indices, "color": PINK[:], "transparency": .82})
    _line(primitives, "true_sine", [[x, y, .01] for x, y in zip(xs, true)], CYAN)
    _line(primitives, "taylor_polynomial", [[x, y, .025] for x, y in zip(xs, approximate)], AMBER)
    _sphere(primitives, "expansion_center", [a, sin(a), .07], .075, MINT)
    _line(primitives, "probe_error", [[point_x, reference, .08], [point_x, estimate, .08]], PINK)
    _sphere(primitives, "probe_true", [point_x, reference, .08], .055, CYAN)
    _sphere(primitives, "probe_polynomial", [point_x, estimate, .11], .055, AMBER)
    bracket_x = point_x+.055*radius
    _line(primitives, "pointwise_remainder_bracket",
          [[bracket_x, estimate-bound, .04], [bracket_x, estimate+bound, .04]], VIOLET)
    for name, y in (("lower", estimate-bound), ("upper", estimate+bound)):
        _line(primitives, "bound_"+name,
              [[bracket_x-.035*radius, y, .04], [bracket_x+.035*radius, y, .04]], VIOLET)
    return primitives, [
        _metric("probe_x", "Probe x", point_x, "", "x=a+R·probe fraction."),
        _metric("polynomial", "Taylor value Tₙ(x)", estimate),
        _metric("error", "Signed error Tₙ(x) − sin x", error),
        _metric("bound", "Guaranteed pointwise |error| ≤", bound, "", "Lagrange remainder with |sin^(n+1)(ξ)|≤1; roundoff is separate."),
        _metric("window_bound", "Uniform window |error| ≤", window_bound, "", "Valid throughout [a−R,a+R], not merely at the sampled vertices."),
    ], {}, {"center": a, "degree": degree, "coefficients": coefficients,
            "x": xs, "reference_values": true, "polynomial_values": approximate,
            "probe_x": point_x, "reference": reference, "approximation": estimate,
            "signed_error": error, "remainder_bound": bound, "window_bound": window_bound}, [
        "The violet bracket is centered on the polynomial value; Taylor's theorem puts the true value inside it. Its validity comes from a derivative bound on the entire interval, not from this plot.",
        "At a=0 every even coefficient vanishes. A nominal increase in degree can therefore leave the polynomial unchanged while changing this general remainder bound.",
        "Increasing degree need not improve pointwise error monotonically. For sine the stated factorial remainder does tend to zero at every fixed x; a generic smooth function need not equal its Taylor series.",
    ]


def _waves(p):
    from .kernel import _line, _metric, _sphere, AMBER, CYAN, MINT, PINK, QUIET

    mode, amplitude, time, speed, probe = (p[k] for k in ("mode", "amplitude", "time", "speed", "probe"))
    length = 6.
    k = mode*pi/length
    omega = speed*k
    phase = 2*pi*time
    period = 2*pi/omega
    physical_time = time*period
    xs = [length*j/240 for j in range(241)]
    right = [amplitude*sin(k*x-phase) for x in xs]
    left = [amplitude*sin(k*x+phase) for x in xs]
    total = [r+l for r, l in zip(right, left)]
    reference = [2*amplitude*sin(k*x)*cos(phase) for x in xs]
    nodes = [length*j/mode for j in range(mode+1)]
    offsets = {"right": [0, 2.7, -.25], "left": [0, -2.7, .25], "sum": [0, 0, 0]}
    primitives = []
    for name, ys, color in (("right", right, CYAN), ("left", left, PINK), ("sum", total, AMBER)):
        _, lane_y, lane_z = offsets[name]
        _line(primitives, name+"_baseline", [[-3, lane_y, lane_z-.04], [3, lane_y, lane_z-.04]], QUIET)
        _line(primitives, name+"_wave", [[x-3, y+lane_y, lane_z] for x, y in zip(xs, ys)], color)
    for sign in (-1, 1):
        _line(primitives, f"sum_envelope_{sign}",
              [[x-3, sign*2*amplitude*abs(sin(k*x)), -.04] for x in xs], QUIET)
    for j, x in enumerate(nodes):
        _sphere(primitives, f"permanent_node_{j}", [x-3, 0, .04], .065, MINT)
    probe_x = probe*length
    probe_right = amplitude*sin(k*probe_x-phase)
    probe_left = amplitude*sin(k*probe_x+phase)
    probe_sum = probe_right+probe_left
    for name, value, color in (("right", probe_right, CYAN), ("left", probe_left, PINK), ("sum", probe_sum, AMBER)):
        _, lane_y, lane_z = offsets[name]
        _line(primitives, name+"_probe_displacement",
              [[probe_x-3, lane_y, lane_z+.04], [probe_x-3, lane_y+value, lane_z+.04]], color)
        _sphere(primitives, name+"_probe", [probe_x-3, lane_y+value, lane_z+.04], .065, color)
    # Direction arrows show the propagation of phase, not particle velocity.
    for name, x0, x1, lane_y, color in (("right", -2.8, -2.1, 3.65, CYAN),
                                      ("left", 2.8, 2.1, -3.65, PINK)):
        direction = 1 if x1>x0 else -1
        _line(primitives, name+"_direction", [[x0, lane_y, 0], [x1, lane_y, 0]], color)
        _line(primitives, name+"_arrowhead",
              [[x1-.14*direction, lane_y-.08, 0], [x1, lane_y, 0],
               [x1-.14*direction, lane_y+.08, 0]], color)
    residual = max(abs(y-r) for y, r in zip(total, reference))
    kinetic, potential = sin(phase)**2, cos(phase)**2
    velocity = -2*amplitude*omega*sin(k*probe_x)*sin(phase)
    return primitives, [
        _metric("nodes", "Permanent nodes including endpoints", len(nodes)),
        _metric("period", "Physical period T", period, "s", "String length L=6. T=2L/(nc)."),
        _metric("time_seconds", "Physical time represented", physical_time, "s", "The time control is a fraction of one current period; changing c changes physical time at the same frozen phase."),
        _metric("kinetic", "Whole-string kinetic energy share", kinetic, "of total", "Ideal undamped linear string; normalized integral over the whole string."),
        _metric("potential", "Whole-string elastic energy share", potential, "of total"),
        _metric("sum_residual", "Sum / standing-form max difference", residual, "", "Sampled floating-point check of the sine addition identity."),
    ], {}, {"length": length, "wavenumber": k, "angular_frequency": omega,
            "period": period, "time_seconds": physical_time, "phase": phase,
            "x": xs, "right": right, "left": left, "sum": total,
            "standing_reference": reference, "nodes": nodes,
            "display_offsets": offsets, "sum_identity_residual": residual,
            "kinetic_energy_fraction": kinetic, "potential_energy_fraction": potential,
            "probe_x": probe_x, "probe_right": probe_right, "probe_left": probe_left,
            "probe_sum": probe_sum, "probe_velocity": velocity}, [
        "All lanes share the same horizontal coordinate x−3. Upper and lower displays are translated by y=±2.7 and z=∓0.25; those are viewing offsets, not physical displacements.",
        "A node remains zero for every time. At a quarter period all displacements are zero only instantaneously, and the non-node points generally have nonzero transverse velocity.",
        "Wave speed c controls phase propagation. A material point moves transversely and its speed is not c. The time slider uses t/T, so changing c at a frozen slider position preserves shape but changes period and physical time.",
        "Energy shares assume the ideal linear, undamped, small-slope string with uniform mass density and tension. The geometry is a conceptual amplitude display, not a nonlinear string solver.",
    ]


MODELS = {"complex": _complex, "taylor": _taylor, "waves": _waves}
