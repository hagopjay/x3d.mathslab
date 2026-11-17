"""Math Lab shared-sample film. Render with Manim Community, Cairo.
Example: manim -ql --renderer=cairo lesson.py MathlabScene
This is a baked reveal of one evaluated sample, not an interactive replay.
Generated locally; inspect before running as trusted Python code.
"""
from manim import *
import hashlib
import json
import math
import numpy as np

BRIDGE_VERSION = 'mathlab.manim-snapshot/1'
SAMPLE_SHA256 = '2fbe16cf995a670d45767fd95d425add8e74258c413f420099b32284d35ba66d'
SAMPLE_JSON = '{"axes":"Left rectangle: all objects, area 24. Right rectangle: positive results only, area 4.8 after conditional rescaling.","bounds":{"center":[-0.75,0.0,0.03125],"size":[9.35,4.5,0.5975]},"formula":"P(H|+)=P(+|H)P(H) / [P(+|H)P(H)+P(+|¬H)P(¬H)]","insights":["Every left-panel cell area divided by 24 is its exact joint probability, including very thin rare-tag cells. The right panel has fixed area 4.8 and is separately normalized to positive results only.","Mint and amber together form the positive-result denominator. Detection probability P(+|H) and posterior P(H|+) answer different questions.","Expected counts for 10,000 objects are probability times 10,000. They are not rounded tiles, observed integer counts, or a Monte Carlo result.","The detector rates are assumed fixed for this population. The model makes no claim that a real detector has constant sensitivity or false-alarm rate across changing populations.","A likelihood ratio multiplies prior odds, not prior probability. The resulting posterior is a consequence of the stated joint model, not a measure of certainty independent of its assumptions."],"lesson":"bayes","metrics":[{"id":"posterior","label":"Tagged among positive results","note":"This conditional probability is the mint share of the right panel.","unit":"%","value":50.0},{"id":"expected_tp","label":"Expected true positives","note":"Expected counts may be fractional; no random population was simulated.","unit":"per 10,000","value":99.00000000000001},{"id":"expected_fp","label":"Expected false positives","note":"","unit":"per 10,000","value":99.00000000000001},{"id":"positive","label":"All positive results","note":"","unit":"% of all objects","value":1.9800000000000002},{"id":"likelihood_ratio","label":"Positive likelihood ratio","note":"","unit":"× prior odds","value":99.0},{"id":"threshold","label":"Prior threshold for posterior >50%","note":"The posterior exceeds one half precisely when the prior exceeds this threshold.","unit":"%","value":1.0}],"numerics":{"conditional_display_area":4.8,"expected_counts":{"false_negative":1.0000000000000009,"false_positive":99.00000000000001,"true_negative":9801.0,"true_positive":99.00000000000001},"masses":{"false_negative":0.00010000000000000009,"false_positive":0.0099,"true_negative":0.9801,"true_positive":0.0099},"odds_update_residual":0.0,"population_display_area":24.0,"positive_likelihood_ratio":99.0,"positive_marginal":0.0198,"posterior":0.5,"posterior_majority_prior_threshold":0.01,"posterior_odds":1.0,"prior":0.01,"prior_odds":0.010101010101010102,"reference_population":10000,"total_mass":1.0},"params":{"false_positive":0.01,"prior":0.01,"sensitivity":0.99},"primitives":[{"color":[0.36,1.0,0.73],"id":"population_true_positive","kind":"box","position":[-4.97,0.020000000000000018,0],"size":[0.06,3.96,0.035],"transparency":0.1},{"color":[1.0,0.35,0.66],"id":"population_false_negative","kind":"box","position":[-4.97,-1.98,0],"size":[0.06,0.040000000000000036,0.035],"transparency":0.1},{"color":[1.0,0.73,0.32],"id":"population_false_positive","kind":"box","position":[-1.9700000000000006,1.98,0],"size":[5.9399999999999995,0.04,0.035],"transparency":0.1},{"color":[0.12,0.25,0.39],"id":"population_true_negative","kind":"box","position":[-1.9700000000000006,-0.020000000000000018,0],"size":[5.9399999999999995,3.96,0.035],"transparency":0.1},{"color":[0.36,1.0,0.73],"id":"positive_true_share","kind":"box","position":[2.9,1.0,0],"size":[1.2,2.0,0.035],"transparency":0.1},{"color":[1.0,0.73,0.32],"id":"positive_false_share","kind":"box","position":[2.9,-1.0,0],"size":[1.2,2.0,0.035],"transparency":0.1},{"color":[0.83,0.91,1.0],"id":"population_frame","kind":"line","points":[[-5.0,-2.0,0.05],[1.0,-2.0,0.05],[1.0,2.0,0.05],[-5.0,2.0,0.05],[-5.0,-2.0,0.05]]},{"color":[0.83,0.91,1.0],"id":"conditioned_frame","kind":"line","points":[[2.3,-2.0,0.05],[3.5,-2.0,0.05],[3.5,2.0,0.05],[2.3,2.0,0.05],[2.3,-2.0,0.05]]},{"color":[0.83,0.91,1.0],"id":"conditioning_arrow","kind":"line","points":[[1.3,0,0.08],[2.05,0,0.08],[1.88,0.11,0.08],[2.05,0,0.08],[1.88,-0.11,0.08]]}],"schema":"mathlab.sample/1","scope":"Bounded sampled mathematical model; source equations and diagnostic meanings are declared per lesson. Geometry is not a proof or a complete interactive savegame.","title":"A Positive Signal Changes the Denominator","view":"planar"}'

