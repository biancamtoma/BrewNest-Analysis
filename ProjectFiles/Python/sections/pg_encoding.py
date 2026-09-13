import streamlit as st
import pandas as pd
from sklearn.preprocessing import LabelEncoder, OneHotEncoder


def render(data):
    customers = data["customers"].copy()
    employees = data["employees"].copy()

    st.title("Encoding Methods")
    st.markdown(
        "Converting categorical variables into numerical representations "
        "required by machine learning algorithms."
    )

    # Clean NaNs first for encoding
    customers["gender"] = customers["gender"].fillna(customers["gender"].mode()[0])
    customers["income_bracket"] = customers["income_bracket"].fillna(customers["income_bracket"].mode()[0])

    st.markdown("---")
    show_raw = st.checkbox("Show raw datasets before encoding", key="show_raw_enc")
    if show_raw:
        st.write("**Raw Customers Data:**")
        st.dataframe(customers.head(), use_container_width=True)
        st.write("**Raw Employees Data:**")
        st.dataframe(employees.head(), use_container_width=True)

    encoding_method = st.radio(
        "Select encoding technique to explore:",
        ["Label Encoding (Ordinal)", "One-Hot Encoding (Nominal)"],
        horizontal=True
    )

    if "Label" in encoding_method:
        # Label Encoding
        st.header("A. Label Encoding (Ordinal Variables)")
        st.markdown(
            "**Use case:** Variables with a natural order. "
            "`income_bracket`: Low < Medium < High."
        )

        # Manual ordinal mapping
        ordinal_map = {"Low": 0, "Medium": 1, "High": 2}
        customers["income_encoded"] = customers["income_bracket"].map(ordinal_map)

        st.subheader("Income Bracket - Ordinal Mapping")
        mapping_df = pd.DataFrame(
            {"Original": list(ordinal_map.keys()), "Encoded": list(ordinal_map.values())}
        )
        st.dataframe(mapping_df, use_container_width=True, hide_index=True)

        col1, col2 = st.columns(2)
        with col1:
            st.write("**Before Encoding**")
            st.dataframe(
                customers[["customer_id", "income_bracket"]].head(10),
                use_container_width=True,
                hide_index=True,
            )
        with col2:
            st.write("**After Encoding**")
            st.dataframe(
                customers[["customer_id", "income_bracket", "income_encoded"]].head(10),
                use_container_width=True,
                hide_index=True,
            )

        # Sklearn LabelEncoder for gender
        st.subheader("Gender — Label Encoding (sklearn)")
        le = LabelEncoder()
        customers["gender_encoded"] = le.fit_transform(customers["gender"])

        le_mapping = pd.DataFrame(
            {"Class": le.classes_, "Encoded": range(len(le.classes_))}
        )
        st.dataframe(le_mapping, use_container_width=True, hide_index=True)
        st.dataframe(
            customers[["customer_id", "gender", "gender_encoded"]].head(10),
            use_container_width=True,
            hide_index=True,
        )

    elif "One-Hot" in encoding_method:
        # One-Hot Encoding
        st.markdown("---")
        st.header("B. One-Hot Encoding (Nominal Variables)")
        st.markdown(
            "**Use case:** Variables without natural order. "
            "Each unique category becomes a binary column."
        )

        # Employee roles
        st.subheader("Employee Role - One-Hot Encoding")
        role_dummies = pd.get_dummies(employees["role"], prefix="role")
        emp_encoded = pd.concat([employees[["employee_id", "role"]], role_dummies], axis=1)

        st.write(f"**Original:** 1 column (role) → **Encoded:** {len(role_dummies.columns)} binary columns")
        st.dataframe(emp_encoded.head(10), use_container_width=True, hide_index=True)

        # Customer city - top 5 only to keep it manageable
        st.subheader("Customer City - One-Hot Encoding (Top 5 cities)")
        top5 = customers["city"].value_counts().head(5).index.tolist()
        customers["city_top5"] = customers["city"].apply(lambda x: x if x in top5 else "Other")
        city_dummies = pd.get_dummies(customers["city_top5"], prefix="city")
        city_encoded = pd.concat([customers[["customer_id", "city"]], city_dummies], axis=1)

        st.dataframe(city_encoded.head(10), use_container_width=True, hide_index=True)

        # One - Hot Encoder 
        st.markdown("---")
        st.header("C. Sklearn OneHotEncoder")
        st.markdown("Using `OneHotEncoder` from scikit-learn with `sparse_output=False`.")

        ohe = OneHotEncoder(sparse_output=False, drop="first")
        gender_ohe = ohe.fit_transform(customers[["gender"]])
        ohe_cols = ohe.get_feature_names_out(["gender"])
        ohe_df = pd.DataFrame(gender_ohe, columns=ohe_cols)
        ohe_result = pd.concat(
            [customers[["customer_id", "gender"]].reset_index(drop=True), ohe_df], axis=1
        )
        st.dataframe(ohe_result.head(10), use_container_width=True, hide_index=True)
        st.info(
            "**Note:** `drop='first'` avoids the dummy variable trap by removing one "
            "redundant category (useful for regression models)."
        )

    
