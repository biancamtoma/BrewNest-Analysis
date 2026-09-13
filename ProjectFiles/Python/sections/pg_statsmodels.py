"""Page 9 — Multiple Regression (Statsmodels)"""
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import statsmodels.api as sm
from scipy import stats


def render(data):
    stores = data["stores"].copy()
    sales = data["sales"].copy()

    st.title(" Regression Analysis — Statsmodels")
    st.markdown(
        "**Problem:** Predict monthly store revenue based on store characteristics "
        "to guide expansion decisions — which features matter most for a new store's success?"
    )

    # Build regression dataset 
    st.header("A. Data Preparation")

    # Monthly revenue per store
    sales["year_month"] = sales["date"].dt.to_period("M")
    monthly_rev = (
        sales.groupby(["store_id", "year_month"])["total_revenue"]
        .sum()
        .reset_index()
    )
    avg_monthly = (
        monthly_rev.groupby("store_id")["total_revenue"]
        .mean()
        .reset_index()
        .rename(columns={"total_revenue": "avg_monthly_revenue"})
    )

    # Merge with store features
    reg_data = stores.merge(avg_monthly, on="store_id")
    reg_data["months_open"] = (
        (pd.Timestamp("2024-12-31") - reg_data["opening_date"]).dt.days / 30
    ).round(0)

    st.write(f"**Observations:** {len(reg_data)} stores")
    st.dataframe(
        reg_data[["store_id", "city", "size_sqm", "monthly_rent", "employee_count",
                   "city_population", "months_open", "avg_monthly_revenue"]].round(0),
        use_container_width=True,
        hide_index=True,
    )

    # Feature Selection 
    st.header("B. Feature Selection")
    available_features = ["size_sqm", "monthly_rent", "employee_count", "city_population", "months_open"]
    selected = st.multiselect(
        "Select predictor variables:",
        available_features,
        default=available_features,
    )

    if len(selected) < 1:
        st.warning("Please select at least one predictor variable.")
        return

    #  OLS Regression 
    st.header("C. OLS Regression Results")

    X = reg_data[selected]
    y = reg_data["avg_monthly_revenue"]
    X_const = sm.add_constant(X)

    model = sm.OLS(y, X_const).fit()

    st.subheader("Model Summary")
    summary_text = model.summary().as_text()
    st.code(summary_text, language="text")

    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("R-squared", f"{model.rsquared:.4f}")
    col2.metric("Adj. R-squared", f"{model.rsquared_adj:.4f}")
    col3.metric("F-statistic", f"{model.fvalue:.2f}")
    col4.metric("Prob (F)", f"{model.f_pvalue:.4f}")

    #  Coefficients 
    st.subheader("Coefficient Interpretation")
    coef_df = pd.DataFrame({
        "Variable": model.params.index,
        "Coefficient": model.params.values.round(2),
        "Std Error": model.bse.values.round(2),
        "t-value": model.tvalues.values.round(3),
        "p-value": model.pvalues.values.round(4),
        "Significant (p<0.05)": ["Yes" if p < 0.05 else "No" for p in model.pvalues],
    })
    st.dataframe(coef_df, use_container_width=True, hide_index=True)

    st.markdown("**Interpretation of significant coefficients:**")
    for _, row in coef_df.iterrows():
        if row["Variable"] != "const" and row["p-value"] < 0.05:
            direction = "increases" if row["Coefficient"] > 0 else "decreases"
            st.markdown(
                f"- A one-unit increase in **{row['Variable']}** {direction} "
                f"average monthly revenue by **{abs(row['Coefficient']):,.2f} RON** "
                f"(p = {row['p-value']:.4f})"
            )

    # Residual Analysis 
    st.markdown("---")
    st.header("D. Residual Analysis")

    residuals = model.resid
    fitted = model.fittedvalues

    plt.rcParams.update({
        "figure.facecolor": "#0e1117", "axes.facecolor": "#0e1117",
        "text.color": "#fafafa", "axes.labelcolor": "#fafafa",
        "xtick.color": "#ccc", "ytick.color": "#ccc",
    })

    fig, axes = plt.subplots(2, 2, figsize=(12, 9))

    # 1. Residuals vs Fitted
    axes[0, 0].scatter(fitted, residuals, color="#d4a76a", alpha=0.7, edgecolor="white", s=60)
    axes[0, 0].axhline(0, color="#ff6b6b", linestyle="--", linewidth=1)
    axes[0, 0].set_xlabel("Fitted Values")
    axes[0, 0].set_ylabel("Residuals")
    axes[0, 0].set_title("Residuals vs Fitted", fontweight="bold", color="#d4a76a")

    # 2. Q-Q plot
    (osm, osr), (slope, intercept, r) = stats.probplot(residuals, dist="norm")
    axes[0, 1].scatter(osm, osr, color="#6abd6a", alpha=0.7, edgecolor="white", s=60)
    axes[0, 1].plot(osm, slope * np.array(osm) + intercept, "--", color="#ff6b6b", linewidth=1.5)
    axes[0, 1].set_xlabel("Theoretical Quantiles")
    axes[0, 1].set_ylabel("Sample Quantiles")
    axes[0, 1].set_title("Q-Q Plot (Normality Check)", fontweight="bold", color="#d4a76a")

    # 3. Histogram of residuals
    axes[1, 0].hist(residuals, bins=8, color="#6a9bd4", edgecolor="white", alpha=0.8)
    axes[1, 0].set_xlabel("Residual Value")
    axes[1, 0].set_ylabel("Count")
    axes[1, 0].set_title("Residual Distribution", fontweight="bold", color="#d4a76a")

    # 4. Actual vs Predicted
    axes[1, 1].scatter(y, fitted, color="#d4a76a", alpha=0.7, edgecolor="white", s=60)
    min_val = min(y.min(), fitted.min())
    max_val = max(y.max(), fitted.max())
    axes[1, 1].plot([min_val, max_val], [min_val, max_val], "--", color="#ff6b6b", linewidth=1.5)
    axes[1, 1].set_xlabel("Actual Revenue (RON)")
    axes[1, 1].set_ylabel("Predicted Revenue (RON)")
    axes[1, 1].set_title("Actual vs Predicted", fontweight="bold", color="#d4a76a")

    fig.suptitle("Regression Diagnostics", fontsize=15, fontweight="bold", color="#d4a76a", y=1.01)
    fig.tight_layout()
    st.pyplot(fig)
    plt.close()

    # Prediction for expansion 
    st.markdown("---")
    st.header("E. Expansion Scenario - Revenue Prediction")
    st.markdown(
        "Use the model to predict expected monthly revenue for a hypothetical new store."
    )

    with st.form("expansion_prediction_form"):
        col_a, col_b = st.columns(2)
        with col_a:
            new_size = st.number_input("Store Size (sqm)", 50, 300, 120)
            new_rent = st.number_input("Monthly Rent (RON)", 1500, 15000, 4500)
            new_emp = st.number_input("Employees", 3, 15, 6)
        with col_b:
            new_pop = st.number_input("City Population", 50000, 2000000, 200000)
            new_months = st.number_input("Months Open (projection)", 1, 60, 12)
            
        submit_prediction = st.form_submit_button("Predict Expected Revenue")

    # Calculate prediction always, so predicted_rev is bound
    new_data = {"const": 1}
    input_map = {
        "size_sqm": new_size, "monthly_rent": new_rent,
        "employee_count": new_emp, "city_population": new_pop,
        "months_open": new_months,
    }
    for feat in selected:
        new_data[feat] = input_map[feat]

    new_df = pd.DataFrame([new_data])
    predicted_rev = model.predict(new_df)[0]

    if submit_prediction:
        with st.spinner("Calculating projection..."):
            import time
            time.sleep(0.4)
            
        st.success("Projection calculated successfully!")
        st.metric("Predicted Avg Monthly Revenue", f"{predicted_rev:,.0f} RON", delta="Estimated")
        st.metric("Projected Annual Revenue", f"{predicted_rev * 12:,.0f} RON", delta="Annualized")

    st.markdown(
        "**Economic Interpretation:** The regression model quantifies how each store "
        "characteristic contributes to revenue. This enables data-driven expansion "
        "decisions: BrewNest can evaluate potential locations by plugging in their "
        "characteristics and comparing predicted revenue against required investment. "
        "For example, a 120 sqm store in a city of 200,000 is predicted to generate "
        f"approximately {predicted_rev:,.0f} RON/month."
    )
