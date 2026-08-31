"""Uniform artifact writer for #982.  Every object we claim anything about is
written through here, so that verify_artifacts.py can re-check it.

Schema (one JSON file, or a JSON file holding a list of these):
{
  "problem": 982,
  "label":   "<short id>",
  "coords_kind": "int" | "sympy" | "mp",
  "coords":  [[x,y], ...]          # ints, or sympy-parseable strings, or decimal strings
  "n": <int>,
  "claim":   "counterexample" | "near_miss" | "reference",
  "claimed_per_vertex": [...],     # distinct-distance count at each vertex
  "claimed_max_per_vertex": <int>,
  "claimed_convex": true/false,
  "target_floor_n_2": <int>,
  "producer": "<exact command line>",
  "notes": "..."
}
"""

import json, os

ART = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'artifacts')


def _counts_int(coords):
    n = len(coords)
    out = []
    for i in range(n):
        s = set()
        for j in range(n):
            if i == j:
                continue
            dx = coords[i][0] - coords[j][0]
            dy = coords[i][1] - coords[j][1]
            s.add(dx * dx + dy * dy)
        out.append(len(s))
    return out


def write(label, coords, coords_kind='int', claim='near_miss', producer='',
          notes='', per_vertex=None, convex=None, extra=None):
    os.makedirs(ART, exist_ok=True)
    n = len(coords)
    if per_vertex is None and coords_kind == 'int':
        per_vertex = _counts_int(coords)
    rec = {
        'problem': 982,
        'label': label,
        'coords_kind': coords_kind,
        'coords': coords,
        'n': n,
        'claim': claim,
        'claimed_per_vertex': per_vertex,
        'claimed_max_per_vertex': (max(per_vertex) if per_vertex else None),
        'claimed_convex': convex,
        'target_floor_n_2': n // 2,
        'producer': producer,
        'notes': notes,
    }
    if extra:
        rec.update(extra)
    path = os.path.join(ART, label + '.json')
    with open(path, 'w') as f:
        json.dump(rec, f, indent=1)
    return path


def write_many(label, records):
    os.makedirs(ART, exist_ok=True)
    path = os.path.join(ART, label + '.json')
    with open(path, 'w') as f:
        json.dump(records, f, indent=1)
    return path
