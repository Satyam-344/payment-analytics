"""
Digital Payment Transaction Analytics
Full EDA + insights for PhonePe-style payment platform
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
import os
import warnings

warnings.filterwarnings("ignore")

# ── Style ──────────────────────────────────────────────────────────────────────
plt.rcParams.update({
    "figure.facecolor": "#0f0f1a",
    "axes.facecolor":   "#0f0f1a",
    "axes.edgecolor":   "#444",
    "axes.labelcolor":  "#ccc",
    "xtick.color":      "#ccc",
    "ytick.color":      "#ccc",
    "text.color":       "#eee",
    "grid.color":       "#2a2a3a",
    "grid.linewidth":   0.6,
    "font.family":      "DejaVu Sans",
    "axes.titlepad":    14,
})

PURPLE = "#7c3aed"
TEAL   = "#06b6d4"
ORANGE = "#f97316"
PINK   = "#ec4899"
GREEN  = "#10b981"
PALETTE = [PURPLE, TEAL, ORANGE, PINK, GREEN, "#f59e0b", "#3b82f6", "#8b5cf6", "#ef4444"]

os.makedirs("charts", exist_ok=True)

def save(fig, name):
    fig.savefig(f"charts/{name}.png", dpi=150, bbox_inches="tight",
                facecolor=fig.get_facecolor())
    plt.close(fig)
    print(f"  Saved: charts/{name}.png")

# ── Load Data ──────────────────────────────────────────────────────────────────
print("Loading data …")
df = pd.read_csv("transactions.csv", parse_dates=["date"])
success = df[df["status"] == "Success"].copy()

print(f"\n{'='*60}")
print("  DATASET OVERVIEW")
print(f"{'='*60}")
print(f"  Total transactions : {len(df):,}")
print(f"  Successful txns    : {len(success):,}  ({len(success)/len(df)*100:.1f}%)")
print(f"  Total GMV          : ₹{success['amount'].sum():,.0f}")
print(f"  Avg transaction    : ₹{success['amount'].mean():,.0f}")
print(f"  Unique users       : {df['user_id'].nunique():,}")
print(f"  Date range         : {df['date'].min().date()} → {df['date'].max().date()}")

# ── 1. Monthly GMV Trend ───────────────────────────────────────────────────────
print("\n[1] Monthly GMV Trend …")
monthly = success.groupby("month_num").agg(
    GMV=("amount", "sum"),
    Txns=("transaction_id", "count")
).reset_index()
month_names = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
monthly["month_name"] = monthly["month_num"].apply(lambda x: month_names[x-1])

fig, ax1 = plt.subplots(figsize=(12, 5))
bars = ax1.bar(monthly["month_name"], monthly["GMV"]/1e6, color=PURPLE, alpha=0.85, zorder=3)
ax1.set_ylabel("GMV (₹ Million)", color=PURPLE)
ax1.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"₹{x:.1f}M"))
ax2 = ax1.twinx()
ax2.plot(monthly["month_name"], monthly["Txns"], color=TEAL, marker="o", linewidth=2.5, markersize=7, zorder=4)
ax2.set_ylabel("Transaction Count", color=TEAL)
ax1.set_title("Monthly GMV & Transaction Volume (2024)", fontsize=15, fontweight="bold", color="#fff")
ax1.grid(axis="y", zorder=0)
fig.patch.set_facecolor("#0f0f1a")
save(fig, "01_monthly_trend")

# ── 2. Category Breakdown ──────────────────────────────────────────────────────
print("[2] Category Breakdown …")
cat = success.groupby("category").agg(
    GMV=("amount", "sum"), Count=("transaction_id", "count")
).sort_values("GMV", ascending=True).reset_index()

fig, axes = plt.subplots(1, 2, figsize=(14, 6))
fig.patch.set_facecolor("#0f0f1a")

colors = PALETTE[:len(cat)]
axes[0].barh(cat["category"], cat["GMV"]/1e6, color=colors, edgecolor="none")
axes[0].set_xlabel("GMV (₹ Million)")
axes[0].set_title("GMV by Category", fontweight="bold", color="#fff")
axes[0].xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"₹{x:.0f}M"))
for spine in axes[0].spines.values():
    spine.set_visible(False)

wedges, texts, autotexts = axes[1].pie(
    cat["Count"], labels=cat["category"],
    autopct="%1.1f%%", colors=colors,
    pctdistance=0.82, startangle=140,
    wedgeprops={"edgecolor": "#0f0f1a", "linewidth": 2}
)
for t in texts + autotexts:
    t.set_color("#eee")
    t.set_fontsize(8)
axes[1].set_title("Transaction Share by Category", fontweight="bold", color="#fff")
save(fig, "02_category_breakdown")

# ── 3. Payment Method Analysis ─────────────────────────────────────────────────
print("[3] Payment Method Analysis …")
pm = success.groupby("payment_method").agg(
    GMV=("amount", "sum"), Count=("transaction_id", "count")
).reset_index().sort_values("Count", ascending=False)

pm_fail = df.groupby("payment_method")["status"].apply(
    lambda x: (x == "Failed").sum() / len(x) * 100
).reset_index(name="failure_rate")

fig, axes = plt.subplots(1, 2, figsize=(14, 5))
fig.patch.set_facecolor("#0f0f1a")

axes[0].bar(pm["payment_method"], pm["Count"], color=PALETTE[:5], edgecolor="none")
axes[0].set_title("Transactions by Payment Method", fontweight="bold", color="#fff")
axes[0].set_ylabel("Count")
for spine in axes[0].spines.values():
    spine.set_visible(False)

colors_fr = [GREEN if r < 5 else ORANGE if r < 8 else PINK for r in pm_fail["failure_rate"]]
axes[1].bar(pm_fail["payment_method"], pm_fail["failure_rate"], color=colors_fr, edgecolor="none")
axes[1].set_title("Failure Rate by Payment Method (%)", fontweight="bold", color="#fff")
axes[1].set_ylabel("Failure Rate (%)")
axes[1].axhline(5, color="#fff", linestyle="--", linewidth=1, alpha=0.5, label="5% threshold")
axes[1].legend(facecolor="#1a1a2e")
for spine in axes[1].spines.values():
    spine.set_visible(False)
save(fig, "03_payment_methods")

# ── 4. Hourly & Day-of-Week Heatmap ───────────────────────────────────────────
print("[4] Hourly Transaction Heatmap …")
day_order = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
heatmap_data = success.groupby(["day_of_week", "hour"])["transaction_id"].count().unstack(fill_value=0)
heatmap_data = heatmap_data.reindex(day_order)

fig, ax = plt.subplots(figsize=(16, 5))
fig.patch.set_facecolor("#0f0f1a")
sns.heatmap(
    heatmap_data, cmap="Purples", ax=ax,
    linewidths=0.3, linecolor="#0f0f1a",
    cbar_kws={"label": "Transactions", "shrink": 0.8}
)
ax.set_title("Transaction Heatmap: Day × Hour", fontsize=14, fontweight="bold", color="#fff")
ax.set_xlabel("Hour of Day")
ax.set_ylabel("")
ax.tick_params(colors="#ccc")
save(fig, "04_heatmap_day_hour")

# ── 5. City-wise Performance ───────────────────────────────────────────────────
print("[5] City-wise Performance …")
city = success.groupby("city").agg(
    GMV=("amount", "sum"),
    Users=("user_id", "nunique"),
    AvgTxn=("amount", "mean")
).sort_values("GMV", ascending=False).reset_index()
city["GMV_per_user"] = city["GMV"] / city["Users"]

fig, axes = plt.subplots(1, 2, figsize=(14, 5))
fig.patch.set_facecolor("#0f0f1a")

axes[0].bar(city["city"], city["GMV"]/1e6, color=PALETTE[:len(city)], edgecolor="none")
axes[0].set_title("GMV by City (₹ Million)", fontweight="bold", color="#fff")
axes[0].set_ylabel("GMV (₹M)")
axes[0].tick_params(axis="x", rotation=40)
for spine in axes[0].spines.values(): spine.set_visible(False)

axes[1].bar(city["city"], city["GMV_per_user"], color=TEAL, alpha=0.85, edgecolor="none")
axes[1].set_title("GMV per Active User by City", fontweight="bold", color="#fff")
axes[1].set_ylabel("₹ per User")
axes[1].tick_params(axis="x", rotation=40)
for spine in axes[1].spines.values(): spine.set_visible(False)
save(fig, "05_city_performance")

# ── 6. Age Group & Gender Analysis ────────────────────────────────────────────
print("[6] Demographics …")
age_cat = success.groupby(["age_group", "category"])["amount"].sum().reset_index()
age_pivot = age_cat.pivot(index="age_group", columns="category", values="amount").fillna(0)
age_order = ["18-24", "25-34", "35-44", "45-54", "55+"]
age_pivot = age_pivot.reindex(age_order)
age_pivot_pct = age_pivot.div(age_pivot.sum(axis=1), axis=0) * 100

fig, axes = plt.subplots(1, 2, figsize=(16, 6))
fig.patch.set_facecolor("#0f0f1a")

age_pivot_pct.plot(kind="bar", stacked=True, ax=axes[0], color=PALETTE, edgecolor="none")
axes[0].set_title("Spending Mix by Age Group (%)", fontweight="bold", color="#fff")
axes[0].set_ylabel("Share of Spend (%)")
axes[0].tick_params(axis="x", rotation=30)
axes[0].legend(fontsize=7, facecolor="#1a1a2e", loc="upper right")
for spine in axes[0].spines.values(): spine.set_visible(False)

gender_data = success.groupby("gender")["amount"].agg(["sum", "mean", "count"]).reset_index()
x = np.arange(len(gender_data))
bars1 = axes[1].bar(x - 0.2, gender_data["sum"]/1e6, 0.35, label="Total GMV (₹M)", color=PURPLE, alpha=0.9)
axes[1].set_ylabel("GMV (₹M)", color=PURPLE)
ax2 = axes[1].twinx()
bars2 = ax2.bar(x + 0.2, gender_data["mean"], 0.35, label="Avg Txn (₹)", color=TEAL, alpha=0.9)
ax2.set_ylabel("Avg Transaction (₹)", color=TEAL)
axes[1].set_xticks(x)
axes[1].set_xticklabels(gender_data["gender"])
axes[1].set_title("GMV & Avg Transaction by Gender", fontweight="bold", color="#fff")
lines = [plt.Line2D([0],[0],color=PURPLE,lw=8,alpha=0.9),
         plt.Line2D([0],[0],color=TEAL,lw=8,alpha=0.9)]
axes[1].legend(lines, ["Total GMV","Avg Txn"], facecolor="#1a1a2e", loc="upper left")
for spine in axes[1].spines.values(): spine.set_visible(False)
save(fig, "06_demographics")

# ── 7. Transaction Amount Distribution ────────────────────────────────────────
print("[7] Amount Distribution …")
fig, axes = plt.subplots(1, 2, figsize=(14, 5))
fig.patch.set_facecolor("#0f0f1a")

axes[0].hist(success["amount"], bins=60, color=PURPLE, edgecolor="#0f0f1a", alpha=0.85)
axes[0].set_title("Transaction Amount Distribution", fontweight="bold", color="#fff")
axes[0].set_xlabel("Amount (₹)")
axes[0].set_ylabel("Frequency")
axes[0].axvline(success["amount"].median(), color=TEAL, linestyle="--", label=f"Median ₹{success['amount'].median():.0f}")
axes[0].axvline(success["amount"].mean(), color=ORANGE, linestyle="--", label=f"Mean ₹{success['amount'].mean():.0f}")
axes[0].legend(facecolor="#1a1a2e")
for spine in axes[0].spines.values(): spine.set_visible(False)

percentiles = [10, 25, 50, 75, 90, 95, 99]
pct_values = [np.percentile(success["amount"], p) for p in percentiles]
axes[1].plot(percentiles, pct_values, color=TEAL, marker="o", linewidth=2.5, markersize=8)
axes[1].fill_between(percentiles, pct_values, alpha=0.2, color=TEAL)
axes[1].set_title("Amount Percentile Curve", fontweight="bold", color="#fff")
axes[1].set_xlabel("Percentile")
axes[1].set_ylabel("Amount (₹)")
axes[1].yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"₹{x:,.0f}"))
for spine in axes[1].spines.values(): spine.set_visible(False)
save(fig, "07_amount_distribution")

# ── 8. Quarter & Growth Analysis ──────────────────────────────────────────────
print("[8] Quarterly Growth …")
qtr = success.groupby("quarter").agg(
    GMV=("amount", "sum"), Txns=("transaction_id", "count")
).reset_index()
qtr["GMV_growth"] = qtr["GMV"].pct_change() * 100
qtr["Txn_growth"] = qtr["Txns"].pct_change() * 100

fig, axes = plt.subplots(1, 2, figsize=(12, 5))
fig.patch.set_facecolor("#0f0f1a")

axes[0].bar(qtr["quarter"], qtr["GMV"]/1e6, color=PALETTE[:4], edgecolor="none", width=0.5)
for i, (q, g, gmv) in enumerate(zip(qtr["quarter"], qtr["GMV_growth"].fillna(0), qtr["GMV"])):
    if i > 0:
        axes[0].text(i, gmv/1e6 + 0.5, f"+{g:.1f}%", ha="center", color=GREEN, fontsize=11, fontweight="bold")
axes[0].set_title("Quarterly GMV (₹ Million)", fontweight="bold", color="#fff")
axes[0].set_ylabel("GMV (₹M)")
for spine in axes[0].spines.values(): spine.set_visible(False)

axes[1].bar(qtr["quarter"], qtr["Txns"], color=PALETTE[4:8], edgecolor="none", width=0.5)
axes[1].set_title("Quarterly Transaction Volume", fontweight="bold", color="#fff")
axes[1].set_ylabel("Transactions")
for spine in axes[1].spines.values(): spine.set_visible(False)
save(fig, "08_quarterly_growth")

# ── 9. Top Merchants ──────────────────────────────────────────────────────────
print("[9] Top Merchants …")
top_merchants = success.groupby("merchant").agg(
    GMV=("amount", "sum"), Count=("transaction_id", "count")
).sort_values("GMV", ascending=False).head(15).reset_index()

fig, ax = plt.subplots(figsize=(12, 6))
fig.patch.set_facecolor("#0f0f1a")
colors = [PALETTE[i % len(PALETTE)] for i in range(len(top_merchants))]
ax.barh(top_merchants["merchant"][::-1], top_merchants["GMV"][::-1]/1e3, color=colors[::-1], edgecolor="none")
ax.set_title("Top 15 Merchants by GMV", fontsize=14, fontweight="bold", color="#fff")
ax.set_xlabel("GMV (₹ Thousands)")
ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"₹{x:.0f}K"))
for spine in ax.spines.values(): spine.set_visible(False)
save(fig, "09_top_merchants")

# ── Summary Insights ───────────────────────────────────────────────────────────
print(f"\n{'='*60}")
print("  KEY BUSINESS INSIGHTS")
print(f"{'='*60}")
print(f"  1. Total GMV 2024      : ₹{success['amount'].sum()/1e7:.2f} Crore")
print(f"  2. Overall success rate: {len(success)/len(df)*100:.1f}%")
print(f"  3. Top category (GMV)  : {success.groupby('category')['amount'].sum().idxmax()}")
print(f"  4. Top city (GMV)      : {success.groupby('city')['amount'].sum().idxmax()}")
print(f"  5. Peak hour           : {success.groupby('hour')['transaction_id'].count().idxmax()}:00")
print(f"  6. UPI dominates       : {success[success['payment_method']=='UPI'].shape[0]/len(success)*100:.1f}% of txns")
print(f"  7. High-value segment  : Top 5% users drive {success.nlargest(int(len(success)*0.05), 'amount')['amount'].sum()/success['amount'].sum()*100:.1f}% of GMV")
top_day = success.groupby("day_of_week")["amount"].sum().idxmax()
print(f"  8. Best day            : {top_day}")
print(f"\n  All charts saved in ./charts/")
print(f"{'='*60}\n")
