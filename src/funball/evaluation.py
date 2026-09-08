"""Offline marker evaluation. A wrong marker is not a successful lock."""
from math import dist, isfinite


def _point(value):
    if (not isinstance(value, (list, tuple)) or len(value) != 2
            or any(type(v) not in (int, float) or not isfinite(v) or v < 0 for v in value)):
        raise ValueError("center_px must contain two finite nonnegative numbers")


def _index(items):
    result = {}
    for item in items:
        key = item.get("frame_id")
        if type(key) is not int or key < 0 or key in result:
            raise ValueError("frame_id must be unique and nonnegative")
        result[key] = item
    return result


def evaluate(annotations, predictions):
    annotations = _index(annotations)
    predictions = _index(predictions)
    if predictions.keys() - annotations.keys():
        raise ValueError("prediction without ground-truth frame")
    for item in predictions.values():
        if item.get("center_px") is not None:
            _point(item["center_px"])
    tp = fp = fn = excluded = 0
    errors = []
    for truth in annotations.values():
        if truth.get("status") not in {"visible", "absent", "occluded", "unresolvable"}:
            raise ValueError("unknown annotation status")
        if truth["status"] == "unresolvable":
            excluded += 1
            continue
        if truth["status"] == "visible":
            _point(truth.get("center_px"))
            radius = truth.get("radius_px")
            if type(radius) not in (int, float) or not isfinite(radius) or radius <= 0:
                raise ValueError("visible target requires positive finite radius_px")
        point = predictions.get(truth["frame_id"], {}).get("center_px")
        visible = truth["status"] == "visible"
        correct = False
        if visible and point is not None:
            error = dist(point, truth["center_px"])
            errors.append(error)
            correct = error <= truth["radius_px"]
        tp += int(correct)
        fp += int(point is not None and not correct)
        fn += int(visible and not correct)
    return {
        "true_positive": tp, "false_positive": fp, "false_negative": fn,
        "precision": tp / (tp + fp) if tp + fp else None,
        "recall": tp / (tp + fn) if tp + fn else None,
        "center_errors_px": errors,
        "excluded_frames": excluded,
    }
