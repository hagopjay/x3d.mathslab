#!/usr/bin/env python3
"""Reproduce independent randomized checks for the six Aha Atlas models.

The standard-library checks always run. NumPy/SciPy comparisons are optional;
missing dependencies produce not_run checks and an overall partial receipt.
No Manim execution, browser rendering, or learning-outcome measurement occurs.
"""
from __future__ import annotations

import argparse
import cmath
from datetime import datetime, timezone
import hashlib
import importlib.metadata
import json
import math
from pathlib import Path
import platform
import random
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from mathlab.catalog import catalog
from mathlab.kernel import evaluate
from mathlab.manim_bridge import generate_manim
from mathlab.x3d import to_x3d

SEED = 24021
CASES = 60


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=False, allow_nan=False)


def sha(value):
    return hashlib.sha256(value).hexdigest()


def identities():
    names = ("mathlab/catalog.py", "mathlab/kernel.py", "mathlab/lessons_analysis.py",
             "mathlab/lessons_structures.py", "mathlab/x3d.py", "mathlab/manim_bridge.py",
             "tools/probe_aha.py")
    return {name: sha((ROOT / name).read_bytes()) for name in names}


def within(value, tolerance, message):
    if not math.isfinite(value) or value > tolerance:
        raise ArithmeticError(f"{message}: {value!r} exceeds {tolerance!r}")


def configs(lesson, seed):
    rng = random.Random(seed)
    spec = next(row for row in catalog() if row["id"] == lesson)
    for _ in range(CASES):
        yield {p["id"]: rng.randint(int(p["min"]), int(p["max"]))
               if p["type"] == "integer" else rng.uniform(p["min"], p["max"])
               for p in spec["parameters"]}


def complex_powers():
    worst = 0.
    for p in configs("complex", SEED):
        data = evaluate("complex", p)["numerics"]
        z = cmath.rect(p["radius"]**p["progress"], p["angle"]*p["progress"])
        worst = max(worst, abs(complex(*data["powers"][-1])-z**p["roots"]))
        for root in data["roots"]:
            within(abs(complex(*root)**p["roots"]-1), 2e-14, "Root-of-unity power")
    within(worst, 1e-12, "Cartesian multiplication versus cmath integer power")
    return {"cases": CASES, "seed": SEED, "max_endpoint_absolute_difference": worst,
            "endpoint_absolute_tolerance": 1e-12, "root_absolute_tolerance": 2e-14,
            "reference": "Python cmath polar construction and built-in complex integer power"}


def taylor_direct_sum():
    worst, excess = 0., 0.
    for p in configs("taylor", SEED+1):
        data = evaluate("taylor", p)["numerics"]
        a, x, n = p["center"], data["probe_x"], p["degree"]
        # Complex exponentials supply derivatives independently of the model's
        # sine/cosine derivative-cycle array and Horner polynomial evaluator.
        reference = math.fsum((1j**j*cmath.exp(1j*a)).imag*(x-a)**j/math.factorial(j)
                              for j in range(n+1))
        worst = max(worst, abs(reference-data["approximation"]))
        excess = max(excess, abs(data["signed_error"])-data["remainder_bound"])
    within(worst, 5e-13, "Horner polynomial versus direct derivative sum")
    within(excess, 1e-12, "Observed sine approximation error minus Taylor bound")
    return {"cases": CASES, "seed": SEED+1, "max_direct_sum_difference": worst,
            "direct_sum_absolute_tolerance": 5e-13,
            "max_error_above_analytic_bound": excess, "roundoff_allowance": 1e-12,
            "reference": "Complex-exponential derivatives summed directly; analytic sine remainder inequality"}


def waves_identity():
    worst = 0.
    for p in configs("waves", SEED+2):
        data = evaluate("waves", p)["numerics"]
        for x, y in zip(data["x"], data["sum"]):
            reference = 2*p["amplitude"]*math.sin(data["wavenumber"]*x)*math.cos(data["phase"])
            worst = max(worst, abs(y-reference))
    within(worst, 1e-12, "Travelling-wave sum versus standing-wave identity")
    return {"cases": CASES, "seed": SEED+2, "max_sample_absolute_difference": worst,
            "absolute_tolerance": 1e-12, "reference": "Sine addition identity evaluated at all emitted abscissae"}


