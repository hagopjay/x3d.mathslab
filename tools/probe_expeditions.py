#!/usr/bin/env python3
"""Independent seeded corroboration for the six Insight Expeditions lessons.

Standard-library checks inspect emitted geometry as well as numerical data.
NumPy/SciPy references are optional: missing dependencies produce not_run checks
and an overall partial result. No browser or Manim renderer is executed.
"""
from __future__ import annotations

import argparse
import cmath
from datetime import datetime, timezone
from decimal import Decimal, localcontext
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
from mathlab.cards import card_from_x3d
from mathlab.kernel import evaluate
from mathlab.manim_bridge import generate_manim
from mathlab.x3d import to_x3d

SEED = 53117
CASES = 60
NEW = ("svd", "bayes", "lagrange", "aliasing", "heat", "refraction")


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=False, allow_nan=False)


def sha(value):
    return hashlib.sha256(value).hexdigest()


def identities():
    names = ("mathlab/catalog.py", "mathlab/kernel.py", "mathlab/lessons_inference.py",
             "mathlab/lessons_science.py", "mathlab/x3d.py", "mathlab/manim_bridge.py",
             "mathlab/cards.py", "tools/probe_expeditions.py")
    return {name: sha((ROOT / name).read_bytes()) for name in names}


def within(value, tolerance, claim):
    if not math.isfinite(value) or value > tolerance:
        raise ArithmeticError(f"{claim}: {value!r} exceeds {tolerance!r}")


def require(condition, claim):
    if not condition:
        raise ArithmeticError(claim)


def configurations(lesson):
    rng = random.Random(SEED + NEW.index(lesson))
    spec = next(row for row in catalog() if row["id"] == lesson)
    for _ in range(CASES):
        yield {p["id"]: rng.randint(int(p["min"]), int(p["max"]))
               if p["type"] == "integer" else rng.uniform(p["min"], p["max"])
               for p in spec["parameters"]}


def primitives(sample):
    return {row["id"]: row for row in sample["primitives"]}


def bayes_decimal_areas():
    worst_posterior = worst_area = worst_odds = 0.
    for p in configurations("bayes"):
        sample = evaluate("bayes", p)
        n, drawn = sample["numerics"], primitives(sample)
        with localcontext() as ctx:
            ctx.prec = 50
            prior, sensitivity, false_alarm = (Decimal(str(p[k])) for k in
                                               ("prior", "sensitivity", "false_positive"))
            masses = {"true_positive": prior*sensitivity,
                      "false_negative": prior*(1-sensitivity),
                      "false_positive": (1-prior)*false_alarm,
                      "true_negative": (1-prior)*(1-false_alarm)}
            posterior = masses["true_positive"]/(masses["true_positive"]+masses["false_positive"])
            worst_posterior = max(worst_posterior, abs(n["posterior"]-float(posterior)))
            odds = (prior/(1-prior))*(sensitivity/false_alarm)
            worst_odds = max(worst_odds, abs(n["posterior_odds"]-float(odds))/(1+float(odds)))
            for key, mass in masses.items():
                box = drawn.get("population_"+key)
                area = box["size"][0]*box["size"][1] if box else 0.
                worst_area = max(worst_area, abs(area/24-float(mass)))
            true_box = drawn["positive_true_share"]
            worst_area = max(worst_area, abs(true_box["size"][0]*true_box["size"][1]/4.8-float(posterior)))
        expected_total = math.fsum(n["expected_counts"].values())
        within(abs(expected_total-10_000), 1e-10, "Expected-count partition")
    within(worst_posterior, 2e-14, "Posterior versus 50-digit Decimal joint law")
    within(worst_area, 2e-14, "Emitted mosaic and conditioned box areas")
    within(worst_odds, 2e-14, "Odds update versus Decimal arithmetic")
    return {"cases": CASES, "max_posterior_difference": worst_posterior,
            "max_emitted_probability_area_difference": worst_area,
            "max_relative_odds_difference": worst_odds, "absolute_tolerance": 2e-14,
            "reference": "50-digit Decimal joint-probability law, emitted box areas, and separate odds update"}


