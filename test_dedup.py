"""
Teste de sanidade: verifica se a deduplicação por empresa funciona corretamente
e que nenhuma empresa aparece duas vezes no Top 12 final.
"""
import pandas as pd
import re

# Simula o df_final com duplicatas (como PETR3 e PETR4)
dados_simulados = {
    'Papel':       ['PETR4', 'PETR3', 'VALE3', 'ITUB4', 'WEGE3', 'BBDC4', 'BBDC3', 'SUZB3', 'RENT3', 'BEEF3'],
    'Score_Final': [  1.2,     2.1,    3.5,     4.0,     4.5,     5.0,      5.8,     6.0,     7.0,     8.0 ],
    'EV/EBITDA':   [  4.1,     4.2,    5.0,     8.0,    20.0,     7.0,      7.1,     6.0,    10.0,     5.0 ],
    'ROE':         [  0.28,    0.28,  0.06,     0.21,    0.33,    0.18,     0.18,    0.14,    0.12,    0.15 ],
    'Momentum':    [  0.10,    0.09,  0.05,     0.15,    0.20,    0.08,     0.07,    0.30,    0.12,    0.25 ],
    'F_SCORE':     [  8,       7,     7,        8,       9,       7,        7,       8,       7,       8    ]
}
df_final = pd.DataFrame(dados_simulados)

print("=== ANTES DA DEDUPLICAÇÃO ===")
print(df_final[['Papel','Score_Final']].to_string())

# Extrai código raiz (remove dígitos finais)
df_final['empresa_base'] = df_final['Papel'].str.replace(r'\d+$', '', regex=True)

# Mantém apenas o melhor ticker por empresa
df_dedup = (df_final
    .sort_values('Score_Final')
    .drop_duplicates(subset='empresa_base', keep='first')
    .reset_index(drop=True)
)

print("\n=== APÓS DEDUPLICAÇÃO ===")
print(df_dedup[['Papel','empresa_base','Score_Final']].to_string())

# Verificação
empresas_unicas = df_dedup['empresa_base'].nunique()
total_ativos = len(df_dedup)
print(f"\n✅ {total_ativos} ativos | {empresas_unicas} empresas distintas")

removidos = set(df_final['Papel']) - set(df_dedup['Papel'])
print(f"⚠️  Removidos por duplicidade: {removidos}")
print("\nQualquer empresa aparece 2x?", df_dedup['empresa_base'].duplicated().any())
