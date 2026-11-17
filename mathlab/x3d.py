"""Deterministic, bounded export of Math Lab samples to native X3D 4.0.

This adapter exports a starting mathematical picture, not the web lesson's
controller, a proof, or a live-state checkpoint. It never parses arbitrary XML,
executes code, or emits an external asset URL. See docs/X3D-CONTRACT.md.
"""

from __future__ import annotations

import hashlib
import json
import math
import xml.etree.ElementTree as ET
from collections.abc import Mapping
from typing import Any

MAX_PRIMITIVES = 1000
MAX_POINTS = 25_000
MAX_INDICES = 150_000
MAX_METADATA_BYTES = 65_536
MAX_ABS = 100_000_000.0
ADAPTER_VERSION = "mathlab.x3d/1"


def _number(value: Any, field: str, *, minimum: float | None = None,
            maximum: float = MAX_ABS) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"X3D_NUMBER: {field} must be a finite number")
    try:
        number = float(value)
    except (ValueError, OverflowError) as error:
        raise ValueError(f"X3D_NUMBER: {field} is outside the numeric budget") from error
    if not math.isfinite(number) or abs(number) > maximum or minimum is not None and number < minimum:
        raise ValueError(f"X3D_NUMBER: {field} is outside its finite range")
    return number


def _vector(value: Any, field: str, *, minimum: float | None = None,
            maximum: float = MAX_ABS) -> tuple[float, float, float]:
    if not isinstance(value, (list, tuple)) or len(value) != 3:
        raise ValueError(f"X3D_VECTOR: {field} requires three numbers")
    return tuple(_number(v, field, minimum=minimum, maximum=maximum) for v in value)  # type: ignore[return-value]


def _scalar(value: float) -> str:
    # Seventeen significant decimal digits retain the incoming binary64 value.
    # Coordinate itself is an X3D single-precision field: renderer rounding is
    # a separate, declared representation boundary.
    return "0" if value == 0 else format(value, ".17g")


def _values(values: Any) -> str:
    return " ".join(_scalar(float(v)) for v in values)


def _mfstring(text: str) -> str:
    """One X3D MFString item; XML escaping is subsequently owned by ElementTree."""
    return '"' + text.replace("\\", "\\\\").replace('"', '\\"') + '"'


def _canonical(value: Any) -> str:
    try:
        return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)
    except (TypeError, ValueError, OverflowError) as error:
        raise ValueError("X3D_METADATA: sample must be finite JSON data") from error


def _text(value: Any, field: str, maximum: int = 200) -> str:
    if not isinstance(value, str) or not value or len(value) > maximum:
        raise ValueError(f"X3D_TEXT: {field} must be nonempty text of at most {maximum} characters")
    # XML 1.0 permits tab/newline/carriage return and these scalar ranges.
    if any(not (ord(c) in (9, 10, 13) or 0x20 <= ord(c) <= 0xD7FF or
                0xE000 <= ord(c) <= 0xFFFD or 0x10000 <= ord(c) <= 0x10FFFF) for c in value):
        raise ValueError(f"X3D_TEXT: {field} contains a character XML 1.0 cannot encode")
    return value