def alias_complex_samples():
    worst_sample = worst_curve = 0.
    for p in configurations("aliasing"):
        sample = evaluate("aliasing", p)
        n, drawn = sample["numerics"], primitives(sample)
        f, fs, phase = p["frequency"], p["sample_rate"], p["phase"]
        fa = f-math.floor(f/fs+.5)*fs
        within(abs(fa-n["alias_frequency"]), 1e-14, "Signed alias representative")
        require(-fs/2-1e-14 <= fa < fs/2+1e-14, "Alias leaves declared interval")
        for j, t in enumerate(n["sample_times"]):
            reference = cmath.exp(1j*(2*math.pi*f*t+phase)).real
            alternate = cmath.exp(1j*(2*math.pi*fa*t+phase)).real
            point = drawn[f"sample_{j}"]["position"]
            worst_sample = max(worst_sample, abs(reference-alternate),
                               abs(reference-point[1]), abs(point[0]-(3*t-3)))
        for point, t in zip(drawn["original_signal"]["points"], n["times"]):
            worst_curve = max(worst_curve, abs(point[1]-cmath.exp(1j*(2*math.pi*f*t+phase)).real))
    # At the Nyquist boundary an unknown-phase sine can be invisible. This
    # control corroborates the strict-bandwidth caveat independently of f_a.
    boundary = evaluate("aliasing", {"frequency": 4, "sample_rate": 8, "phase": math.pi/2})
    invisible = max(abs(v) for v in boundary["numerics"]["samples"])
    within(worst_sample, 2e-12, "Complex phases and emitted sample markers")
    within(worst_curve, 2e-12, "Emitted signal samples versus complex exponentials")
    within(invisible, 2e-13, "Nyquist quadrature-phase samples")
    return {"cases": CASES, "max_sample_or_position_difference": worst_sample,
            "max_curve_difference": worst_curve, "sample_absolute_tolerance": 2e-12,
            "nyquist_phase_sample_magnitude": invisible, "nyquist_absolute_tolerance": 2e-13,
            "reference": "Complex exponentials at every emitted sample; explicit exact-Nyquist phase-loss control"}


def heat_emitted_integrals(integrate):
    worst_mean = worst_energy = worst_geometry = worst_dissipation = 0.
    for p in configurations("heat"):
        sample = evaluate("heat", p)
        n, drawn = sample["numerics"], primitives(sample)
        a, m, alpha, t = p["amplitude"], p["mode"], p["diffusivity"], p["time"]
        temperature = lambda x: 1+.45*math.exp(-alpha*t)*math.cos(x)+a*math.exp(-alpha*m*m*t)*math.cos(m*x)
        slope = lambda x: -.45*math.exp(-alpha*t)*math.sin(x)-m*a*math.exp(-alpha*m*m*t)*math.sin(m*x)
        mean = integrate.quad(temperature, 0, 2*math.pi, epsabs=1e-12)[0]/(2*math.pi)
        energy = integrate.quad(lambda x: (temperature(x)-1)**2, 0, 2*math.pi, epsabs=1e-12)[0]/(2*math.pi)
        dissipation = -alpha/math.pi*integrate.quad(lambda x: slope(x)**2, 0, 2*math.pi, epsabs=1e-12)[0]
        worst_mean = max(worst_mean, abs(mean-n["quadrature_mean"]))
        worst_energy = max(worst_energy, abs(energy-n["fluctuation_energy"]))
        worst_dissipation = max(worst_dissipation, abs(dissipation-n["energy_derivative"]))
        require(n["fluctuation_energy"] <= n["initial_fluctuation_energy"]+1e-14, "Heat fluctuations grow")
        require(n["energy_derivative"] <= 1e-14, "Heat dissipation has wrong sign")
        for point, x in zip(drawn["current_profile"]["points"], n["x"]):
            worst_geometry = max(worst_geometry, abs(point[0]-(x-math.pi)),
                                 abs(point[1]/2+1-temperature(x)), abs(point[2]-(4*t/3-2+.025)))
        for point in drawn["diffusion_history"]["points"][::17]:
            x, u, history_t = point[0]+math.pi, point[1]/2+1, (point[2]+2)*3/4
            reference = 1+.45*math.exp(-alpha*history_t)*math.cos(x)+a*math.exp(-alpha*m*m*history_t)*math.cos(m*x)
            worst_geometry = max(worst_geometry, abs(u-reference))
    within(worst_mean, 2e-12, "Heat mean via adaptive integration")
    within(worst_energy, 2e-12, "Heat fluctuations via adaptive integration")
    within(worst_dissipation, 2e-11, "Heat dissipation identity −2α average(u_x²)")
    within(worst_geometry, 2e-12, "Emitted current/history coordinates")
    return {"cases": CASES, "max_mean_difference": worst_mean,
            "max_energy_difference": worst_energy, "max_dissipation_difference": worst_dissipation,
            "max_geometry_difference": worst_geometry, "integral_absolute_tolerance": 2e-12,
            "dissipation_absolute_tolerance": 2e-11,
            "reference": "Adaptive spatial integrals of u, (u−1)² and u_x² plus decoded mesh/line coordinates"}


