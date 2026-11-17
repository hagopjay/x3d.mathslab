"""Mathematical references and visible area/coordinate contracts for inference lessons."""
import ast
import json
import math
import unittest
import xml.etree.ElementTree as ET

from mathlab.lessons_inference import LESSONS, MODELS


def run_model(name, **params):
    spec = next(row for row in LESSONS if row['id'] == name)
    config = {p['id']: p['default'] for p in spec['parameters']}
    config.update(params)
    return MODELS[name](config)


def multiply(matrix, vector):
    return [sum(a*b for a, b in zip(row, vector)) for row in matrix]


class SingularDirections(unittest.TestCase):
    def test_singular_directions_are_eigenvectors_of_gram_matrix(self):
        for first, ratio, u, v in ((2,.35,.65,-.45), (.5,0,math.pi,-math.pi),
                                    (2.5,1,-2,1.2), (1.3,.001,.8,-1.7)):
            data = run_model('svd', sigma1=first, ratio=ratio, angle_u=u, angle_v=v)[3]
            A = data['target_matrix']
            gram = [[sum(A[k][i]*A[k][j] for k in range(2)) for j in range(2)] for i in range(2)]
            for vector, output, sigma in zip(data['input_directions'], data['output_directions'], data['singular_values']):
                for actual, expected in zip(multiply(A, vector), output):
                    self.assertAlmostEqual(actual, sigma*expected, places=13)
                for actual, expected in zip(multiply(gram, vector), vector):
                    self.assertAlmostEqual(actual, sigma*sigma*expected, places=12)
            self.assertLess(data['reconstruction_residual'], 1e-14)
            self.assertLess(data['orthogonality_residual'], 1e-14)

    def test_instructional_stages_are_not_confused_with_the_target(self):
        params = {'sigma1':2, 'ratio':.2, 'angle_u':.8, 'angle_v':-.7}
        start = run_model('svd', **params, progress=0)[3]
        first = run_model('svd', **params, progress=1)[3]
        second = run_model('svd', **params, progress=2)[3]
        done = run_model('svd', **params, progress=3)[3]
        self.assertEqual(start['displayed_matrix'], [[1,0],[0,1]])
        self.assertEqual(first['displayed_matrix'], first['Vt'])
        self.assertAlmostEqual(first['displayed_determinant'],1)
        self.assertAlmostEqual(second['displayed_determinant'], .8)
        self.assertEqual(done['displayed_matrix'],done['target_matrix'])
        self.assertNotEqual(start['displayed_matrix'],start['target_matrix'])
        self.assertEqual(start['singular_values'],done['singular_values'])

    def test_rank_collapse_and_equal_singular_values_have_declared_limits(self):
        collapsed = run_model('svd', ratio=0, progress=3)[3]
        self.assertEqual(collapsed['target_rank'],1)
        self.assertIsNone(collapsed['target_condition'])
        self.assertAlmostEqual(collapsed['target_determinant'],0)
        json.dumps(collapsed, allow_nan=False)
        first = run_model('svd', ratio=1, angle_u=.4, angle_v=-.3)[3]
        changed = run_model('svd', ratio=1, angle_u=1.1, angle_v=.4)[3]
        for row, twin in zip(first['target_matrix'], changed['target_matrix']):
            for x,y in zip(row,twin): self.assertAlmostEqual(x,y,places=14)
        self.assertNotEqual(first['input_directions'],changed['input_directions'])

    def test_displayed_vector_endpoints_retain_exact_panel_offsets(self):
        geometry,_,_,data,_ = run_model('svd', progress=1.6)
        rows = {row['id']:row for row in geometry}
        cx = data['panel_centers']['image'][0]
        for j, vector in enumerate(data['input_directions']):
            endpoint = rows[f'displayed_direction_{j}']['points'][-1]
            mathematical = multiply(data['displayed_matrix'], vector)
            self.assertAlmostEqual(endpoint[0]-cx,mathematical[0])
            self.assertAlmostEqual(endpoint[1],mathematical[1])


class ConditionalEvidence(unittest.TestCase):
    def test_rare_positive_counts_reproduce_the_counterexample(self):
        data = run_model('bayes', prior=.001, sensitivity=.99, false_positive=.01)[3]
        self.assertAlmostEqual(data['expected_counts']['true_positive'],9.9)
        self.assertAlmostEqual(data['expected_counts']['false_positive'],99.9)
        self.assertAlmostEqual(data['posterior'],9.9/(9.9+99.9))
        self.assertLess(data['posterior'],.1)
        self.assertAlmostEqual(data['total_mass'],1)

    def test_every_mosaic_cell_area_and_positive_share_has_the_stated_denominator(self):
        for prior,sensitivity,fpr in ((.001,.5,.25),(.01,.99,.01),(.5,1,.001)):
            geometry,_,_,data,_ = run_model('bayes',prior=prior,sensitivity=sensitivity,false_positive=fpr)
            population = {row['id'].removeprefix('population_'):row for row in geometry
                          if row['kind']=='box' and row['id'].startswith('population_')}
            for name,mass in data['masses'].items():
                if mass == 0:
                    self.assertNotIn(name,population)
                    continue
                row=population[name]
                self.assertAlmostEqual(row['size'][0]*row['size'][1]/data['population_display_area'],mass)
            conditioned = next(row for row in geometry if row['id']=='positive_true_share')
            self.assertAlmostEqual(conditioned['size'][0]*conditioned['size'][1]/data['conditional_display_area'],data['posterior'])
            self.assertAlmostEqual(sum(data['expected_counts'].values()),10_000)
            self.assertTrue(all(min(row['size'])>0 for row in geometry if row['kind']=='box'))

    def test_odds_identity_threshold_and_base_rate_monotonicity(self):
        posterior=[]
        for prior in (.001,.01,.1,.5):
            data=run_model('bayes',prior=prior,sensitivity=.8,false_positive=.1)[3]
            posterior.append(data['posterior'])
            self.assertAlmostEqual(data['posterior_odds'],data['prior_odds']*data['positive_likelihood_ratio'])
            self.assertEqual(data['posterior']>.5,prior>data['posterior_majority_prior_threshold'])
        self.assertEqual(posterior,sorted(posterior))
        threshold=.1/(.8+.1)
        self.assertAlmostEqual(run_model('bayes',prior=threshold,sensitivity=.8,false_positive=.1)[3]['posterior'],.5)

    def test_fixed_prior_changes_in_sensitivity_and_false_alarm_have_expected_effects(self):
        base=run_model('bayes',prior=.02,sensitivity=.5,false_positive=.1)[3]['posterior']
        sensitive=run_model('bayes',prior=.02,sensitivity=.9,false_positive=.1)[3]['posterior']
        specific=run_model('bayes',prior=.02,sensitivity=.5,false_positive=.01)[3]['posterior']
        self.assertGreater(sensitive,base)
        self.assertGreater(specific,base)