def _validate(sample: Any) -> tuple[list[dict[str, Any]], dict[str, Any], str]:
    if not isinstance(sample, Mapping) or sample.get("schema") != "mathlab.sample/1":
        raise ValueError("X3D_SAMPLE: expected mathlab.sample/1")
    lesson = _text(sample.get("lesson"), "lesson", 80)
    title = _text(sample.get("title"), "title", 200)
    if not isinstance(sample.get("params"), Mapping):
        raise ValueError("X3D_METADATA: params must be an object")
    bounds = sample.get("bounds")
    if not isinstance(bounds, Mapping):
        raise ValueError("X3D_BOUNDS: bounds are required")
    center = _vector(bounds.get("center"), "bounds.center")
    size = _vector(bounds.get("size"), "bounds.size", minimum=0)
    if max(size) <= 0:
        raise ValueError("X3D_BOUNDS: at least one dimension must be positive")
    primitives = sample.get("primitives")
    if not isinstance(primitives, list) or not 1 <= len(primitives) <= MAX_PRIMITIVES:
        raise ValueError(f"X3D_BUDGET: requires 1..{MAX_PRIMITIVES} primitives")
    normalized: list[dict[str, Any]] = []
    ids: set[str] = set()
    point_count = index_count = 0
    for n, primitive in enumerate(primitives):
        if not isinstance(primitive, Mapping):
            raise ValueError("X3D_PRIMITIVE: every primitive must be an object")
        kind = primitive.get("kind")
        if kind not in ("line", "sphere", "mesh", "box"):
            raise ValueError("X3D_PRIMITIVE: supported kinds are line, sphere, mesh, box")
        identity = _text(primitive.get("id", f"primitive-{n}"), "primitive.id", 160)
        if identity in ids:
            raise ValueError("X3D_ID: duplicate primitive source identity")
        ids.add(identity)
        row: dict[str, Any] = {"kind": kind, "id": identity,
                               "color": _vector(primitive.get("color", [0.4, 0.8, 1.0]), "color", minimum=0, maximum=1),
                               "transparency": _number(primitive.get("transparency", 0), "transparency", minimum=0, maximum=1)}
        if kind in ("line", "mesh"):
            points = primitive.get("points")
            if not isinstance(points, (list, tuple)) or len(points) < (2 if kind == "line" else 3):
                raise ValueError("X3D_POINTS: line needs two points; mesh needs at least three")
            point_count += len(points)
            if point_count > MAX_POINTS:
                raise ValueError(f"X3D_BUDGET: aggregate coordinate limit is {MAX_POINTS}")
            row["points"] = [_vector(p, "point") for p in points]
            if kind == "mesh":
                indices = primitive.get("indices")
                if not isinstance(indices, (list, tuple)) or not indices:
                    raise ValueError("X3D_INDICES: mesh needs face indices")
                index_count += len(indices)
                if index_count > MAX_INDICES:
                    raise ValueError(f"X3D_BUDGET: aggregate index limit is {MAX_INDICES}")
                face: list[int] = []
                clean: list[int] = []
                for index in indices:
                    if isinstance(index, bool) or not isinstance(index, int) or index < -1 or index >= len(points):
                        raise ValueError("X3D_INDICES: face index must reference an existing point or be -1")
                    clean.append(index)
                    if index == -1:
                        if len(face) < 3 or len(set(face)) != len(face):
                            raise ValueError("X3D_INDICES: a face needs at least three distinct indices")
                        face.clear()
                    else:
                        face.append(index)
                if face:
                    if len(face) < 3 or len(set(face)) != len(face):
                        raise ValueError("X3D_INDICES: a face needs at least three distinct indices")
                    clean.append(-1)
                row["indices"] = clean
        else:
            row["position"] = _vector(primitive.get("position"), "position")
            if kind == "sphere":
                radius = _number(primitive.get("radius"), "radius", minimum=0)
                if radius <= 0:
                    raise ValueError("X3D_GEOMETRY: radius must be positive")
                row["radius"] = radius
            else:
                dimensions = _vector(primitive.get("size"), "box.size", minimum=0)
                if min(dimensions) <= 0:
                    raise ValueError("X3D_GEOMETRY: box dimensions must be positive")
                row["size"] = dimensions
        normalized.append(row)
    metadata = {"adapter": ADAPTER_VERSION, "sample_schema": sample["schema"], "lesson": lesson,
                "title": title, "parameters": dict(sample["params"]),
                "metrics": sample.get("metrics", []), "insights": sample.get("insights", []),
                "bounds": {"center": center, "size": size},
                "scope": "Static sampled geometry and authored lesson parameters; not a proof, live controller, or checkpoint."}
    # A full-sample identity distinguishes geometry/metric changes even with
    # unchanged parameters. It identifies bytes, not an authenticated publisher.
    source = _canonical(dict(sample))
    metadata["sample_sha256"] = hashlib.sha256(source.encode("utf-8")).hexdigest()
    metadata["configuration_sha256"] = hashlib.sha256(_canonical({"lesson": lesson, "params": dict(sample["params"])}).encode("utf-8")).hexdigest()
    encoded = _canonical(metadata)
    if len(encoded.encode("utf-8")) > MAX_METADATA_BYTES:
        raise ValueError(f"X3D_BUDGET: metadata limit is {MAX_METADATA_BYTES} bytes")
    _text(encoded, "metadata", MAX_METADATA_BYTES)
    return normalized, metadata, encoded