def probability_reference(np, stats):
    worst_pmf, worst_gap = 0., 0.
    for p in configs("probability", SEED+3):
        data = evaluate("probability", p)["numerics"]
        outcomes = np.arange(p["n"]+1)
        pmf = stats.binom.pmf(outcomes, p["n"], p["p"])
        worst_pmf = max(worst_pmf, float(np.max(np.abs(pmf-data["probabilities"]))))
        sd = math.sqrt(p["n"]*p["p"]*(1-p["p"]))
        normal = stats.norm.cdf((outcomes+.5-p["n"]*p["p"])/sd)
        gap = float(np.max(np.abs(stats.binom.cdf(outcomes, p["n"], p["p"])-normal)))
        worst_gap = max(worst_gap, abs(gap-data["max_cc_cdf_gap"]))
    within(worst_pmf, 3e-13, "Binomial PMF versus SciPy")
    within(worst_gap, 3e-13, "Continuity-corrected CDF gap versus SciPy")
    return {"cases": CASES, "seed": SEED+3, "max_pmf_absolute_difference": worst_pmf,
            "max_cc_cdf_gap_difference": worst_gap, "absolute_tolerance": 3e-13,
            "reference": "scipy.stats.binom.pmf/cdf and scipy.stats.norm.cdf"}


def least_squares_reference(np):
    worst_projection, worst_coefficients, worst_condition = 0., 0., 0.
    for p in configs("least_squares", SEED+4):
        data = evaluate("least_squares", p)["numerics"]
        matrix = np.array(data["columns"]).T
        coefficients = np.linalg.lstsq(matrix, np.array(data["target"]), rcond=None)[0]
        worst_projection = max(worst_projection, float(np.linalg.norm(matrix@coefficients-data["projection"])))
        worst_coefficients = max(worst_coefficients, float(np.linalg.norm(coefficients-data["coefficients"])))
        worst_condition = max(worst_condition, abs(float(np.linalg.cond(matrix))-data["condition_A"]))
    for value in (worst_projection, worst_coefficients, worst_condition):
        within(value, 1e-11, "Geometric projection/coordinates/condition versus NumPy SVD")
    return {"cases": CASES, "seed": SEED+4, "max_projection_norm_difference": worst_projection,
            "max_coefficient_norm_difference": worst_coefficients,
            "max_condition_absolute_difference": worst_condition, "absolute_tolerance": 1e-11,
            "reference": "numpy.linalg.lstsq and numpy.linalg.cond (SVD-based, not the model's geometric QR)"}


def vector_reference(np, integrate):
    worst_flow, worst_flux, worst_circulation = 0., 0., 0.
    for p in configs("vector_field", SEED+5):
        data = evaluate("vector_field", p)["numerics"]
        a, b, radius, t = (p[k] for k in ("a", "b", "radius", "time"))
        solution = integrate.solve_ivp(lambda _, v: [a*v[0]-b*v[1], b*v[0]+a*v[1]],
                                       [0, t], [radius, 0], rtol=1e-11, atol=1e-13)
        if not solution.success:
            raise ArithmeticError("Independent RK45 integration did not finish")
        worst_flow = max(worst_flow, float(np.linalg.norm(solution.y[:, -1]-np.array(data["marked_tracer"][:2]))))
        def field(theta):
            x, y = radius*math.cos(theta), radius*math.sin(theta)
            return a*x-b*y, b*x+a*y
        flux = integrate.quad(lambda q: field(q)[0]*radius*math.cos(q)+field(q)[1]*radius*math.sin(q),
                              0, 2*math.pi, epsabs=1e-11, epsrel=1e-11)[0]
        circulation = integrate.quad(lambda q: -field(q)[0]*radius*math.sin(q)+field(q)[1]*radius*math.cos(q),
                                     0, 2*math.pi, epsabs=1e-11, epsrel=1e-11)[0]
        worst_flux = max(worst_flux, abs(flux-data["flux"]))
        worst_circulation = max(worst_circulation, abs(circulation-data["circulation"]))
    within(worst_flow, 5e-10, "Exact flow versus independently integrated RK45 trajectory")
    within(max(worst_flux, worst_circulation), 1e-11, "Boundary formulas versus adaptive quadrature")
    return {"cases": CASES, "seed": SEED+5, "max_flow_endpoint_norm_difference": worst_flow,
            "flow_absolute_tolerance": 5e-10, "solver_rtol": 1e-11, "solver_atol": 1e-13,
            "max_flux_absolute_difference": worst_flux, "max_circulation_absolute_difference": worst_circulation,
            "boundary_absolute_tolerance": 1e-11,
            "reference": "scipy.integrate.solve_ivp RK45 and adaptive QUADPACK boundary integration"}


