import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    confusion_matrix, classification_report, accuracy_score,
    ConfusionMatrixDisplay,
)


def render(data):
    sales = data["sales"].copy()
    customers = data["customers"].copy()

    st.title(" Machine Learning — Scikit-learn")

    tab_clust, tab_logreg = st.tabs(["Customer Clustering (K-Means)", "Loyalty Prediction (Logistic Regression)"])

    # A. CLUSTERING

    with tab_clust:
        st.header("A. Customer Segmentation — K-Means Clustering")
        st.markdown(
            "**Problem:** Segment customers by purchasing behavior to identify "
            "high-value, regular, and dormant customer groups for targeted marketing."
        )

        # Build customer features from sales
        cust_sales = sales.dropna(subset=["customer_id"])
        cust_features = (
            cust_sales.groupby("customer_id")
            .agg(
                total_spend=("total_revenue", "sum"),
                frequency=("transaction_id", "count"),
                avg_basket=("total_revenue", "mean"),
            )
            .reset_index()
        )
        cust_features = cust_features.merge(
            customers[["customer_id", "loyalty_member"]], on="customer_id", how="left"
        )

        st.subheader("Customer Features (RFM-style)")
        st.dataframe(cust_features.describe().round(2), use_container_width=True)

        # Scale
        feature_cols = ["total_spend", "frequency", "avg_basket"]
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(cust_features[feature_cols])

        # Elbow method
        st.subheader("Optimal K — Elbow Method")
        K_range = range(2, 9)
        inertias = []
        for k in K_range:
            km = KMeans(n_clusters=k, random_state=42, n_init=10)
            km.fit(X_scaled)
            inertias.append(km.inertia_)

        plt.rcParams.update({
            "figure.facecolor": "#0e1117", "axes.facecolor": "#0e1117",
            "text.color": "#fafafa", "axes.labelcolor": "#fafafa",
            "xtick.color": "#ccc", "ytick.color": "#ccc",
        })

        fig_elbow, ax_e = plt.subplots(figsize=(8, 4))
        ax_e.plot(list(K_range), inertias, "o-", color="#d4a76a", linewidth=2)
        ax_e.set_xlabel("Number of Clusters (K)")
        ax_e.set_ylabel("Inertia (Within-cluster Sum of Squares)")
        ax_e.set_title("Elbow Method", fontsize=13, fontweight="bold", color="#d4a76a")
        ax_e.grid(alpha=0.3)
        fig_elbow.tight_layout()
        st.pyplot(fig_elbow)
        plt.close()

        # Fit final model
        with st.form("cluster_form"):
            st.subheader("Configure K-Means")
            n_clusters = st.slider("Select K (number of clusters)", 2, 8, 4)
            submit_cluster = st.form_submit_button("Run Clustering")
            
        if submit_cluster:
            with st.spinner(f"Clustering customers into {n_clusters} segments..."):
                import time
                time.sleep(0.5)
                
        kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        cust_features["cluster"] = kmeans.fit_predict(X_scaled)

        # Cluster profiles
        st.subheader("Cluster Profiles")
        profiles = (
            cust_features.groupby("cluster")[feature_cols + ["loyalty_member"]]
            .mean()
            .round(2)
        )
        profiles["count"] = cust_features.groupby("cluster")["customer_id"].count()
        st.dataframe(profiles, use_container_width=True)

        # Labels
        cluster_labels = {}
        for c in range(n_clusters):
            spend = profiles.loc[c, "total_spend"]
            freq = profiles.loc[c, "frequency"]
            if spend > profiles["total_spend"].median() and freq > profiles["frequency"].median():
                cluster_labels[c] = "High-Value Regulars"
            elif spend > profiles["total_spend"].median():
                cluster_labels[c] = "Big Spenders"
            elif freq > profiles["frequency"].median():
                cluster_labels[c] = "Frequent Visitors"
            else:
                cluster_labels[c] = "Occasional / Dormant"

        label_df = pd.DataFrame(
            {"Cluster": list(cluster_labels.keys()), "Label": list(cluster_labels.values())}
        )
        st.dataframe(label_df, use_container_width=True, hide_index=True)

        # Visualization
        st.subheader("Cluster Visualization")
        fig_c, ax_c = plt.subplots(figsize=(10, 6))
        scatter = ax_c.scatter(
            cust_features["total_spend"], cust_features["frequency"],
            c=cust_features["cluster"], cmap="Set2", alpha=0.6, s=30, edgecolor="none",
        )
        ax_c.set_xlabel("Total Spend (RON)", fontsize=11)
        ax_c.set_ylabel("Purchase Frequency", fontsize=11)
        ax_c.set_title("Customer Clusters", fontsize=14, fontweight="bold", color="#d4a76a")
        plt.colorbar(scatter, ax=ax_c, label="Cluster")
        fig_c.tight_layout()
        st.pyplot(fig_c)
        plt.close()



    # B. LOGISTIC REGRESSION

    with tab_logreg:
        st.header("B. Loyalty Program Prediction — Logistic Regression")
        st.markdown(
            "**Problem:** Predict whether a customer will join the loyalty program "
            "based on demographics and purchasing behavior, to target acquisition campaigns."
        )

        # Build features
        cust_sales = sales.dropna(subset=["customer_id"])
        cust_agg = (
            cust_sales.groupby("customer_id")
            .agg(
                total_spend=("total_revenue", "sum"),
                frequency=("transaction_id", "count"),
                avg_basket=("total_revenue", "mean"),
            )
            .reset_index()
        )
        model_data = customers.merge(cust_agg, on="customer_id", how="inner")
        model_data = model_data.dropna(subset=["age", "gender", "income_bracket"])

        # Encode
        model_data["gender_num"] = model_data["gender"].map({"F": 0, "M": 1})
        model_data["income_num"] = model_data["income_bracket"].map({"Low": 0, "Medium": 1, "High": 2})
        model_data = model_data.dropna(subset=["gender_num", "income_num"])

        feature_cols_lr = ["age", "gender_num", "income_num", "total_spend", "frequency", "avg_basket"]
        X = model_data[feature_cols_lr]
        y = model_data["loyalty_member"]

        st.subheader("Features & Target")
        st.write(f"**Samples:** {len(X):,}  |  **Features:** {len(feature_cols_lr)}")
        st.write(f"**Target distribution:** {dict(y.value_counts())}")

        # Session state for training history
        if "lr_history" not in st.session_state:
            st.session_state.lr_history = []

        with st.form("lr_model_form"):
            st.subheader("Model Configuration")
            col_f1, col_f2 = st.columns(2)
            with col_f1:
                test_size = st.slider("Test set size (%)", 10, 40, 25) / 100
            with col_f2:
                max_iter = st.number_input("Max Iterations", 100, 2000, 1000, step=100)
            
            submit_train = st.form_submit_button("Train Logistic Regression Model")

        if submit_train:
            with st.spinner("Training model..."):
                import time
                time.sleep(0.5)  # Simulate slow computation
                
                X_train, X_test, y_train, y_test = train_test_split(
                    X, y, test_size=test_size, random_state=42, stratify=y
                )
                
                lr = LogisticRegression(random_state=42, max_iter=max_iter)
                lr.fit(X_train, y_train)
                y_pred = lr.predict(X_test)
                
                acc = accuracy_score(y_test, y_pred)
                st.session_state.lr_history.append({"Test Size": test_size, "Max Iter": max_iter, "Accuracy": round(acc, 4)})

            st.success(f"Training Complete! Accuracy: **{acc:.2%}**")

            if st.session_state.lr_history:
                st.write("**Training History (Session State):**")
                st.dataframe(pd.DataFrame(st.session_state.lr_history), use_container_width=True)

            # Results
            st.subheader("Model Performance")
            st.metric("Accuracy", f"{acc:.2%}")

            # Confusion matrix
            cm = confusion_matrix(y_test, y_pred)
            fig_cm, ax_cm = plt.subplots(figsize=(6, 5))
            disp = ConfusionMatrixDisplay(cm, display_labels=["Non-Loyal", "Loyal"])
            disp.plot(ax=ax_cm, cmap="YlOrBr")
            ax_cm.set_title("Confusion Matrix", fontsize=13, fontweight="bold")
            fig_cm.tight_layout()
            st.pyplot(fig_cm)
            plt.close()

            # Classification report
            st.subheader("Classification Report")
            report = classification_report(y_test, y_pred, target_names=["Non-Loyal", "Loyal"],
                                           output_dict=True)
            st.dataframe(pd.DataFrame(report).T.round(3), use_container_width=True)

            # Feature importance
            st.subheader("Feature Importance (Coefficients)")
            coef_df = pd.DataFrame({
                "Feature": feature_cols_lr,
                "Coefficient": lr.coef_[0].round(4),
            }).sort_values("Coefficient", key=abs, ascending=False)

            fig_fi, ax_fi = plt.subplots(figsize=(8, 4))
            colors_fi = ["#6abd6a" if c > 0 else "#d46a6a" for c in coef_df["Coefficient"]]
            ax_fi.barh(coef_df["Feature"], coef_df["Coefficient"], color=colors_fi)
            ax_fi.set_xlabel("Coefficient")
            ax_fi.set_title("Logistic Regression Coefficients", fontsize=13, fontweight="bold", color="#d4a76a")
            ax_fi.axvline(0, color="#555", linewidth=0.8)
            fig_fi.tight_layout()
            st.pyplot(fig_fi)
            plt.close()

            st.markdown(
                "**Economic Interpretation:** The model identifies which customer attributes "
                "most strongly predict loyalty membership. Higher spending and purchase frequency "
                "are the strongest positive predictors. BrewNest can use these insights to target "
                "non-loyal customers who exhibit similar spending patterns with loyalty program "
                "promotions, improving conversion rates and customer lifetime value."
            )
