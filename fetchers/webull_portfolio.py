import yfinance

TICKERS = ["TSM", "GOOG", "AVGO", "NET", "TSLA", "ARM"]

def fetch():
    result = []
    data = yfinance.download(
        TICKERS,
        period="2d",
        interval="1d",
        progress=False,
        auto_adjust=True,
    )
    for ticker in TICKERS:
        try:
            closes = data["Close"][ticker].dropna()
            if len(closes) < 2:
                continue
            prev, last = float(closes.iloc[-2]), float(closes.iloc[-1])
            change     = last - prev
            change_pct = (change / prev) * 100
            result.append({
                "ticker":     ticker,
                "price":      round(last, 2),
                "change":     round(change, 2),
                "change_pct": round(change_pct, 2),
            })
        except Exception:
            continue
    return result or None
