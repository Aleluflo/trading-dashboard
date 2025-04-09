from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import os
from models import PriceInfo

from dotenv import load_dotenv

from client import BinanceTestClient
from models import AccountInfo, OrderRequest

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
    res = client.get_account(str)
    return res


@app.get("/api/price")
async def get_price(symbol: str) -> PriceInfo:
    """
    Get price of a symbol
    """
    res = client.get_price(symbol)
    return res


@app.get("/api/price-history")
async def get_price(symbol: str, interval: str = '1h'):
    """
    Get price of a symbol
    """
    ...


@app.post("/api/order")
async def create_order(order: OrderRequest):
    """
    Create a Binance order
    """
    ...
