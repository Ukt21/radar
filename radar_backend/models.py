from pydantic import BaseModel
from typing import Optional, List


class Scenario(BaseModel):
    text: str
    entry: str
    sl: str
    tp1: str
    tp2: str
    score: float


class AnalysisResponse(BaseModel):
    pair: str
    tf: str
    price: float

    vs_btc: str

    rsi: float
    ema_50: float
    ema_200: float

    volume_24h: str
    money_flow: str
    money_flow_strength: str

    whale_activity: str
    whale_netflow: str

    image_url: Optional[str] = None

    long_scenario: Scenario
    short_scenario: Scenario

    best_side: str
    ai_comment: str
