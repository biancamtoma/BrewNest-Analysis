"""Page 4 — Scaling Methods"""
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler, MinMaxScaler


def render(data):
    employees = data["employees"].copy()
    stores = data["stores"].copy()
    sales = data["sales"].copy()

    st.title(" Scaling Methods")
    st.markdown(
        "Normalizing feature scales so that no single variable dominates "
        "machine learning models due to its magnitude."
    )

    # Prepare numerical features
    employees["performance_score"] = employees["performance_score"].fillna(employees["performance_score"].median())
    employees["satisfaction_score"] = employees["satisfaction_score"].fillna(employees["satisfaction_score"].median())

    features = employees[["salary", "performance_score", "satisfaction_score"]].copy()

    st.header("Original Data — Different Scales")
    st.dataframe(features.describe().round(2), use_container_width=True)
    st.warning(
        "**Problem:** Salary ranges 2800-7400, while scores range 2-10. "
        "Distance-based algorithms (K-Means, KNN) would be dominated by salary."
    )

    # ── Standard Scaler ─────────────────────────────────────
    st.markdown("---")
    st.header("A. StandardScaler (Z-score Normalization)")
    st.latex(r"z = \frac{x - \mu}{\sigma}")
    st.markdown("Transforms data to have **mean = 0** and **std = 1**.")

    scaler_std = StandardScaler()
    features_std = pd.DataFrame(
        scaler_std.fit_transform(features),
        columns=[f"{c}_std" for c in features.columns],
    )

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Before Scaling")
        st.dataframe(features.describe().round(2), use_container_width=True)
    with col2:
        st.subheader("After StandardScaler")
        st.dataframe(features_std.describe().round(2), use_container_width=True)

    # ── MinMax Scaler ───────────────────────────────────────
    st.markdown("---")
    st.header("B. MinMaxScaler (0–1 Normalization)")
    st.latex(r"x_{scaled} = \frac{x - x_{min}}{x_{max} - x_{min}}")
    st.markdown("Transforms all values to the **[0, 1]** range.")

    scaler_mm = MinMaxScaler()
    features_mm = pd.DataFrame(
        scaler_mm.fit_transform(features),
        columns=[f"{c}_mm" for c in features.columns],
    )

    col3, col4 = st.columns(2)
    with col3:
        st.subheader("Before Scaling")
        st.dataframe(features.describe().round(2), use_container_width=True)
    with col4:
        st.subheader("After MinMaxScaler")
        st.dataframe(features_mm.describe().round(2), use_container_width=True)

    # ── Visual Comparison ───────────────────────────────────
    st.markdown("---")
    st.header("C. Visual Comparison")

    fig, axes = plt.subplots(3, 3, figsize=(14, 10))
    colors = ["#d4a76a", "#6abd6a", "#6a9bd4"]

    for i, col in enumerate(features.columns):
        axes[i, 0].hist(features[col], bins=20, color=colors[i], edgecolor="white", alpha=0.85)
        axes[i, 0].set_title(f"Original: {col}", fontsize=10)

        axes[i, 1].hist(features_std.iloc[:, i], bins=20, color=colors[i], edgecolor="white", alpha=0.85)
        axes[i, 1].set_title(f"StandardScaler: {col}", fontsize=10)

        axes[i, 2].hist(features_mm.iloc[:, i], bins=20, color=colors[i], edgecolor="white", alpha=0.85)
        axes[i, 2].set_title(f"MinMaxScaler: {col}", fontsize=10)

    fig.suptitle("Feature Distributions: Original vs Scaled", fontsize=14, fontweight="bold")
    fig.tight_layout(rect=[0, 0, 1, 0.96])
    st.pyplot(fig)
    plt.close()

    # ── When to use which ───────────────────────────────────
    st.markdown("---")
    st.header("D. When to Use Which Scaler?")

    comparison = pd.DataFrame({
        "Criterion": [
            "Output range", "Sensitive to outliers", "Preserves distribution shape",
            "Best for", "Mean after scaling", "Std after scaling"
        ],
        "StandardScaler": [
            "Unbounded", "Moderate", "Yes",
            "PCA, Logistic Regression, SVM", "0", "1"
        ],
        "MinMaxScaler": [
            "[0, 1]", "High", "Yes",
            "Neural Networks, KNN, K-Means", "Depends on data", "Depends on data"
        ],
    })
    st.dataframe(comparison, use_container_width=True, hide_index=True)
