#!/usr/bin/env python3
"""Render an honest orthographic contact sheet of six evaluated model samples.

Matplotlib is an optional documentation dependency, never an interactive-lab
dependency. No scene geometry is re-solved or invented here. Lines, mesh faces,
boxes and sphere silhouettes come directly from evaluate(...)["primitives"].
This is a sampled-geometry projection, not a native X_ITE screenshot.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from math import sqrt
from pathlib import Path
import sys
import textwrap

ROOT = Path(__file__).resolve().parents[1]
LESSONS = ("svd", "bayes", "lagrange", "aliasing", "heat", "refraction")
BACKGROUND = "#071421"
INK = "#d8e9ed"
MUTED = "#91afbd"


def _dot(a, b):
    return sum(x*y for x, y in zip(a, b))


def _unit(v):
    size = sqrt(_dot(v, v))
    return tuple(x/size for x in v)


def projection(spatial=False):
    """Return one orthonormal camera basis, matching the authored view direction."""
    if not spatial:
        return ((1., 0., 0.), (0., 1., 0.), (0., 0., 1.))
    direction = _unit((.52, .42, 1.))
    right = _unit((direction[2], 0., -direction[0]))
    up = (direction[1]*right[2]-direction[2]*right[1],
          direction[2]*right[0]-direction[0]*right[2],
          direction[0]*right[1]-direction[1]*right[0])
    return (right, up, direction)


def project(point, basis):
    return tuple(_dot(point, axis) for axis in basis)


def mesh_faces(indices):
    face = []
    for i in indices:
        if i == -1:
            if face:
                yield face
            face = []
        else:
            face.append(i)
    if face:
        yield face


def box_faces(center, size):
    points = [[center[0]+sx*size[0]/2, center[1]+sy*size[1]/2,
               center[2]+sz*size[2]/2]
              for sz in (-1, 1) for sy in (-1, 1) for sx in (-1, 1)]
    for face in ((0, 1, 3, 2), (4, 6, 7, 5), (0, 4, 5, 1),
                 (2, 3, 7, 6), (0, 2, 6, 4), (1, 5, 7, 3)):
        yield [points[i] for i in face]


def drawables(sample):
    """Depth-sort projected primitives without changing their display coordinates."""
    basis = projection(sample.get("view") == "spatial")
    result = []
    for primitive in sample["primitives"]:
        color = tuple(primitive["color"])
        alpha = 1-primitive.get("transparency", 0)
        kind = primitive["kind"]
        if kind == "line":
            points = [project(point, basis) for point in primitive["points"]]
            # Segment sorting lets the surface hide far portions of a long line.
            for a, b in zip(points, points[1:]):
                result.append(((a[2]+b[2])/2, "line", [a[:2], b[:2]], color, alpha))
        elif kind == "sphere":
            p = project(primitive["position"], basis)
            result.append((p[2], "sphere", (p[:2], primitive["radius"]), color, alpha))
        else:
            faces = (box_faces(primitive["position"], primitive["size"]) if kind == "box"
                     else ([primitive["points"][i] for i in face]
                           for face in mesh_faces(primitive["indices"])))
            for face in faces:
                points = [project(point, basis) for point in face]
                result.append((sum(p[2] for p in points)/len(points), "face",
                               [p[:2] for p in points], color, alpha))
    return sorted(result, key=lambda row: row[0])


def self_check():
    """Check the independent projection utility before importing model code."""
    for spatial in (False, True):
        basis = projection(spatial)
        for i, axis in enumerate(basis):
            for j, other in enumerate(basis):
                assert abs(_dot(axis, other)-(1 if i == j else 0)) < 1e-14
        point = (.4, -.8, 1.7)
        projected = project(point, basis)
        assert abs(_dot(point, point)-_dot(projected, projected)) < 1e-14
    assert list(mesh_faces([0, 1, 2, -1, 3, 4, 5])) == [[0, 1, 2], [3, 4, 5]]
    faces = list(box_faces((1, 2, 3), (2, 4, 6)))
    assert len(faces) == 6 and all(len(face) == 4 for face in faces)
    toy = {"primitives": [
        {"kind": "line", "points": [[0, 0, -2], [1, 1, -2]], "color": [1, 0, 0]},
        {"kind": "sphere", "position": [0, 0, 1], "radius": .2, "color": [0, 1, 0]},
    ]}
    rows = drawables(toy)
    assert rows[0][0] == -2 and rows[1][0] == 1
    assert rows[0][2] == [(0., 0.), (1., 1.)]


def formatted(value):
    if isinstance(value, (int, float)):
        return f"{value:.4g}"
    return str(value)


def render(output, dpi=140):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.lines import Line2D
    from matplotlib.patches import Circle, Polygon

    sys.path.insert(0, str(ROOT))
    from mathlab.catalog import lesson_spec
    from mathlab.kernel import evaluate

    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10,
                         "text.color": INK, "axes.facecolor": BACKGROUND,
                         "figure.facecolor": BACKGROUND, "savefig.facecolor": BACKGROUND})
    fig = plt.figure(figsize=(16, 19.4))
    grid = fig.add_gridspec(3, 2, left=.045, right=.955, bottom=.055, top=.925,
                           wspace=.13, hspace=.19)
    fig.text(.045, .973, "X3D.MATHLAB  /  INSIGHT EXPEDITIONS", fontsize=11,
             color="#80d8c8", weight="bold")
    fig.text(.045, .946, "Insight Expeditions · sampled geometry preview", fontsize=21,
             color="#ecf6f6", weight="bold")
    for position, lesson in enumerate(LESSONS):
        spec, sample = lesson_spec(lesson), evaluate(lesson)
        slots = grid[position//2, position%2].subgridspec(4, 1,
                            height_ratios=(.14, .62, .10, .14), hspace=.025)
        head = fig.add_subplot(slots[0]); head.set_axis_off()
        head.text(0, .95, f"{position+1:02}  {spec['domain']}", fontsize=8,
                  color=spec.get("accent", "#80d8c8"), va="top")
        title = "\n".join(textwrap.wrap(spec["title"], 43))
        head.text(0, .63, title, fontsize=15, weight="bold", va="top", linespacing=1.15)
        ax = fig.add_subplot(slots[1])
        ax.set_aspect("equal", adjustable="box")
        ax.set_axis_off()
        allx, ally = [], []
        for order, (z, kind, data, color, alpha) in enumerate(drawables(sample)):
            if kind == "line":
                x, y = zip(*data)
                ax.plot(x, y, color=color, alpha=alpha, linewidth=1.15,
                        solid_capstyle="round", antialiased=True, zorder=order)
                allx.extend(x); ally.extend(y)
            elif kind == "sphere":
                center, radius = data
                ax.add_patch(Circle(center, radius, facecolor=color, edgecolor="none",
                                    alpha=alpha, antialiased=True, zorder=order))
                allx.extend((center[0]-radius, center[0]+radius))
                ally.extend((center[1]-radius, center[1]+radius))
            else:
                ax.add_patch(Polygon(data, facecolor=color, edgecolor="none",
                                     alpha=alpha, antialiased=True, zorder=order))
                allx.extend(p[0] for p in data); ally.extend(p[1] for p in data)
        xspan, yspan = max(allx)-min(allx), max(ally)-min(ally)
        ax.set_xlim(min(allx)-max(.12, .035*xspan), max(allx)+max(.12, .035*xspan))
        ax.set_ylim(min(ally)-max(.12, .06*yspan), max(ally)+max(.12, .06*yspan))
        legend = fig.add_subplot(slots[2]); legend.set_axis_off()
        entries = spec.get("legend", [])
        handles = [Line2D([0], [0], color=row["color"], linewidth=2,
                          label="\n".join(textwrap.wrap(row["label"], 29))) for row in entries]
        legend.legend(handles=handles, loc="center left", frameon=False,
                      ncol=2, fontsize=7.2, labelcolor=MUTED, handlelength=1.5,
                      columnspacing=1.4, borderaxespad=0, labelspacing=.55)
        caption = fig.add_subplot(slots[3]); caption.set_axis_off()
        readings = [f"{m['label']}: {formatted(m['value'])}" +
                    (" " + m["unit"] if m.get("unit") else "")
                    for m in sample["metrics"][:2]]
        text = "  |  ".join(readings)
        caption.text(0, .98, "\n".join(textwrap.wrap(text, 80)), fontsize=8,
                     color="#d2e5e6", va="top", linespacing=1.5)
        axes = spec.get("axes", "")
        caption.text(0, .48, "\n".join(textwrap.wrap(axes, 95)), fontsize=7.3,
                     color=MUTED, va="top", linespacing=1.45)

    fig.text(.045, .027, "Projection of exported model geometry · not an X_ITE browser capture",
             fontsize=9, color=MUTED)
    fig.text(.955, .027, "One model · inspectable mathematics", fontsize=9,
             color="#80d8c8", ha="right")
    identity = {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                for p in sorted((ROOT/"mathlab").glob("*.py"))}
    identity["render_expedition_preview.py"] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    metadata = {"Title": "Insight Expeditions · sampled geometry preview",
                "Description": json.dumps({"lessons": LESSONS, "source_sha256": identity,
                                            "projection": "orthographic; authored spatial view basis",
                                            "scope": "Matplotlib projection of actual evaluated model primitives; not native browser pixels"}, sort_keys=True),
                "Software": "MathLab optional preview renderer / Matplotlib " + matplotlib.__version__}
    output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output, dpi=dpi, metadata=metadata)
    plt.close(fig)
    print(json.dumps({"output": str(output), "lessons": list(LESSONS),
                      "pixels": [16*dpi, round(19.4*dpi)],
                      "scope": "Actual sampled model geometry; no native browser render claim."}))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT/"docs/Insight-Preview.png")
    parser.add_argument("--dpi", type=int, default=140)
    parser.add_argument("--self-check", action="store_true", help="check projection/face utilities without rendering")
    args = parser.parse_args()
    if not 72 <= args.dpi <= 300:
        parser.error("dpi must be between 72 and 300")
    self_check()
    if args.self_check:
        print("PASS orthonormal projection, exact point transform, mesh/box faces and depth ordering")
        return 0
    render(args.output.resolve(), args.dpi)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
