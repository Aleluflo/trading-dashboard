from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import os
from models import PriceInfo
from typing import List
from dotenv import load_dotenv
import requests
from datetime import datetime
from client import BinanceTestClient
from models import AccountInfo, OrderRequest, CandleInfo


load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

api_key = os.getenv("BINANCE_API_KEY")
api_secret = os.getenv("BINANCE_API_SECRET")
client = BinanceTestClient(api_key, api_secret)


@app.get("/api/health")
async def health():
    return {"message": "OK"}


@app.get("/api/account")
async def get_account() -> AccountInfo:
    """
    Get Binance account information
    """
    res = client.get_account()
    return AccountInfo(**res)


@app.get("/api/price")
async def get_price(symbol: str) -> PriceInfo:
    """
    Get price of a symbol
    """
    res = client.get_price(symbol)
    return res

@app.get("/api/price-history", response_model=List[CandleInfo])
async def get_price_history(symbol: str, interval: str = '1h'):
    try:
        endpoint = "/v3/klines"
        params = {
            "symbol": symbol,
            "interval": interval,
            "limit": 100
        }
        res = requests.get(f"{client.base_url}{endpoint}", params=params)
        if res.status_code != 200:
            raise HTTPException(status_code=res.status_code, detail=res.text)

        raw_candles = res.json()
        print(raw_candles)
        formatted = []

        for c in raw_candles:
            formatted.append(CandleInfo(
                open_time=datetime.fromtimestamp(c[0] / 1000).isoformat(),
                open=float(c[1]),
                high=float(c[2]),
                low=float(c[3]),
                close=float(c[4]),
                volume=float(c[5]),
                close_time=datetime.fromtimestamp(c[6] / 1000).isoformat(),
                quote_asset_volume=float(c[7]),
                number_of_trades=c[8],
                taker_buy_base_asset_volume=float(c[9]),
                taker_buy_quote_asset_volume=float(c[10]),
                ignore=c[11]
            ))

        return formatted

    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/order")
async def create_order(order: OrderRequest):
    endpoint = "/api/v3/order/test" if order.test else "/api/v3/order"

    params = {
        "symbol": order.symbol.upper(),
        "side": order.side.upper(),
        "type": order.order_type.upper(),  # use order.order_type here
        "quantity": order.quantity
    }

    response = client._execute_request(endpoint=endpoint, params=params, method="POST")
    print(response)
    return {
        "status": "success",
        "order_sent": params,
        "response": response
    }
