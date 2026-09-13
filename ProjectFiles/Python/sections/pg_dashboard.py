import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import time

def render(data):
    stores = data["stores"]
    sales = data["sales"]
    products = data["products"]
    customers = data["customers"]
    employees = data["employees"]

    st.title(" BrewNest — Dashboard Overview")
    st.markdown(
        "Interactive overview of BrewNest Coffee Chain activity across **{}** stores "
        "in **{}** Romanian cities.".format(len(stores), stores["city"].nunique())
    )

    # Sidebar Controls 
    st.sidebar.markdown("---")
    st.sidebar.subheader("Dashboard Controls")
    
    selected_city = st.sidebar.selectbox(
        "Filter by City",
        ["All Cities"] + sorted(stores["city"].unique().tolist()),
    )
    
    date_range = st.sidebar.date_input(
        "Date Range",
        value=(sales["date"].min().date(), sales["date"].max().date()),
        min_value=sales["date"].min().date(),
        max_value=sales["date"].max().date(),
    )
    
    st.sidebar.markdown("---")
    if st.sidebar.button("Generate Regional Report"):
        progress_bar = st.sidebar.progress(0, text="Compiling data...")
        for i in range(100):
            time.sleep(0.01)
            progress_bar.progress(i + 1, text=f"Compiling... {i+1}%")
        st.sidebar.success("Report successfully generated!")

    # Apply filters
    filtered = sales.copy()
    if selected_city != "All Cities":
        city_stores = stores[stores["city"] == selected_city]["store_id"].tolist()
        filtered = filtered[filtered["store_id"].isin(city_stores)]
    if isinstance(date_range, tuple) and len(date_range) == 2:
        filtered = filtered[
            (filtered["date"] >= pd.Timestamp(date_range[0]))
            & (filtered["date"] <= pd.Timestamp(date_range[1]))
        ]

    # KPI Row
    total_rev = filtered["total_revenue"].sum()
    total_tx = len(filtered)
    avg_basket = filtered["total_revenue"].mean() if total_tx > 0 else 0
    # Loyalty rate across all customers to keep it simple
    loyalty_pct = customers["loyalty_member"].mean() * 100

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Revenue", f"{total_rev:,.0f} RON")
    c2.metric("Transactions", f"{total_tx:,}")
    c3.metric("Avg Basket", f"{avg_basket:.1f} RON")
    c4.metric("Global Loyalty Rate", f"{loyalty_pct:.1f}%")

    st.markdown("---")

    #  Interactive Charts 
    chart1, chart2 = st.columns(2)

    with chart1:
        st.markdown("**Revenue Trend**")
        if len(filtered) > 0:
            daily_rev = filtered.groupby(filtered['date'].dt.date)['total_revenue'].sum().reset_index()
            fig_line = px.line(daily_rev, x='date', y='total_revenue', 
                               labels={'date': 'Date', 'total_revenue': 'Daily Revenue (RON)'},
                               color_discrete_sequence=['#d4a76a'])
            fig_line.update_layout(height=350, margin=dict(l=0, r=0, t=10, b=0))
            st.plotly_chart(fig_line, use_container_width=True)
        else:
            st.info("No data available for this selection.")

    with chart2:
        st.markdown("**Revenue by Category**")
        if len(filtered) > 0:
            prod_stats = filtered.merge(products[['product_id', 'category']], on='product_id')
            cat_rev = prod_stats.groupby('category')['total_revenue'].sum().reset_index()
            fig_bar = px.bar(cat_rev, x='category', y='total_revenue', 
                             labels={'category': 'Category', 'total_revenue': 'Revenue (RON)'},
                             color='total_revenue', color_continuous_scale='Blues')
            fig_bar.update_layout(height=350, margin=dict(l=0, r=0, t=10, b=0), showlegend=False)
            st.plotly_chart(fig_bar, use_container_width=True)
        else:
            st.info("No data available for this selection.")

    # Raw Data Expander
    st.markdown("---")
    with st.expander("Explore Detailed Tables"):
        tab1, tab2, tab3 = st.tabs(["Store Overview", "Product Performance", "Employee Roster"])

        with tab1:
            store_rev = (filtered.groupby("store_id")["total_revenue"].sum().reset_index().rename(columns={"total_revenue": "revenue"}))
            store_view = stores.merge(store_rev, on="store_id", how="left").fillna(0)
            store_view["revenue"] = store_view["revenue"].round(0)
            st.dataframe(store_view[["store_id", "city", "region", "size_sqm", "monthly_rent", "employee_count", "revenue"]], use_container_width=True, hide_index=True)

        with tab2:
            if len(filtered) > 0:
                prod_details = (filtered.merge(products[["product_id", "name", "category"]], on="product_id")
                                .groupby(["category", "name"])
                                .agg(qty_sold=("quantity", "sum"), revenue=("total_revenue", "sum"))
                                .reset_index()
                                .sort_values("revenue", ascending=False))
                st.dataframe(prod_details, use_container_width=True, hide_index=True)

        with tab3:
            emp_view = employees.merge(stores[["store_id", "city"]], on="store_id")
            st.dataframe(emp_view[["employee_id", "name", "role", "city", "salary", "performance_score", "satisfaction_score"]], use_container_width=True, hide_index=True)
