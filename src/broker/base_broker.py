from abc import ABC, abstractmethod

import pandas as pandas


class BaseBroker(ABC):

    @abstractmethod
    def connect(self) -> bool:
        pass

    @abstractmethod
    def get_token(self, symbol: str) -> str:
        pass

    @abstractmethod
    def get_candles(self, symbol: str, token: str, interval: str, days: int) -> pandas.DataFrame:
        pass
