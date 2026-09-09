"""Disease Agent — image classification wrapper."""
from __future__ import annotations
import os
from functools import lru_cache
from orchestrator.state import DiseaseResult

LOW_CONFIDENCE_GATE = 0.60
_HIGH_SEVERITY_KEYWORDS = ("blight", "rot", "wilt", "rust")


def _infer_severity(predicted_class: str) -> str:
    label = (predicted_class or "").strip().lower()
    # PlantVillage labels are prefixed with the crop name, e.g.
    # "Apple___healthy". Treat any class whose disease component is
    # "healthy" as low severity.
    disease_component = label.split("___", 1)[-1] if "___" in label else label
    if disease_component == "healthy":
        return "low"
    return "high" if any(k in disease_component for k in _HIGH_SEVERITY_KEYWORDS) else "moderate"


@lru_cache(maxsize=1)
def _load_default_model():
    path = os.getenv("DISEASE_MODEL_PATH", "ml/artifacts/best.pt")
    if not os.path.exists(path):
        raise RuntimeError(f"Disease model checkpoint not found: {path}")
    from ml.disease_model import DiseasePredictor
    return DiseasePredictor(path, confidence_gate=LOW_CONFIDENCE_GATE)


def classify(image_path: str, model=None) -> dict:
    if not image_path:
        raise ValueError("image_path is required when disease_override is not provided")
    predictor = model or _load_default_model()
    return predictor.predict(image_path)


def run(image_path: str | None = None, model=None, override: dict | None = None) -> DiseaseResult:
    result = override if override is not None else classify(image_path, model=model)
    predicted_class = result["predicted_class"]
    confidence = float(result["confidence"])
    return DiseaseResult(
        predicted_class=predicted_class,
        confidence=round(confidence, 4),
        severity=_infer_severity(predicted_class),
        actionable=confidence >= LOW_CONFIDENCE_GATE,
    )
