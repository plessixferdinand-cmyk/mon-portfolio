import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="Mon Portfolio", layout="wide")
st.title("📈 Mon Portfolio Tracker (Pro)")

# 1. BASE DE DONNÉES
portfolio_data = {
    "Ticker": ["AAPL", "MC.PA", "AI.PA", "MSFT"],
    "Nom": ["Apple", "LVMH", "Air Liquide", "Microsoft"],
    "Quantité": [15, 5, 10, 8],
    "PRU": [145.0, 700.0, 140.0, 310.0]
}
df_portfolio = pd.DataFrame(portfolio_data)

st.subheader("💼 Mes Positions Actuelles")

total_investi = 0
total_actuel = 0
prix_actuels = []
pourcentages_gain = []
valeurs_totales = []

for index, row in df_portfolio.iterrows():
    try:
        ticker = yf.Ticker(row["Ticker"])
        current_price = ticker.fast_info['last_price']
        valeur_achat = row["Quantité"] * row["PRU"]
        valeur_actuelle = row["Quantité"] * current_price
        gain_pct = ((current_price - row["PRU"]) / row["PRU"]) * 100
        total_investi += valeur_achat
        total_actuel += valeur_actuelle
        prix_actuels.append(round(current_price, 2))
        pourcentages_gain.append(round(gain_pct, 2))
        valeurs_totales.append(round(valeur_actuelle, 2))
    except Exception as e:
        prix_actuels.append("Erreur")
        pourcentages_gain.append(0)
        valeurs_totales.append(0)

df_portfolio["Prix Actuel"] = prix_actuels
df_portfolio["Plus-Value (%)"] = pourcentages_gain
df_portfolio["Valeur Totale"] = valeurs_totales
st.dataframe(df_portfolio, use_container_width=True)

st.markdown("---")
plus_value_globale_euros = total_actuel - total_investi
plus_value_globale_pct = (plus_value_globale_euros / total_investi) * 100 if total_investi > 0 else 0

col1, col2, col3 = st.columns(3)
col1.metric("Total Investi", f"{round(total_investi, 2)} €")
col2.metric("Valeur du Portefeuille", f"{round(total_actuel, 2)} €")
col3.metric("Plus-Value Globale", f"{round(plus_value_globale_euros, 2)} €", f"{round(plus_value_globale_pct, 2)} %")

st.markdown("---")
st.subheader("📊 Comparaison des performances (Dernière année)")

@st.cache_data
def get_normalized_data(tickers, period="1y"):
    data = yf.download(tickers, period=period)["Close"]
    normalized = (data / data.iloc[0] - 1) * 100 
    return normalized

indices_tickers = ["^FCHI", "^GSPC"]
portfolio_tickers = df_portfolio["Ticker"].tolist()
all_tickers = indices_tickers + portfolio_tickers

with st.spinner("Chargement des graphiques comparatifs..."):
    historique_data = get_normalized_data(all_tickers)

fig = go.Figure()
fig.add_trace(go.Scatter(x=historique_data.index, y=historique_data["^FCHI"], mode='lines', name='CAC 40', line=dict(color='blue', width=2, dash='dash')))
fig.add_trace(go.Scatter(x=historique_data.index, y=historique_data["^GSPC"], mode='lines', name='S&P 500', line=dict(color='red', width=2, dash='dash')))

for ticker in portfolio_tickers:
    nom_action = df_portfolio[df_portfolio["Ticker"] == ticker]["Nom"].values[0]
    fig.add_trace(go.Scatter(x=historique_data.index, y=historique_data[ticker], mode='lines', name=nom_action))

fig.update_layout(title="Évolution en % (Base 0 sur 1 an)", yaxis_title="Performance (%)", xaxis_title="Date", hovermode="x unified", height=600)
st.plotly_chart(fig, use_container_width=True)