def svd_numpy(np):
    worst_values = worst_pairs = worst_geometry = worst_matrix = 0.
    for p in configurations("svd"):
        sample = evaluate("svd", p)
        n, drawn = sample["numerics"], primitives(sample)
        matrix = np.asarray(n["target_matrix"])
        u, singular, vh = np.linalg.svd(matrix)
        declared = np.asarray([p["sigma1"], p["sigma1"]*p["ratio"]])
        worst_values = max(worst_values, float(np.max(np.abs(singular-declared))))
        worst_matrix = max(worst_matrix, float(np.max(np.abs(u@np.diag(singular)@vh-matrix))))
        # Compare singular-pair equations without treating nonunique vector
        # signs or repeated-value bases as a disagreement.
        inputs = np.asarray(n["input_directions"]).T
        outputs = np.asarray(n["output_directions"]).T
        worst_pairs = max(worst_pairs, float(np.max(np.abs(matrix@inputs-outputs@np.diag(declared)))))
        rot = lambda theta: np.asarray([[math.cos(theta), -math.sin(theta)], [math.sin(theta), math.cos(theta)]])
        s = p["progress"]
        amounts = np.clip([s, s-1, s-2], 0, 1)
        scales = 1+amounts[1]*(declared-1)
        current = rot(amounts[2]*p["angle_u"])@np.diag(scales)@rot(-amounts[0]*p["angle_v"])
        for point, index in zip(drawn["displayed_ellipse"]["points"], range(193)):
            z = cmath.exp(2j*math.pi*index/192)
            reference = current@np.asarray([z.real, z.imag])
            worst_geometry = max(worst_geometry, float(np.max(np.abs(np.asarray(point[:2])-[2.3, 0]-reference))))
    deficient = evaluate("svd", {"ratio": 0})["numerics"]
    require(deficient["target_rank"] == 1 and deficient["target_condition"] is None,
            "Rank-one condition handling is not explicit finite JSON")
    within(worst_values, 2e-12, "NumPy target singular values")
    within(worst_pairs, 2e-12, "Authored singular-pair equations")
    within(max(worst_matrix, worst_geometry), 2e-12, "SVD reconstruction and staged emitted circle")
    return {"cases": CASES, "max_singular_value_difference": worst_values,
            "max_singular_pair_residual": worst_pairs, "max_numpy_reconstruction_residual": worst_matrix,
            "max_emitted_circle_difference": worst_geometry, "absolute_tolerance": 2e-12,
            "reference": "NumPy SVD, independent staged NumPy matrix product, complex unit-circle samples; no unique-basis assumption"}


