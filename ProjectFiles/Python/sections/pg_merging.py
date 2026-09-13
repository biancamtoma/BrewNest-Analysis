import streamlit as st
import pandas as pd


def render(data):
    stores = data["stores"]
    products = data["products"]
    customers = data["customers"]
    sales = data["sales"].copy()
    employees = data["employees"]

    st.title(" Data Integration - Merge & Join")
    st.markdown(
        "Combining BrewNest's 5 separate datasets into unified views "
        "for comprehensive analysis."
    )

    # Join 1: Sales + Products 
    st.header("A. Sales + Products (Inner Join)")
    st.markdown("`pd.merge(sales, products, on='product_id', how='inner')`")

    sales_products = pd.merge(
        sales[["transaction_id", "store_id", "product_id", "date", "quantity", "total_revenue"]],
        products[["product_id", "name", "category", "unit_price", "cost_price"]],
        on="product_id",
        how="inner",
        suffixes=("_sale", "_list"),
    )
    col1, col2, col3 = st.columns(3)
    col1.metric("Sales rows", f"{len(sales):,}")
    col2.metric("Products rows", f"{len(products):,}")
    col3.metric("Result rows", f"{len(sales_products):,}")
    st.dataframe(sales_products.head(10), use_container_width=True, hide_index=True)

    # Join 2: Sales + Stores
    st.markdown("---")
    st.header("B. Sales + Stores (Left Join)")
    st.markdown("`pd.merge(sales, stores, on='store_id', how='left')`")

    sales_stores = pd.merge(
        sales[["transaction_id", "store_id", "date", "total_revenue"]],
        stores[["store_id", "city", "region", "size_sqm"]],
        on="store_id",
        how="left",
    )
    st.dataframe(sales_stores.head(10), use_container_width=True, hide_index=True)

    # Join 3: Sales + Customers 
    st.markdown("---")
    st.header("C. Sales + Customers (Left Join)")
    st.markdown(
        "`pd.merge(sales, customers, on='customer_id', how='left')` — "
        "walk-in customers (null customer_id) will have NaN for customer fields."
    )

    sales_cust = pd.merge(
        sales[["transaction_id", "customer_id", "total_revenue"]],
        customers[["customer_id", "age", "gender", "income_bracket", "loyalty_member"]],
        on="customer_id",
        how="left",
    )
    null_rows = sales_cust["age"].isnull().sum()
    st.metric("Rows with null customer info (walk-ins)", f"{null_rows:,}")
    st.dataframe(sales_cust.head(10), use_container_width=True, hide_index=True)

    # Join 4: Multi-table join 
    st.markdown("---")
    st.header("D. Full Transaction View (Multi-Table Join)")
    st.markdown("Joining **Sales + Products + Stores + Customers** in a single pipeline.")

    full_view = (
        sales
        .merge(products[["product_id", "name", "category"]], on="product_id", how="inner")
        .merge(stores[["store_id", "city", "region"]], on="store_id", how="left")
        .merge(
            customers[["customer_id", "age", "gender", "loyalty_member"]],
            on="customer_id",
            how="left",
        )
    )
    st.write(f"**Result:** {full_view.shape[0]:,} rows x {full_view.shape[1]} columns")

    with st.expander("Explore the Multi-Table View", expanded=True):
        default_cols = ["transaction_id", "date", "name", "city", "total_revenue"]
        selected_cols = st.multiselect(
            "Select columns to display:",
            options=full_view.columns.tolist(),
            default=default_cols
        )
        if selected_cols:
            st.dataframe(full_view[selected_cols].head(15), use_container_width=True, hide_index=True)
        else:
            st.warning("Please select at least one column.")

    # Join type comparison
    st.markdown("---")
    st.header("E. Join Type Comparison")
    st.markdown("Comparing row counts across different join types for Sales + Customers:")

    # Need a small subset with some mismatches for clarity
    join_types = ["inner", "left", "right", "outer"]
    results = []
    for jt in join_types:
        merged = pd.merge(
            sales[["transaction_id", "customer_id"]],
            customers[["customer_id", "age"]],
            on="customer_id",
            how=jt,
        )
        results.append({
            "Join Type": jt.upper(),
            "Result Rows": len(merged),
            "Null from Left (sales)": merged["transaction_id"].isnull().sum(),
            "Null from Right (customers)": merged["age"].isnull().sum(),
        })

    comparison_df = pd.DataFrame(results)
    st.dataframe(comparison_df, use_container_width=True, hide_index=True)

    # Employees per Store Aggregation + Join
    st.markdown("---")
    st.header("F. Store Summary (Aggregation + Join)")
    st.markdown("Joining aggregated employee stats with store information.")

    emp_agg = (
        employees.groupby("store_id")
        .agg(
            actual_employees=("employee_id", "count"),
            avg_salary=("salary", "mean"),
            avg_performance=("performance_score", "mean"),
        )
        .reset_index()
        .round(1)
    )

    store_summary = stores.merge(emp_agg, on="store_id", how="left")
    st.dataframe(store_summary, use_container_width=True, hide_index=True)


