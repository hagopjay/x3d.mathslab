"""Independent references, changed-input twins and bounded-geometry controls."""
import json
import math
import unittest

from mathlab.catalog import catalog, lesson_spec
from mathlab.kernel import evaluate, normalize_params, _lorenz_rhs, _rk4_lorenz


class CatalogAndBoundaryTests(unittest.TestCase):
    def test_catalog_is_independent_and_every_lesson_is_discoverable(self):
        lessons=catalog()
        self.assertEqual({s["id"] for s in lessons},{"linear","derivative","integral","fourier","lorenz","gradient"})
        lessons[0]["parameters"][0]["max"]=999
        self.assertEqual(lesson_spec("linear")["parameters"][0]["max"],2.5)

    def test_unknown_inputs_and_wrong_types_refuse(self):
        for name,p in [("missing",{}),("linear",[]),("derivative",{"formula":"__import__('os')"}),
                       ("derivative",{"h":0}),("derivative",{"h":float("nan")}),
                       ("linear",{"a":True}),("linear",{"a":"1"}),
                       ("linear",{"a":10**500}),("integral",{"n":4.5}),
                       ("fourier",{"terms":13}),("gradient",{"condition":0})]:
            with self.subTest(name=name,p=p):
                with self.assertRaises(ValueError):evaluate(name,p)
        self.assertEqual(normalize_params("integral",{"n":8.0})["n"],8)

    def test_default_and_extreme_geometry_are_finite_and_within_adapter_budgets(self):
        for spec in catalog():
            configurations=[{}, {p["id"]:p["min"] for p in spec["parameters"]},
                            {p["id"]:p["max"] for p in spec["parameters"]}]
            for config in configurations:
                with self.subTest(lesson=spec["id"],config=config):
                    sample=evaluate(spec["id"],config)
                    json.dumps(sample,allow_nan=False)
                    primitives=sample["primitives"]
                    self.assertLessEqual(len(primitives),1000)
                    self.assertEqual(len(primitives),len({q["id"] for q in primitives}))
                    self.assertLessEqual(sum(len(q.get("points",[])) for q in primitives),25000)
                    self.assertLessEqual(sum(len(q.get("indices",[])) for q in primitives),150000)
                    for q in primitives:
                        for xyz in q.get("points",[]):
                            self.assertEqual(len(xyz),3)
                            self.assertTrue(all(math.isfinite(v) for v in xyz))
                        self.assertTrue(all(0<=c<=1 for c in q["color"]))

    def test_every_displayed_primitive_fits_bounds_for_default_and_extreme_parameters(self):
        for spec in catalog():
            configs=[{}, {p["id"]:p["min"] for p in spec["parameters"]},
                     {p["id"]:p["max"] for p in spec["parameters"]}]
            if spec["id"]=="fourier":configs.append({"terms":12,"phase":math.pi})
            if spec["id"]=="lorenz":configs.append({"sigma":16,"rho":40,"beta":1,"dt":.03,"duration":20})
            for params in configs:
                with self.subTest(lesson=spec["id"],params=params):
                    sample=evaluate(spec["id"],params)
                    center,size=sample["bounds"]["center"],sample["bounds"]["size"]
                    lower=[c-s/2 for c,s in zip(center,size)]
                    upper=[c+s/2 for c,s in zip(center,size)]
                    for primitive in sample["primitives"]:
                        points=primitive.get("points",[])
                        if primitive["kind"]=="sphere":
                            r=primitive["radius"];p=primitive["position"]
                            points=[[v-r for v in p],[v+r for v in p]]
                        elif primitive["kind"]=="box":
                            p=primitive["position"];s=primitive["size"]
                            points=[[v-w/2 for v,w in zip(p,s)],[v+w/2 for v,w in zip(p,s)]]
                        for point in points:
                            self.assertTrue(all(lo<=v<=hi for v,lo,hi in zip(point,lower,upper)))


