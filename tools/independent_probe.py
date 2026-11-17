#!/usr/bin/env python3
"""Reproduce independent Math Lab review calculations.

Required probes use the standard library. SciPy's DOP853 comparison is optional:
absence or --no-scipy records not_run and an overall partial result, never pass.
These development checks are not a formal Loom acceptance or browser witness.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import importlib.metadata
import itertools
import json
import math
from pathlib import Path
import platform
import random
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from mathlab.kernel import evaluate  # noqa: E402


def sha(data):
    return hashlib.sha256(data).hexdigest()


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)


def identities():
    return {str(path.relative_to(ROOT)): sha(path.read_bytes()) for path in
            (ROOT / "mathlab/kernel.py", ROOT / "mathlab/catalog.py", Path(__file__).resolve())}


def require(condition, message):
    if not condition:
        raise ArithmeticError(message)


def drawn_eigenvectors():
    """Recompute residuals from the emitted geometry, not the metric's value."""
    generator = random.Random(7821)
    worst = 0.0
    count = 0
    for _ in range(500):
        params = {name: generator.uniform(-2.5, 2.5) for name in ("a", "b", "c", "d")}
        params["blend"] = generator.random()
        sample = evaluate("linear", params)
        (a, b), (c, d) = sample["numerics"]["matrix"]
        lines = [row for row in sample["primitives"] if row["id"].startswith("eigenline_")]
        values = sample["numerics"]["real_eigenvalues"]
        require(len(lines) == len(values), "Drawn eigenline/value counts differ")
        for line, value in zip(lines, values):
            px, py, _ = line["points"][1]
            norm = math.hypot(px, py)
            require(norm > 0, "A drawn eigenline has no direction")
            x, y = px / norm, py / norm
            residual = math.hypot(a * x + b * y - value * x,
                                  c * x + d * y - value * y)
            worst = max(worst, residual)
            count += 1
    require(count > 0 and worst < 1e-11, "Drawn eigenvector residual exceeds the development tolerance")
    return {"seed": 7821, "matrices": 500, "drawn_real_eigenvectors": count,
            "max_recomputed_residual": worst, "absolute_development_tolerance": 1e-11,
            "scope": "Residuals of normalized emitted eigenline directions under the displayed matrix; not a theorem prover."}


def derivative_five_point():
    """A five-point stencil differs from both lesson secant approximations."""
    f = lambda x: math.sin(x) + 0.15 * x * x
    h = 1e-4
    rows = []
    bad_errors = []
    for x in (-2.5, -1.0, 0.7, 2.5):
        five = (f(x - 2 * h) - 8 * f(x - h) + 8 * f(x + h) - f(x + 2 * h)) / (12 * h)
        reference = evaluate("derivative", {"x": x})["numerics"]["analytic_slope"]
        error = abs(reference - five)
        rows.append({"x": x, "five_point": five, "lesson_analytic": reference, "absolute_difference": error})
        bad_errors.append(abs(math.cos(x) - five))
    tolerance = 1e-8
    require(all(row["absolute_difference"] < tolerance for row in rows), "Analytic derivative disagrees with the five-point probe")
    caught = max(bad_errors) > tolerance
    require(caught, "The omitted-quadratic-derivative twin was not distinguished")
    return {"stencil_h": h, "rows": rows, "absolute_development_tolerance": tolerance,
            "negative_control": {"description": "Omit the 0.3x derivative contribution", "max_difference": max(bad_errors), "caught": caught},
            "scope": "Finite-difference corroboration of the authored derivative; finite precision and truncation remain."}