def _appearance(shape: ET.Element, color: tuple[float, float, float], transparency: float = 0,
                *, line: bool = False) -> None:
    appearance = ET.SubElement(shape, "Appearance")
    ET.SubElement(appearance, "Material", diffuseColor=_values(color),
                  emissiveColor=_values(color if line else [v * 0.045 for v in color]),
                  specularColor="0.22 0.28 0.34", shininess="0.28",
                  transparency=_scalar(transparency))
    if line:
        ET.SubElement(appearance, "LineProperties", applied="true", linewidthScaleFactor="2")


def _line(parent: ET.Element, points: list[tuple[float, float, float]], color: tuple[float, float, float],
          *, identity: str | None = None, transparency: float = 0) -> ET.Element:
    shape = ET.SubElement(parent, "Shape", **({"DEF": identity} if identity else {}))
    _appearance(shape, color, transparency, line=True)
    geometry = ET.SubElement(shape, "IndexedLineSet", coordIndex=" ".join(map(str, range(len(points)))) + " -1")
    ET.SubElement(geometry, "Coordinate", point=" ".join(_values(p) for p in points))
    return shape


def _grid(scene: ET.Element, center: tuple[float, float, float], size: tuple[float, float, float], *, planar: bool) -> None:
    """A bounded decorative reference plane; it is not part of the numerical model."""
    group = ET.SubElement(scene, "Group", DEF="MathLabReferenceGrid")
    sx, sy, sz = (max(v, 1) for v in size)
    points: list[tuple[float, float, float]] = []
    indices: list[int] = []
    for n in range(11):
        u = n / 10 - 0.5
        if planar:
            z = center[2] - max(sx, sy) * 0.008
            pairs = [((center[0] + u * sx, center[1] - sy / 2, z), (center[0] + u * sx, center[1] + sy / 2, z)),
                     ((center[0] - sx / 2, center[1] + u * sy, z), (center[0] + sx / 2, center[1] + u * sy, z))]
        else:
            y = center[1] - sy * 0.56
            pairs = [((center[0] + u * sx, y, center[2] - sz / 2), (center[0] + u * sx, y, center[2] + sz / 2)),
                     ((center[0] - sx / 2, y, center[2] + u * sz), (center[0] + sx / 2, y, center[2] + u * sz))]
        for a, b in pairs:
            indices.extend([len(points), len(points) + 1, -1]); points.extend([a, b])
    shape = ET.SubElement(group, "Shape")
    _appearance(shape, (0.065, 0.13, 0.21), line=True)
    line = ET.SubElement(shape, "IndexedLineSet", coordIndex=" ".join(map(str, indices)))
    ET.SubElement(line, "Coordinate", point=" ".join(_values(p) for p in points))