class LinearTests(unittest.TestCase):
    def test_basis_columns_and_oriented_area_agree(self):
        sample=evaluate("linear",{"a":2,"b":.5,"c":1,"d":-1})
        n=sample["numerics"]
        self.assertEqual(n["matrix"],[[2,.5],[1,-1]])
        self.assertAlmostEqual(n["determinant"],-2.5)
        polygon=next(p for p in sample["primitives"] if p["id"]=="unit_square_image")["points"]
        area=.5*sum(a[0]*b[1]-a[1]*b[0] for a,b in zip(polygon,polygon[1:]+polygon[:1]))
        self.assertAlmostEqual(area,n["determinant"])

    def test_identity_blend_and_singular_map_are_valid(self):
        self.assertEqual(evaluate("linear",{"blend":0})["numerics"]["matrix"],[[1.,0.],[0.,1.]])
        singular=evaluate("linear",{"a":1,"b":2,"c":1,"d":2})
        self.assertEqual(singular["numerics"]["determinant"],0)
        self.assertEqual(len(singular["numerics"]["real_eigenvalues"]),2)

    def test_rotation_has_no_real_eigenlines_but_shear_has_small_residual(self):
        rotation=evaluate("linear",{"a":0,"b":-1,"c":1,"d":0})
        self.assertEqual(rotation["numerics"]["real_eigenvalues"],[])
        self.assertFalse(any(p["id"].startswith("eigenline") for p in rotation["primitives"]))
        shear=evaluate("linear",{"a":1,"b":1,"c":0,"d":1})
        self.assertLess(next(m["value"] for m in shear["metrics"] if m["id"]=="eigen_residual"),1e-12)


class CalculusTests(unittest.TestCase):
    def test_analytic_derivative_and_central_bound(self):
        for x in (-2.5,-.7,0,.7,2.5):
            for h in (.005,.1,.6,1.5):
                n=evaluate("derivative",{"x":x,"h":h})["numerics"]
                self.assertAlmostEqual(n["analytic_slope"],math.cos(x)+.3*x)
                self.assertLessEqual(abs(n["central_slope"]-n["analytic_slope"]),n["central_bound"]+2e-13)

    def test_changed_h_refines_slope_but_not_the_reference(self):
        a=evaluate("derivative",{"x":0,"h":.4})["numerics"]
        b=evaluate("derivative",{"x":0,"h":.2})["numerics"]
        self.assertEqual(a["analytic_slope"],b["analytic_slope"])
        self.assertLess(abs(b["central_slope"]-1),abs(a["central_slope"]-1)/3.8)
        self.assertNotEqual(a["forward_slope"],b["forward_slope"])

    def test_integral_reference_and_midpoint_bound(self):
        for n in (1,4,12,64):
            s=evaluate("integral",{"a":-3,"b":2.5,"n":n})["numerics"]
            F=lambda x:x**3/12+.175*math.sin(2*x)+1.2*x
            self.assertAlmostEqual(s["reference"],F(2.5)-F(-3))
            self.assertLessEqual(abs(s["signed_error"]),s["midpoint_bound"]+1e-12)

    def test_left_mid_right_are_actual_changed_sampling_rules(self):
        results=[evaluate("integral",{"a":-2,"b":1.5,"sample":r})["numerics"] for r in (-1,0,1)]
        self.assertEqual(len({r["reference"] for r in results}),1)
        self.assertEqual(len({r["approximation"] for r in results}),3)
        self.assertEqual([r["rule"] for r in results],["left","midpoint","right"])
        self.assertTrue(all(h>0 for r in results for h in r["heights"]))

    def test_integral_drawn_rectangle_area_equals_numeric_sum(self):
        for rule in (-1,0,1):
            sample=evaluate("integral",{"a":-2.4,"b":1.7,"n":17,"sample":rule})
            boxes=[p for p in sample["primitives"] if p["kind"]=="box"]
            self.assertEqual(len(boxes),17)
            drawn=sum(p["size"][0]*p["size"][1] for p in boxes)
            self.assertAlmostEqual(drawn,sample["numerics"]["approximation"],places=13)
            self.assertTrue(all(p["size"][0]==sample["numerics"]["dx"] for p in boxes))


