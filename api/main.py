from __future__ import annotations
import os, tempfile
from pathlib import Path
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from orchestrator.graph import run_advisory
from observability import database as obs
from llm.explainer import explain
app = FastAPI(title="AgriMind API", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=[x.strip() for x in os.getenv("CORS_ORIGINS", "*").split(",")], allow_credentials=False, allow_methods=["*"], allow_headers=["*"])
class AdvisoryRequest(BaseModel):
    lat: float | None = Field(default=None, ge=-90, le=90); lon: float | None = Field(default=None, ge=-180, le=180)
    crop: str = ""; growth_stage: str = ""; n: float = Field(ge=0); p: float = Field(ge=0); k: float = Field(ge=0)
    current_price: float = Field(default=0, ge=0); price_history: list[float] = Field(default_factory=list); image_path: str | None = None
    weather_override: dict | None = None; disease_override: dict | None = None; soil_type: str = ""; farm: dict = Field(default_factory=dict)
class FeedbackRequest(BaseModel):
    run_id: str; farmer_action_taken: str; outcome_reported: str = ""; comment: str = ""
def _serialize(state):
    trail = obs.get_run_trail(state.run_id); evidence = []
    try:
        from rag.retriever import KnowledgeRetriever
        evidence = KnowledgeRetriever().search(f"{state.crop.crop} {state.crop.growth_stage} {state.final_recommendation} soil weather disease", n_results=4)
    except Exception: pass
    return {"run_id":state.run_id,"recommendation":state.final_recommendation,"confidence":state.confidence,"explanation":explain(state,evidence),"weather":state.weather.__dict__,"soil":state.soil.__dict__,"disease":state.disease.__dict__,"advisory":state.advisory.__dict__,"market":state.market.__dict__,"conflicts":state.conflicts,"execution_trace":state.execution_trace,"evidence":evidence,"audit":trail}
@app.on_event("startup")
def startup(): obs.init_db()
@app.get("/health")
def health(): return {"status":"ok","service":"agrimind-api","version":"1.0.0"}
@app.post("/api/advisory")
def advisory(payload: AdvisoryRequest):
    try: return _serialize(run_advisory(payload.model_dump()))
    except Exception as exc: raise HTTPException(status_code=422, detail=str(exc)) from exc
@app.post("/api/advisory/upload")
async def advisory_upload(crop: str=Form("Tomato"), growth_stage: str=Form("vegetative"), lat: float|None=Form(None), lon: float|None=Form(None), n: float=Form(50), p: float=Form(50), k: float=Form(50), current_price: float=Form(0), price_history: str=Form(""), soil_type: str=Form(""), image: UploadFile|None=File(None)):
    path=None
    try:
        if image:
            suffix=Path(image.filename or "leaf.jpg").suffix.lower() or ".jpg"
            with tempfile.NamedTemporaryFile(delete=False,suffix=suffix) as tmp: tmp.write(await image.read()); path=tmp.name
        history=[float(x.strip()) for x in price_history.split(",") if x.strip()]
        payload=AdvisoryRequest(lat=lat,lon=lon,crop=crop,growth_stage=growth_stage,n=n,p=p,k=k,current_price=current_price,price_history=history,image_path=path,soil_type=soil_type)
        return _serialize(run_advisory(payload.model_dump()))
    except Exception as exc: raise HTTPException(status_code=422, detail=str(exc)) from exc
    finally:
        if path:
            try: os.unlink(path)
            except OSError: pass
@app.get("/api/runs/{run_id}")
def get_run(run_id: str): return obs.get_run_trail(run_id)
@app.post("/api/feedback")
def feedback(payload: FeedbackRequest): obs.log_feedback(**payload.model_dump()); return {"status":"saved","run_id":payload.run_id}
