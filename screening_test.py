import requests
import pandas as pd
import io

def get_fundamentus_data():
    headers = {'User-Agent': 'Mozilla/5.0'}
    res = requests.get('https://www.fundamentus.com.br/resultado.php', headers=headers)
    
    # Extract HTML table
    df = pd.read_html(io.StringIO(res.text), decimal=',', thousands='.')[0]
    
    # Process string percentages
    for col in ['Div.Yield', 'Mrg Ebit', 'Mrg. Líq.', 'ROIC', 'ROE', 'Cresc. Rec.5a']:
        df[col] = df[col].astype(str).str.replace('.', '', regex=False).str.replace(',', '.', regex=False).str.replace('%', '', regex=False)
        df[col] = pd.to_numeric(df[col], errors='coerce') / 100.0
        
    for col in ['P/L', 'P/VP', 'Dív.Brut/ Patrim.', 'Liq.2meses']:
        df[col] = pd.to_numeric(df[col], errors='coerce')
        
    # Drop rows without liquid2meses or PL or ROE
    df = df.dropna(subset=['Liq.2meses', 'P/L', 'ROE'])
    
    return df

df = get_fundamentus_data()

# Filtros
# Liquidez > 5,000,000 BRL
# P/L positivo e menor que 20 (empresas sem prejuízo e não tão caras)
# ROE > 15%
filtered = df[(df['Liq.2meses'] > 5000000) & (df['P/L'] > 0) & (df['P/L'] < 25) & (df['ROE'] > 0.15)].copy()

# Remove tickers with '11' (mostly FIIs or Units, we prefer ordinary/preferred stocks according to typical analysis, or leave them, Competition allows FIIs)
# Wait, user said "trocando uma das ações por um FII". Let's allow FIIs if they show up, though Fundamentus separates FIIs to /fii_resultado.php.

# Ranking 'Magic Formula' (Earnings yield + ROE)
# P/L rank (lowest to highest) -> index 1 to N
# ROE rank (highest to lowest) -> index 1 to N
filtered['rank_pl'] = filtered['P/L'].rank(ascending=True)
filtered['rank_roe'] = filtered['ROE'].rank(ascending=False)
filtered['rank_final'] = filtered['rank_pl'] + filtered['rank_roe']

filtered = filtered.sort_values('rank_final')
top_10 = filtered.head(10)['Papel'].tolist()

print("Top 10 Tickers from Fundamentus Screening:")
print(top_10)
