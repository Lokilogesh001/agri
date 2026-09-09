"""LangGraph orchestration for AgriMind.

The graph deliberately separates the Advisory Agent from conflict resolution:
START -> weather -> soil -> disease -> advisory -> market -> decision -> END
"""
from __future__ import annotations
import time
import uuid
try:
    from langgraph.graph import END, StateGraph
    LANGGRAPH_AVAILABLE = True
except ImportError:
    END = "__end__"
    StateGraph = None
    LANGGRAPH_AVAILABLE = False
from agents import advisory_agent, disease_agent, market_agent, soil_agent, weather_agent
from decision.rules import resolve_conflict
from observability import database as obs
from orchestrator.state import AgriMindState, CropContext

def _timed(fn, *args, **kwargs):
    start = time.perf_counter(); result = fn(*args, **kwargs)
    return result, round((time.perf_counter() - start) * 1000, 2)

def node_weather(state):
    inputs = state.raw_inputs
    result, latency = _timed(weather_agent.run, lat=inputs.get("lat"), lon=inputs.get("lon"), override=inputs.get("weather_override"))
    state.weather = result; state.log(f"weather_agent -> rainfall_risk={result.rainfall_risk}")
    obs.log_agent_call(state.run_id, "weather", inputs.get("weather_override") or {}, result.__dict__, "ok" if result.confidence > 0 else "degraded", result.confidence, latency)
    return state

def node_soil(state):
    inputs = state.raw_inputs
    result, latency = _timed(soil_agent.run, n=inputs["n"], p=inputs["p"], k=inputs["k"], crop=state.crop.crop, soil_type=inputs.get("soil_type", ""))
    state.soil = result; state.log(f"soil_agent -> overall_deficiency={result.overall_deficiency}")
    obs.log_agent_call(state.run_id, "soil", {"n": inputs["n"], "p": inputs["p"], "k": inputs["k"]}, result.__dict__, "ok", result.confidence, latency)
    return state

def node_disease(state):
    inputs = state.raw_inputs
    result, latency = _timed(disease_agent.run, image_path=inputs.get("image_path"), override=inputs.get("disease_override"))
    state.disease = result; state.log(f"disease_agent -> {result.predicted_class} ({result.confidence})")
    obs.log_agent_call(state.run_id, "disease", inputs.get("disease_override") or {"image_path": inputs.get("image_path")}, result.__dict__, "ok", result.confidence, latency)
    return state

def node_advisory(state):
    result, latency = _timed(advisory_agent.run, state)
    state.advisory = result; state.log(f"advisory_agent -> preliminary={result.preliminary_recommendation}")
    obs.log_agent_call(state.run_id, "advisory", {"crop": state.crop.__dict__}, result.__dict__, "ok", result.confidence, latency)
    return state

def node_market(state):
    inputs = state.raw_inputs
    result, latency = _timed(market_agent.run, current_price=inputs.get("current_price", 0), price_history=inputs.get("price_history", []))
    state.market = result; state.log(f"market_agent -> score={result.market_score} signal={result.signal}")
    obs.log_agent_call(state.run_id, "market", {"current_price": inputs.get("current_price"), "price_history": inputs.get("price_history")}, result.__dict__, "ok", 0.75, latency)
    return state

def node_decision(state):
    decision, _latency = _timed(resolve_conflict, state)
    state.final_recommendation = decision.action; state.conflicts.extend(decision.to_conflict_rows(state.run_id))
    for row in decision.to_conflict_rows(state.run_id): obs.log_conflict(**row)
    confidence = max(decision.scores.values()) if decision.scores else 0.85
    state.confidence = confidence; state.log(f"orchestrator -> {decision.action} ({decision.reason})")
    obs.log_decision(state.run_id, decision.action, decision.reason, confidence)
    return state

_COMPILED_GRAPH = None

def build_graph():
    if not LANGGRAPH_AVAILABLE: return None
    graph = StateGraph(AgriMindState)
    for name, fn in (("weather",node_weather),("soil",node_soil),("disease",node_disease),("advisory",node_advisory),("market",node_market),("decision",node_decision)): graph.add_node(name, fn)
    graph.set_entry_point("weather"); graph.add_edge("weather","soil"); graph.add_edge("soil","disease"); graph.add_edge("disease","advisory"); graph.add_edge("advisory","market"); graph.add_edge("market","decision"); graph.add_edge("decision",END)
    return graph.compile()

def get_graph():
    global _COMPILED_GRAPH
    if _COMPILED_GRAPH is None: _COMPILED_GRAPH = build_graph()
    return _COMPILED_GRAPH

def run_advisory(inputs: dict):
    initial_state = AgriMindState(run_id=str(uuid.uuid4()), raw_inputs=inputs, farm=inputs.get("farm", {}), crop=CropContext(crop=inputs.get("crop", ""), growth_stage=inputs.get("growth_stage", ""), suitability_hint=float(inputs.get("crop_suitability_hint", 0.6))))
    obs.init_db(); graph = get_graph()
    if graph is None:
        state = initial_state
        for node in (node_weather,node_soil,node_disease,node_advisory,node_market,node_decision): state = node(state)
        return state
    final_state = graph.invoke(initial_state)
    return final_state if isinstance(final_state, AgriMindState) else AgriMindState(**final_state)
