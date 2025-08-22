import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objs as go
from datetime import datetime
import os

# ==============================
# Einstellungen
# ==============================
UPDATE_INTERVAL = 5  # Sekunden
MAX_HISTORY = 200    # Anzahl gespeicherter Historienpunkte
HISTORY_FILE = os.path.join(os.path.expanduser("~"), "Desktop", "dashboard_history.csv")

KRITERIEN = {
    "Marktplatzierung": "Rank",
    "Soziale Aktivität": "Posts",
    "Entwicklungsaktivität": "Commits",
    "Netzwerkaktivität": "Txs",
    "Liquidität": "Liquidity",
    "Volatilität": "Volatility",
    "Adoption": "Users",
    "Medienpräsenz": "Mentions",
    "Partnerschaften": "Partners",
    "Tokenomics": "Supply",
    "Community": "Members",
    "Innovation": "Score"
}

KRYPTOS = {
    "bitcoin": "BTC",
    "ethereum": "ETH",
    "cardano": "ADA"
}

# ==============================
# Historie laden oder initialisieren
# ==============================
if "data" not in st.session_state:
    if os.path.exists(HISTORY_FILE):
        df = pd.read_csv(HISTORY_FILE, index_col=0, parse_dates=True)
        st.session_state.data = df.tail(MAX_HISTORY)
    else:
        times = pd.date_range(end=datetime.now(), periods=20, freq=f'{UPDATE_INTERVAL}S')
        init_data = {k: np.random.randint(50, 150, size=20) for k in KRITERIEN.keys()}
        for k in KRYPTOS.keys():
            init_data[f"{k}-Preis"] = np.random.uniform(20000, 60000, size=20)
            init_data[f"{k}-Volumen"] = np.random.uniform(1e6, 1e8, size=20)
        st.session_state.data = pd.DataFrame(init_data, index=times)
        st.session_state.data.to_csv(HISTORY_FILE)

df = st.session_state.data

# ==============================
# Neue Daten simulieren
# ==============================
def generate_new_data():
    new_values = {k: np.random.randint(50, 150) for k in KRITERIEN.keys()}
    for k in KRYPTOS.keys():
        new_values[f"{k}-Preis"] = np.random.uniform(20000, 60000)
        new_values[f"{k}-Volumen"] = np.random.uniform(1e6, 1e8)
    return pd.DataFrame([new_values], index=[datetime.now()])

# ==============================
# Daten aktualisieren
# ==============================
if (datetime.now() - df.index[-1]).seconds > UPDATE_INTERVAL:
    new_data = generate_new_data()
    df = pd.concat([df, new_data])
    df = df.tail(MAX_HISTORY)
    st.session_state.data = df
    df.to_csv(HISTORY_FILE)  # sofort speichern

# ==============================
# Funktion für farbige Linien pro Segment
# ==============================
def add_colored_line(fig, x, y, width=2):
    for i in range(1, len(y)):
        color = "green" if y.iloc[i] >= y.iloc[i-1] else "red"
        fig.add_trace(go.Scatter(
            x=x[i-1:i+1],
            y=y[i-1:i+1],
            mode="lines",
            line=dict(color=color, width=width),
            showlegend=False
        ))
    if len(y) == 1:
        fig.add_trace(go.Scatter(x=x, y=y, mode="lines", line=dict(color="blue", width=width), showlegend=False))

# ==============================
# Dashboard Layout
# ==============================
st.set_page_config(page_title="12-Kriterien Live Dashboard", layout="wide")
st.title("12-Kriterien Live Gesamtspur 🛡️")

# ==============================
# Gesamtspur als Durchschnitt
# ==============================
st.subheader("Gesamtspur aller 12 Kriterien (Aggregiert)")
df_avg = df[KRITERIEN.keys()].mean(axis=1)
fig_total = go.Figure()
add_colored_line(fig_total, df_avg.index, df_avg, width=3)
fig_total.update_layout(
    xaxis_title="Zeit",
    yaxis_title="Durchschnittswerte",
    template="plotly_dark",
    height=400,
    margin=dict(l=10, r=10, t=30, b=10)
)
st.plotly_chart(fig_total, use_container_width=True, key="gesamtspur_aggregiert")

# ==============================
# Wichtige aktuelle Werte mit Verlauf
# ==============================
st.subheader("Wichtige aktuelle Werte")
for kriterium in KRITERIEN.keys():
    col1, col2 = st.columns([1, 4])
    with col1:
        st.markdown(f"**{kriterium} ({KRITERIEN[kriterium]})**")
    with col2:
        fig = go.Figure()
        add_colored_line(fig, df.index, df[kriterium], width=2)
        fig.update_layout(
            xaxis=dict(showticklabels=True),
            yaxis=dict(showticklabels=True),
            height=120,
            margin=dict(l=10, r=10, t=10, b=10),
            showlegend=False,
            template="plotly_dark"
        )
        st.plotly_chart(fig, use_container_width=True, key=f"{kriterium}_plot")

# ==============================
# Krypto-Daten
# ==============================
st.subheader("Kryptowährungen")
for krypto in KRYPTOS.keys():
    # Preis
    col1, col2 = st.columns([1, 4])
    with col1:
        st.markdown(f"**{krypto.capitalize()} Preis**")
    with col2:
        fig = go.Figure()
        add_colored_line(fig, df.index, df[f"{krypto}-Preis"], width=2)
        fig.update_layout(height=120, margin=dict(l=10, r=10, t=10, b=10), showlegend=False, template="plotly_dark")
        st.plotly_chart(fig, use_container_width=True, key=f"{krypto}_preis_plot")

    # Volumen
    col1, col2 = st.columns([1, 4])
    with col1:
        st.markdown(f"**{krypto.capitalize()} Volumen**")
    with col2:
        fig = go.Figure()
        add_colored_line(fig, df.index, df[f"{krypto}-Volumen"], width=2)
        fig.update_layout(height=120, margin=dict(l=10, r=10, t=10, b=10), showlegend=False, template="plotly_dark")
        st.plotly_chart(fig, use_container_width=True, key=f"{krypto}_volumen_plot")
