```bash
algo-trading/
│
├── config/
│   ├── .env                  # API keys, secrets
│   └── settings.py           # Global config
│
├── broker/
│   ├── base_broker.py        # Abstract broker class
│   ├── zerodha.py            # Kite Connect wrapper
│   └── angelone.py           # SmartAPI wrapper
│
├── data/
│   ├── market_feed.py        # Live tick/OHLC data
│   ├── historical.py         # Historical data fetcher
│   └── universe.py           # Stock universe filter
│
├── strategies/
│   ├── base_strategy.py      # Abstract strategy class
│   ├── orb_strategy.py       # Opening Range Breakout
│   ├── momentum.py           # Momentum strategy
│   └── mean_reversion.py     # Mean reversion
│
├── risk/
│   ├── position_sizer.py     # How many shares to buy
│   ├── stop_loss.py          # SL/Target calculator
│   └── risk_manager.py       # Daily loss limits
│
├── execution/
│   ├── order_manager.py      # Place/modify/cancel orders
│   └── trade_logger.py       # Log all trades to DB
│
├── backtest/
│   ├── engine.py             # Backtesting engine
│   └── performance.py        # Sharpe, drawdown, PnL
│
├── dashboard/
│   └── app.py                # Streamlit monitoring UI
│
├── tests/                    # Unit tests
└── main.py                   # Entry point
```