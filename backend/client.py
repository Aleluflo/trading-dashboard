import hashlib
import hmac

import requests
import time

from urllib.parse import urlencode

# cd trading-dashboard, cd backend
# pip install "fastapi[all]"
# estando en backend correr: uvicorn main:app --port 8000 --reload


class BinanceTestClient:
    def __init__(self, api_key: str, api_secret: str):
        self.api_key = api_key
        self.api_secret = api_secret
        self.base_url = 'https://testnet.binance.vision/api'

    def _generate_signature(self, query_string: str) -> str:
        return hmac.new(
            self.api_secret.encode('utf-8'),
            query_string.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()

    def _execute_request(self, endpoint: str, params: dict, method: str = 'GET'):
        timestamp = int(time.time() * 1000)
        params['timestamp'] = timestamp

        query_string = urlencode(params)
        signature = self._generate_signature(query_string)
        params['signature'] = signature

        headers = {
            'X-MBX-APIKEY': self.api_key
        }

        if method == 'GET':
            return requests.get(f"{self.base_url}{endpoint}", params=params, headers=headers)

        return requests.post(f"{self.base_url}{endpoint}", params=params, headers=headers)

    def get_price(self,symbol:str):
        res = requests.get(self.base_url + "/v3/ticker/price?symbol="+symbol)
        res_dict = res.json()
        return res_dict

    def get_account(self):
        response = self._execute_request("/v3/account", params={})
        if response.status_code != 200:
            raise Exception(f"Error: {response.status_code}, {response.text}")
        data = response.json()

        def find_asset(asset):
            for b in data["balances"]:
                if b["asset"] == asset:
                    total = str(float(b["free"]) + float(b["locked"]))
                    return {"asset": asset, "balance": total}
            return {"asset": asset, "balance": "0"}

        return {
            "uid": data.get("accountNumber", 0),
            "account_type": data.get("accountType", ""),
            "btc_balance": find_asset("BTC"),
            "usdt_balance": find_asset("USDT"),
            "eth_balance": find_asset("ETH"),
        }

