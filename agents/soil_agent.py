"""Soil Agent — nutrient deficiency scoring."""
from __future__ import annotations
from data_sources.soil import get_reference_targets
from orchestrator.state import SoilResult
def _deficiency(actual: float,target: float)->float:
    if target<=0: return 0.0
    return round(max(0.0,(target-actual)/target),4)
def run(n: float,p: float,k: float,crop: str="",soil_type: str="",targets: dict|None=None,weights: dict|None=None)->SoilResult:
    targets,weights=targets or get_reference_targets(crop,soil_type)[0],weights or get_reference_targets(crop,soil_type)[1]
    dn,dp,dk=_deficiency(float(n),targets["N"]),_deficiency(float(p),targets["P"]),_deficiency(float(k),targets["K"])
    deficiencies={"nitrogen":dn,"phosphorus":dp,"potassium":dk}; overall=round(weights["N"]*dn+weights["P"]*dp+weights["K"]*dk,4)
    return SoilResult(nitrogen_deficiency=dn,phosphorus_deficiency=dp,potassium_deficiency=dk,overall_deficiency=overall,priority_nutrient=max(deficiencies,key=deficiencies.get),confidence=0.9)
