import pandas as pandas


class ORBStrategy:
    """
   Opening Range Breakout Strategy.

   The opening range is defined as the first 15 minutes
   of the trading session (9:15 AM to 9:30 AM).

   We find the highest HIGH and lowest LOW in that window.
   These two levels become our breakout triggers.
   """

    def __init__(self, orb_minutes: int = 15):
        """
        orb_minutes: how many minutes define the opening range.
                     Default is 15 (9:15 to 9:30).
                     You can try 30 for a wider range.
        """
        self.orb_minutes = orb_minutes
        self.opening_range_high = None  # will be set after calculate_opening_range()
        self.opening_range_low = None  # will be set after calculate_opening_range()

    def calculate_opening_range(self, candles: pandas.DataFrame) -> dict:
        """
        Takes the full day's candle DataFrame and extracts
        the opening range high and low.

        Args:
            candles: DataFrame from get_candles() with columns
                [open, high, low, close, volume]
                indexed by timestamp

        Returns:
            dict with opening_range_high, opening_range_low, orb_range (size of the range)
        """
        # Step 1 — figure out the end time of the opening range
        # If orb_minutes=15, opening range is 9:15 to 9:30
        # We build the end time string dynamically from orb_minutes
        start_time = "09:15"
        end_minute = 15 + self.orb_minutes - 1  # 15 + 15 - 1 = 29 → "09:29"
        end_time = f"09:{end_minute}"  # "09:29"

        # Step 2 — filter only the opening range candles
        # between_time() works because timestamp is the index
        opening_candles = candles.between_time(start_time, end_time)

        # Step 3 — check we actually have data
        # (market might be closed, holiday, or data not yet available)
        if opening_candles.empty:
            raise ValueError(
                f"No candles found between {start_time} and {end_time}. "
                f"Is today a trading day? Did you fetch enough data?"
            )

        # Step 4 — find the highest high and lowest low
        # .max() scans every row in the 'high' column and returns the biggest
        # .min() scans every row in the 'low' column and returns the smallest
        self.opening_range_high = opening_candles["high"].max()
        self.opening_range_low = opening_candles["low"].min()
        orb_range = round(self.opening_range_high - self.opening_range_low, 2)

        result = {
            "opening_range_high": self.opening_range_high,
            "opening_range_low": self.opening_range_low,
            "orb_range": orb_range,  # size of the range in ₹
            "candles_used": len(opening_candles)  # how many candles were in the range
        }

        return result

    def detect_signal(self, candles: pandas.DataFrame) -> dict:
        """
        Scans candles after the opening range and detects
        the first breakout signal.

        A signal fires when a candle CLOSES above opening_range_high (BUY)
        or CLOSES below opening_range_low (SELL).

        We use close price — not high/low — to avoid false breakouts
        caused by temporary wicks that immediately reverse.

        Args:
            candles: same full day DataFrame from get_candles()

        Returns:
            dict with signal details, or None if no signal found
        """
        # Guard — opening range must be calculated first
        if self.opening_range_high is None or self.opening_range_low is None:
            raise RuntimeError(
                "Opening range not calculated yet. "
                "Call calculate_opening_range() before detect_signal()."
            )

        # Step 1 — only look at candles AFTER the opening range ends
        # We don't want to trade during the opening range itself
        post_opening_candles = candles.between_time("09:31", "15:15")

        if post_opening_candles.empty:
            return {"signal": "NONE", "reason": "No candles found after opening range"}

        # Step 2 — scan each candle one by one
        for candle_time, candle_data in post_opening_candles.iterrows():

            closing_price = candle_data["close"]

            # ── BUY signal ───────────────────────────────────────
            if closing_price > self.opening_range_high:

                entry_price = closing_price

                # Stop loss = below the opening_range_low
                # If price reverses all the way to opening_range_low, we were wrong
                stop_loss_price = self.opening_range_low

                # Target = entry + 1.5x the range size
                # Risk:Reward of 1:1.5 minimum
                orb_range_size = self.opening_range_high - self.opening_range_low
                target_price = round(entry_price + (1.5 * orb_range_size), 2)
                stop_loss_price = round(stop_loss_price, 2)
                risk_per_share = round(entry_price - stop_loss_price, 2)
                reward_per_share = round(target_price - entry_price, 2)

                return {
                    "signal": "BUY",
                    "signal_time": candle_time,
                    "entry_price": entry_price,
                    "stop_loss_price": stop_loss_price,
                    "target_price": target_price,
                    "risk_per_share": risk_per_share,
                    "reward_per_share": reward_per_share,
                    "opening_range_high": self.opening_range_high,
                    "opening_range_low": self.opening_range_low,
                }

            # ── SELL signal ──────────────────────────────────────
            elif closing_price < self.opening_range_low:

                entry_price = closing_price

                # Stop loss = above opening_range_high
                stop_loss_price = self.opening_range_high

                # Target = entry - 1.5x the range (price going down)
                orb_range_size = self.opening_range_high - self.opening_range_low
                target_price = round(entry_price - (1.5 * orb_range_size), 2)
                stop_loss_price = round(stop_loss_price, 2)
                risk_per_share = round(stop_loss_price - entry_price, 2)
                reward_per_share = round(entry_price - target_price, 2)

                return {
                    "signal": "SELL",
                    "signal_time": candle_time,
                    "entry_price": entry_price,
                    "stop_loss_price": stop_loss_price,
                    "target_price": target_price,
                    "risk_per_share": risk_per_share,
                    "reward_per_share": reward_per_share,
                    "opening_range_high": self.opening_range_high,
                    "opening_range_low": self.opening_range_low,
                }

        # Step 3 — if we scanned all candles and found nothing
        return {"signal": "NONE", "reason": "Price never broke the opening range today"}

    def evaluate_trade(self, candle_dataframe: pandas.DataFrame, trade_signal: dict) -> dict:
        """
        After a signal fires, scans the remaining candles to check
        whether the trade hit TARGET, STOP LOSS, or TIME EXIT.

        This simulates what would happen if you actually took the trade.

        Args:
            candle_dataframe : full day candle DataFrame
            trade_signal     : the dict returned by detect_signal()

        Returns:
            dict with outcome, exit price, and profit/loss per share
        """
        # No trade was taken, nothing to evaluate
        if trade_signal["signal"] == "NONE":
            return {"outcome": "NO TRADE", "reason": trade_signal["reason"]}

        signal_time = trade_signal["signal_time"]
        entry_price = trade_signal["entry_price"]
        target_price = trade_signal["target_price"]
        stop_loss_price = trade_signal["stop_loss_price"]
        signal_direction = trade_signal["signal"]

        # Step 1 — get all candles AFTER the signal fired
        # We only care about what happens after we enter the trade
        candles_after_entry = candle_dataframe[candle_dataframe.index > signal_time]

            # Step 2 — scan each candle and check if target or SL was hit
        for candle_time, candle_data in candles_after_entry.iterrows():

            candle_high  = candle_data["high"]
            candle_low   = candle_data["low"]
            candle_close = candle_data["close"]

            # For BUY trades — we profit when price goes UP
            if signal_direction == "BUY":

                # Check target first — did the high touch our target?
                if candle_high >= target_price:
                    profit_per_share = round(target_price - entry_price, 2)
                    return {
                        "outcome":           "TARGET HIT ✅",
                        "exit_price":        target_price,
                        "exit_time":         candle_time,
                        "profit_per_share":  profit_per_share,
                        "result":            "PROFIT"
                    }

                # Check stop loss — did the low touch our stop loss?
                if candle_low <= stop_loss_price:
                    loss_per_share = round(entry_price - stop_loss_price, 2)
                    return {
                        "outcome":          "STOP LOSS HIT ❌",
                        "exit_price":       stop_loss_price,
                        "exit_time":        candle_time,
                        "profit_per_share": -loss_per_share,
                        "result":           "LOSS"
                    }

            # For SELL trades — we profit when price goes DOWN
            elif signal_direction == "SELL":

                # Check target — did the low touch our target?
                if candle_low <= target_price:
                    profit_per_share = round(entry_price - target_price, 2)
                    return {
                        "outcome":          "TARGET HIT ✅",
                        "exit_price":       target_price,
                        "exit_time":        candle_time,
                        "profit_per_share": profit_per_share,
                        "result":           "PROFIT"
                    }

                # Check stop loss — did the high touch our stop loss?
                if candle_high >= stop_loss_price:
                    loss_per_share = round(stop_loss_price - entry_price, 2)
                    return {
                        "outcome":          "STOP LOSS HIT ❌",
                        "exit_price":       stop_loss_price,
                        "exit_time":        candle_time,
                        "profit_per_share": -loss_per_share,
                        "result":           "LOSS"
                    }

        # Step 3 — neither target nor SL hit before 3:15
        # Exit at the last available candle's close price
        last_candle_close = candles_after_entry.iloc[-1]["close"]

        if signal_direction == "BUY":
            pnl_per_share = round(last_candle_close - entry_price, 2)
        else:
            pnl_per_share = round(entry_price - last_candle_close, 2)

        return {
            "outcome":          "TIME EXIT 🕒",
            "exit_price":       last_candle_close,
            "exit_time":        "15:15",
            "profit_per_share": pnl_per_share,
            "result":           "PROFIT" if pnl_per_share > 0 else "LOSS"
    }


