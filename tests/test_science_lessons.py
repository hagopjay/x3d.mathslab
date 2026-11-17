"""Independent sampled-signal, diffusion and stationary-optical-path checks."""
import ast
import cmath
import json
import math
import unittest

from mathlab.lessons_science import LESSONS, MODELS


def _run(name, **params):
    spec=next(row for row in LESSONS if row["id"]==name)
    config={p["id"]:p["default"] for p in spec["parameters"]}
    config.update(params)
    return MODELS[name](config)


class AliasingTests(unittest.TestCase):
    def test_sample_identity_for_full_frequency_and_rate_domain_edges(self):
        for frequency in (.2,.5,1,7,8,11.7,12):
            for sample_rate in (1,2,8,16):
                for phase in (-math.pi,0,.65,math.pi):
                    data=_run("aliasing",frequency=frequency,sample_rate=sample_rate,phase=phase)[3]
                    self.assertGreaterEqual(data["alias_frequency"],-sample_rate/2-1e-14)
                    self.assertLess(data["alias_frequency"],sample_rate/2+1e-14)
                    for t,shown in zip(data["sample_times"],data["samples"]):
                        reference=cmath.exp(1j*(2*math.pi*data["alias_frequency"]*t+phase)).real
                        self.assertAlmostEqual(shown,reference,places=12)
                    self.assertLess(data["max_sample_error"],4e-13)

    def test_seven_hertz_alias_and_frozen_eight_hertz(self):
        data=_run("aliasing")[3]
        self.assertEqual(data["alias_frequency"],-1)
        self.assertGreater(max(abs(a-b) for a,b in zip(data["original"],data["alias"])),1)
        frozen=_run("aliasing",frequency=8,sample_rate=8,phase=.65)[3]
        self.assertEqual(frozen["alias_frequency"],0)
        for sample in frozen["samples"]:
            self.assertAlmostEqual(sample,math.cos(.65),places=13)

    def test_below_nyquist_and_explicit_half_open_tie_policy(self):
        data=_run("aliasing",frequency=7,sample_rate=16)[3]
        self.assertEqual(data["alias_frequency"],7)
        self.assertEqual(data["original"],data["alias"])
        self.assertEqual(_run("aliasing",frequency=4,sample_rate=8)[3]["alias_frequency"],-4)
        self.assertEqual(_run("aliasing",frequency=12,sample_rate=8)[3]["alias_frequency"],-4)

    def test_display_mapping_and_every_visible_marker_match_numeric_samples(self):
        geometry,_,_,data,_=_run("aliasing",sample_rate=16)
        samples=[row for row in geometry if row["id"].startswith("sample_")]
        self.assertEqual(len(samples),33)
        for marker,t,value in zip(samples,data["sample_times"],data["samples"]):
            self.assertEqual(marker["position"][:2],[3*t-3,value])


class HeatTests(unittest.TestCase):
    def test_periodic_mean_and_energy_from_independent_midpoint_integrals(self):
        count=2048
        for mode,amplitude,alpha,time in ((2,0,.05,0),(5,.4,.25,.6),(8,.45,1,3)):
            data=_run("heat",mode=mode,amplitude=amplitude,diffusivity=alpha,time=time)[3]
            values=[1+.45*math.exp(-alpha*time)*math.cos(2*math.pi*(i+.5)/count)
                    +amplitude*math.exp(-alpha*mode**2*time)*math.cos(mode*2*math.pi*(i+.5)/count)
                    for i in range(count)]
            self.assertAlmostEqual(math.fsum(values)/count,1,places=14)
            self.assertAlmostEqual(math.fsum((u-1)**2 for u in values)/count,data["fluctuation_energy"],places=14)
            self.assertAlmostEqual(data["quadrature_mean"],1,places=14)
            self.assertAlmostEqual(data["quadrature_energy"],data["fluctuation_energy"],places=14)

    def test_energy_decreases_and_mean_is_preserved(self):
        energies=[_run("heat",mode=8,time=t)[3]["fluctuation_energy"] for t in (0,.1,.3,1,3)]
        self.assertTrue(all(a>b for a,b in zip(energies,energies[1:])))
        for t in (0,.5,3):
            data=_run("heat",time=t)[3]
            self.assertLess(data["energy_derivative"],0)
            self.assertLessEqual(data["fluctuation_energy"],data["initial_fluctuation_energy"])
            self.assertEqual(data["mean"],1)

    def test_decay_rate_and_time_diffusivity_product(self):
        slow=_run("heat",diffusivity=.2,time=1)[3]
        fast=_run("heat",diffusivity=.4,time=.5)[3]
        self.assertEqual(slow["current_values"],fast["current_values"])
        for mode in (2,5,8):
            data=_run("heat",mode=mode,time=.25)[3]
            self.assertEqual(data["fine_to_broad_decay_rate"],mode**2)
            self.assertAlmostEqual(data["fine_decay_rate"]/data["broad_decay_rate"],mode**2)

    def test_pde_residual_is_an_h_squared_stencil_diagnostic(self):
        data=_run("heat",mode=8,diffusivity=1,time=0,amplitude=.45)[3]
        x=data["pde_probe_x"];alpha=data["diffusivity"];mode=data["mode"]
        f=lambda q:1+.45*math.cos(q)+.45*math.cos(mode*q)
        residuals=[]
        for h in (.01,.005,.0025):
            residuals.append(abs(data["analytic_ut"]-alpha*(f(x+h)-2*f(x)+f(x-h))/h**2))
        self.assertGreater(residuals[0]/residuals[1],3.9)
        self.assertGreater(residuals[1]/residuals[2],3.9)
        self.assertLess(data["finite_difference_pde_residual"],.0002)

    def test_sheet_and_current_slice_have_declared_coordinates(self):
        geometry,_,_,data,_=_run("heat",time=.7)
        current=next(row for row in geometry if row["id"]=="current_profile")
        for point,x,u in zip(current["points"],data["x"],data["current_values"]):
            self.assertEqual(point,[x-math.pi,2*(u-1),4*.7/3-2+.025])
        mesh=next(row for row in geometry if row["id"]=="diffusion_history")
        self.assertEqual(mesh["indices"].count(-1),1152)


