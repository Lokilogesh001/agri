"""Shared state object passed through the LangGraph orchestrator."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional
@dataclass
class WeatherResult:
    rainfall_risk: float = 0.0
    temperature_risk: float = 0.0
    irrigation_condition: str = "normal"
    fertilizer_condition: str = "normal"
    confidence: float = 0.0
    reason: str = ""
@dataclass
class SoilResult:
    nitrogen_deficiency: float = 0.0
    phosphorus_deficiency: float = 0.0
    potassium_deficiency: float = 0.0
    overall_deficiency: float = 0.0
    priority_nutrient: str = ""
    confidence: float = 0.0
@dataclass
class DiseaseResult:
    predicted_class: Optional[str] = None
    confidence: float = 0.0
    severity: str = "low"
    actionable: bool = False
@dataclass
class AdvisoryResult:
    scores: dict = field(default_factory=dict)
    preliminary_recommendation: str = "monitor"
    confidence: float = 0.0
    reason: str = ""
@dataclass
class MarketResult:
    price_change_pct: float = 0.0
    moving_average: float = 0.0
    market_score: float = 0.0
    signal: str = "hold"
@dataclass
class CropContext:
    crop: str = ""
    growth_stage: str = ""
    suitability_hint: float = 0.6
@dataclass
class AgriMindState:
    run_id: str
    raw_inputs: dict = field(default_factory=dict)
    farm: dict = field(default_factory=dict)
    crop: CropContext = field(default_factory=CropContext)
    weather: WeatherResult = field(default_factory=WeatherResult)
    soil: SoilResult = field(default_factory=SoilResult)
    disease: DiseaseResult = field(default_factory=DiseaseResult)
    advisory: AdvisoryResult = field(default_factory=AdvisoryResult)
    market: MarketResult = field(default_factory=MarketResult)
    conflicts: list = field(default_factory=list)
    final_recommendation: Optional[str] = None
    confidence: Optional[float] = None
    execution_trace: list = field(default_factory=list)
    def log(self, event: str): self.execution_trace.append(event)
