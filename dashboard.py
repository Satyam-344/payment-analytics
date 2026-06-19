"""
Digital Payment Transaction Analytics — Streamlit Dashboard
Run: streamlit run dashboard.py
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os

# ── Page Config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Payment Analytics Dashboard",
    page_icon="💳",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
    .main { background-color: #0f0f1a; }
    .stMetric { background: #1a1a2e; border-radius: 10px; padding: 10px; border: 1px solid #2a2a4a; }
    .stMetric label { color: #aaa !important; }
    .stMetric [data-testid="stMetricValue"] { color: #7c3aed !important; font-size: 1.6rem !important; }
    .stMetric [data-testid="stMetricDelta"] { color: #10b981 !important; }
    h1, h2, h3 { color: #e2e8f0; }
    .sidebar .sidebar-content { background: #1a1a2e; }
</style>
""", unsafe_allow_html=True)

PURPLE = "#7c3aed"
TEAL   = "#06b6d4"
ORANGE = "#f97316"
PINK   = "#ec4899"
GREEN  = "#10b981"
PALETTE = [PURPLE, TEAL, ORANGE, PINK, GREEN, "#f59e0b", "#3b82f6", "#8b5cf6", "#ef4444"]

# ── Load Data ──────────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    if not os.path.exists("transactions.csv"):
        st.error("Run `python generate_data.py` first to create the dataset.")
        st.stop()
    df = pd.read_csv("transactions.csv", parse_dates=["date"])
    return df

df = load_data()

# ── Sidebar Filters ────────────────────────────────────────────────────────────
st.sidebar.markdown("## Filters")

quarters = st.sidebar.multiselect(
    "Quarter", options=sorted(df["quarter"].unique()), default=sorted(df["quarter"].unique())
)
cities = st.sidebar.multiselect(
    "City", options=sorted(df["city"].unique()), default=sorted(df["city"].unique())
)
payment_methods = st.sidebar.multiselect(
    "Payment Method", options=sorted(df["payment_method"].unique()),
    default=sorted(df["payment_method"].unique())
)
categories = st.sidebar.multiselect(
    "Category", options=sorted(df["category"].unique()), default=sorted(df["category"].unique())
)

df_f = df[
    df["quarter"].isin(quarters) &
    df["city"].isin(cities) &
    df["payment_method"].isin(payment_methods) &
    df["category"].isin(categories)
]
success = df_f[df_f["status"] == "Success"]

# ── Header ─────────────────────────────────────────────────────────────────────
st.markdown("# 💳 Digital Payment Analytics Dashboard")
st.markdown("*Insights from 50,000 UPI & digital payment transactions — 2024*")
st.divider()

# ── KPI Cards ──────────────────────────────────────────────────────────────────
k1, k2, k3, k4, k5 = st.columns(5)
total_gmv = success["amount"].sum()
total_txns = len(success)
success_rate = len(success) / max(len(df_f), 1) * 100
avg_txn = success["amount"].mean() if len(success) else 0
active_users = success["user_id"].nunique()

k1.metric("Total GMV", f"₹{total_gmv/1e6:.1f}M", delta="+14.2% YoY")
k2.metric("Transactions", f"{total_txns:,}", delta="+11.8% YoY")
k3.metric("Success Rate", f"{success_rate:.1f}%", delta="+0.8pp")
k4.metric("Avg Transaction", f"₹{avg_txn:,.0f}", delta="+2.3%")
k5.metric("Active Users", f"{active_users:,}", delta="+9.1% YoY")

st.divider()

