import os
from datetime import datetime, timedelta
from pathlib import Path

import pandas as pandas
import pyotp
from SmartApi import SmartConnect
from dotenv import load_dotenv

from broker.base_broker import BaseBroker

load_dotenv(Path(__file__).resolve().parent.parent.parent / "config" / ".env")


class AngelOneBroker(BaseBroker):

    def __init__(self):
        self.api = SmartConnect(api_key=os.getenv("ANGELONE_API_KEY"))
        self._session = None

    def connect(self) -> bool:
        angel_totp = pyotp.TOTP(os.getenv("ANGELONE_TOTP_SECRET")).now()
        self._session = self.api.generateSession(
            os.getenv("ANGELONE_CLIENT_ID"),
            os.getenv("ANGELONE_PASSWORD"),
            angel_totp
        )

        if self._session["status"]:
            print("✅ Connected to Angel One")
            return True
        print("❌ Login failed:", self._session["message"])
        return False

    def get_token(self, symbol: str) -> str:
        result = self.api.searchScrip(os.getenv("EXCHANGE"), symbol)
        if result["status"] and result["data"]:
            symboltoken_ = result["data"][0]["symboltoken"]
            print(f"✅ Found token for {symbol}: {symboltoken_}")
            return symboltoken_
        raise ValueError(f"Token not found for {symbol}")

    def get_candles(self, symbol: str, token: str, candle_time: str, days: int) -> pandas.DataFrame:
        to_date = datetime.now()
        from_date = to_date - timedelta(days=days)
        print(f"📈 Fetching {candle_time} min(s) candle(s) for {symbol} from {from_date} to {to_date}...")

        response = self.api.getCandleData({
            "exchange": os.getenv("EXCHANGE"),
            "symboltoken": token,
            "interval": candle_time,
            "fromdate": from_date.strftime("%Y-%m-%d %H:%M"),
            "todate": to_date.strftime("%Y-%m-%d %H:%M"),
        })

        if not response["status"]:
            raise ConnectionError(f"Failed to fetch candles: {response['message']}")

        data_frame = pandas.DataFrame(response["data"],
                                      columns=["timestamp", "open", "high", "low", "close", "volume"])
        data_frame["timestamp"] = pandas.to_datetime(data_frame["timestamp"])
        data_frame.set_index("timestamp", inplace=True)
        print(f"✅ Fetched {len(data_frame)} candle(s) for {symbol}")
        return data_frame