def lagrange_scalar_optimize(optimize):
    worst_value = worst_point = worst_constraint = worst_normal = 0.
    for p in configurations("lagrange"):
        sample = evaluate("lagrange", p)
        n, drawn = sample["numerics"], primitives(sample)
        a, b, phi = p["axis_a"], p["axis_b"], p["direction"]
        cx, cy = math.cos(phi), math.sin(phi)
        objective = lambda theta: cx*a*math.cos(theta)+cy*b*math.sin(theta)
        grid = [-math.pi+2*math.pi*j/32 for j in range(32)]
        center = max(grid, key=objective)
        # The coarse global sweep selects a local bracket on the periodic
        # parameter, avoiding a false unimodality assumption over a full turn.
        result = optimize.minimize_scalar(lambda theta: -objective(theta), bounds=(center-math.pi/8, center+math.pi/8),
                                          method="bounded", options={"xatol": 1e-12})
        require(result.success, "Independent constrained scalar minimizer failed")
        reference_point = [a*math.cos(result.x), b*math.sin(result.x)]
        point = drawn["constrained_maximum"]["position"][:2]
        worst_value = max(worst_value, abs(-result.fun-n["maximum_objective"]))
        worst_point = max(worst_point, math.dist(reference_point, point))
        worst_constraint = max(worst_constraint, abs((point[0]/a)**2+(point[1]/b)**2-1))
        normal = [2*point[0]/a**2, 2*point[1]/b**2]
        worst_normal = max(worst_normal, abs(cx*normal[1]-cy*normal[0]))
    within(worst_value, 2e-11, "Independent constrained optimum value")
    within(worst_point, 2e-6, "Emitted ellipse maximum versus scalar optimization")
    within(max(worst_constraint, worst_normal), 2e-12, "Feasibility and parallel normals from emitted maximum")
    return {"cases": CASES, "max_objective_difference": worst_value,
            "max_emitted_maximum_point_difference": worst_point,
            "max_emitted_constraint_residual": worst_constraint,
            "max_normal_parallel_residual": worst_normal,
            "value_absolute_tolerance": 2e-11, "optimizer_point_absolute_tolerance": 2e-6,
            "reference": "Global coarse bracket plus independent SciPy bounded scalar solve on the ellipse; emitted point feasibility and normal determinant"}


def refraction_scalar_optimize(optimize):
    worst_point = worst_cost = worst_snell = worst_geometry = 0.
    for p in configurations("refraction"):
        sample = evaluate("refraction", p)
        n, drawn = sample["numerics"], primitives(sample)
        n1, n2, h, depth, d = (p[k] for k in ("n1", "n2", "height", "depth", "span"))
        cost = lambda q: n1*math.hypot(q, h)+n2*math.hypot(d-q, depth)
        result = optimize.minimize_scalar(cost, bounds=(0, d), method="bounded", options={"xatol": 1e-12})
        require(result.success, "Independent optical minimum solve failed")
        q = n["optimal_crossing"]
        worst_point = max(worst_point, abs(result.x-q))
        worst_cost = max(worst_cost, abs(result.fun-n["minimum_cost"]))
        snell = abs(n1*q/math.hypot(q, h)-n2*(d-q)/math.hypot(d-q, depth))
        worst_snell = max(worst_snell, snell)
        require(0 < q < d and n["minimum_second_derivative"] > 0,
                "Refraction optimum is not interior and strictly convex")
        require(cost(q) <= min(cost(0), cost(d), cost(n["trial_crossing"]))+1e-12,
                "Reported optical minimum exceeds an admissible path")
        line = drawn["minimum_path"]["points"]
        for point, reference in zip(line, [[-d/2, h], [q-d/2, 0], [d/2, -depth]]):
            worst_geometry = max(worst_geometry, math.dist(point[:2], reference))
    within(worst_point, 2e-6, "Bisection crossing versus independent scalar minimizer")
    within(worst_cost, 2e-11, "Optical minimum value")
    within(worst_snell, 2e-12, "Snell's law from independent path lengths")
    within(worst_geometry, 2e-12, "Emitted minimum ray positions")
    return {"cases": CASES, "max_optimal_crossing_difference": worst_point,
            "max_minimum_cost_difference": worst_cost, "max_snell_residual": worst_snell,
            "max_emitted_ray_difference": worst_geometry, "optimizer_point_absolute_tolerance": 2e-6,
            "cost_absolute_tolerance": 2e-11, "snell_absolute_tolerance": 2e-12,
            "reference": "SciPy bounded scalar minimization of optical length, independent sine ratios and emitted ray coordinates"}


