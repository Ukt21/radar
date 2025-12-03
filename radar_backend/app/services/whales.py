# radar_backend/app/services/whales.py
from typing import List
import asyncio

import httpx

from radar_backend.app.config import MEMPOOL_API_URL, WHALE_ADDRESSES

async def get_whales(symbol: str):
    # Заглушка — потом подключим Glassnode/CryptoQuant
    return "neutral", "0 USDT"


async def _fetch_address_stats(client: httpx.AsyncClient, address: str) -> dict:
    resp = await client.get(f"{MEMPOOL_API_URL}/address/{address}")
    resp.raise_for_status()
    data = resp.json()

    chain = data.get("chain_stats", {})
    mem = data.get("mempool_stats", {})

    # Сумма в BTC, не в сатоши
    unconfirmed_net_btc = (
        mem.get("funded_txo_sum", 0) - mem.get("spent_txo_sum", 0)
    ) / 1e8

    return {
        "address": address,
        "unconfirmed_net_btc": unconfirmed_net_btc,
        "unconfirmed_txs": mem.get("tx_count", 0),
        "total_received_btc": chain.get("funded_txo_sum", 0) / 1e8,
        "total_sent_btc": chain.get("spent_txo_sum", 0) / 1e8,
    }


async def summarize_whales(addresses: List[str] | None = None) -> str:
    addrs = addresses or WHALE_ADDRESSES
    if not addrs:
        return "Кошельки китов не настроены."

    async with httpx.AsyncClient(timeout=10) as client:
        tasks = [_fetch_address_stats(client, a) for a in addrs]
        results = await asyncio.gather(*tasks, return_exceptions=True)

    ok_stats = []
    for res in results:
        if isinstance(res, Exception):
            continue
        ok_stats.append(res)

    if not ok_stats:
        return "Не удалось получить данные по кошелькам китов (mempool недоступен)."

    total_unconfirmed = sum(s["unconfirmed_net_btc"] for s in ok_stats)
    total_unconfirmed_txs = sum(s["unconfirmed_txs"] for s in ok_stats)

    direction = "нейтрально"
    if total_unconfirmed > 0.5:
        direction = "чистый приток (покупка)"
    elif total_unconfirmed < -0.5:
        direction = "чистый отток (продажа/вывод)"

    lines = [
        f"Всего отслеживаемых кошельков: {len(ok_stats)}",
        f"Неподтверждённый суммарный поток: {total_unconfirmed:.3f} BTC ({direction}),",
        f"Неподтверждённых транзакций в мемпуле: {total_unconfirmed_txs}",
        "",
        "Топ-адреса по текущему потоку:",
    ]

    for s in sorted(ok_stats, key=lambda x: abs(x["unconfirmed_net_btc"]), reverse=True)[:3]:
        flow = s["unconfirmed_net_btc"]
        flabel = "покупка" if flow > 0 else "продажа/вывод" if flow < 0 else "нет движения"
        lines.append(
            f"- {s['address'][:10]}…: {flow:+.3f} BTC, {flabel}, "
            f"получено всего ~{s['total_received_btc']:.1f} BTC"
        )

    return "\n".join(lines)
