from __future__ import annotations
import json, os
from datetime import datetime, timezone
from sqlalchemy import create_engine, Column, Integer, String, Float, Text, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
DATABASE_URL=os.environ.get("DATABASE_URL","sqlite:///agrimind_local.db")
Base=declarative_base(); _engine=None; _SessionLocal=None
def _get_session_factory():
    global _engine,_SessionLocal
    url=os.environ.get("DATABASE_URL",DATABASE_URL)
    if _engine is None or str(_engine.url)!=url:
        connect_args={"check_same_thread":False} if url.startswith("sqlite") else {}
        _engine=create_engine(url,echo=False,future=True,connect_args=connect_args); _SessionLocal=sessionmaker(bind=_engine,future=True)
    return _SessionLocal
def _get_engine(): _get_session_factory(); return _engine
def reset_engine_for_tests():
    global _engine,_SessionLocal; _engine=None; _SessionLocal=None
class AgentLog(Base):
    __tablename__="agent_logs"; id=Column(Integer,primary_key=True,autoincrement=True); run_id=Column(String,index=True,nullable=False); agent_name=Column(String,nullable=False); input=Column(Text); output=Column(Text); status=Column(String); confidence=Column(Float); latency=Column(Float); timestamp=Column(DateTime,default=lambda:datetime.now(timezone.utc))
class Decision(Base):
    __tablename__="decisions"; decision_id=Column(Integer,primary_key=True,autoincrement=True); run_id=Column(String,index=True,nullable=False); recommendation=Column(String); reason=Column(String); confidence=Column(Float); timestamp=Column(DateTime,default=lambda:datetime.now(timezone.utc))
class Conflict(Base):
    __tablename__="conflicts"; conflict_id=Column(Integer,primary_key=True,autoincrement=True); run_id=Column(String,index=True,nullable=False); agent_a=Column(String); agent_b=Column(String); issue=Column(String); resolution=Column(String); priority=Column(Integer)
class Feedback(Base):
    __tablename__="feedback"; id=Column(Integer,primary_key=True,autoincrement=True); run_id=Column(String,index=True,nullable=False); farmer_action_taken=Column(String); outcome_reported=Column(String); comment=Column(Text); timestamp=Column(DateTime,default=lambda:datetime.now(timezone.utc))
def init_db(): Base.metadata.create_all(bind=_get_session_factory().kw["bind"])
def log_agent_call(run_id,agent_name,input_data,output_data,status,confidence,latency_ms):
    with _get_session_factory()() as session:
        session.add(AgentLog(run_id=run_id,agent_name=agent_name,input=json.dumps(input_data,default=str),output=json.dumps(output_data,default=str),status=status,confidence=confidence,latency=latency_ms)); session.commit()
def log_decision(run_id,recommendation,reason,confidence):
    with _get_session_factory()() as session: session.add(Decision(run_id=run_id,recommendation=recommendation,reason=reason,confidence=confidence)); session.commit()
def log_conflict(run_id,agent_a,agent_b,issue,resolution,priority):
    with _get_session_factory()() as session: session.add(Conflict(run_id=run_id,agent_a=agent_a,agent_b=agent_b,issue=issue,resolution=resolution,priority=priority)); session.commit()
def log_feedback(run_id,farmer_action_taken,outcome_reported="",comment=""):
    with _get_session_factory()() as session: session.add(Feedback(run_id=run_id,farmer_action_taken=farmer_action_taken,outcome_reported=outcome_reported,comment=comment)); session.commit()
def get_run_trail(run_id):
    with _get_session_factory()() as session:
        logs=session.query(AgentLog).filter_by(run_id=run_id).all(); decisions=session.query(Decision).filter_by(run_id=run_id).all(); conflicts=session.query(Conflict).filter_by(run_id=run_id).all()
        return {"run_id":run_id,"agent_logs":[{"agent":l.agent_name,"status":l.status,"confidence":l.confidence,"latency_ms":l.latency,"output":json.loads(l.output) if l.output else {}} for l in logs],"decisions":[{"recommendation":d.recommendation,"reason":d.reason,"confidence":d.confidence} for d in decisions],"conflicts":[{"agent_a":c.agent_a,"agent_b":c.agent_b,"issue":c.issue,"resolution":c.resolution,"priority":c.priority} for c in conflicts]}
