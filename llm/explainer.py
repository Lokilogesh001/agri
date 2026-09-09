"""Source-grounded explanation adapter."""
from __future__ import annotations
import os,json
def deterministic_explanation(state,evidence=None)->str:
    parts=[f"Recommendation: {state.final_recommendation.replace('_',' ')}.",f"Rainfall risk is {state.weather.rainfall_risk:.2f}.",f"Overall soil deficiency is {state.soil.overall_deficiency:.2f}, with {state.soil.priority_nutrient} as the priority nutrient."]
    if state.disease.predicted_class:
        parts.append(f"Disease signal: {state.disease.predicted_class} at {state.disease.confidence:.2f} confidence.")
        if not state.disease.actionable: parts.append("The disease signal is below the 0.60 confidence gate, so it is not used as an actionable disease decision.")
    parts.append(f"Market signal: {state.market.signal}.")
    if evidence: parts.append(f"{len(evidence)} source-grounded agronomy record(s) were retrieved for context.")
    return " ".join(parts)
def _xai_explain(state,evidence):
    import requests
    key=os.getenv("XAI_API_KEY")
    if not key: return None
    model=os.getenv("XAI_MODEL","grok-3-mini")
    payload={"model":model,"messages":[{"role":"system","content":"You explain an already-selected agricultural advisory. Never change the recommendation, invent pesticide/fertilizer doses, or override safety rules. Use only the supplied evidence. Be concise and farmer-friendly."},{"role":"user","content":json.dumps({"recommendation":state.final_recommendation,"reason":state.execution_trace[-1] if state.execution_trace else "","weather":state.weather.__dict__,"soil":state.soil.__dict__,"disease":state.disease.__dict__,"market":state.market.__dict__,"evidence":evidence or []},default=str)}],"temperature":0.1}
    r=requests.post("https://api.x.ai/v1/chat/completions",headers={"Authorization":f"Bearer {key}","Content-Type":"application/json"},json=payload,timeout=20); r.raise_for_status(); return r.json()["choices"][0]["message"]["content"]
def explain(state,evidence=None):
    try:
        text=_xai_explain(state,evidence or [])
        if text: return text
    except Exception: pass
    return deterministic_explanation(state,evidence)
