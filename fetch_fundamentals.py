import yfinance as yf

assets = ['ITUB4.SA', 'WEGE3.SA', 'VALE3.SA', 'PETR4.SA']

for asset in assets:
    try:
        ticker = yf.Ticker(asset)
        info = ticker.info
        print(f'\n--- {asset} ---')
        print(f"ROE: {info.get('returnOnEquity')}")
        print(f"P/E: {info.get('trailingPE')}")
        print(f"P/B: {info.get('priceToBook')}")
        print(f"Debt/Equity: {info.get('debtToEquity')}")
    except Exception as e:
        print(f'Error: {e}')
