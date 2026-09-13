"""Page 7 — Matplotlib Visualizations"""
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns


def render(data):
    stores = data["stores"]
    products = data["products"]
    sales = data["sales"].copy()
    customers = data["customers"]
    employees = data["employees"]

    st.title(" Matplotlib Visualizations")
    st.markdown(
        "Comprehensive graphical analysis of BrewNest's business data "
        "using matplotlib and seaborn."
    )

    # Prepare enriched data
    sales_full = (
        sales
        .merge(products[["product_id", "name", "category", "cost_price"]], on="product_id")
        .merge(stores[["store_id", "city", "region"]], on="store_id")
    )
    sales_full["month"] = sales_full["date"].dt.to_period("M")
    sales_full["profit"] = sales_full["total_revenue"] - (sales_full["cost_price"] * sales_full["quantity"])

    plt.rcParams.update({
        "figure.facecolor": "#0e1117",
        "axes.facecolor": "#0e1117",
        "axes.edgecolor": "#555",
        "text.color": "#fafafa",
        "axes.labelcolor": "#fafafa",
        "xtick.color": "#ccc",
        "ytick.color": "#ccc",
        "grid.color": "#333",
    })

    # ── 1. Bar Chart: Revenue by City ───────────────────────
    st.header("1. Bar Chart — Revenue by City")
    city_rev = sales_full.groupby("city")["total_revenue"].sum().sort_values(ascending=True)

    fig1, ax1 = plt.subplots(figsize=(10, 5))
    colors = plt.cm.YlOrBr(np.linspace(0.3, 0.9, len(city_rev)))
    bars = ax1.barh(city_rev.index, city_rev.values, color=colors, edgecolor="none")
    ax1.set_xlabel("Total Revenue (RON)", fontsize=11)
    ax1.set_title("Total Revenue by City", fontsize=14, fontweight="bold", color="#d4a76a")
    for bar, val in zip(bars, city_rev.values):
        ax1.text(val + city_rev.max() * 0.01, bar.get_y() + bar.get_height() / 2,
                 f"{val:,.0f}", va="center", fontsize=9, color="#fafafa")
    fig1.tight_layout()
    st.pyplot(fig1)
    plt.close()

    # ── 2. Line Chart: Monthly Sales Trend ──────────────────
    st.header("2. Line Chart — Monthly Sales Trend")
    monthly = sales_full.groupby("month")["total_revenue"].sum().reset_index()
    monthly["month"] = monthly["month"].astype(str)

    fig2, ax2 = plt.subplots(figsize=(12, 4))
    ax2.plot(monthly["month"], monthly["total_revenue"], color="#d4a76a",
             linewidth=2, marker="o", markersize=4)
    ax2.fill_between(range(len(monthly)), monthly["total_revenue"],
                     alpha=0.1, color="#d4a76a")
    ax2.set_title("Monthly Revenue Trend", fontsize=14, fontweight="bold", color="#d4a76a")
    ax2.set_xlabel("Month")
    ax2.set_ylabel("Revenue (RON)")
    plt.xticks(rotation=45, ha="right")
    fig2.tight_layout()
    st.pyplot(fig2)
    plt.close()

    # ── 3. Pie Chart: Revenue by Category ───────────────────
    st.header("3. Pie Chart — Revenue Share by Product Category")
    cat_rev = sales_full.groupby("category")["total_revenue"].sum()

    fig3, ax3 = plt.subplots(figsize=(7, 7))
    wedge_colors = ["#d4a76a", "#6abd6a", "#6a9bd4", "#d46a6a", "#b06abd"]
    wedges, texts, autotexts = ax3.pie(
        cat_rev.values, labels=cat_rev.index, autopct="%1.1f%%",
        colors=wedge_colors[:len(cat_rev)],
        startangle=140, pctdistance=0.8,
        wedgeprops=dict(edgecolor="#0e1117", linewidth=2),
    )
    for t in autotexts:
        t.set_fontsize(11)
        t.set_color("#0e1117")
        t.set_fontweight("bold")
    ax3.set_title("Revenue Share by Category", fontsize=14, fontweight="bold", color="#d4a76a")
    fig3.tight_layout()
    st.pyplot(fig3)
    plt.close()

    # ── 4. Scatter Plot: Store Size vs Revenue ──────────────
    st.header("4. Scatter Plot — Store Size vs Revenue")
    store_rev = sales_full.groupby("store_id")["total_revenue"].sum().reset_index()
    store_scatter = stores.merge(store_rev, on="store_id")

    fig4, ax4 = plt.subplots(figsize=(10, 5))
    scatter = ax4.scatter(
        store_scatter["size_sqm"], store_scatter["total_revenue"],
        c=store_scatter["employee_count"], cmap="YlOrBr",
        s=120, edgecolor="white", linewidth=0.5, alpha=0.9,
    )
    plt.colorbar(scatter, ax=ax4, label="Employee Count")
    # Trend line
    z = np.polyfit(store_scatter["size_sqm"], store_scatter["total_revenue"], 1)
    p = np.poly1d(z)
    x_line = np.linspace(store_scatter["size_sqm"].min(), store_scatter["size_sqm"].max(), 50)
    ax4.plot(x_line, p(x_line), "--", color="#ff6b6b", linewidth=1.5, label="Trend line")
    ax4.legend()
    ax4.set_xlabel("Store Size (sqm)", fontsize=11)
    ax4.set_ylabel("Total Revenue (RON)", fontsize=11)
    ax4.set_title("Store Size vs Revenue", fontsize=14, fontweight="bold", color="#d4a76a")
    # Label cities
    for _, row in store_scatter.iterrows():
        ax4.annotate(row["city"], (row["size_sqm"], row["total_revenue"]),
                     fontsize=7, color="#aaa", ha="center", va="bottom")
    fig4.tight_layout()
    st.pyplot(fig4)
    plt.close()

    # ── 5. Box Plot: Salary by Role ─────────────────────────
    st.header("5. Box Plot — Salary Distribution by Role")
    fig5, ax5 = plt.subplots(figsize=(10, 5))
    roles_order = ["Barista", "Baker", "Shift Manager", "Store Manager"]
    emp_plot = employees[employees["role"].isin(roles_order)]
    bp_data = [emp_plot[emp_plot["role"] == r]["salary"].values for r in roles_order]
    bp = ax5.boxplot(bp_data, labels=roles_order, patch_artist=True, widths=0.5)
    box_colors = ["#d4a76a", "#6abd6a", "#6a9bd4", "#d46a6a"]
    for patch, color in zip(bp["boxes"], box_colors):
        patch.set_facecolor(color)
        patch.set_alpha(0.7)
    for median in bp["medians"]:
        median.set_color("white")
        median.set_linewidth(2)
    ax5.set_ylabel("Monthly Salary (RON)", fontsize=11)
    ax5.set_title("Salary Distribution by Role", fontsize=14, fontweight="bold", color="#d4a76a")
    ax5.grid(axis="y", alpha=0.3)
    fig5.tight_layout()
    st.pyplot(fig5)
    plt.close()

    # ── 6. Heatmap: Correlation ─────────────────────────────
    st.header("6. Heatmap — Store-Level Correlation Matrix")
    store_metrics = store_scatter[["size_sqm", "monthly_rent", "employee_count", "total_revenue",
                                    "city_population"]].copy()
    corr = store_metrics.corr().round(2)

    fig6, ax6 = plt.subplots(figsize=(8, 6))
    sns.heatmap(
        corr, annot=True, cmap="YlOrBr", center=0, linewidths=1,
        linecolor="#333", fmt=".2f", ax=ax6,
        annot_kws={"fontsize": 11, "color": "#0e1117"},
    )
    ax6.set_title("Correlation Matrix — Store Metrics", fontsize=14, fontweight="bold", color="#d4a76a")
    fig6.tight_layout()
    st.pyplot(fig6)
    plt.close()

    st.markdown(
        "**Economic Interpretation:** The visualizations confirm that larger stores "
        "in bigger cities generate more revenue (positive size-revenue correlation). "
        "Coffee products dominate revenue share at ~40-50%, while merchandise has the "
        "highest per-unit profit margin. Salary distributions show clear role-based "
        "stratification, important for HR budgeting during expansion."
    )