def integral_quadrature_and_geometry():
    """Numerically integrate independently of the lesson's antiderivative."""
    f = lambda x: 0.25 * x * x + 0.35 * math.cos(2 * x) + 1.2
    count = 20_000
    rows = []
    for a, b in ((-3.0, 0.2), (-3.0, 3.0), (-0.25, 2.75)):
        dx = (b - a) / count
        quadrature = math.fsum(f(a + (i + 0.5) * dx) for i in range(count)) * dx
        sample = evaluate("integral", {"a": a, "b": b})
        reference = sample["numerics"]["reference"]
        error = abs(reference - quadrature)
        # Independent midpoint-rule bound using |f''| <= 1.9, plus rounding guard.
        bound = 1.9 * (b - a) ** 3 / (24 * count * count)
        require(error <= bound + 1e-11, "Antiderivative and independent quadrature disagree beyond the stated bound")
        drawn = math.fsum(row["size"][0] * row["size"][1] for row in sample["primitives"] if row["kind"] == "box")
        approximation = sample["numerics"]["approximation"]
        require(abs(drawn - approximation) <= 1e-11 * (1 + abs(approximation)), "Emitted rectangle widths no longer represent the numeric rectangle sum")
        rows.append({"a": a, "b": b, "subintervals": count, "independent_midpoint_quadrature": quadrature,
                     "lesson_analytic_integral": reference, "absolute_difference": error,
                     "quadrature_error_bound": bound, "rounding_guard": 1e-11,
                     "emitted_rectangle_area": drawn, "lesson_rectangle_sum": approximation,
                     "emitted_to_numeric_area_ratio": drawn / approximation})
    return {"rows": rows, "scope": "Independent dense quadrature checks the analytic reference; emitted box area separately checks the visual rectangle-sum contract."}


def expanded_hessian_recurrence():
    """Iterate an explicitly expanded 2x2 Hessian instead of modal coordinates."""
    angle = 0.4
    c, s = math.cos(angle), math.sin(angle)
    rows = []
    for rate, condition in ((0.15, 8), (0.05, 20), (0.28, 20), (0.1, 20)):
        h00, h01 = c * c + condition * s * s, (1 - condition) * c * s
        h11 = s * s + condition * c * c
        x, y = 2.2, 1.6
        for _ in range(60):
            x, y = x - rate * (h00 * x + h01 * y), y - rate * (h01 * x + h11 * y)
        sample = evaluate("gradient", {"rate": rate, "condition": condition, "steps": 60})
        qx, qy = sample["numerics"]["iterates"][-1]
        difference = math.hypot(x - qx, y - qy) / (1 + math.hypot(x, y))
        require(difference < 1e-11, "Expanded-Hessian recurrence disagrees with the lesson iteration")
        rows.append({"rate": rate, "condition": condition, "steps": 60,
                     "expanded_hessian": [[h00, h01], [h01, h11]], "independent_endpoint": [x, y],
                     "lesson_endpoint": [qx, qy], "relative_difference": difference,
                     "contraction_factor": sample["numerics"]["contraction_factor"]})
    return {"rotation_radians": angle, "relative_development_tolerance": 1e-11, "rows": rows,
            "scope": "A separately expanded Hessian recurrence checks stable, unstable and neutral-boundary cases; not a proof about arbitrary optimization losses."}


def framing_violation_count(sample):
    bounds = sample["bounds"]
    count = 0
    for row in sample["primitives"]:
        points = list(row.get("points", []))
        if "position" in row:
            extents = [row["radius"]] * 3 if row["kind"] == "sphere" else [value / 2 for value in row["size"]]
            points.extend([[row["position"][i] + sign * extents[i] for i in range(3)] for sign in (-1, 1)])
        for point in points:
            require(all(math.isfinite(v) for v in point), "Nonfinite emitted position")
            count += any(abs(point[i] - bounds["center"][i]) > bounds["size"][i] / 2 + 1e-9 for i in range(3))
    return count


def dynamics_corners_and_framing():
    rows = []
    for sigma, rho, beta, dt in itertools.product((5, 16), (1, 40), (1, 4), (0.005, 0.03)):
        sample = evaluate("lorenz", {"sigma": sigma, "rho": rho, "beta": beta, "dt": dt, "duration": 20, "separation": 0.1})
        numerics = sample["numerics"]
        require(all(math.isfinite(v) for key in ("endpoint", "nearby_endpoint", "fine_endpoint") for v in numerics[key]), "Nonfinite Lorenz endpoint")
        outside = framing_violation_count(sample)
        require(outside == 0, "A valid Lorenz corner leaves the declared geometry bounds")
        rows.append({"sigma": sigma, "rho": rho, "beta": beta, "maximum_step": dt,
                     "duration": 20, "initial_separation": 0.1, "points_outside_bounds": outside,
                     "endpoint_halfstep_difference": numerics["refinement"]})
    for lesson, params in (("integral", {}), ("fourier", {"terms": 12, "phase": math.pi}),
                           ("gradient", {"condition": 20, "rate": 0.28, "steps": 60})):
        require(framing_violation_count(evaluate(lesson, params)) == 0, "A reviewed scene leaves its declared geometry bounds: " + lesson)
    return {"lorenz_corner_count": len(rows), "rows": rows,
            "additional_framing_cases": ["default integral", "12-harmonic Fourier at phase pi", "unstable gradient"],
            "scope": "Finite endpoint and framing checks at sixteen declared corners, not exhaustive parameter coverage or proof of chaos."}


