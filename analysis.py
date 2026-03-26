import yfinance as yf
import pandas as pd
import numpy as np

assets = ['ITUB4.SA', 'WEGE3.SA', 'VALE3.SA', 'PETR4.SA']

print('Fetching data...')
# Fetching from 2021-01-01 to 2024-01-01 to have historical context
data = yf.download(assets, start='2021-01-01', end='2024-01-01')['Adj Close']

# Calculate daily returns
returns = data.pct_change().dropna()

# Expected return and covariance
mean_returns = returns.mean() * 252
cov_matrix = returns.cov() * 252

# Risk-free rate (approximate CDI, say 10.75%)
rf = 0.1075

# Monte Carlo simulation to find the optimal portfolio (Max Sharpe)
num_portfolios = 10000
results = np.zeros((3, num_portfolios))
weights_record = []

for i in range(num_portfolios):
    weights = np.random.random(len(assets))
    weights /= np.sum(weights)
    weights_record.append(weights)
    
    portfolio_return = np.sum(mean_returns * weights)
    portfolio_std_dev = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))
    
    results[0,i] = portfolio_return
    results[1,i] = portfolio_std_dev
    results[2,i] = (portfolio_return - rf) / portfolio_std_dev

max_sharpe_idx = np.argmax(results[2])
optimal_weights = weights_record[max_sharpe_idx]

print('\nOptimal Weights (Max Sharpe):')
for asset, weight in zip(assets, optimal_weights):
    print(f'{asset}: {weight:.4f}')

print(f'\nExpected Portfolio Return: {results[0,max_sharpe_idx]:.4f}')
print(f'Expected Portfolio Volatility: {results[1,max_sharpe_idx]:.4f}')
print(f'Sharpe Ratio: {results[2,max_sharpe_idx]:.4f}')

print('\nFetching Fundamental Data...')
for asset in assets:
    try:
        ticker = yf.Ticker(asset)
        info = ticker.info
        print(f'\n--- {asset} ---')
        print(f"ROE (Profitability): {info.get('returnOnEquity', 'N/A')}")
        print(f"P/E (Valuation): {info.get('trailingPE', 'N/A')}")
        print(f"P/B (Valuation): {info.get('priceToBook', 'N/A')}")
        print(f"Debt/Equity (Indebtedness): {info.get('debtToEquity', 'N/A')}")
    except Exception as e:
        print(f'Error fetching fundamentals for {asset}: {e}')