class FourierTests(unittest.TestCase):
    def test_epicycle_endpoint_wave_and_formula_agree(self):
        for terms in (1,5,12):
            for phase in (0,.9,math.pi,2*math.pi):
                n=evaluate("fourier",{"terms":terms,"phase":phase})["numerics"]
                reference=4/math.pi*sum(math.sin((2*k+1)*phase)/(2*k+1) for k in range(terms))
                self.assertAlmostEqual(n["tip"][1],reference,13)
                self.assertAlmostEqual(n["partial_value"],reference,13)

    def test_parseval_rms_matches_independent_midpoint_quadrature(self):
        terms=5;count=12000
        n=evaluate("fourier",{"terms":terms})["numerics"]
        error=0
        for i in range(count):
            t=(i+.5)*2*math.pi/count
            target=1 if t<math.pi else -1
            value=4/math.pi*sum(math.sin((2*k+1)*t)/(2*k+1) for k in range(terms))
            error+=(value-target)**2
        self.assertAlmostEqual(math.sqrt(error/count),n["rms_error"],places=5)

    def test_more_terms_reduce_average_error_without_removing_ringing(self):
        one=evaluate("fourier",{"terms":1})["numerics"]
        many=evaluate("fourier",{"terms":12})["numerics"]
        self.assertLess(many["rms_error"],one["rms_error"])
        self.assertGreater(many["sampled_peak"],1.1)


class DynamicsTests(unittest.TestCase):
    def test_lorenz_rhs_equilibrium_and_short_time_refinement(self):
        self.assertEqual(_lorenz_rhs((1,1,1),10,28,8/3),(0,26,1-8/3))
        self.assertEqual(_rk4_lorenz((0.,0.,0.),.01,10,28,8/3),(0.,0.,0.))
        endpoints=[evaluate("lorenz",{"duration":2,"dt":h})["numerics"]["endpoint"] for h in (.02,.01,.005)]
        self.assertLess(math.dist(endpoints[1],endpoints[2]),math.dist(endpoints[0],endpoints[2])/10)

    def test_lorenz_separates_initial_condition_and_method_comparisons(self):
        s=evaluate("lorenz",{"duration":3,"dt":.013,"separation":.001})["numerics"]
        changed=evaluate("lorenz",{"duration":3,"dt":.013,"separation":.01})["numerics"]
        self.assertAlmostEqual(s["h"]*s["steps"],3)
        self.assertLessEqual(s["h"],.013)
        self.assertEqual(s["endpoint"],changed["endpoint"])
        self.assertEqual(s["fine_endpoint"],changed["fine_endpoint"])
        self.assertNotEqual(s["nearby_endpoint"],changed["nearby_endpoint"])

    def test_lorenz_camera_encloses_actual_extreme_trajectory_and_markers(self):
        # This valid configuration escaped the previous fixed "typical orbit" bounds.
        for params in ({},{"sigma":16,"rho":40,"beta":1,"dt":.03,"duration":20}):
            sample=evaluate("lorenz",params)
            center,size=sample["bounds"]["center"],sample["bounds"]["size"]
            lower=[c-s/2 for c,s in zip(center,size)]
            upper=[c+s/2 for c,s in zip(center,size)]
            for primitive in sample["primitives"]:
                points=primitive.get("points",[])
                if primitive["kind"]=="sphere":
                    r=primitive["radius"];p=primitive["position"]
                    points=[[v-r for v in p],[v+r for v in p]]
                for point in points:
                    self.assertTrue(all(lo<=value<=hi for value,lo,hi in zip(point,lower,upper)))

    def test_gradient_stable_decreases_loss_and_matches_closed_form(self):
        s=evaluate("gradient")["numerics"]
        self.assertLess(s["contraction_factor"],1)
        self.assertTrue(all(b<=a+1e-13 for a,b in zip(s["losses"],s["losses"][1:])))
        self.assertLess(s["relative_residual"],1e-12)
        self.assertFalse(s["display_truncated"])

    def test_gradient_unstable_twin_is_bounded_visually_and_explicit(self):
        stable=evaluate("gradient",{"condition":20,"rate":.05,"steps":60})
        unstable=evaluate("gradient",{"condition":20,"rate":.28,"steps":60})
        n=unstable["numerics"]
        self.assertGreater(n["contraction_factor"],1)
        self.assertTrue(n["display_truncated"])
        self.assertEqual(len(n["iterates"]),61)
        self.assertGreater(n["losses"][-1],stable["numerics"]["losses"][-1]*1e6)
        self.assertLess(n["relative_residual"],1e-12)
        for p in unstable["primitives"]:
            for xyz in p.get("points",[]):self.assertLess(max(abs(v) for v in xyz),40)

    def test_gradient_origin_stays_minimum_even_when_some_modes_amplify(self):
        n=evaluate("gradient",{"start_x":0,"start_y":0,"rate":.28,"condition":20})["numerics"]
        self.assertGreater(n["contraction_factor"],1)
        self.assertTrue(all(v==0 for v in n["losses"]))


if __name__=="__main__":
    unittest.main()
