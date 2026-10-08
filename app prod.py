import time
from pathlib import Path
from urllib.parse import urlencode

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests
import streamlit as st

st.set_page_config(page_title="Dashboard Pedidos Cancelados", page_icon=":bar_chart:",
                   layout="wide", initial_sidebar_state="expanded")

DATA_PATH = Path(__file__).parent / "data" / "pedidos_demo.csv"

# Auth0 es opcional: si no hay secretos configurados, la demo es pública.
REQUIRE_LOGIN = "auth0" in st.secrets


# ---------------------------------------------------------------- Auth0 ---
def run_auth0():
    cfg = st.secrets["auth0"]
    domain, client_id = cfg["domain"], cfg["client_id"]
    redirect_uri = cfg.get("redirect_uri", "https://jvsgkwerkx2ezoutzryudr.streamlit.app")

    def login_url():
        return f"https://{domain}/authorize?" + urlencode({
            "response_type": "code", "client_id": client_id,
            "redirect_uri": redirect_uri, "scope": "openid profile email"})

    code = st.query_params.get("code")
    if "user" not in st.session_state and code:
        token = requests.post(f"https://{domain}/oauth/token", data={
            "grant_type": "authorization_code", "client_id": client_id,
            "client_secret": cfg["client_secret"], "code": code,
            "redirect_uri": redirect_uri}, timeout=10).json()
        if token.get("access_token"):
            st.session_state.user = requests.get(
                f"https://{domain}/userinfo",
                headers={"Authorization": f"Bearer {token['access_token']}"},
                timeout=10).json()
            st.query_params.clear()

    if "user" not in st.session_state:
        st.title("Dashboard de Pedidos Cancelados")
        st.markdown(f"[🔐 Iniciar sesión con Auth0]({login_url()})")
        st.stop()

    user = st.session_state.user
    with st.sidebar:
        if user.get("picture"):
            st.image(user["picture"], width=90)
        st.markdown(f"**{user.get('name', '')}**")
        if st.button("Cerrar sesión", use_container_width=True):
            st.session_state.clear()
            st.markdown(
                '<meta http-equiv="refresh" content="0;URL=\'https://%s/v2/logout?%s\'" />'
                % (domain, urlencode({"returnTo": redirect_uri, "client_id": client_id})),
                unsafe_allow_html=True)
    if "welcome_shown" not in st.session_state:
        st.toast(f"Bienvenido, {user.get('name', '')} 👋")
        st.session_state.welcome_shown = True


if REQUIRE_LOGIN:
    run_auth0()


# ---------------------------------------------------------------- Datos ---
@st.cache_data
def load_data():
    df = pd.read_csv(DATA_PATH)
    df["FECHA CREACION"] = pd.to_datetime(df["FECHA CREACION"])
    df["CLIENTE"] = df["CLIENTE"].fillna("Sin cliente")
    return df


df = load_data()
st.caption("Demo con datos de ejemplo. El dashboard original se alimentaba por SQL desde una red privada.")


def donut(pct):
    fig = go.Figure(go.Pie(labels=["CANCELADO", "FACTURADO"], values=[100 - pct, pct],
                           hole=0.6, marker_colors=["#29b5e8", "#155F7A"], textinfo="none"))
    fig.add_annotation(text=f"{pct}%", font_size=24, showarrow=False)
    fig.update_layout(showlegend=False, height=250, margin=dict(t=0, b=0, l=0, r=0))
    return fig


# -------------------------------------------------------------- Filtros ---
st.sidebar.header("⚙️ Configurar filtros")
años = sorted(df["FECHA CREACION"].dt.year.unique())
meses = sorted(df["FECHA CREACION"].dt.month.unique())
fil_año = st.sidebar.selectbox("Año", años, index=len(años) - 1)
fil_mes = st.sidebar.selectbox("Mes", meses)


def multi(label, col):
    opts = sorted(df[col].unique())
    sel = st.sidebar.multiselect(label, opts, placeholder="Todos")
    return sel or opts  # vacío = todos


fil_al, fil_cli, fil_fa = multi("Almacén", "ALMACEN"), multi("Clientes", "CLIENTE"), multi("Familia", "FAMILIA")

f = df[(df["FECHA CREACION"].dt.year == fil_año) & (df["FECHA CREACION"].dt.month == fil_mes)
       & df["ALMACEN"].isin(fil_al) & df["CLIENTE"].isin(fil_cli) & df["FAMILIA"].isin(fil_fa)]

# ------------------------------------------------------------- Métricas ---
facturada = int(f["CANTIDAD FACTURADA"].fillna(0).sum())
ordenada = int(f["CANTIDAD ORDENADA"].fillna(0).sum())
cancelada = int(f["CANTIDAD CANCELADA"].fillna(0).sum())
total = ordenada + cancelada
pct = round(facturada / total * 100, 2) if total else 0

st.sidebar.subheader("% Cantidad")
st.sidebar.plotly_chart(donut(pct), use_container_width=True)

c1, c2, c3 = st.columns(3)
c1.metric("CANTIDAD FACTURADA", f"{facturada:,}")
c2.metric("CANTIDAD ORDENADA", f"{ordenada:,}")
c3.metric("CANTIDAD CANCELADA", f"{cancelada:,}")

with st.expander("Vista previa de los datos filtrados"):
    st.dataframe(f)

# ------------------------------------------------------------ Top clientes ---
top = (f.groupby("CLIENTE")["CANTIDAD ORDENADA"].sum().reset_index()
       .sort_values("CANTIDAD ORDENADA", ascending=False).head(10))
fig = px.bar(top, x="CLIENTE", y="CANTIDAD ORDENADA", color="CLIENTE", text="CANTIDAD ORDENADA",
             labels={"CANTIDAD ORDENADA": "Cantidad ordenada", "CLIENTE": "Cliente"})
fig.update_layout(xaxis_tickangle=-45, showlegend=False, margin=dict(t=30, l=10, r=10, b=10), height=500)
fig.update_traces(texttemplate="%{text:.2s}", textposition="outside")

st.markdown("<h3 style='text-align:center'>📊 Top 10 clientes por cantidad ordenada</h3>", unsafe_allow_html=True)
st.plotly_chart(fig, use_container_width=True)
