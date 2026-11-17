"""Independent mathematics and export checks for the analysis lesson extension."""
import ast
import cmath
import json
import math
import unittest
import xml.etree.ElementTree as ET

from mathlab.kernel import evaluate
from mathlab.lessons_analysis import LESSONS
from mathlab.manim_bridge import generate_manim
from mathlab.x3d import to_x3d


class ComplexMotionTests(unittest.TestCase):
    def test_cartesian_powers_match_python_complex_and_polar_formula(self):
        for radius, angle, progress, roots in ((.7, -math.pi, .37, 12),
                                              (1.15, math.pi, 1, 12),
                                              (1, 2*math.pi/5, 1, 5),
                                              (.84, 1.7, 0, 7)):
            n = evaluate("complex", {"radius": radius, "angle": angle,
                                     "progress": progress, "roots": roots})["numerics"]
            z = radius**progress*cmath.exp(1j*angle*progress)
            for j, (real, imaginary) in enumerate(n["powers"]):
                self.assertAlmostEqual(real, (z**j).real, places=12)
                self.assertAlmostEqual(imaginary, (z**j).imag, places=12)
            self.assertAlmostEqual(n["endpoint_modulus"], radius**(progress*roots), 12)
            self.assertLess(n["cartesian_polar_residual"], 2e-13)

    def test_roots_solve_equation_and_primitive_distinction_is_real(self):
        for count in range(3, 13):
            n = evaluate("complex", {"roots": count})["numerics"]
            for real, imaginary in n["roots"]:
                self.assertLess(abs(complex(real, imaginary)**count-1), 2e-14)
        triangle = evaluate("complex", {"radius": 1, "angle": 2*math.pi/3,
                                        "progress": 1, "roots": 6})["numerics"]
        self.assertLess(triangle["closure_distance"], 1e-14)
        self.assertAlmostEqual(triangle["powers"][3][0], 1)
        self.assertAlmostEqual(triangle["powers"][3][1], 0)
        self.assertGreater(math.dist(triangle["powers"][1], [1, 0]), 1)

    def test_modulus_change_prevents_closure_despite_whole_turn(self):
        n = evaluate("complex", {"radius": .84, "angle": 2*math.pi/5,
                                 "progress": 1, "roots": 5})["numerics"]
        self.assertAlmostEqual(n["closure_distance"], 1-.84**5)


class TaylorLensTests(unittest.TestCase):
    def test_maclaurin_coefficients_and_missing_even_term(self):
        cubic = evaluate("taylor", {"center": 0, "degree": 3})["numerics"]
        quartic = evaluate("taylor", {"center": 0, "degree": 4})["numerics"]
        self.assertEqual(cubic["coefficients"], [0, 1, 0, -1/6])
        self.assertEqual(quartic["coefficients"][-1], 0)
        self.assertEqual(cubic["polynomial_values"], quartic["polynomial_values"])
        self.assertNotEqual(cubic["remainder_bound"], quartic["remainder_bound"])
        for x, y in zip(cubic["x"], cubic["polynomial_values"]):
            self.assertAlmostEqual(y, x-x**3/6, places=13)

    def test_shifted_coefficients_and_values_against_direct_sum(self):
        for center in (-2, -.45, 0, 1.5, 2):
            for degree in (0, 1, 4, 7, 10):
                n = evaluate("taylor", {"center": center, "degree": degree,
                                        "radius": 3.5, "probe": -.73})["numerics"]
                x = n["probe_x"]
                # A direct derivative-phase formula is independent of the
                # builder's derivative cycle and Horner evaluation.
                direct = sum(math.sin(center+j*math.pi/2)*(x-center)**j/math.factorial(j)
                             for j in range(degree+1))
                self.assertAlmostEqual(n["approximation"], direct, places=12)
                self.assertAlmostEqual(n["reference"], math.sin(x))

    def test_remainder_bounds_hold_at_every_display_sample_and_probe(self):
        for center in (-2, 0, 2):
            for degree in range(11):
                n = evaluate("taylor", {"center": center, "degree": degree,
                                        "radius": 3.5, "probe": -1})["numerics"]
                self.assertLessEqual(abs(n["signed_error"]), n["remainder_bound"]+2e-13)
                for x, actual, approx in zip(n["x"], n["reference_values"], n["polynomial_values"]):
                    point_bound = abs(x-center)**(degree+1)/math.factorial(degree+1)
                    self.assertLessEqual(abs(actual-approx), point_bound+2e-13)
                    self.assertLessEqual(abs(actual-approx), n["window_bound"]+2e-13)

    def test_center_is_exact_to_roundoff_and_derivative_coefficients_match(self):
        for center in (-1.2, 0, 1.7):
            n = evaluate("taylor", {"center": center, "degree": 8, "probe": 0})["numerics"]
            self.assertEqual(n["probe_x"], center)
            self.assertEqual(n["remainder_bound"], 0)
            self.assertEqual(n["approximation"], n["reference"])
            self.assertAlmostEqual(n["coefficients"][1], math.cos(center))
            self.assertAlmostEqual(2*n["coefficients"][2], -math.sin(center))