if hashlib.sha256(SAMPLE_JSON.encode("utf-8")).hexdigest() != SAMPLE_SHA256:
    raise ValueError("Baked Math Lab sample identity changed")
SAMPLE = json.loads(SAMPLE_JSON)


def _hex(rgb):
    return "#" + "".join(f"{round(float(c) * 255):02x}" for c in rgb)


class MathlabScene(ThreeDScene):
    """An editorial reveal of the exact retained sample geometry."""

    def construct(self):
        self.camera.background_color = "#071421"
        is_3d = SAMPLE.get("view") == "spatial" or SAMPLE["lesson"] in ("lorenz", "gradient")
        center = np.array(SAMPLE["bounds"]["center"], dtype=float)
        size = np.array(SAMPLE["bounds"]["size"], dtype=float)
        if is_3d:
            scale = 4.7 / max(float(np.linalg.norm(size)), 1e-9)
            self.set_camera_orientation(phi=65 * DEGREES, theta=-65 * DEGREES)
        else:
            scale = min(10.4 / max(float(size[0]), 1e-9),
                        4.6 / max(float(size[1]), 1e-9))
            self.set_camera_orientation(phi=0, theta=-90 * DEGREES)

        def point(p):
            # One uniform affine display transform, not another mathematical solve.
            return (np.array(p, dtype=float) - center) * scale + np.array([0, -.15, 0])

        title = Text(str(SAMPLE["title"]), font_size=30, color="#ecf5ff")
        if title.width > 12:
            title.scale_to_fit_width(12)
        title.to_edge(UP, buff=.35)
        eyebrow = Text("X3D.MATHLAB  /  ONE MODEL, TWO VIEWS", font_size=11,
                       color="#70dfcc").next_to(title, DOWN, buff=.12)
        readings = []
        metric_rows = SAMPLE.get("metrics", [])
        for metric in (metric_rows[:2] if isinstance(metric_rows, list) else []):
            if not isinstance(metric, dict):
                continue
            value = metric.get("value")
            shown = f"{value:.5g}" if isinstance(value, (int, float)) else str(value)
            readings.append(str(metric.get("label", "Reading"))[:48] + ": " + shown[:38]
                            + (" " + str(metric["unit"])[:12] if metric.get("unit") else ""))
        reading = Text("   |   ".join(readings) or "One evaluated mathematical sample",
                       font_size=12, color="#ffcd7b").next_to(eyebrow, DOWN, buff=.14)
        if reading.width > 12:
            reading.scale_to_fit_width(12)
        params = "  ".join(str(k)[:22] + "=" + str(v)[:28]
                           for k, v in list(SAMPLE["params"].items())[:10])
        caption = Text(params, font_size=12, color="#9fb9cd")
        if caption.width > 12:
            caption.scale_to_fit_width(12)
        caption.to_edge(DOWN, buff=.33)
        footer = Text("BAKED GEOMETRY  ·  INTERACTIVE PARAMETERS IN THE LAB",
                      font_size=10, color="#70dfcc").next_to(caption, UP, buff=.15)
        self.add_fixed_in_frame_mobjects(title, eyebrow, reading, caption, footer)

        solids, traces, markers = VGroup(), VGroup(), VGroup()
        # Draw surfaces before curves. Mathematical source ordering and vertices
        # remain intact in SAMPLE_JSON even when presentation groups are layered.
        for primitive in SAMPLE["primitives"]:
            color = _hex(primitive.get("color", [.4, .8, 1]))
            opacity = 1 - float(primitive.get("transparency", 0))
            kind = primitive["kind"]
            if kind == "line":
                path = VMobject(color=color, stroke_width=2.1, stroke_opacity=opacity)
                path.set_points_as_corners([point(p) for p in primitive["points"]])
                traces.add(path)
            elif kind == "sphere":
                marker = Sphere(radius=float(primitive["radius"]) * scale,
                                resolution=(8, 12), color=color,
                                fill_opacity=opacity, stroke_width=0)
                markers.add(marker.move_to(point(primitive["position"])))
            elif kind == "box":
                box = Cube(side_length=1, fill_color=color, fill_opacity=opacity,
                           stroke_color=color, stroke_width=.6)
                box.scale(np.array(primitive["size"], dtype=float) * scale)
                solids.add(box.move_to(point(primitive["position"])))
            elif kind == "mesh":
                mesh, face = VGroup(), []
                points = primitive["points"]
                for index in list(primitive["indices"]) + [-1]:
                    if index == -1:
                        if face:
                            polygon = Polygon(*[point(points[i]) for i in face],
                                              fill_color=color, fill_opacity=opacity,
                                              stroke_color=color, stroke_width=.18,
                                              stroke_opacity=min(opacity, .45))
                            mesh.add(polygon)
                        face = []
                    else:
                        face.append(index)
                solids.add(mesh)

        self.wait(.6)
        if len(solids):
            self.play(FadeIn(solids), run_time=1.3)
        else:
            self.wait(1.3)
        if len(traces):
            self.play(AnimationGroup(*[Create(path) for path in traces], lag_ratio=.018),
                      run_time=4.2, rate_func=linear)
        else:
            self.wait(4.2)
        if len(markers):
            self.play(FadeIn(markers, scale=.7), run_time=.8)
        else:
            self.wait(.8)
        # A static close lets the learner compare the completed model with the lab.
        # It is a reveal timeline; there is no claim that each drawn frame is an
        # evaluated ODE time or a historical interactive continuation state.
        self.wait(2.3)
