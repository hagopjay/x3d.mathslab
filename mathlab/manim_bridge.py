"""Bake an evaluated Math Lab sample into inspectable Manim Community source.

This module generates source only. It never imports Manim or executes that source.
The caller must treat running any Manim Python file as trusted local code execution.
"""

from __future__ import annotations

import hashlib
import json
from typing import Any

MAX_BAKED_BYTES = 2 * 1024 * 1024
MAX_MESH_FACES = 1600
BRIDGE_VERSION = "mathlab.manim-snapshot/1"


def generate_manim(sample: dict[str, Any]) -> str:
    """Return a complete ``MathlabScene(ThreeDScene)`` script for one sample.

    The same validator as native X3D export runs before generation. The snapshot
    additionally has a Cairo polygon budget; exceeding it is an explicit refusal,
    never a silently reduced mathematical surface.
    """
    from .x3d import to_x3d

    to_x3d(sample)
    try:
        encoded = json.dumps(sample, ensure_ascii=False, allow_nan=False,
                             sort_keys=True, separators=(",", ":"))
    except (TypeError, ValueError, RecursionError) as exc:
        raise ValueError("MANIM_SAMPLE_JSON: sample must be finite JSON data") from exc
    if len(encoded.encode("utf-8")) > MAX_BAKED_BYTES:
        raise ValueError("MANIM_SAMPLE_BUDGET: baked sample exceeds 2 MiB")
    face_count = 0
    for primitive in sample["primitives"]:
        if primitive["kind"] != "mesh":
            continue
        current = 0
        for index in primitive["indices"]:
            if index == -1:
                face_count += bool(current)
                current = 0
            else:
                current += 1
        face_count += bool(current)
    if face_count > MAX_MESH_FACES:
        raise ValueError("MANIM_FACE_BUDGET: snapshot exceeds 1600 mesh faces")
    digest = hashlib.sha256(encoded.encode("utf-8")).hexdigest()
    # Concatenate literals once. Replacing template markers after inserting user
    # text can accidentally rewrite data containing those marker strings.
    header = (
        '"""Math Lab shared-sample film. Render with Manim Community, Cairo.\n'
        'Example: manim -ql --renderer=cairo lesson.py MathlabScene\n'
        'This is a baked reveal of one evaluated sample, not an interactive replay.\n'
        'Generated locally; inspect before running as trusted Python code.\n"""\n'
        'from manim import *\n'
        'import hashlib\nimport json\nimport math\nimport numpy as np\n\n'
        f'BRIDGE_VERSION = {BRIDGE_VERSION!r}\n'
        f'SAMPLE_SHA256 = {digest!r}\n'
        f'SAMPLE_JSON = {encoded!r}\n'
    )
    return header + _RUNTIME


_RUNTIME = '''
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
'''
