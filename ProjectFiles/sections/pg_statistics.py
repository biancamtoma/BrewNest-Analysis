"""Page 5 — Statistical Processing, Grouping & Aggregation (Pandas)"""
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


def render(data):
    stores = data["stores"]
    products = data["products"]
    sales = data["sales"].copy()
    customers = data["customers"]

    st.title(" Statistical Analysis — Pandas")
    st.markdown(
        "Grouping, aggregation, pivot tables, and descriptive statistics "
        "to understand BrewNest's business performance."
    )

    # Enrich sales
    sales_full = sales.merge(products[["product_id", "name", "category", "cost_price"]], on="product_id")
    sales_full = sales_full.merge(stores[["store_id", "city", "region"]], on="store_id")
    sales_full["month"] = sales_full["date"].dt.to_period("M").astype(str)
    sales_full["quarter"] = sales_full["date"].dt.to_period("Q").astype(str)
    sales_full["profit"] = sales_full["total_revenue"] - (sales_full["cost_price"] * sales_full["quantity"])

    # ── Descriptive Statistics ──────────────────────────────
    st.header("A. Descriptive Statistics")
    num_cols = ["quantity", "unit_price", "discount", "total_revenue", "profit"]
    desc = sales_full[num_cols].describe().round(2)
    st.dataframe(desc, use_container_width=True)

    # ── Groupby + Aggregation ───────────────────────────────
    st.markdown("---")
    st.header("B. Revenue by Store & City")

    num_rows = st.number_input("Number of top stores to display:", min_value=1, max_value=len(stores), value=5, step=1)

    store_stats = (
        sales_full.groupby(["store_id", "city", "region"])
        .agg(
            total_revenue=("total_revenue", "sum"),
            total_profit=("profit", "sum"),
            avg_basket=("total_revenue", "mean"),
            transaction_count=("transaction_id", "count"),
        )
        .reset_index()
        .sort_values("total_revenue", ascending=False)
    )
    store_stats["profit_margin"] = (
        store_stats["total_profit"] / store_stats["total_revenue"] * 100
    ).round(1)
    st.dataframe(store_stats.head(num_rows).round(0), use_container_width=True, hide_index=True)

    # ── Category Performance ────────────────────────────────
    st.markdown("---")
    st.header("C. Revenue by Product Category")

    cat_stats = (
        sales_full.groupby("category")
        .agg(
            revenue=("total_revenue", "sum"),
            profit=("profit", "sum"),
            qty=("quantity", "sum"),
            transactions=("transaction_id", "count"),
        )
        .reset_index()
        .sort_values("revenue", ascending=False)
    )
    cat_stats["revenue_share_%"] = (cat_stats["revenue"] / cat_stats["revenue"].sum() * 100).round(1)
    cat_stats["avg_margin_%"] = (cat_stats["profit"] / cat_stats["revenue"] * 100).round(1)
    st.dataframe(cat_stats.round(0), use_container_width=True, hide_index=True)

    # ── Pivot Table ─────────────────────────────────────────
    st.markdown("---")
    st.header("D. Monthly Revenue Pivot Table")

    # Last 6 months for readability
    recent_months = sorted(sales_full["month"].unique())[-6:]
    pivot = sales_full[sales_full["month"].isin(recent_months)].pivot_table(
        index="city",
        columns="month",
        values="total_revenue",
        aggfunc="sum",
        fill_value=0,
    ).round(0)
    st.dataframe(pivot, use_container_width=True)

    # Crosstab
    st.markdown("---")
    st.header("E. Transactions: Category by City (Crosstab)")
    
    crosstab_df = pd.crosstab(
        index=sales_full["city"],
        columns=sales_full["category"],
        margins=True,
        margins_name="Total"
    )
    st.dataframe(crosstab_df, use_container_width=True)

    # Quarterly Trend 
    st.markdown("---")
    st.header("F. Quarterly Revenue Trend")

    quarterly = (
        sales_full.groupby("quarter")["total_revenue"]
        .sum()
        .reset_index()
    )
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot(quarterly["quarter"], quarterly["total_revenue"], marker="o",
            color="#d4a76a", linewidth=2, markersize=6)
    ax.fill_between(range(len(quarterly)), quarterly["total_revenue"],
                    alpha=0.15, color="#d4a76a")
    ax.set_title("Quarterly Revenue Trend", fontsize=13, fontweight="bold")
    ax.set_xlabel("Quarter")
    ax.set_ylabel("Revenue (RON)")
    plt.xticks(rotation=45)
    fig.tight_layout()
    st.pyplot(fig)
    plt.close()

    # Correlation
    st.markdown("---")
    st.header("G. Correlation Matrix")

    corr_data = store_stats[["total_revenue", "total_profit", "avg_basket", "transaction_count"]].copy()
    corr_data = corr_data.merge(
        stores[["store_id", "size_sqm", "monthly_rent", "employee_count"]],
        left_index=True,
        right_index=True,
        how="left",
    ) if False else store_stats.merge(
        stores[["store_id", "size_sqm", "monthly_rent", "employee_count"]], on="store_id"
    )

    corr_cols = ["total_revenue", "total_profit", "transaction_count", "size_sqm", "monthly_rent", "employee_count"]
    corr_matrix = corr_data[corr_cols].corr().round(2)
    st.dataframe(corr_matrix, use_container_width=True)

    st.markdown(
        "**Economic Interpretation:** Coffee dominates revenue but pastries "
        "may have higher profit margins. Stores in Bucharest lead revenue, "
        "while smaller cities show higher per-transaction profitability, "
        "suggesting untapped expansion potential in mid-tier cities."
    )