class RefractionTests(unittest.TestCase):
    def test_equal_indices_recover_the_straight_geometric_path(self):
        for height,depth,span in ((.4,2,.5),(1.1,1.2,3),(2,.4,4)):
            data=_run("refraction",n1=1.7,n2=1.7,height=height,depth=depth,span=span)[3]
            self.assertAlmostEqual(data["optimal_crossing"],span*height/(height+depth),places=13)
            self.assertAlmostEqual(data["minimum_cost"],1.7*math.hypot(span,height+depth),places=12)
            self.assertAlmostEqual(data["optimum_geometric_length"],data["geometric_straight_length"],places=13)

    def test_snell_and_strict_convexity_across_domain_extremes(self):
        for n1,n2,height,depth,span in ((1,2.5,.4,2,4),(2.5,1,2,.4,4),(1,1,.4,.4,.5),(2.5,2.5,2,2,4)):
            data=_run("refraction",n1=n1,n2=n2,height=height,depth=depth,span=span)[3]
            q=data["optimal_crossing"]
            self.assertGreater(q,0);self.assertLess(q,span)
            self.assertGreater(data["minimum_second_derivative"],0)
            self.assertLess(abs(data["minimum_derivative"]),2e-14)
            self.assertAlmostEqual(n1*math.sin(data["theta1_radians"]),n2*math.sin(data["theta2_radians"]),places=13)
            self.assertLess(data["snell_residual"],2e-14)
            for i in range(501):
                x=span*i/500
                cost=n1*math.hypot(x,height)+n2*math.hypot(span-x,depth)
                self.assertLessEqual(data["minimum_cost"],cost+2e-14)

    def test_bending_can_lengthen_the_route_and_reduce_travel_cost(self):
        data=_run("refraction",n1=1,n2=2.5,height=.6,depth=1.8,span=4)[3]
        self.assertLess(data["minimum_cost"],data["straight_cost"])
        self.assertGreater(data["optimum_geometric_length"],data["geometric_straight_length"])
        self.assertGreater(data["theta1_radians"],data["theta2_radians"])

    def test_cost_inset_stays_below_physical_rays_with_exact_cost_height(self):
        for n1,n2,height,depth,span in ((1,2.5,.4,2,4),(2.5,1,2,.4,4),(1,1,.4,.4,.5)):
            geometry,_,_,data,_=_run("refraction",n1=n1,n2=n2,height=height,depth=depth,span=span)
            curve=next(row for row in geometry if row["id"]=="optical_cost_curve")
            self.assertLess(max(p[1] for p in curve["points"]),-depth-.9)
            for point,q,cost in zip(curve["points"],data["cost_crossings"],data["cost_values"]):
                self.assertAlmostEqual(point[0],-2.5+5*q/span)
                self.assertAlmostEqual(point[1]-data["cost_plot_baseline"],cost-data["minimum_cost"])


class ScienceExportTests(unittest.TestCase):
    def test_defaults_extremes_and_presets_fit_geometry_and_export_budgets(self):
        from mathlab.kernel import _geometry_bounds
        from mathlab.manim_bridge import generate_manim
        from mathlab.x3d import to_x3d
        for spec in LESSONS:
            configs=[{}, {p["id"]:p["min"] for p in spec["parameters"]},
                     {p["id"]:p["max"] for p in spec["parameters"]}]
            configs += [row["params"] for row in spec["presets"]]
            for config in configs:
                with self.subTest(lesson=spec["id"],config=config):
                    params={p["id"]:p["default"] for p in spec["parameters"]};params.update(config)
                    primitives,metrics,_,numerics,insights=MODELS[spec["id"]](params)
                    self.assertEqual(len(primitives),len({p["id"] for p in primitives}))
                    self.assertLessEqual(len(primitives),1000)
                    self.assertLessEqual(sum(len(p.get("points",[])) for p in primitives),25000)
                    sample={"schema":"mathlab.sample/1","lesson":spec["id"],"title":spec["title"],
                            "params":params,"primitives":primitives,"metrics":metrics,"numerics":numerics,
                            "bounds":_geometry_bounds(primitives),"insights":insights,"formula":spec["formula"],
                            "view":spec["view"]}
                    json.dumps(sample,allow_nan=False)
                    self.assertLess(len(to_x3d(sample).encode()),2*1024*1024)
                    ast.parse(generate_manim(sample))


if __name__=="__main__":
    unittest.main()
