# AgriMind

**An Observable Multi-Agent Orchestration System for Intelligent Crop Advisory**

AgriMind coordinates specialist agents for weather, soil, crop disease, fertilizer/advisory, and market intelligence. A deterministic, safety-first decision layer resolves conflicts, while an observability layer records the agent execution trail, conflicts, evidence, and final decision.

## Architecture

- Weather Agent
- Soil Agent
- Crop Disease Agent (MobileNetV3)
- Fertilizer/Advisory Agent
- Market Intelligence Agent
- Orchestrator (LangGraph when installed, deterministic fallback otherwise)
- Conflict resolver with rainfall safety veto, disease confidence gate, disease urgency, nutrient requirement, and market tie-breaking
- ICAR-grounded RAG with ChromaDB/TF-IDF fallback
- FastAPI backend
- SQLite observability
- Next.js farmer dashboard

## Quick start

See [`RUN.md`](RUN.md) for the reproducible setup and run sequence.

The large PlantVillage image archive is **not** committed to GitHub. `scripts/setup_runtime.py` downloads the official archive and official train/test manifests when needed. A real trained disease checkpoint must be produced by the training pipeline; no fake checkpoint is included.

## Safety principle

The LLM explanation layer does not override the deterministic agricultural safety policy. It explains an already-selected action.

## Data sources

PlantVillage, ICAR agro-advisories, Open-Meteo, Agmarknet/eNAM and Soil Health Card resources are used by the project as described in the code and documentation.
