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
SAMPLE_SHA256 = 'ae35593f041018c03e9ee1a5690b3302903e73dd816c469db7eb571cebb7a64c'
SAMPLE_JSON = '{"axes":"Spatial coordinates: mathematical (x,y,z). Orbit to separate the target, plane and perpendicular residual.","bounds":{"center":[0.0,0.0,0.057125542138681595],"size":[8.8,7.50221579412365,4.795748915722637]},"formula":"minₓ ||Ax−b||²    ·    p=A x̂    ·    Aᵀ(b−p)=0","insights":["The world uses mathematical coordinates (x,y,z) without flattening. Orbit the camera to see the target, plane, and perpendicular residual.","Columns a₁=(1,0,0) and a₂=(1,ε cos θ,ε sin θ) remain independent because ε≥0.05. Their span is fixed as ε changes, so the projection stays fixed while coordinates can grow.","The mint point uses a stable geometric QR calculation with orthonormal basis q₁=(1,0,0), q₂=(0,cos θ,sin θ). The normal-equation coefficients are retained only as a comparison.","A large condition number describes worst-case sensitivity; it does not say every target has a large error. Drawing the projection directly avoids huge opposing coefficient vectors obscuring its geometry."],"lesson":"least_squares","metrics":[{"id":"residual","label":"Closest distance ||b−p||","note":"","unit":"","value":1.163076821608171},{"id":"orthogonality","label":"Max |aⱼ·(b−p)|","note":"Zero is the analytic optimality condition; this is a floating-point diagnostic.","unit":"","value":5.551115123125783e-17},{"id":"coefficient_1","label":"Coefficient x̂₁","note":"","unit":"","value":-2.4557683767741656},{"id":"coefficient_2","label":"Coefficient x̂₂","note":"","unit":"","value":3.8557683767741655},{"id":"condition","label":"2-norm condition number κ₂(A)","note":"κ₂(AᵀA)=κ₂(A)². The display solves by the known orthonormal basis rather than forming the normal equations.","unit":"","value":3.932042912437429}],"numerics":{"coefficients":[-2.4557683767741656,3.8557683767741655],"columns":[[1.0,0.0,0.0],[1.0,0.4688884871327282,0.2874779759118626]],"condition_A":3.932042912437429,"condition_gram":15.46096146524942,"normal_equation_coefficient_gap":6.280369834735101e-16,"normal_equation_coefficients":[-2.455768376774165,3.855768376774165],"orthogonality":[0.0,-5.551115123125783e-17],"projection":[1.4,1.8079254009198535,1.1084484885400052],"q1":[1.0,0.0,0.0],"q2":[0.0,0.8525245220595057,0.5226872289306592],"reconstructed":[1.4,1.8079254009198535,1.108448488540005],"residual":[0.0,-0.6079254009198536,0.9915515114599949],"residual_norm":1.163076821608171,"target":[1.4,1.2,2.1]},"params":{"bx":1.4,"by":1.2,"bz":2.1,"epsilon":0.55,"tilt":0.55},"primitives":[{"color":[0.65,0.55,1.0],"id":"reachable_plane","indices":[0,1,2,3,-1],"kind":"mesh","points":[[-4,-3.4100980882380227,-2.090748915722637],[4,-3.4100980882380227,-2.090748915722637],[4,3.4100980882380227,2.090748915722637],[-4,3.4100980882380227,2.090748915722637]],"transparency":0.8},{"color":[0.12,0.25,0.39],"id":"plane_u_-4","kind":"line","points":[[-4,-3.4100980882380227,-2.090748915722637],[-4,3.4100980882380227,2.090748915722637]]},{"color":[0.12,0.25,0.39],"id":"plane_v_-4","kind":"line","points":[[-4,-3.4100980882380227,-2.090748915722637],[4,-3.4100980882380227,-2.090748915722637]]},{"color":[0.12,0.25,0.39],"id":"plane_u_-3","kind":"line","points":[[-3,-3.4100980882380227,-2.090748915722637],[-3,3.4100980882380227,2.090748915722637]]},{"color":[0.12,0.25,0.39],"id":"plane_v_-3","kind":"line","points":[[-4,-2.557573566178517,-1.5680616867919777],[4,-2.557573566178517,-1.5680616867919777]]},{"color":[0.12,0.25,0.39],"id":"plane_u_-2","kind":"line","points":[[-2,-3.4100980882380227,-2.090748915722637],[-2,3.4100980882380227,2.090748915722637]]},{"color":[0.12,0.25,0.39],"id":"plane_v_-2","kind":"line","points":[[-4,-1.7050490441190114,-1.0453744578613184],[4,-1.7050490441190114,-1.0453744578613184]]},{"color":[0.12,0.25,0.39],"id":"plane_u_-1","kind":"line","points":[[-1,-3.4100980882380227,-2.090748915722637],[-1,3.4100980882380227,2.090748915722637]]},{"color":[0.12,0.25,0.39],"id":"plane_v_-1","kind":"line","points":[[-4,-0.8525245220595057,-0.5226872289306592],[4,-0.8525245220595057,-0.5226872289306592]]},{"color":[0.12,0.25,0.39],"id":"plane_u_0","kind":"line","points":[[0,-3.4100980882380227,-2.090748915722637],[0,3.4100980882380227,2.090748915722637]]},{"color":[0.12,0.25,0.39],"id":"plane_v_0","kind":"line","points":[[-4,0.0,0.0],[4,0.0,0.0]]},{"color":[0.12,0.25,0.39],"id":"plane_u_1","kind":"line","points":[[1,-3.4100980882380227,-2.090748915722637],[1,3.4100980882380227,2.090748915722637]]},{"color":[0.12,0.25,0.39],"id":"plane_v_1","kind":"line","points":[[-4,0.8525245220595057,0.5226872289306592],[4,0.8525245220595057,0.5226872289306592]]},{"color":[0.12,0.25,0.39],"id":"plane_u_2","kind":"line","points":[[2,-3.4100980882380227,-2.090748915722637],[2,3.4100980882380227,2.090748915722637]]},{"color":[0.12,0.25,0.39],"id":"plane_v_2","kind":"line","points":[[-4,1.7050490441190114,1.0453744578613184],[4,1.7050490441190114,1.0453744578613184]]},{"color":[0.12,0.25,0.39],"id":"plane_u_3","kind":"line","points":[[3,-3.4100980882380227,-2.090748915722637],[3,3.4100980882380227,2.090748915722637]]},{"color":[0.12,0.25,0.39],"id":"plane_v_3","kind":"line","points":[[-4,2.557573566178517,1.5680616867919777],[4,2.557573566178517,1.5680616867919777]]},{"color":[0.12,0.25,0.39],"id":"plane_u_4","kind":"line","points":[[4,-3.4100980882380227,-2.090748915722637],[4,3.4100980882380227,2.090748915722637]]},{"color":[0.12,0.25,0.39],"id":"plane_v_4","kind":"line","points":[[-4,3.4100980882380227,2.090748915722637],[4,3.4100980882380227,2.090748915722637]]},{"color":[1.0,0.73,0.32],"id":"target_b","kind":"line","points":[[0,0,0],[1.4,1.2,2.1]]},{"color":[0.36,1.0,0.73],"id":"projection_p","kind":"line","points":[[0,0,0],[1.4,1.8079254009198535,1.1084484885400052]]},{"color":[1.0,0.35,0.66],"id":"residual_e","kind":"line","points":[[1.4,1.8079254009198535,1.1084484885400052],[1.4,1.2,2.1]]},{"color":[0.28,0.84,1.0],"id":"column_1","kind":"line","points":[[0,0,0],[1.0,0.0,0.0]]},{"color":[0.65,0.55,1.0],"id":"column_2","kind":"line","points":[[0,0,0],[1.0,0.4688884871327282,0.2874779759118626]]},{"color":[1.0,0.73,0.32],"id":"target_tip","kind":"sphere","position":[1.4,1.2,2.1],"radius":0.105},{"color":[0.36,1.0,0.73],"id":"projection_tip","kind":"sphere","position":[1.4,1.8079254009198535,1.1084484885400052],"radius":0.09},{"color":[0.28,0.84,1.0],"id":"column_1_tip","kind":"sphere","position":[1.0,0.0,0.0],"radius":0.065},{"color":[0.65,0.55,1.0],"id":"column_2_tip","kind":"sphere","position":[1.0,0.4688884871327282,0.2874779759118626],"radius":0.065},{"color":[1.0,0.35,0.66],"id":"right_angle","kind":"line","points":[[1.4,1.6772535936871886,1.3215796190548816],[1.65,1.6772535936871886,1.3215796190548816],[1.65,1.8079254009198535,1.1084484885400052]]}],"schema":"mathlab.sample/1","scope":"Bounded sampled mathematical model; source equations and diagnostic meanings are declared per lesson. Geometry is not a proof or a complete interactive savegame.","title":"The Closest Reachable Point","view":"spatial"}'

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