class ConstrainedExtrema(unittest.TestCase):
    def test_analytic_support_bounds_all_sampled_feasible_points(self):
        for a,b,phi in ((2,1,.7),(.7,2.6,-math.pi),(2.6,.7,1.5),(1.6,1.6,.7)):
            data=run_model('lagrange',axis_a=a,axis_b=b,direction=phi)[3]
            support=data['maximum_objective']
            for i in range(2048):
                theta=2*math.pi*i/2048
                value=a*math.cos(theta)*math.cos(phi)+b*math.sin(theta)*math.sin(phi)
                self.assertLessEqual(value,support+1e-14)
                self.assertGreaterEqual(value,-support-1e-14)
            self.assertAlmostEqual(data['maximum_constraint_value'],1)
            c=data['objective_direction']
            self.assertAlmostEqual(sum(x*y for x,y in zip(c,data['maximum_point'])),support)
            self.assertLess(data['multiplier_residual'],1e-14)

    def test_tangent_stationarity_leaves_the_ambient_gradient_nonzero(self):
        base=run_model('lagrange',axis_a=2,axis_b=1,direction=.7)[3]
        optimum=run_model('lagrange',axis_a=2,axis_b=1,direction=.7,probe=base['maximizing_theta'])[3]
        self.assertAlmostEqual(optimum['probe_tangent_derivative'],0,places=14)
        self.assertAlmostEqual(math.hypot(*optimum['objective_direction']),1)
        self.assertAlmostEqual(optimum['probe_objective'],optimum['maximum_objective'])
        g=optimum['probe_constraint_gradient']; t=optimum['probe_tangent']
        self.assertAlmostEqual(sum(x*y for x,y in zip(g,t)),0)
        wrong=run_model('lagrange',axis_a=2,axis_b=1,direction=.7,probe=.7)[3]
        self.assertGreater(abs(wrong['probe_tangent_derivative']),.1)

    def test_feasible_derivative_agrees_with_independent_central_difference(self):
        for theta in (-math.pi,-.8,0,.9,math.pi):
            data=run_model('lagrange',axis_a=1.3,axis_b=2.4,direction=-.5,probe=theta)[3]
            def f(t): return 1.3*math.cos(t)*math.cos(-.5)+2.4*math.sin(t)*math.sin(-.5)
            h=1e-5
            self.assertAlmostEqual(data['probe_tangent_derivative'],(f(theta+h)-f(theta-h))/(2*h),places=9)
            self.assertAlmostEqual(data['probe_constraint_value'],1)

    def test_contour_geometry_has_equal_objective_values(self):
        for phi in (0,math.pi/2,-math.pi,.73):
            geometry,_,_,data,_=run_model('lagrange',direction=phi)
            c=data['objective_direction']; support=data['maximum_objective']
            contours=[row for row in geometry if row['id'].startswith('objective_contour_')]
            self.assertEqual(len(contours),5)
            for row,fraction in zip(contours,(-1,-.5,0,.5,1)):
                for x,y,_ in row['points']:
                    self.assertAlmostEqual(c[0]*x+c[1]*y,fraction*support,places=12)


class InferenceExportContracts(unittest.TestCase):
    def test_extremes_and_presets_are_finite_bounded_and_exportable(self):
        from mathlab.kernel import evaluate
        from mathlab.x3d import to_x3d
        from mathlab.cards import card_from_x3d
        from mathlab.manim_bridge import generate_manim

        for spec in LESSONS:
            defaults={p['id']:p['default'] for p in spec['parameters']}
            configs=[defaults,{p['id']:p['min'] for p in spec['parameters']},
                     {p['id']:p['max'] for p in spec['parameters']}]
            configs.extend(defaults|preset['params'] for preset in spec['presets'])
            for config in configs:
                with self.subTest(lesson=spec['id'],config=config):
                    sample=evaluate(spec['id'],config)
                    json.dumps(sample,allow_nan=False)
                    self.assertLess(len(sample['primitives']),1000)
                    self.assertLess(sum(len(row.get('points',[])) for row in sample['primitives']),25_000)
                    self.assertEqual(len(sample['primitives']),len({row['id'] for row in sample['primitives']}))
                    xml=to_x3d(sample)
                    ET.fromstring(xml)
                    self.assertEqual(card_from_x3d(xml)['params'],sample['params'])
                    ast.parse(generate_manim(sample))


if __name__ == '__main__':
    unittest.main()
