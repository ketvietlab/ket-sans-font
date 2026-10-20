"""Load the KÉT Sans design system (``design-system.json``) for one master
or one interpolated instance."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SYSTEM_PATH = ROOT / "design-system.json"


class Namespace(dict):
    def __getattr__(self, key):
        try:
            value = self[key]
        except KeyError as exc:  # pragma: no cover - programming error
            raise AttributeError(key) from exc
        return Namespace(value) if isinstance(value, dict) else value


@dataclass
class System:
    raw: dict
    master: str

    @property
    def meta(self):
        return Namespace(self.raw["meta"])

    @property
    def m(self):
        return Namespace(self.raw["metrics"])

    def _layer(self, key):
        """Family-wide values with this master's overrides on top."""
        values = dict(self.raw[key])
        values.update(self.raw["masters"][self.master].get(key, {}))
        return Namespace(values)

    @property
    def masters(self) -> list[str]:
        return list(self.raw["masters"])

    @property
    def k(self):
        return self._layer("curves")

    @property
    def st(self):
        return Namespace(self.raw["masters"][self.master]["stroke"])

    @property
    def wght(self) -> int:
        return self.raw["masters"][self.master]["wght"]

    @property
    def sh(self):
        return self._layer("shapes")

    @property
    def w(self):
        return self._layer("proportions")

    @property
    def sp(self):
        return self._layer("spacing")


LAYERS = ("curves", "shapes", "proportions", "spacing")


def _interpolate(a: dict, b: dict, t: float) -> dict:
    """``a + t (b - a)`` for every number in both tables; whole numbers stay whole."""
    out = {}
    for key, va in a.items():
        vb = b.get(key, va)
        if isinstance(va, bool) or not all(isinstance(v, (int, float)) for v in (va, vb)):
            continue
        v = va + t * (vb - va)
        out[key] = round(v) if isinstance(va, int) and isinstance(vb, int) else round(v, 4)
    return out


def expand_instances(raw: dict) -> dict:
    """Add every ``instances`` entry to ``masters`` (ordered by wght),
    interpolated between the two drawn masters around its weight."""
    drawn = dict(raw["masters"])
    for name, inst in raw.get("instances", {}).items():
        if name == "comment":
            continue
        w = inst["wght"]
        lo = max((m for m in drawn.values() if m["wght"] <= w), key=lambda m: m["wght"])
        hi = min((m for m in drawn.values() if m["wght"] >= w), key=lambda m: m["wght"])
        t = (w - lo["wght"]) / (hi["wght"] - lo["wght"])
        entry = {"wght": w, "comment": f"Instance at t = {t:.3f} between the drawn masters (see instances).",
                 "stroke": _interpolate(lo["stroke"], hi["stroke"], t)}
        for key in LAYERS:
            entry[key] = _interpolate({**raw[key], **lo.get(key, {})}, {**raw[key], **hi.get(key, {})}, t)
        raw["masters"][name] = entry
    raw["masters"] = dict(sorted(raw["masters"].items(), key=lambda kv: kv[1]["wght"]))
    return raw


def load(master: str = "Regular", path: Path = SYSTEM_PATH) -> System:
    return System(expand_instances(json.loads(path.read_text(encoding="utf-8"))), master)
