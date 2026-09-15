from fastapi import APIRouter, HTTPException, Query
from typing import List
from app.services.market_data import CSVMarketDataProvider
from app.engine.indicators import add_full_indicators
from app.models.schemas import CandleSchema
from app.config import settings

router = APIRouter(tags=["Market"])

@router.get("/market/{symbol:path}", response_model=List[CandleSchema])
def get_market_data(symbol: str = "BTC/USD", limit: int = Query(100, ge=1, le=1000)):
    normalized_symbol = symbol.replace("-", "/")
    data_provider = CSVMarketDataProvider(settings.DATA_FILE)
    try:
        df = data_provider.fetch_ohlcv(symbol=normalized_symbol, limit=limit)
        df_ind = add_full_indicators(df)

        candles = []
        for _, row in df_ind.iterrows():
            candles.append(
                CandleSchema(
                    timestamp=str(row["timestamp"]),
                    open=float(row["open"]),
                    high=float(row["high"]),
                    low=float(row["low"]),
                    close=float(row["close"]),
                    volume=float(row["volume"]),
                    ema_20=round(float(row["ema_20"]), 2) if "ema_20" in row else None,
                    ema_50=round(float(row["ema_50"]), 2) if "ema_50" in row else None,
                    ema_200=round(float(row["ema_200"]), 2) if "ema_200" in row else None,
                    rsi=round(float(row["rsi"]), 2) if "rsi" in row else None,
                    macd=round(float(row["macd"]), 2) if "macd" in row else None,
                    macd_signal=round(float(row["macd_signal"]), 2) if "macd_signal" in row else None,
                    atr=round(float(row["atr"]), 2) if "atr" in row else None,
                    upper_band=round(float(row["upper_band"]), 2) if "upper_band" in row else None,
                    lower_band=round(float(row["lower_band"]), 2) if "lower_band" in row else None
                )
            )
        return candles

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
