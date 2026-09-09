"""
Weighted advisory scoring: S(a) = w_s*S_soil + w_w*S_weather + w_d*S_disease + w_c*S_crop

Only invoked by decision.rules.resolve_conflict for actions that survive
Stage 1 (the veto layer). Weights are prototype parameters — see canonical
doc Section 10 for the "pending empirical validation" note.
"""

from __future__ import annotations

DEFAULT_WEIGHTS = {
    "soil": 0.35,
    "weather": 0.30,
    "disease": 0.15,
    "crop": 0.20,
}


def _soil_support(state, action: str) -> float:
    d = state.soil.overall_deficiency
    if action == "apply_fertilizer":
        return d
    if action == "delay":
        return 1 - d
    return 0.5


def _weather_suitability(state, action: str) -> float:
    r = state.weather.rainfall_risk
    if action == "apply_fertilizer":
        return 1 - r
    if action == "delay":
        return r
    return 0.5


def _disease_relevance(state, action: str) -> float:
    if not state.disease.actionable:
        return 0.3
    if action == "apply_fertilizer":
        return 1 - (state.disease.confidence * 0.3)
    return 0.5


def _crop_suitability(state, action: str) -> float:
    return state.crop.suitability_hint if hasattr(state.crop, "suitability_hint") else 0.6


def weighted_score(state, action: str, weights: dict | None = None) -> float:
    w = weights or DEFAULT_WEIGHTS
    s_soil = _soil_support(state, action)
    s_weather = _weather_suitability(state, action)
    s_disease = _disease_relevance(state, action)
    s_crop = _crop_suitability(state, action)

    score = (
        w["soil"] * s_soil
        + w["weather"] * s_weather
        + w["disease"] * s_disease
        + w["crop"] * s_crop
    )
    return round(score, 4)
