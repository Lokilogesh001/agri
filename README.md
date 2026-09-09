# AgriMind

**An Observable Multi-Agent Orchestration System for Intelligent Crop Advisory.**

AgriMind coordinates specialist agents for weather, soil, crop disease, fertilizer/advisory, and market intelligence. A deterministic safety-first decision layer resolves conflicts, while an observability layer records the agent execution trail, decisions, conflicts, evidence, and feedback.

## Architecture

```text
Farmer Input
    |
    v
Orchestrator
    +--> Weather Agent
    +--> Soil Agent
    +--> Crop Disease Agent --> MobileNetV3-Large
    +--> Fertilizer / Advisory Agent
    +--> Market Intelligence Agent
    |
    v
Safety-first Conflict Resolver
    |
    v
Final Advisory + Evidence + Audit Trail
```

## Quick start

1. Install dependencies: `pip install -r requirements.txt`
2. Prepare PlantVillage assets: `python scripts/setup_runtime.py`
3. Train the disease model using `COLAB_TRAINING.md` (GPU recommended).
4. Start API: `uvicorn api.main:app --reload`
5. Start frontend: `cd web && npm install && npm run dev`

The raw PlantVillage image archive is intentionally not committed to GitHub. The setup script downloads the official archive and train/test manifests. The disease checkpoint is not fabricated; it must come from an actual training run.

## Disease model

MobileNetV3-Large is trained with augmentation, class-weighted cross-entropy, label smoothing, AdamW, cosine learning-rate scheduling, CUDA AMP, early stopping, and a leaf-grouped validation split. The official test manifest is held out until final evaluation. See `ml/train_disease.py` and `COLAB_TRAINING.md`.

## RAG and evidence

The `rag/` package supports ICAR-grounded retrieval with ChromaDB when available and a local TF-IDF fallback. Evidence is retained with source metadata so recommendations can be audited.

## Safety policy

1. `rainfall_risk > 0.70` -> `DELAY` safety veto.
2. Disease confidence `< 0.60` makes the disease output non-actionable; it does not terminate the advisory flow.
3. Actionable high-severity disease takes priority over nutrient optimization.
4. `soil_deficiency > 0.60` can trigger fertilizer application after higher-priority safety rules.
5. Market/economic score is a tie-breaker and cannot override agronomic safety.

The LLM explanation layer explains the selected action and does not override deterministic safety policy.

## Data sources

PlantVillage, ICAR agro-advisories, Open-Meteo, Agmarknet/eNAM, and Soil Health Card resources are used by the project as described in the code and documentation.