def export_boundaries():
    largest_xml = largest_source = count = 0
    for spec in catalog():
        if spec["id"] not in NEW:
            continue
        for p in ({}, {q["id"]: q["min"] for q in spec["parameters"]},
                  {q["id"]: q["max"] for q in spec["parameters"]}):
            sample = evaluate(spec["id"], p)
            xml, source = to_x3d(sample), generate_manim(sample)
            require(card_from_x3d(xml)["params"] == sample["params"], "X3D parameter recovery changed a boundary configuration")
            compile(source, "<expedition-manim-source>", "exec")
            largest_xml = max(largest_xml, len(xml.encode("utf-8")))
            largest_source = max(largest_source, len(source.encode("utf-8")))
            count += 1
    return {"cases": count, "configurations": "default, simultaneous minimum, simultaneous maximum for all six new lessons",
            "largest_x3d_bytes": largest_xml, "largest_manim_source_bytes": largest_source,
            "scope": "Adapter budgets, parameter-card recovery, generated Python compilation; no renderer execution"}


def refusal_controls():
    caught = 0
    for value in (float("nan"), float("inf"), .01):
        try:
            within(value, 1e-8, "Deliberately incorrect reference")
        except ArithmeticError:
            caught += 1
    require(caught == 3, "Numeric comparator failed a paired bad control")
    return {"paired_bad_controls_caught": caught,
            "scope": "Checks the instrument comparator rejects nonfinite and excessive reference differences"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT/"receipts/expeditions-independent.json")
    parser.add_argument("--no-scipy", action="store_true")
    args = parser.parse_args()
    source = identities()
    report = {"schema": "mathlab.expeditions-independent/1", "created_utc": datetime.now(timezone.utc).isoformat(),
              "source_sha256": source, "seed": SEED, "cases_per_new_model": CASES,
              "environment": {"python": platform.python_version(), "platform": platform.platform()},
              "checks": [], "scope": "Finite seeded development corroboration with independent references and explicit tolerances; not a proof or learning-outcome study.",
              "limitations": ["One numerical host; random coverage is not exhaustive.",
                              "No native X3D pixels, browser runtime, Manim video or GPU performance is measured."]}
    missing = None
    try:
        if args.no_scipy:
            raise ImportError("Explicit --no-scipy option")
        import numpy as np
        from scipy import integrate, optimize
        report["environment"].update({name: importlib.metadata.version(name) for name in ("numpy", "scipy")})
    except (ImportError, importlib.metadata.PackageNotFoundError) as error:
        missing = type(error).__name__+": "+str(error)
    instruments = [("bayes_decimal_emitted_areas", bayes_decimal_areas, False),
                   ("alias_complex_samples_and_nyquist_phase", alias_complex_samples, False),
                   ("svd_numpy_and_emitted_circle", lambda: svd_numpy(np), True),
                   ("lagrange_scipy_and_emitted_maximum", lambda: lagrange_scalar_optimize(optimize), True),
                   ("heat_adaptive_integrals_and_emitted_history", lambda: heat_emitted_integrals(integrate), True),
                   ("refraction_scipy_and_emitted_ray", lambda: refraction_scalar_optimize(optimize), True),
                   ("six_model_export_boundaries", export_boundaries, False),
                   ("instrument_refusal_controls", refusal_controls, False)]
    for name, instrument, optional in instruments:
        started = time.perf_counter()
        row = {"id": name}
        try:
            if optional and missing:
                row.update(status="not_run", reason=missing)
            else:
                row.update(status="pass", observation=instrument())
        except Exception as error:
            row.update(status="fail", error=type(error).__name__+": "+str(error))
        row["elapsed_seconds"] = time.perf_counter()-started
        report["checks"].append(row)
        print(row["status"].upper(), name, flush=True)
    report["source_drift"] = "none" if identities() == source else "changed"
    states = [row["status"] for row in report["checks"]]
    report["status"] = "fail" if "fail" in states or report["source_drift"] != "none" else "partial" if "not_run" in states else "pass"
    report["report_sha256"] = sha(canonical(report).encode())
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, ensure_ascii=False, allow_nan=False)+"\n", encoding="utf-8")
    print(canonical({"status": report["status"], "checks": len(states), "source_drift": report["source_drift"]}))
    return 1 if report["status"] == "fail" else 0


if __name__ == "__main__":
    raise SystemExit(main())