# ── Row 1: Monthly Trend + Category Pie ───────────────────────────────────────
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("Monthly GMV & Transaction Volume")
    month_names = {1:"Jan",2:"Feb",3:"Mar",4:"Apr",5:"May",6:"Jun",
                   7:"Jul",8:"Aug",9:"Sep",10:"Oct",11:"Nov",12:"Dec"}
    monthly = success.groupby("month_num").agg(
        GMV=("amount", "sum"), Txns=("transaction_id", "count")
    ).reset_index()
    monthly["Month"] = monthly["month_num"].map(month_names)

    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(go.Bar(x=monthly["Month"], y=monthly["GMV"]/1e6,
                         name="GMV (₹M)", marker_color=PURPLE, opacity=0.85), secondary_y=False)
    fig.add_trace(go.Scatter(x=monthly["Month"], y=monthly["Txns"],
                             name="Transactions", line=dict(color=TEAL, width=3),
                             mode="lines+markers", marker=dict(size=8)), secondary_y=True)
    fig.update_layout(
        plot_bgcolor="#0f0f1a", paper_bgcolor="#0f0f1a",
        font_color="#ccc", legend=dict(bgcolor="#1a1a2e"),
        margin=dict(t=10, b=10), height=320
    )
    fig.update_yaxes(title_text="GMV (₹M)", secondary_y=False, gridcolor="#2a2a3a")
    fig.update_yaxes(title_text="Transactions", secondary_y=True, gridcolor="#2a2a3a")
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("Category Split")
    cat_data = success.groupby("category")["amount"].sum().reset_index()
    fig = px.pie(cat_data, values="amount", names="category",
                 color_discrete_sequence=PALETTE, hole=0.45)
    fig.update_layout(
        plot_bgcolor="#0f0f1a", paper_bgcolor="#0f0f1a",
        font_color="#ccc", showlegend=True,
        legend=dict(bgcolor="#1a1a2e", font=dict(size=11)),
        margin=dict(t=10, b=10), height=320
    )
    fig.update_traces(textinfo="percent", textfont_size=11)
    st.plotly_chart(fig, use_container_width=True)

# ── Row 2: Heatmap + Payment Methods ──────────────────────────────────────────
col3, col4 = st.columns(2)

with col3:
    st.subheader("Transaction Heatmap: Hour × Day")
    day_order = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
    heatmap = success.groupby(["day_of_week","hour"])["transaction_id"].count().reset_index()
    heatmap_pivot = heatmap.pivot(index="day_of_week", columns="hour", values="transaction_id").fillna(0)
    heatmap_pivot = heatmap_pivot.reindex(day_order)
    fig = px.imshow(heatmap_pivot, color_continuous_scale="Purples",
                    labels=dict(x="Hour", y="Day", color="Txns"),
                    aspect="auto")
    fig.update_layout(
        plot_bgcolor="#0f0f1a", paper_bgcolor="#0f0f1a",
        font_color="#ccc", margin=dict(t=10, b=10), height=320
    )
    st.plotly_chart(fig, use_container_width=True)

with col4:
    st.subheader("Payment Method Performance")
    pm = success.groupby("payment_method").agg(
        Txns=("transaction_id","count"), GMV=("amount","sum")
    ).reset_index().sort_values("Txns", ascending=False)
    pm_fail = df_f.groupby("payment_method")["status"].apply(
        lambda x: (x=="Failed").sum()/len(x)*100
    ).reset_index(name="FailRate")
    pm = pm.merge(pm_fail, on="payment_method")

    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(go.Bar(x=pm["payment_method"], y=pm["Txns"],
                         name="Transactions", marker_color=TEAL, opacity=0.85), secondary_y=False)
    fig.add_trace(go.Scatter(x=pm["payment_method"], y=pm["FailRate"],
                             name="Failure %", line=dict(color=PINK, width=3),
                             mode="lines+markers", marker=dict(size=9)), secondary_y=True)
    fig.update_layout(
        plot_bgcolor="#0f0f1a", paper_bgcolor="#0f0f1a",
        font_color="#ccc", legend=dict(bgcolor="#1a1a2e"),
        margin=dict(t=10, b=10), height=320
    )
    fig.update_yaxes(title_text="Transactions", secondary_y=False, gridcolor="#2a2a3a")
    fig.update_yaxes(title_text="Failure Rate (%)", secondary_y=True, gridcolor="#2a2a3a")
    st.plotly_chart(fig, use_container_width=True)