def scipy_rk4_ladder(disabled=False):
    if disabled:
        return {"status": "not_run", "reason": "Explicit --no-scipy option", "dependency": "scipy"}
    try:
        from scipy.integrate import solve_ivp
        version = importlib.metadata.version("scipy")
    except (ImportError, importlib.metadata.PackageNotFoundError) as error:
        return {"status": "not_run", "reason": type(error).__name__ + ": " + str(error), "dependency": "scipy"}
    rhs = lambda t, p: (10 * (p[1] - p[0]), p[0] * (28 - p[2]) - p[1], p[0] * p[1] - (8 / 3) * p[2])
    solution = solve_ivp(rhs, (0, 2), (1, 1, 1), method="DOP853", rtol=1e-12, atol=1e-13)
    require(solution.success, "Independent DOP853 integration did not finish")
    reference = solution.y[:, -1].tolist()
    rows = []
    for step in (0.02, 0.01, 0.005):
        endpoint = evaluate("lorenz", {"duration": 2, "dt": step})["numerics"]["endpoint"]
        rows.append({"rk4_maximum_step": step, "endpoint": endpoint, "endpoint_norm_difference": math.dist(endpoint, reference)})
    errors = [row["endpoint_norm_difference"] for row in rows]
    require(all(b < a for a, b in zip(errors, errors[1:])) and errors[-1] < 1e-4,
            "Short-time RK4 refinement did not approach the independent integration")
    return {"status": "pass", "dependency": "scipy", "version": version, "reference_method": "DOP853",
            "rtol": 1e-12, "atol": 1e-13, "duration": 2, "initial": [1, 1, 1],
            "parameters": {"sigma": 10, "rho": 28, "beta": 8 / 3}, "reference_endpoint": reference,
            "rows": rows, "scope": "Independent numerical corroboration at short time; neither solver is an exact solution or rigorous error certificate."}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "receipts/independent-math.json")
    parser.add_argument("--no-scipy", action="store_true")
    args = parser.parse_args()
    source = identities()
    report = {"schema": "mathlab.independent-probes/1", "created_utc": datetime.now(timezone.utc).isoformat(),
              "environment": {"python": platform.python_version(), "platform": platform.platform(), "machine": platform.machine()},
              "source_sha256": source, "checks": [], "status": "not_run",
              "limits_scope": "Authored development tolerances and stated analytic quadrature bound; not a formal precommitted Loom acceptance run.",
              "limitations": ["One local numerical host; no browser, native X3D render, hardware GPU, MCP transport or human learning measurement.",
                              "Finite sampled comparisons corroborate authored models; they do not prove theorems or generalize to arbitrary functions/ODEs."]}
    for name, function in (("drawn_eigenvectors", drawn_eigenvectors), ("five_point_derivative", derivative_five_point),
                           ("independent_quadrature_and_rectangle_area", integral_quadrature_and_geometry),
                           ("expanded_hessian_recurrence", expanded_hessian_recurrence),
                           ("dynamics_corners_and_framing", dynamics_corners_and_framing),
                           ("optional_scipy_dop853", lambda: scipy_rk4_ladder(args.no_scipy))):
        start = time.perf_counter()
        try:
            observation = function()
            row = {"id": name, "status": observation.pop("status", "pass"), "observation": observation}
        except Exception as error:
            row = {"id": name, "status": "fail", "error": type(error).__name__ + ": " + str(error)}
        row["elapsed_seconds"] = time.perf_counter() - start
        report["checks"].append(row)
        print(row["status"].upper(), name)
    report["source_drift"] = "none" if identities() == source else "changed"
    states = [row["status"] for row in report["checks"]]
    report["status"] = "fail" if "fail" in states or report["source_drift"] != "none" else "partial" if "not_run" in states else "pass"
    report["report_sha256"] = sha(canonical(report).encode("utf-8"))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, allow_nan=False, indent=2) + "\n", encoding="utf-8")
    print(canonical({"status": report["status"], "checks": len(states), "source_drift": report["source_drift"], "output": str(args.output)}))
    return 1 if report["status"] == "fail" else 0


if __name__ == "__main__":
    raise SystemExit(main())
