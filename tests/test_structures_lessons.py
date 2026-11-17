"""Independent identities and observable geometry for the added structure lessons."""
import json
import math
import unittest

from mathlab.lessons_structures import LESSONS, MODELS


def _run(name, **params):
    spec = next(item for item in LESSONS if item["id"] == name)
    config = {item["id"]: item["default"] for item in spec["parameters"]}
    config.update(params)
    return MODELS[name](config)


class ProbabilityLessonTests(unittest.TestCase):
    def test_every_finite_distribution_has_unit_mass_zero_mean_and_unit_variance(self):
        for n in (1, 2, 12, 30, 80):
            for p in (.05, .35, .5, .95):
                with self.subTest(n=n, p=p):
                    _, _, _, data, _ = _run("probability", n=n, p=p)
                    self.assertAlmostEqual(sum(data["probabilities"]), 1, places=13)
                    self.assertAlmostEqual(data["standardized_mean"], 0, places=12)
                    self.assertAlmostEqual(data["standardized_variance"], 1, places=12)

    def test_bar_area_is_probability_and_undrawn_mass_is_accounted_for(self):
        for n, p in ((1,.05), (80,.05), (80,.5), (80,.95)):
            geometry, _, _, data, _ = _run("probability", n=n, p=p)
            bars = [item for item in geometry if item["kind"] == "box"]
            area = sum(bar["size"][0]*bar["size"][1] for bar in bars)
            self.assertAlmostEqual(area/data["density_display_scale"]+data["omitted_mass"], 1, places=13)
            for bar in bars:
                outcome = int(bar["id"].split("_")[-1])
                self.assertAlmostEqual(bar["size"][0]*bar["size"][1]/data["density_display_scale"], data["probabilities"][outcome])

    def test_fair_coin_symmetry_and_normal_approximation_improves_in_selected_case(self):
        data = _run("probability", n=12, p=.5)[3]
        self.assertEqual(data["probabilities"], list(reversed(data["probabilities"])))
        coarse = _run("probability", n=2, p=.5)[3]
        fine = _run("probability", n=80, p=.5)[3]
        self.assertLess(fine["max_cc_cdf_gap"], coarse["max_cc_cdf_gap"])
        self.assertAlmostEqual(_run("probability",n=1,p=.35)[3]["probabilities"][1], .35)


class ProjectionLessonTests(unittest.TestCase):
    def test_projection_obeys_normal_equations_and_pythagoras(self):
        for tilt in (-1.2,0,.55,1.2):
            for epsilon in (.05,.55,1):
                data = _run("least_squares", tilt=tilt, epsilon=epsilon)[3]
                dot = lambda a,b: sum(x*y for x,y in zip(a,b))
                e = data["residual"]
                for column in data["columns"]:
                    self.assertAlmostEqual(dot(column,e),0,places=13)
                for expected,actual in zip(data["projection"],data["reconstructed"]):
                    self.assertAlmostEqual(expected,actual,places=13)
                displacement = [.7*data["q1"][i]-.4*data["q2"][i] for i in range(3)]
                another_residual = [e[i]-displacement[i] for i in range(3)]
                self.assertAlmostEqual(dot(another_residual,another_residual),
                                       dot(e,e)+dot(displacement,displacement),places=12)

    def test_column_collinearity_changes_coordinates_but_not_reachable_projection(self):
        wide = _run("least_squares",epsilon=1)[3]
        narrow = _run("least_squares",epsilon=.05)[3]
        self.assertEqual(wide["projection"], narrow["projection"])
        self.assertAlmostEqual(narrow["coefficients"][1],20*wide["coefficients"][1])
        self.assertGreater(narrow["condition_A"],wide["condition_A"])
        self.assertAlmostEqual(narrow["condition_gram"],narrow["condition_A"]**2)
        gram = [[sum(a*b for a,b in zip(c1,c2)) for c2 in narrow["columns"]]
                for c1 in narrow["columns"]]
        self.assertAlmostEqual(gram[0][0]*gram[1][1]-gram[0][1]**2,.05**2)

    def test_target_in_plane_is_recovered_and_zero_residual_has_no_false_angle_marker(self):
        geometry, _, _, data, _ = _run("least_squares",tilt=0,by=1.2,bz=0)
        self.assertEqual(data["projection"],data["target"])
        self.assertEqual(data["residual_norm"],0)
        self.assertNotIn("right_angle",{item["id"] for item in geometry})


class VectorFieldLessonTests(unittest.TestCase):
    def test_boundary_sums_match_interior_divergence_and_curl(self):
        for a in (-.5,0,.5):
            for b in (-1.5,0,1.5):
                for radius in (.4,1.3,2):
                    data = _run("vector_field",a=a,b=b,radius=radius)[3]
                    self.assertAlmostEqual(data["flux_quadrature"],data["divergence"]*math.pi*radius**2,places=12)
                    self.assertAlmostEqual(data["circulation_quadrature"],data["curl_z"]*math.pi*radius**2,places=12)

    def test_exact_flow_turns_at_half_curl_and_scales_area_by_divergence(self):
        for a,b,time in ((0,1,1),(.45,0,1),(-.4,-1,1.2)):
            data = _run("vector_field",a=a,b=b,time=time)[3]
            self.assertAlmostEqual(data["flow_area_factor"], math.exp(data["divergence"]*time))
            self.assertAlmostEqual(data["flow_angle"],data["curl_z"]*time/2)
            marker = data["marked_tracer"]
            self.assertAlmostEqual(math.hypot(*marker[:2]),data["flow_radius"])

    def test_time_zero_keeps_tracers_on_the_integration_circle(self):
        geometry,_,_,data,_ = _run("vector_field",time=0)
        fixed = next(item["points"] for item in geometry if item["id"]=="integration_circle")
        moved = next(item["points"] for item in geometry if item["id"]=="tracer_ring")
        for first,second in zip(fixed,moved):
            self.assertEqual(first[:2],second[:2])
        self.assertEqual(data["flow_area_factor"],1)


class StructureContracts(unittest.TestCase):
    def test_presets_stay_inside_catalog_domains_and_samples_stay_finite(self):
        for lesson in LESSONS:
            defaults = {p["id"]:p["default"] for p in lesson["parameters"]}
            configurations = [defaults,
                              {p["id"]:p["min"] for p in lesson["parameters"]},
                              {p["id"]:p["max"] for p in lesson["parameters"]}]
            for preset in lesson["presets"]:
                configurations.append(defaults | preset["params"])
            for config in configurations:
                with self.subTest(lesson=lesson["id"],config=config):
                    for parameter in lesson["parameters"]:
                        self.assertLessEqual(parameter["min"],config[parameter["id"]])
                        self.assertLessEqual(config[parameter["id"]],parameter["max"])
                    result = MODELS[lesson["id"]](config)
                    json.dumps(result,allow_nan=False)
                    geometry = result[0]
                    self.assertEqual(len(geometry),len({q["id"] for q in geometry}))
                    self.assertLess(len(geometry),1000)
                    self.assertLess(sum(len(q.get("points",[])) for q in geometry),25000)


if __name__ == "__main__":
    unittest.main()
