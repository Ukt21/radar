from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from models import AnalysisResponse, Scenario

from services.binance import build_indicators, fetch_klines
from services.whales import get_whales
from services.gpt import build_scenarios
import httpx


app = FastAPI(title="Radar Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/analysis", response_model=AnalysisResponse)
async def analysis(pair: str = Query(...), tf: str = Query("1H")):

    price, rsi, ema50, ema200, vol24 = await build_indicators(pair, tf)

    whale_act, whale_net = await get_whales(pair)

    vs_btc = "0%"  # потом можно заменить на real

    money_flow = "inflow" if price > ema50 else "outflow"
    money_flow_strength = "medium"

    best_side = "LONG" if price > ema50 else "SHORT"

    data = dict(
        price=price,
        rsi=rsi,
        ema50=ema50,
        ema200=ema200,
        volume24=vol24,
        money_flow=money_flow,
        whales=whale_act,
        vs_btc=vs_btc,
        best_side=best_side
    )

    gpt = await build_scenarios(pair, tf, data)

    long_s = gpt["long"]
    short_s = gpt["short"]

    return AnalysisResponse(
        pair=pair,
        tf=tf,
        price=price,
        vs_btc=vs_btc,
        rsi=rsi,
        ema_50=ema50,
        ema_200=ema200,
        volume_24h=f"{vol24}",
        money_flow=money_flow,
        money_flow_strength=money_flow_strength,
        whale_activity=whale_act,
        whale_netflow=whale_net,
        image_url=None,
        long_scenario=Scenario(**long_s),
        short_scenario=Scenario(**short_s),
        best_side=best_side,
        ai_comment=gpt["comment"]
    )