def to_x3d(sample: Mapping[str, Any]) -> str:
    """Return a self-contained standard-node X3D 4.0 document or raise ValueError.

    Validation completes before XML construction. Unknown primitive kinds and
    malformed references are refused rather than partially exported.
    """
    primitives, metadata, encoded = _validate(sample)
    root = ET.Element("X3D", profile="Immersive", version="4.0")
    head = ET.SubElement(root, "head")
    for name, content in [("title", metadata["title"] + ".x3d"), ("generator", ADAPTER_VERSION),
                          ("description", metadata["scope"]), ("mathlab.lesson", metadata["lesson"]),
                          ("mathlab.configuration_sha256", metadata["configuration_sha256"])]:
        ET.SubElement(head, "meta", name=name, content=content)
    scene = ET.SubElement(root, "Scene")
    info = ET.SubElement(scene, "WorldInfo", title=metadata["title"], info=_mfstring("X3D Math Lab • " + metadata["scope"]))
    ET.SubElement(info, "MetadataString", containerField="metadata", name="mathlab.sample", reference=ADAPTER_VERSION, value=_mfstring(encoded))
    ET.SubElement(scene, "Background", skyColor="0.018 0.035 0.075")
    ET.SubElement(scene, "NavigationInfo", DEF="MathLabNavigation", type='"EXAMINE" "ANY"', headlight="true", speed="1")
    center = metadata["bounds"]["center"]
    size = metadata["bounds"]["size"]
    radius = max(1.0, math.sqrt(sum(v * v for v in size)) / 2)
    distance = radius / math.sin(0.35) * 1.16
    # Thin integral boxes are an area diagram, not a request for an oblique
    # camera. These authored plane lessons deliberately preserve XY reading.
    planar = metadata["lesson"] in ("linear", "derivative", "integral", "fourier") or size[2] <= max(size[0], size[1]) * 1e-8
    direction = (0.0, 0.0, 1.0) if planar else (0.52, 0.42, 1.0)
    length = math.sqrt(sum(v * v for v in direction))
    unit = tuple(v / length for v in direction)
    position = tuple(center[i] + unit[i] * distance for i in range(3))
    axis = (-unit[1], unit[0], 0.0)
    axis_length = math.sqrt(axis[0] ** 2 + axis[1] ** 2)
    orientation = (0.0, 0.0, 1.0, 0.0) if axis_length == 0 else (axis[0] / axis_length, axis[1] / axis_length, 0.0, math.acos(unit[2]))
    ET.SubElement(scene, "Viewpoint", DEF="MathLabView", description="Math Lab • " + metadata["title"],
                  position=_values(position), orientation=_values(orientation), centerOfRotation=_values(center), fieldOfView="0.70")
    ET.SubElement(scene, "DirectionalLight", direction="-0.4 -0.7 -1", color="0.78 0.88 1", intensity="0.8")
    ET.SubElement(scene, "DirectionalLight", direction="0.8 0.4 0.6", color="1 0.76 0.49", intensity="0.35")
    _grid(scene, center, size, planar=planar)
    group = ET.SubElement(scene, "Group", DEF="MathLabModel")
    for n, primitive in enumerate(primitives):
        parent = group
        if primitive["kind"] in ("sphere", "box"):
            parent = ET.SubElement(group, "Transform", translation=_values(primitive["position"]))
        identity = f"MathLabPrimitive_{n:04d}"
        if primitive["kind"] == "line":
            shape = _line(parent, primitive["points"], primitive["color"], identity=identity, transparency=primitive["transparency"])
        else:
            shape = ET.SubElement(parent, "Shape", DEF=identity)
            _appearance(shape, primitive["color"], primitive["transparency"])
            if primitive["kind"] == "sphere":
                ET.SubElement(shape, "Sphere", radius=_scalar(primitive["radius"]))
            elif primitive["kind"] == "box":
                ET.SubElement(shape, "Box", size=_values(primitive["size"]))
            else:
                geometry = ET.SubElement(shape, "IndexedFaceSet", solid="false", creaseAngle="0.75",
                                         coordIndex=" ".join(map(str, primitive["indices"])))
                ET.SubElement(geometry, "Coordinate", point=" ".join(_values(p) for p in primitive["points"]))
        # Shape's XML content model orders metadata before appearance/geometry.
        shape.insert(0, ET.Element("MetadataString", containerField="metadata", name="mathlab.primitive", value=_mfstring(primitive["id"])))
    ET.indent(root, space="  ")
    return '<?xml version="1.0" encoding="UTF-8"?>\n' + ET.tostring(root, encoding="unicode", short_empty_elements=True) + "\n"
