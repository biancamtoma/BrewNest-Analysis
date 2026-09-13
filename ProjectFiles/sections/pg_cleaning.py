import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objects as go
import plotly.express as px


def render(data):
    sales = data["sales"].copy()
    customers = data["customers"].copy()
    employees = data["employees"].copy()

    st.title(" Data Cleaning - Missing & Extreme Values")
    st.markdown(
        "Detecting, analyzing, and treating missing values and outliers "
        "across BrewNest datasets."
    )

    
    # SECTION A: MISSING VALUES
    st.header("A. Missing Values Analysis")

    tab_cust, tab_emp, tab_sales = st.tabs(["Customers", "Employees", "Sales"])

    with tab_cust:
        st.subheader("Customers - Missing Values")
        miss = customers.isnull().sum()
        miss_pct = (customers.isnull().sum() / len(customers) * 100).round(2)
        miss_df = pd.DataFrame({"Missing Count": miss, "Missing %": miss_pct})
        miss_df = miss_df[miss_df["Missing Count"] > 0]
        st.dataframe(miss_df, use_container_width=True)

        # Heatmap
        st.markdown("**Missing Values Heatmap - Customers**")
        fig_hm = go.Figure(data=go.Heatmap(
            z=customers.isnull().T.values.astype(int),
            x=customers.index,
            y=customers.columns,
            colorscale="Blues",
            showscale=False,
            hoverongaps=False
        ))
        fig_hm.update_layout(
            xaxis_title="Row Index",
            height=350,
            margin=dict(l=0, r=0, t=10, b=30)
        )
        st.plotly_chart(fig_hm, use_container_width=True)

        #Filling in the values 
        st.subheader("Filling in the values Strategy")
        cust_clean = customers.copy()
        median_age = cust_clean["age"].median()
        mode_gender = cust_clean["gender"].mode()[0]
        mode_income = cust_clean["income_bracket"].mode()[0]

        cust_clean["age"] = cust_clean["age"].fillna(median_age)
        cust_clean["gender"] = cust_clean["gender"].fillna(mode_gender)
        cust_clean["income_bracket"] = cust_clean["income_bracket"].fillna(mode_income)

        col1, col2, col3 = st.columns(3)
        col1.metric("Age computed with median", f"{median_age:.0f}")
        col2.metric("Gender computed with mode", mode_gender)
        col3.metric("Income computed with mode", mode_income)
        st.success(
            f"After computation: {cust_clean.isnull().sum().sum()} missing values remain."
        )

    with tab_emp:
        st.subheader("Employees - Missing Values")
        miss_e = employees.isnull().sum()
        miss_e_pct = (employees.isnull().sum() / len(employees) * 100).round(2)
        miss_e_df = pd.DataFrame({"Missing Count": miss_e, "Missing %": miss_e_pct})
        miss_e_df = miss_e_df[miss_e_df["Missing Count"] > 0]
        st.dataframe(miss_e_df, use_container_width=True)

        emp_clean = employees.copy()
        for col in ["performance_score", "satisfaction_score"]:
            med = emp_clean[col].median()
            emp_clean[col] = emp_clean[col].fillna(med)
            st.info(f"**{col}** computed with median = {med:.1f}")
        st.success(
            f"After computation: {emp_clean.isnull().sum().sum()} missing values remain."
        )

    with tab_sales:
        st.subheader("Sales - Missing customer_id (walk-in customers)")
        null_cust = sales["customer_id"].isnull().sum()
        st.metric("Null customer_id", f"{null_cust:,} ({null_cust/len(sales)*100:.1f}%)")
        st.info(
            "These represent walk-in customers without loyalty accounts. "
            "We keep them as-is for revenue analysis but exclude them from "
            "customer-level analysis."
        )

    # SECTION B: EXTREME VALUES (OUTLIERS)
    st.markdown("---")
    st.header("B. Extreme Values (Outliers)")

    st.subheader("Outlier Removal - Sales Revenue")

    df = sales
    selected_column = "total_revenue"

    Q1 = df[selected_column].quantile(0.25)
    Q3 = df[selected_column].quantile(0.75)
    IQR = Q3 - Q1
    lower_bound, upper_bound = Q1 - 1.5 * IQR, Q3 + 1.5 * IQR
    df_cleaned = df[(df[selected_column] >= lower_bound) & (df[selected_column] <= upper_bound)]

    outliers_removed = len(df) - len(df_cleaned)

    st.markdown("**Outlier removal**")
    fig_after = px.histogram(df_cleaned, x=selected_column, nbins=30, title="Cleaned")
    fig_after.update_layout(height=350)
    st.plotly_chart(fig_after, use_container_width=True)
    st.write(f"Total rows: {len(df_cleaned)} (removed {outliers_removed})")

    

    st.markdown("---")
    st.subheader("Download Cleaned Data")
    csv_data = df_cleaned.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="Download Cleaned Sales Data (CSV)",
        data=csv_data,
        file_name="cleaned_sales.csv",
        mime="text/csv"
    )
