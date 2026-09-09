"""Soil reference provider."""
from __future__ import annotations
DEFAULT_TARGETS={"N":100.0,"P":50.0,"K":100.0}
DEFAULT_WEIGHTS={"N":0.5,"P":0.2,"K":0.3}
def get_reference_targets(crop: str="", soil_type: str="") -> tuple[dict,dict]: return DEFAULT_TARGETS.copy(), DEFAULT_WEIGHTS.copy()