def wave_energy_reference(integrate):
    worst = 0.
    for p in list(configs("waves", SEED+6))[:20]:
        data = evaluate("waves", p)["numerics"]
        k, omega, t, length = (data[key] for key in ("wavenumber", "angular_frequency", "time_seconds", "length"))
        amplitude, speed = p["amplitude"], p["speed"]
        kinetic = integrate.quad(lambda x: (-2*amplitude*omega*math.sin(k*x)*math.sin(omega*t))**2,
                                 0, length, epsabs=1e-10)[0]
        elastic = integrate.quad(lambda x: speed**2*(2*amplitude*k*math.cos(k*x)*math.cos(omega*t))**2,
                                 0, length, epsabs=1e-10)[0]
        worst = max(worst, abs(kinetic/(kinetic+elastic)-data["kinetic_energy_fraction"]),
                    abs(elastic/(kinetic+elastic)-data["potential_energy_fraction"]))
    within(worst, 1e-11, "Whole-string energy fractions versus integrated velocity/slope squares")
    return {"cases": 20, "seed": SEED+6, "max_fraction_absolute_difference": worst,
            "absolute_tolerance": 1e-11, "reference": "Adaptive integrals of y_t² and c² y_x² over the full ideal string"}


def export_samples():
    largest_xml, largest_source, count = 0, 0, 0
    for index, spec in enumerate(catalog()):
        for params in list(configs(spec["id"], SEED+100+index))[:4]:
            sample = evaluate(spec["id"], params)
            xml, source = to_x3d(sample), generate_manim(sample)
            compile(source, "<generated-manim-source>", "exec")
            largest_xml = max(largest_xml, len(xml.encode("utf-8")))
            largest_source = max(largest_source, len(source.encode("utf-8")))
            count += 1
    return {"cases": count, "per_lesson": 4, "seed_by_catalog_index": "24121 + index",
            "largest_x3d_bytes": largest_xml, "largest_manim_source_bytes": largest_source,
            "scope": "Adapter validation and generated Python compilation only; no schema validator, X3D rendering, or Manim execution"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "receipts/aha-independent.json")
    parser.add_argument("--no-scipy", action="store_true")
    args = parser.parse_args()
    source_hashes = identities()
    report = {"schema": "mathlab.aha-independent/1", "created_utc": datetime.now(timezone.utc).isoformat(),
              "source_sha256": source_hashes, "seed": SEED, "cases_per_new_model": CASES,
              "environment": {"python": platform.python_version(), "platform": platform.platform()},
              "checks": [], "scope": "Reproducible development corroboration with explicit numeric tolerances, not formal proof or a learning-outcome study.",
              "limitations": ["One numerical host; finite random coverage is not exhaustive.",
                              "No native X3D rendering, browser interaction, GPU benchmark, or Manim video is performed."]}
    dependency_reason = None
    try:
        if args.no_scipy:
            raise ImportError("Explicit --no-scipy option")
        import numpy as np
        from scipy import integrate, stats
        report["environment"].update({name: importlib.metadata.version(name) for name in ("numpy", "scipy")})
    except (ImportError, importlib.metadata.PackageNotFoundError) as error:
        dependency_reason = type(error).__name__ + ": " + str(error)
    instruments = [("complex_cmath", complex_powers, False),
                   ("taylor_complex_derivative_sum", taylor_direct_sum, False),
                   ("wave_addition_identity", waves_identity, False),
                   ("binomial_scipy", lambda: probability_reference(np, stats), True),
                   ("least_squares_numpy_svd", lambda: least_squares_reference(np), True),
                   ("field_scipy_flow_and_boundary", lambda: vector_reference(np, integrate), True),
                   ("wave_scipy_integrated_energy", lambda: wave_energy_reference(integrate), True),
                   ("mixed_parameter_exports", export_samples, False)]
    for name, instrument, optional in instruments:
        started = time.perf_counter()
        row = {"id": name}
        try:
            if optional and dependency_reason:
                row.update(status="not_run", reason=dependency_reason)
            else:
                row.update(status="pass", observation=instrument())
        except Exception as error:
            row.update(status="fail", error=type(error).__name__ + ": " + str(error))
        row["elapsed_seconds"] = time.perf_counter()-started
        report["checks"].append(row)
        print(row["status"].upper(), name, flush=True)
    report["source_drift"] = "none" if identities() == source_hashes else "changed"
    states = [row["status"] for row in report["checks"]]
    report["status"] = "fail" if "fail" in states or report["source_drift"] != "none" else "partial" if "not_run" in states else "pass"
    report["report_sha256"] = sha(canonical(report).encode("utf-8"))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, ensure_ascii=False, allow_nan=False)+"\n", encoding="utf-8")
    print(canonical({"status": report["status"], "checks": len(states), "source_drift": report["source_drift"]}))
    return 1 if report["status"] == "fail" else 0


if __name__ == "__main__":
    raise SystemExit(main())
