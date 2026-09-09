"""Market Agent — trend and sell/hold signal."""
from __future__ import annotations
from orchestrator.state import MarketResult
def _pct_change(current: float, previous: float)->float: return 0.0 if previous==0 else round(((current-previous)/previous)*100,2)
def _moving_average(prices: list[float])->float: return round(sum(prices)/len(prices),2) if prices else 0.0
def run(current_price: float, price_history: list[float], weights: dict|None=None)->MarketResult:
    weights=weights or {"trend":0.5,"volatility":0.3,"arrival":0.2}; prices=[float(x) for x in price_history if float(x)>=0]
    ma=_moving_average(prices) if prices else float(current_price); pct_change=_pct_change(float(current_price),prices[-1]) if prices else 0.0
    trend=1.0 if float(current_price)>ma else 0.0
    if len(prices)>1 and ma>0:
        variance=sum((p-ma)**2 for p in prices)/len(prices); volatility=min((variance**0.5)/ma,1.0)
    else: volatility=0.3
    score=round(weights["trend"]*trend+weights["volatility"]*(1-volatility)+weights["arrival"]*0.5,4)
    signal="sell" if score>0.65 else ("hold" if score>0.4 else "caution")
    return MarketResult(price_change_pct=pct_change,moving_average=ma,market_score=score,signal=signal)
