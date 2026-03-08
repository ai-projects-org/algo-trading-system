import time

from broker.angelone_broker import AngelOneBroker
from strategy.orb_strategy import ORBStrategy

broker = AngelOneBroker()
broker.connect()

# ── Stocks to scan ────────────────────────────
watchlist = [
    "ITC-EQ",
    "SBIN-EQ",
    "TATASTEEL-EQ",
    "HINDALCO-EQ",
    "COALINDIA-EQ",
    "ONGC-EQ",
    "NTPC-EQ",
    "POWERGRID-EQ",
    "IOC-EQ",
    "BPCL-EQ",

    "CANBK-EQ",
    "PNB-EQ",
    "BANKBARODA-EQ",
    "FEDERALBNK-EQ",
    "IDFCFIRSTB-EQ",
    "INDIANB-EQ",
    "UCOBANK-EQ",
    "CENTRALBK-EQ",
    "UNIONBANK-EQ",
    "BANDHANBNK-EQ",

    "IRFC-EQ",
    "IRCTC-EQ",
    "RVNL-EQ",
    "RITES-EQ",
    "RAILTEL-EQ",

    "SAIL-EQ",
    "NMDC-EQ",
    "JINDALSTEL-EQ",
    "VEDL-EQ",
    "NATIONALUM-EQ",

    "BEL-EQ",
    "BHEL-EQ",
    "HAL-EQ",
    "BDL-EQ",
    "MAZDOCK-EQ",

    "SUZLON-EQ",
    "YESBANK-EQ",
    "IDEA-EQ",
    "GMRINFRA-EQ",
    "NHPC-EQ",

    "ADANIPOWER-EQ",
    "TATAPOWER-EQ",
    "JSWENERGY-EQ",
    "TORNTPOWER-EQ",
    "CESC-EQ",

    "ASHOKLEY-EQ",
    "TATAMOTORS-EQ",
    "ESCORTS-EQ",
    "TVSMOTOR-EQ",
    "MOTHERSON-EQ"
]

strategy = ORBStrategy(orb_minutes=15)
paper_trades = []

print("=" * 60)
print("   PAPER TRADING — ORB STRATEGY SCAN")
print("=" * 60)

for stock_symbol in watchlist:
    try:
        print(f"\n📌 Scanning {stock_symbol}...")

        # Fetch data
        stock_token = broker.get_token(stock_symbol)
        time.sleep(2)
        candles_dataframe = broker.get_candles(
            stock_symbol, stock_token,
            candle_time="ONE_MINUTE", days=10
        )

        # Reset strategy state for each stock
        strategy.orb_high = None
        strategy.orb_low = None

        # Opening range
        opening_range = strategy.calculate_opening_range(candles_dataframe)

        # Signal
        trade_signal = strategy.detect_signal(candles=candles_dataframe)

        # Outcome
        trade_outcome = strategy.evaluate_trade(candles_dataframe, trade_signal)

        # Collect result
        paper_trades.append({
            "symbol": stock_symbol,
            "orb_high": opening_range["opening_range_high"],
            "orb_low": opening_range["opening_range_low"],
            "signal": trade_signal["signal"],
            "entry_price": trade_signal.get("entry_price", "-"),
            "stop_loss": trade_signal.get("stop_loss_price", "-"),
            "target": trade_signal.get("target_price", "-"),
            "outcome": trade_outcome.get("outcome", "NO TRADE"),
            "pnl_per_share": trade_outcome.get("profit_per_share", 0),
        })

    except Exception as error:
        print(f"   ⚠️  Skipping {stock_symbol} — {error}")
        continue

# ── Print Summary ─────────────────────────────
print("\n")
print("=" * 60)
print("   PAPER TRADE SUMMARY")
print("=" * 60)

total_pnl = 0

for trade in paper_trades:
    print(f"\n  {trade['symbol']}")
    print(f"    Signal   : {trade['signal']}")
    print(f"    Entry    : ₹{trade['entry_price']}")
    print(f"    Target   : ₹{trade['target']}")
    print(f"    Stop Loss: ₹{trade['stop_loss']}")
    print(f"    Outcome  : {trade['outcome']}")
    print(f"    P&L/share: ₹{trade['pnl_per_share']}")
    total_pnl += trade["pnl_per_share"] if isinstance(trade["pnl_per_share"], float) else 0

print("\n" + "=" * 60)
print(f"  Total P&L (per share basis): ₹{round(total_pnl, 2)}")
print("=" * 60)

# from broker.angelone_broker import AngelOneBroker
# from strategy.orb_strategy import ORBStrategy
#
# # Tomorrow if you switch to Zerodha:
# # from zerodha_broker import ZerodhaBroker
#
# broker = AngelOneBroker()
# broker.connect()
#
# symbol = "RITES-EQ"
# token = broker.get_token(symbol)
# candles_dataframe = broker.get_candles(symbol, token, candle_time="ONE_MINUTE", days=2)
#
# strategy = ORBStrategy(orb_minutes=15)
# orb_strategy = strategy.calculate_opening_range(candles_dataframe)
#
# print(f"\n📊 Opening Range for {symbol}:")
# print(f"   ORB High    : ₹{orb_strategy['opening_range_high']}")
# print(f"   ORB Low     : ₹{orb_strategy['opening_range_low']}")
# print(f"   ORB Range   : ₹{orb_strategy['orb_range']}  ← size of the range")
# print(f"   Candles used: {orb_strategy['candles_used']}")
#
# trade_signal = strategy.detect_signal(candles=candles_dataframe)
#
# print(f"\n🚦 Signal Detected: {trade_signal['signal']}")
#
# if trade_signal["signal"] != "NONE":
#     print(f"   Time        : {trade_signal['signal_time']}")
#     print(f"   Entry Price : ₹{trade_signal['entry_price']}")
#     print(f"   Stop Loss   : ₹{trade_signal['stop_loss_price']}")
#     print(f"   Target      : ₹{trade_signal['target_price']}")
#     print(f"   Risk/share  : ₹{trade_signal['risk_per_share']}")
#     print(f"   Reward/share: ₹{trade_signal['reward_per_share']}")
# else:
#     print(f"   Reason: {trade_signal['reason']}")
#
# # Part 3 — Trade Outcome
# trade_outcome = strategy.evaluate_trade(candles_dataframe, trade_signal)
# print("\n📈 Trade Outcome:")
# print(f"   Result     : {trade_outcome['outcome']}")
# print(f"   Exit Price : ₹{trade_outcome['exit_price']}")
# print(f"   Exit Time  : {trade_outcome['exit_time']}")
# print(f"   P&L/share  : ₹{trade_outcome['profit_per_share']}")