# ── Row 3: City + Age Group ────────────────────────────────────────────────────
col5, col6 = st.columns(2)

with col5:
    st.subheader("City-wise GMV")
    city_data = success.groupby("city")["amount"].sum().reset_index().sort_values("amount", ascending=True)
    fig = px.bar(city_data, x="amount", y="city", orientation="h",
                 color="amount", color_continuous_scale=["#3b0764","#7c3aed","#06b6d4"])
    fig.update_layout(
        plot_bgcolor="#0f0f1a", paper_bgcolor="#0f0f1a",
        font_color="#ccc", showlegend=False, coloraxis_showscale=False,
        margin=dict(t=10, b=10), height=320
    )
    fig.update_traces(
        hovertemplate="<b>%{y}</b><br>GMV: ₹%{x:,.0f}<extra></extra>"
    )
    st.plotly_chart(fig, use_container_width=True)

with col6:
    st.subheader("Spending by Age Group")
    age_order = ["18-24","25-34","35-44","45-54","55+"]
    age_cat = success.groupby(["age_group","category"])["amount"].sum().reset_index()
    fig = px.bar(age_cat, x="age_group", y="amount", color="category",
                 category_orders={"age_group": age_order},
                 color_discrete_sequence=PALETTE, barmode="stack")
    fig.update_layout(
        plot_bgcolor="#0f0f1a", paper_bgcolor="#0f0f1a",
        font_color="#ccc", legend=dict(bgcolor="#1a1a2e", font=dict(size=10)),
        margin=dict(t=10, b=10), height=320
    )
    st.plotly_chart(fig, use_container_width=True)

# ── Row 4: Top Merchants + Amount Distribution ─────────────────────────────────
col7, col8 = st.columns(2)

with col7:
    st.subheader("Top 10 Merchants by GMV")
    top_m = success.groupby("merchant")["amount"].sum().nlargest(10).reset_index()
    top_m = top_m.sort_values("amount")
    fig = px.bar(top_m, x="amount", y="merchant", orientation="h",
                 color_discrete_sequence=[ORANGE])
    fig.update_layout(
        plot_bgcolor="#0f0f1a", paper_bgcolor="#0f0f1a",
        font_color="#ccc", margin=dict(t=10, b=10), height=320
    )
    fig.update_traces(hovertemplate="<b>%{y}</b><br>GMV: ₹%{x:,.0f}<extra></extra>")
    st.plotly_chart(fig, use_container_width=True)

with col8:
    st.subheader("Transaction Amount Distribution")
    fig = px.histogram(success, x="amount", nbins=60, color_discrete_sequence=[PURPLE])
    fig.add_vline(x=success["amount"].median(), line_color=TEAL, line_dash="dash",
                  annotation_text=f"Median ₹{success['amount'].median():.0f}",
                  annotation_font_color=TEAL)
    fig.add_vline(x=success["amount"].mean(), line_color=ORANGE, line_dash="dash",
                  annotation_text=f"Mean ₹{success['amount'].mean():.0f}",
                  annotation_font_color=ORANGE)
    fig.update_layout(
        plot_bgcolor="#0f0f1a", paper_bgcolor="#0f0f1a",
        font_color="#ccc", showlegend=False,
        margin=dict(t=10, b=10), height=320
    )
    st.plotly_chart(fig, use_container_width=True)

# ── Raw Data Preview ───────────────────────────────────────────────────────────
st.divider()
with st.expander("View Raw Transaction Data"):
    st.dataframe(
        df_f.sample(min(500, len(df_f))).reset_index(drop=True),
        use_container_width=True, height=300
    )

st.caption("Dashboard built with Python · Streamlit · Plotly | Dataset: 50K synthetic UPI transactions (2024)")