class StandingWaveTests(unittest.TestCase):
    def test_sum_boundary_nodes_and_period(self):
        for mode in range(1, 7):
            for time in (0, .12, .25, .5, 1):
                n = evaluate("waves", {"mode": mode, "time": time,
                                       "speed": 1.7, "amplitude": .8})["numerics"]
                self.assertAlmostEqual(n["period"], 12/(mode*1.7))
                self.assertEqual(len(n["nodes"]), mode+1)
                self.assertLess(n["sum_identity_residual"], 5e-15)
                self.assertAlmostEqual(n["sum"][0], 0, places=13)
                self.assertAlmostEqual(n["sum"][-1], 0, places=13)
                for x in n["nodes"]:
                    right = .8*math.sin(n["wavenumber"]*x-n["phase"])
                    left = .8*math.sin(n["wavenumber"]*x+n["phase"])
                    self.assertAlmostEqual(right+left, 0, places=13)
                for r, l, total in zip(n["right"], n["left"], n["sum"]):
                    self.assertEqual(total, r+l)

    def test_flat_string_can_have_maximum_kinetic_energy(self):
        n = evaluate("waves", {"mode": 3, "time": .25, "probe": .5})["numerics"]
        self.assertLess(max(abs(y) for y in n["sum"]), 1e-14)
        self.assertAlmostEqual(n["kinetic_energy_fraction"], 1)
        self.assertAlmostEqual(n["potential_energy_fraction"], 0)
        self.assertGreater(abs(n["probe_velocity"]), 1)

    def test_energy_shares_match_integrated_derivative_fields(self):
        n = evaluate("waves", {"mode": 5, "time": .18,
                               "amplitude": .7, "speed": 2.2})["numerics"]
        count = 2000
        dx = n["length"]/count
        kinetic = potential = 0.
        # Midpoint quadrature of (mu/2)y_t² and (T/2)y_x²,
        # with mu=1 and tension=c². This independently checks the shares.
        for i in range(count):
            x = (i+.5)*dx
            velocity = -1.4*n["angular_frequency"]*math.sin(n["wavenumber"]*x)*math.sin(n["phase"])
            slope = 1.4*n["wavenumber"]*math.cos(n["wavenumber"]*x)*math.cos(n["phase"])
            kinetic += .5*velocity**2*dx
            potential += .5*2.2**2*slope**2*dx
        energy = kinetic+potential
        self.assertAlmostEqual(kinetic/energy, n["kinetic_energy_fraction"], places=12)
        self.assertAlmostEqual(potential/energy, n["potential_energy_fraction"], places=12)

    def test_phase_and_wave_speed_are_distinct(self):
        slow = evaluate("waves", {"time": .37, "speed": .5})["numerics"]
        fast = evaluate("waves", {"time": .37, "speed": 3})["numerics"]
        self.assertEqual(slow["sum"], fast["sum"])
        self.assertAlmostEqual(slow["period"], 6*fast["period"])
        self.assertAlmostEqual(slow["time_seconds"], 6*fast["time_seconds"])
        self.assertAlmostEqual(fast["probe_velocity"], 6*slow["probe_velocity"])

    def test_display_offsets_preserve_physical_displacements(self):
        sample = evaluate("waves", {"time": .17})
        primitives = {p["id"]: p for p in sample["primitives"]}
        for lane, data_key in (("right", "right"), ("left", "left"), ("sum", "sum")):
            offset = sample["numerics"]["display_offsets"][lane]
            for point, x, displacement in zip(primitives[lane+"_wave"]["points"],
                                               sample["numerics"]["x"],
                                               sample["numerics"][data_key]):
                self.assertEqual(point[0], x-3)
                self.assertAlmostEqual(point[1]-offset[1], displacement)
                self.assertEqual(point[2], offset[2])


class AnalysisExportTests(unittest.TestCase):
    def test_defaults_extremes_and_presets_are_finite_and_exportable(self):
        for lesson in LESSONS:
            configurations = [{},
                              {p["id"]: p["min"] for p in lesson["parameters"]},
                              {p["id"]: p["max"] for p in lesson["parameters"]},
                              *(p["params"] for p in lesson["presets"])]
            for params in configurations:
                with self.subTest(lesson=lesson["id"], params=params):
                    sample = evaluate(lesson["id"], params)
                    json.dumps(sample, allow_nan=False)
                    self.assertEqual(ET.fromstring(to_x3d(sample)).tag, "X3D")
                    source = generate_manim(sample)
                    tree = ast.parse(source)
                    self.assertTrue(any(isinstance(node, ast.ClassDef) and node.name == "MathlabScene"
                                        for node in tree.body))
                    self.assertLess(len(source.encode()), 2*1024*1024)
                    self.assertEqual(len(sample["primitives"]),
                                     len({p["id"] for p in sample["primitives"]}))


if __name__ == "__main__":
    unittest.main()
